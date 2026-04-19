"""
Video Generator — LTX-Video 2.3 pipeline.
  Stage 1: Pollinations.ai  → 1080x1920 still image (free FLUX)
  Stage 2: LTX-Video 2.3    → 576x1024 portrait video WITH native audio (free ZeroGPU)
  Fallback: FFmpeg Ken Burns → silent video if LTX fails

LTX-Video 2.3 generates ASMR-quality audio matching the video content.
"""

import os
import subprocess
import time
import urllib.parse
import requests
from pathlib import Path

SEED = 42

VIDEO_FPS      = 24   # LTX native fps
VIDEO_DURATION = 8    # seconds per clip (LTX max is 10s)

# LTX portrait output: 576 wide × 1024 tall = 9:16 for Shorts
LTX_WIDTH  = 576
LTX_HEIGHT = 1024


# ─── STAGE 1: IMAGE ───────────────────────────────────────────────────────────

def generate_image(prompt, output_path, seed=SEED, max_retries=3):
    """1080x1920 portrait image via Pollinations.ai (free FLUX)."""
    clean = prompt
    for term in ["seamless loop,", "seamless loop", "slow motion 240fps,"]:
        clean = clean.replace(term, "")
    clean = clean.strip().strip(",").strip()

    encoded = urllib.parse.quote(clean)
    url = (f"https://image.pollinations.ai/prompt/{encoded}"
           f"?width=1080&height=1920&seed={seed}&nologo=true&model=flux")

    print(f"  Pollinations image (seed={seed})...", end="", flush=True)
    for attempt in range(max_retries):
        try:
            r = requests.get(url, timeout=120)
            if r.status_code == 200 and len(r.content) > 5000:
                Path(output_path).write_bytes(r.content)
                print(f" OK ({len(r.content)//1024} KB)")
                return True
            print(f" {r.status_code}", end="", flush=True)
            time.sleep(10)
        except Exception as e:
            print(f" err: {e}", end="", flush=True)
            time.sleep(10)
    print(" FAILED")
    return False


# ─── STAGE 2: LTX-VIDEO 2.3 ──────────────────────────────────────────────────

def generate_video_ltx(image_path, output_path, motion_prompt, clip_index=0,
                        duration=VIDEO_DURATION, max_retries=2):
    """
    LTX-Video 2.3 via Hugging Face Space (free ZeroGPU, no token needed).
    Generates portrait video WITH native ASMR audio.
    Returns True if video saved successfully.
    """
    try:
        from gradio_client import Client, handle_file
    except ImportError:
        print("  gradio_client not installed")
        return False

    for attempt in range(max_retries):
        print(f"  LTX-Video 2.3 (attempt {attempt+1}/{max_retries})...", end="", flush=True)
        try:
            client = Client("Lightricks/LTX-2-3")
            result = client.predict(
                input_image=handle_file(str(image_path)),
                prompt=motion_prompt,
                duration=float(min(duration, 10)),
                enhance_prompt=False,
                seed=SEED + clip_index,
                randomize_seed=False,
                height=LTX_HEIGHT,
                width=LTX_WIDTH,
                api_name="/generate_video"
            )

            # Extract video path/url from result
            video_data = result[0] if isinstance(result, (list, tuple)) else result
            if isinstance(video_data, dict):
                src = video_data.get("url") or video_data.get("path")
            else:
                src = str(video_data) if video_data else None

            if not src:
                print(f" no src in result")
                time.sleep(30)
                continue

            print(f"\n    src: {src[:90]}", end="", flush=True)

            if src.startswith("http"):
                data = requests.get(src, timeout=300).content
                if len(data) > 100_000:
                    Path(output_path).write_bytes(data)
                    print(f" OK ({len(data)//1024} KB, with audio)")
                    return True
                print(f" too small ({len(data)} bytes)")
            else:
                local = Path(src)
                if local.exists() and local.stat().st_size > 100_000:
                    import shutil
                    shutil.copy(str(local), str(output_path))
                    print(f" OK ({local.stat().st_size//1024} KB, local)")
                    return True
                print(f" local missing or too small")

        except Exception as e:
            err = str(e)
            print(f" error: {err[:120]}")
            if "quota" in err.lower() or "ZeroGPU" in err:
                print("    ZeroGPU quota — waiting 60s")
                time.sleep(60)
            else:
                time.sleep(30)

    return False


# ─── FALLBACK: KEN BURNS (silent, if LTX fails) ──────────────────────────────

_MOTIONS = [
    ("min(zoom+0.0008,1.35)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)", "zoom-in"),
    ("min(zoom+0.0006,1.25)", "iw/2-(iw/zoom/2)+on*0.04", "ih/3-(ih/zoom/2)", "drift-right"),
    ("max(1.3-on*0.0001,1.0)", "iw/2-(iw/zoom/2)", "2*ih/3-(ih/zoom/2)", "zoom-out"),
]
_GRADES = [
    "eq=saturation=1.4:contrast=1.08:brightness=0.04:gamma_r=1.05",
    "eq=saturation=1.3:contrast=1.10:brightness=0.02",
    "eq=saturation=1.5:contrast=1.05:brightness=0.03:gamma_b=1.05",
]

def generate_video_ffmpeg_fallback(image_path, output_path, clip_index=0, duration=VIDEO_DURATION):
    """Ken Burns fallback — silent video, used only if LTX fails."""
    image_path  = str(image_path)
    output_path = str(output_path)
    total_frames = duration * 30  # zoompan uses 30fps internally

    idx = clip_index % 3
    zoom_expr, x_expr, y_expr, label = _MOTIONS[idx]
    grade = _GRADES[idx]

    zp = (f"zoompan=z='{zoom_expr}':d={total_frames}"
          f":x='{x_expr}':y='{y_expr}':s=1080x1920,fps=30")
    vf = f"{zp},{grade},vignette=angle=PI/5"

    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", image_path,
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-pix_fmt", "yuv420p", "-t", str(duration), "-an",
        output_path
    ]
    print(f"  FFmpeg fallback [{label}]...", end="", flush=True)
    try:
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
        if r.returncode == 0 and Path(output_path).stat().st_size > 50_000:
            print(f" OK ({Path(output_path).stat().st_size//1024} KB, silent)")
            return True, False  # (success, has_audio)
        print(f" FAILED (rc={r.returncode})")
        return False, False
    except Exception as e:
        print(f" error: {e}")
        return False, False


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def generate_clip(image_prompt, ltx_motion_prompt, output_path, clip_index=0, max_retries=2):
    """
    Full clip generation:
      1. Generate image via Pollinations.ai
      2. Animate with LTX-Video 2.3 (with native audio)
      3. Fallback to FFmpeg Ken Burns (silent) if LTX fails

    Returns (success: bool, has_audio: bool)
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    image_path = output_path.parent / f"{output_path.stem}_ref.jpg"
    if not generate_image(image_prompt, image_path, seed=SEED + clip_index):
        return False, False

    if generate_video_ltx(image_path, output_path, ltx_motion_prompt,
                           clip_index=clip_index, max_retries=max_retries):
        return True, True   # LTX success — has native audio

    print("  LTX failed — falling back to FFmpeg Ken Burns")
    return generate_video_ffmpeg_fallback(image_path, output_path, clip_index=clip_index)
