"""
LTX-Flow Pipeline — GitHub Actions CI
LTX-Video 2.3 (free ZeroGPU) + Hinglish TTS + synced captions + Hindi YouTube titles.
"""

import json
import os
import random
import subprocess
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

import requests

import checkpoint as ckpt
import cleanup
from prompt_engine import generate_prompt, generate_title, generate_fact_and_subtitle, NICHES
from video_generator import generate_clip

# ─── CONFIG ───────────────────────────────────────────────────────────────────
BASE_DIR   = Path(".")
MUSIC_DIR  = BASE_DIR / "music"
OUTPUT_DIR = BASE_DIR / "output"
TEMP_DIR   = OUTPUT_DIR / "temp"
MUSIC_LIB  = BASE_DIR / "music_library.json"

CLIPS_PER_SHORT = 3
POSTS_PER_DAY   = 6
MUSIC_VOLUME    = 0.08   # background music — very low, LTX audio is primary
LTX_AUDIO_VOL   = 0.45  # LTX native ASMR audio
TTS_VOLUME      = 1.2    # Hindi narration at full
MAX_DURATION    = 59
CLIP_DURATION   = 8      # seconds — LTX generates up to 10s

TTS_VOICE = "hi-IN-SwaraNeural"
TTS_DELAY = 0.9

TG_TOKEN       = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TG_CHAT_ID     = os.environ.get("TELEGRAM_CHAT_ID", "")
FORCE_RUN      = os.environ.get("FORCE_RUN", "false").lower() == "true"
SHEET_ID       = os.environ.get("SHEET_ID", "")
SARVAM_API_KEY = os.environ.get("SARVAM_API_KEY", "")

SARVAM_CREDIT_WARN = 25000   # alert when total chars used exceeds this (~75% of free ₹100)

for d in [MUSIC_DIR, OUTPUT_DIR, TEMP_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ─── TELEGRAM ─────────────────────────────────────────────────────────────────
def tg(msg, parse_mode="Markdown"):
    if not TG_TOKEN or not TG_CHAT_ID:
        print(f"[TG] {msg}")
        return
    try:
        payload = {"chat_id": TG_CHAT_ID, "text": msg}
        if parse_mode:
            payload["parse_mode"] = parse_mode
        requests.post(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            json=payload, timeout=10
        )
    except Exception:
        pass

def tg_error(context, exc):
    """Send error summary to Telegram with traceback snippet."""
    tb = traceback.format_exc()
    short_tb = tb[-800:] if len(tb) > 800 else tb
    msg = (
        f"❌ *LTX Pipeline Failed*\n"
        f"Step: `{context}`\n"
        f"Error: `{str(exc)[:200]}`\n\n"
        f"```\n{short_tb}\n```"
    )
    tg(msg)

# ─── GOOGLE SHEETS ────────────────────────────────────────────────────────────
def log_to_sheet(row: list):
    """Append one row to the LTX tracking sheet."""
    if not SHEET_ID:
        return
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

        creds = Credentials.from_authorized_user_file("drive_token.json", [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ])
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        svc = build("sheets", "v4", credentials=creds, cache_discovery=False)
        svc.spreadsheets().values().append(
            spreadsheetId=SHEET_ID,
            range="Sheet1!A1",
            valueInputOption="USER_ENTERED",
            body={"values": [row]},
        ).execute()
        print(f"  Sheet logged: {row[0]}")
    except Exception as e:
        print(f"  Sheet log failed: {e}")

# ─── TRACKER ──────────────────────────────────────────────────────────────────
TRACKER_FILE = Path("tracker.json")

def load_tracker():
    if TRACKER_FILE.exists():
        with open(TRACKER_FILE) as f:
            return json.load(f)
    return {"used_prompts": [], "used_music": [], "posts_today": [], "total_posts": 0}

def save_tracker(data):
    with open(TRACKER_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ─── MUSIC ────────────────────────────────────────────────────────────────────
def select_music(tracker):
    with open(MUSIC_LIB) as f:
        library = json.load(f)

    recently_used = tracker.get("used_music", [])[-5:]
    available = [t for t in library["tracks"] if t["id"] not in recently_used]
    if not available:
        available = library["tracks"]

    CHILL_VIBES = {
        "edm-chill", "edm-emotional", "edm-feel-good", "edm-sunrise",
        "edm-uplifting", "edm-happy", "edm-vibrant", "edm-summer",
        "edm-motivational"
    }
    chill = [t for t in available if t["vibe"] in CHILL_VIBES]
    pool = chill if chill else available
    selected = random.choice(pool)

    # Fall back to all tracks to always find a file on disk
    for candidate in [selected] + pool + library["tracks"]:
        f = MUSIC_DIR / f"track_{candidate['id']}.mp3"
        if f.exists():
            return candidate, f

    raise RuntimeError(f"No music files in {MUSIC_DIR}/. Files: {list(MUSIC_DIR.glob('*.mp3'))}")

# ─── TTS ──────────────────────────────────────────────────────────────────────
def generate_tts(tts_text, output_path, tracker=None):
    """
    Hindi TTS via Sarvam AI (bulbul:v2, meera voice).
    Falls back to edge-tts if Sarvam key missing.
    Returns (audio_path, word_timings=[]) — Sarvam has no word timings.
    """
    if SARVAM_API_KEY:
        try:
            resp = requests.post(
                "https://api.sarvam.ai/text-to-speech",
                headers={"api-subscription-key": SARVAM_API_KEY, "Content-Type": "application/json"},
                json={
                    "inputs": [tts_text],
                    "target_language_code": "hi-IN",
                    "speaker": "meera",
                    "pitch": 0,
                    "pace": 1.1,
                    "loudness": 1.5,
                    "speech_sample_rate": 22050,
                    "enable_preprocessing": True,
                    "model": "bulbul:v2",
                },
                timeout=60
            )
            if resp.status_code == 200:
                import base64
                audio_b64 = resp.json()["audios"][0]
                audio_bytes = base64.b64decode(audio_b64)
                Path(output_path).write_bytes(audio_bytes)
                size_kb = len(audio_bytes) // 1024
                print(f"  TTS OK (Sarvam) — {size_kb} KB")

                # Track chars used and alert if nearing limit
                if tracker is not None:
                    used = tracker.get("sarvam_chars_used", 0) + len(tts_text)
                    tracker["sarvam_chars_used"] = used
                    if used > SARVAM_CREDIT_WARN:
                        tg(f"Sarvam TTS credit warning!\n{used:,} chars used — free credits (~33K chars) nearly exhausted.\nCreate a new account at sarvam.ai and update the SARVAM_API_KEY secret in ltxflows repo.", parse_mode=None)

                return Path(output_path), []
            else:
                print(f"  Sarvam TTS failed ({resp.status_code}): {resp.text[:200]}")
        except Exception as e:
            print(f"  Sarvam TTS error: {e}")

    # Fallback: edge-tts
    print("  Falling back to edge-tts...")
    try:
        import asyncio, edge_tts
        words = []

        async def _synth():
            comm = edge_tts.Communicate(tts_text, voice=TTS_VOICE, rate="+8%")
            buf = bytearray()
            async for chunk in comm.stream():
                if chunk["type"] == "audio": buf += chunk["data"]
                elif chunk["type"] == "WordBoundary":
                    words.append({"word": chunk["text"],
                        "start": chunk["offset"] / 10_000_000,
                        "end":   (chunk["offset"] + chunk["duration"]) / 10_000_000})
            Path(output_path).write_bytes(bytes(buf))

        asyncio.run(_synth())
        if Path(output_path).exists() and Path(output_path).stat().st_size > 0:
            print(f"  TTS OK (edge-tts) — {Path(output_path).stat().st_size//1024} KB, {len(words)} word events")
            return Path(output_path), words
    except Exception as e:
        print(f"  TTS failed: {e}")
    return None, []


def build_srt(words, offset=TTS_DELAY, words_per_phrase=4):
    """Group word timings into 4-word phrases → SRT content string."""
    def _fmt(s):
        h = int(s // 3600)
        m = int((s % 3600) // 60)
        sec = s % 60
        return f"{h:02d}:{m:02d}:{sec:06.3f}".replace(".", ",")

    lines = []
    idx = 1
    for i in range(0, len(words), words_per_phrase):
        phrase = words[i:i + words_per_phrase]
        start  = phrase[0]["start"] + offset
        end    = phrase[-1]["end"]  + offset
        text   = " ".join(w["word"] for w in phrase)
        lines.append(f"{idx}\n{_fmt(start)} --> {_fmt(end)}\n{text}\n")
        idx += 1
    return "\n".join(lines)

# ─── VIDEO PROCESSING ─────────────────────────────────────────────────────────
def normalize_clip(src, dst, index, has_ltx_audio=True):
    """
    Scale LTX output (576×1024) to 1080×1920. Keep audio if LTX generated it.
    """
    print(f"  Normalizing clip {index+1}...", end="", flush=True)
    if has_ltx_audio:
        # Keep audio from LTX clip
        vf = f"scale=1080:1920:flags=lanczos,setsar=1"
        audio_opts = ["-c:a", "aac", "-b:a", "128k"]
    else:
        # Silent fallback clip — add silent audio track for concat compatibility
        vf = (f"scale=1080:1920:force_original_aspect_ratio=decrease,"
              f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,setsar=1")
        audio_opts = ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                      "-c:a", "aac", "-b:a", "128k", "-shortest"]

    if has_ltx_audio:
        cmd = [
            "ffmpeg", "-y", "-i", str(src),
            "-vf", vf,
            "-t", str(CLIP_DURATION),
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        ] + audio_opts + [str(dst)]
    else:
        cmd = [
            "ffmpeg", "-y", "-i", str(src),
        ] + audio_opts[:2] + audio_opts[2:4] if not has_ltx_audio else [] + [
            "-vf", vf,
            "-t", str(CLIP_DURATION),
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "aac", "-b:a", "128k",
            "-shortest", str(dst)
        ]
        # Simpler fallback cmd for silent clips
        cmd = [
            "ffmpeg", "-y",
            "-i", str(src),
            "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
            "-vf", f"scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,setsar=1",
            "-t", str(CLIP_DURATION),
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "aac", "-b:a", "128k",
            "-shortest",
            str(dst)
        ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Normalize failed: {result.stderr[-300:]}")
    print(" OK")
    return dst


def merge_clips(normalized_files):
    concat_list = TEMP_DIR / "concat.txt"
    with open(concat_list, "w") as f:
        for n in normalized_files:
            f.write(f"file '{Path(n).resolve().as_posix()}'\n")
    merged = TEMP_DIR / "merged.mp4"
    print("  Merging...", end="", flush=True)
    result = subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list), "-c", "copy", str(merged)
    ], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Merge failed: {result.stderr[-300:]}")
    print(" OK")
    return merged


def encode_final(merged, music_file, tts_file, output_path, has_ltx_audio=True):
    """
    Mix audio layers:
      - LTX native ASMR audio (if available) — ambient sounds
      - Background music — very low volume
      - Hindi TTS narration — full volume, starts at 0.9s
    """
    print("  Encoding final audio mix...", end="", flush=True)
    total_dur = CLIPS_PER_SHORT * CLIP_DURATION

    has_tts = tts_file and Path(tts_file).exists()

    if has_ltx_audio and has_tts:
        filter_complex = (
            f"[0:a]volume={LTX_AUDIO_VOL}[ltx_a];"
            f"[1:a]volume={MUSIC_VOLUME},afade=t=in:d=1,afade=t=out:st={total_dur-2}:d=2[music_a];"
            f"[2:a]volume={TTS_VOLUME},adelay=900|900[voice_a];"
            f"[ltx_a][music_a][voice_a]amix=inputs=3:duration=first:dropout_transition=2[out_a]"
        )
        cmd = [
            "ffmpeg", "-y",
            "-i", str(merged), "-i", str(music_file), "-i", str(tts_file),
            "-filter_complex", filter_complex,
            "-map", "0:v", "-map", "[out_a]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(MAX_DURATION), "-movflags", "+faststart", str(output_path)
        ]
    elif has_ltx_audio:
        filter_complex = (
            f"[0:a]volume={LTX_AUDIO_VOL}[ltx_a];"
            f"[1:a]volume={MUSIC_VOLUME},afade=t=in:d=1,afade=t=out:st={total_dur-2}:d=2[music_a];"
            f"[ltx_a][music_a]amix=inputs=2:duration=first:dropout_transition=2[out_a]"
        )
        cmd = [
            "ffmpeg", "-y",
            "-i", str(merged), "-i", str(music_file),
            "-filter_complex", filter_complex,
            "-map", "0:v", "-map", "[out_a]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(MAX_DURATION), "-movflags", "+faststart", str(output_path)
        ]
    elif has_tts:
        # Silent clips (FFmpeg fallback) — music + TTS only
        filter_complex = (
            f"[1:a]volume={MUSIC_VOLUME},afade=t=in:d=1,afade=t=out:st={total_dur-2}:d=2[music_a];"
            f"[2:a]volume={TTS_VOLUME},adelay=900|900[voice_a];"
            f"[music_a][voice_a]amix=inputs=2:duration=longest:dropout_transition=2[out_a]"
        )
        cmd = [
            "ffmpeg", "-y",
            "-i", str(merged), "-i", str(music_file), "-i", str(tts_file),
            "-filter_complex", filter_complex,
            "-map", "0:v", "-map", "[out_a]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(MAX_DURATION), "-movflags", "+faststart", str(output_path)
        ]
    else:
        # Music only
        filter_complex = (
            f"[1:a]volume=0.15,afade=t=in:d=1,afade=t=out:st={total_dur-2}:d=2[out_a]"
        )
        cmd = [
            "ffmpeg", "-y",
            "-i", str(merged), "-i", str(music_file),
            "-filter_complex", filter_complex,
            "-map", "0:v", "-map", "[out_a]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(MAX_DURATION), "-movflags", "+faststart", str(output_path)
        ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Encode failed: {result.stderr[-300:]}")
    print(" OK")
    return output_path

# ─── TEXT OVERLAY ─────────────────────────────────────────────────────────────
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def _esc(text):
    return text.replace("'", "\u2019").replace(":", r"\:").replace("\\", r"\\")

def _wrap(text, max_chars=28):
    """Split text into lines of max_chars, break at word boundaries."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > max_chars:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return r"\n".join(lines)

def burn_text_overlay(input_path, output_path, fact, hook):
    """
    Burn overlays:
      TOP    — viral hook in Hinglish, gold (word-wrapped)
      CENTER — synced Hinglish captions from SRT (phrase by phrase)
      BOTTOM — fact line, white (word-wrapped)
    """
    print("  Burning text overlay...", end="", flush=True)
    filters = []

    # Hook at top — wrapped, smaller font
    hook_wrapped = _wrap(hook.upper(), max_chars=26)
    filters.append(
        f"drawtext=fontfile='{FONT}'"
        f":text='{_esc(hook_wrapped)}'"
        f":fontsize=38:fontcolor=0xFFD700"
        f":borderw=3:bordercolor=black"
        f":x=(w-text_w)/2:y=80"
        f":enable='between(t,0.5,{MAX_DURATION})'"
    )

    # Fact at bottom — wrapped, smaller font
    fact_wrapped = _wrap(fact[:80], max_chars=30)
    filters.append(
        f"drawtext=fontfile='{FONT}'"
        f":text='{_esc(fact_wrapped)}'"
        f":fontsize=32:fontcolor=white"
        f":borderw=3:bordercolor=black"
        f":x=(w-text_w)/2:y=h-320"
        f":enable='between(t,1,{MAX_DURATION})'"
    )


    vf = ",".join(filters)
    result = subprocess.run([
        "ffmpeg", "-y", "-i", str(input_path),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "copy", str(output_path)
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f" WARN: {result.stderr[-150:]}")
        import shutil
        shutil.copy(str(input_path), str(output_path))
    else:
        print(" OK")
    return output_path

# ─── YOUTUBE ──────────────────────────────────────────────────────────────────
def get_youtube_service():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds = Credentials.from_authorized_user_file("yt_token.json", [
        "https://www.googleapis.com/auth/youtube.upload"
    ])
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open("yt_token.json", "w") as f:
            f.write(creds.to_json())
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def upload_to_youtube(video_path, track_info, niche, fact):
    from googleapiclient.http import MediaFileUpload

    youtube = get_youtube_service()
    title = generate_title(niche)
    print(f"  Title: {title}")

    description = (
        f"{fact}\n\n"
        f"🎬 LTX-Video AI se banaya gaya satisfying video\n"
        f"🧠 Aisa kuch aap nahi jaante the — ab sab jaante ho!\n\n"
        f"🎵 Music: {track_info['title']} by {track_info['artist']}\n"
        f"Provided by NoCopyrightSounds (NCS)\n"
        f"Free Download/Stream: https://ncs.io/\n"
        f"Watch: https://www.youtube.com/watch?v={track_info['youtube_id']}\n\n"
        f"#Shorts #Satisfying #ASMR #Relaxing #OddlySatisfying "
        f"#Hindi #India #Facts #DidYouKnow #SatisfyingVideo #NCS"
    )

    media = MediaFileUpload(str(video_path), mimetype="video/mp4",
                            resumable=True, chunksize=512*1024)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["Satisfying", "ASMR", "Hindi", "India", "Facts",
                         "Shorts", "OddlySatisfying", "NCS", "DidYouKnow"],
                "categoryId": "22",
                "defaultLanguage": "hi",
            },
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
        },
        media_body=media
    )

    print("  Uploading", end="", flush=True)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"\r  Uploading: {int(status.progress()*100)}%", end="", flush=True)
    url = f"https://www.youtube.com/shorts/{response['id']}"
    print(f"\r  Uploaded: {url}")
    return response["id"], url


# ─── MAIN PIPELINE ────────────────────────────────────────────────────────────
def run():
    start = time.time()
    print("\n" + "="*54)
    print("  LTX-VIDEO HINDI SHORTS PIPELINE")
    print("="*54)

    tracker = load_tracker()
    today = datetime.now().strftime("%Y-%m-%d")
    posts_today = [p for p in tracker.get("posts_today", []) if p.startswith(today)]

    print(f"  Posts today : {len(posts_today)}/{POSTS_PER_DAY}")
    print(f"  Total posts : {tracker.get('total_posts', 0)}")

    if len(posts_today) >= POSTS_PER_DAY and not FORCE_RUN:
        msg = f"Daily limit reached ({POSTS_PER_DAY}/day). Skipping."
        print(f"\n  {msg}")
        tg(f"⏭️ Skipped — {msg}")
        return

    cp = ckpt.load()
    cp = cleanup.startup_check(cp)
    state = cp.get("state", "idle")
    print(f"  Checkpoint  : {state}")
    print("-"*54)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = str(OUTPUT_DIR / f"short_{timestamp}.mp4")

    # ── Step 1: Prompts + TTS ─────────────────────────────────────────────────
    if not ckpt.past(state, "videos_selected"):
        print("\n[1/4] Generating prompts & TTS...")
        niche = random.choice(NICHES)
        clip_info = []
        for i in range(CLIPS_PER_SHORT):
            img_prompt, ltx_prompt, clip_niche = generate_prompt(niche)
            clip_info.append({
                "niche": clip_niche,
                "image_prompt": img_prompt,
                "ltx_prompt": ltx_prompt,
                "subject": img_prompt[:60],
            })

        track_info, audio_file = select_music(tracker)
        fact, hook, subtitle, tts_text = generate_fact_and_subtitle(niche)

        for i, c in enumerate(clip_info):
            print(f"  Clip {i+1} [{c['niche']}]: {c['subject'][:50]}")
        print(f"  Music : {track_info['title']} — {track_info['artist']}")
        print(f"  Hook  : {hook}")
        print(f"  Generating Hinglish TTS ({len(tts_text.split())} words)...")

        tts_file, word_timings = generate_tts(tts_text, TEMP_DIR / "narration.mp3", tracker)

        srt_file = None
        if tts_file and word_timings:
            srt_content = build_srt(word_timings)
            srt_file = TEMP_DIR / "captions.srt"
            srt_file.write_text(srt_content, encoding="utf-8")
            print(f"  SRT  : {len(word_timings)} words → captions.srt")

        ckpt.save("videos_selected",
                  clip_info=clip_info, track_id=track_info["id"],
                  audio_file=str(audio_file), output_file=output_path,
                  fact=fact, hook=hook, tts_text=tts_text)
        tg(f"✅ Step 1/4 — Prompts ready\nNiche: {niche}\nMusic: {track_info['title']}\nHook: {hook}")
    else:
        clip_info  = cp["clip_info"]
        audio_file = Path(cp["audio_file"])
        output_path = cp["output_file"]
        fact     = cp.get("fact", "Yeh facts aapka dimag ghumaa denge!")
        hook     = cp.get("hook", "Yeh toh koi nahi jaanta tha!")
        tts_text = cp.get("tts_text", "Kya aap jaante hain? Duniya mein bahut kuch aisa hai jo aapne kabhi suna hi nahi.")
        track_info, audio_file = select_music(tracker)
        audio_file = Path(cp["audio_file"])
        tts_file, word_timings = generate_tts(tts_text, TEMP_DIR / "narration.mp3", tracker)
        srt_file = None
        if tts_file and word_timings:
            srt_content = build_srt(word_timings)
            srt_file = TEMP_DIR / "captions.srt"
            srt_file.write_text(srt_content, encoding="utf-8")
        print(f"\n[1/4] Resuming — {len(clip_info)} prompts loaded")

    # ── Step 2: Generate clips with LTX-Video ────────────────────────────────
    print("\n[2/4] Generating video clips via LTX-Video 2.3...")
    tg("🎬 Step 2/4 — Generating LTX-Video clips...")

    normalized = []
    all_have_audio = True
    vid_sources = []

    for i, clip in enumerate(clip_info):
        if ckpt.past(state, f"clip_{i}_done"):
            norm_file = TEMP_DIR / f"norm_{i}.mp4"
            if norm_file.exists():
                normalized.append(str(norm_file))
                print(f"  Clip {i+1}: cached")
                continue

        raw_file  = TEMP_DIR / f"raw_{i}.mp4"
        norm_file = TEMP_DIR / f"norm_{i}.mp4"

        print(f"\n  Clip {i+1}: {clip['subject'][:50]}")
        success, has_audio, vid_source = generate_clip(
            clip["image_prompt"], clip["ltx_prompt"], raw_file, clip_index=i
        )
        if not success:
            raise RuntimeError(f"Failed to generate clip {i+1}")
        if vid_source == "replicate":
            tg(f"💰 Replicate fallback used for clip {i+1} (~$0.01)\nHF ZeroGPU quota was exhausted.")

        if not has_audio:
            all_have_audio = False
        vid_sources.append(vid_source)

        normalize_clip(raw_file, norm_file, i, has_ltx_audio=has_audio)
        normalized.append(str(norm_file))

        ckpt.save(f"clip_{i}_done", clip_info=clip_info,
                  track_id=cp.get("track_id", track_info["id"]),
                  audio_file=str(audio_file), output_file=output_path,
                  fact=fact, hook=hook, tts_text=tts_text,
                  all_have_audio=all_have_audio, vid_sources=vid_sources)

    # ── Step 3: Merge + encode ────────────────────────────────────────────────
    print("\n[3/4] Merging & encoding final Short...")
    tg("🎛️ Step 3/4 — Encoding...")

    all_have_audio = cp.get("all_have_audio", all_have_audio)
    merged_file = TEMP_DIR / "merged.mp4"
    if not (ckpt.past(state, "merged") and merged_file.exists()):
        merge_clips(normalized)
        ckpt.save("merged", clip_info=clip_info,
                  track_id=cp.get("track_id", track_info["id"]),
                  audio_file=str(audio_file), output_file=output_path,
                  all_have_audio=all_have_audio)

    encoded_raw = str(OUTPUT_DIR / f"short_raw_{timestamp}.mp4")
    encode_final(merged_file, audio_file, tts_file, encoded_raw, has_ltx_audio=all_have_audio)

    print("  Adding text overlay...")
    burn_text_overlay(encoded_raw, output_path, fact, hook)

    ckpt.save("encoded", clip_info=clip_info,
              track_id=cp.get("track_id", track_info["id"]),
              audio_file=str(audio_file), output_file=output_path,
              fact=fact, hook=hook, all_have_audio=all_have_audio)

    # ── Step 4: Upload ────────────────────────────────────────────────────────
    print("\n[4/4] Uploading to YouTube...")
    tg("📤 Step 4/4 — Uploading to YouTube...")

    niche = clip_info[0]["niche"]
    video_id, url = upload_to_youtube(output_path, track_info, niche, fact)

    ckpt.save("uploaded", clip_info=clip_info,
              track_id=cp.get("track_id", track_info["id"]),
              audio_file=str(audio_file), output_file=output_path, video_id=video_id)

    # ── Sheet log ────────────────────────────────────────────────────────────
    elapsed = time.time() - start
    vid_sources = cp.get("vid_sources", vid_sources)
    source_summary = "/".join(set(vid_sources)) if vid_sources else "unknown"
    log_to_sheet([
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        niche,
        hook,
        url,
        source_summary,
        f"{track_info['title']} — {track_info['artist']}",
        f"{elapsed:.0f}s",
    ])

    # ── Done ─────────────────────────────────────────────────────────────────
    used_music = tracker.get("used_music", [])
    used_music.append(track_info["id"])
    tracker["used_music"] = used_music[-20:]
    tracker["posts_today"] = posts_today + [f"{today}_{datetime.now().strftime('%H%M%S')}"]
    tracker["total_posts"] = tracker.get("total_posts", 0) + 1
    save_tracker(tracker)
    ckpt.clear()
    cleanup.clean_temp()

    elapsed = time.time() - start
    sheet_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}" if SHEET_ID else "N/A"
    tg(
        f"Short posted!\n"
        f"Video: {url}\n"
        f"Sheet: {sheet_url}\n"
        f"Niche: {niche}\n"
        f"Music: {track_info['title']}\n"
        f"Source: {source_summary}\n"
        f"Posts today: {len(posts_today)+1}/{POSTS_PER_DAY}\n"
        f"Total: {tracker['total_posts']}\n"
        f"Time: {elapsed:.0f}s",
        parse_mode=None
    )
    print(f"\n{'='*54}")
    print(f"  Done in {elapsed:.0f}s | Total: {tracker['total_posts']}")
    print(f"  URL: {url}")
    print(f"{'='*54}\n")


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        tg_error("pipeline run()", e)
        raise
