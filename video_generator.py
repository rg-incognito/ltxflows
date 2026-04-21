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
VIDEO_DURATION = 10   # seconds per clip (LTX max is 10s)

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
            if "quota" in err.lower() or "zerogpu" in err.lower():
                print("    ZeroGPU quota exhausted — skip retries")
                return False, True   # quota signal: (failed, quota_exhausted)
            time.sleep(30)

    return False, False


# ─── FALLBACK 1: REPLICATE LTX-VIDEO (paid, ~$0.01/clip) ────────────────────

def generate_video_replicate(image_path, output_path, motion_prompt, clip_index=0,
                              duration=VIDEO_DURATION):
    """
    LTX-Video via Replicate API. Used when HF ZeroGPU quota is exhausted.
    Needs REPLICATE_API_TOKEN env var. Returns True on success.
    """
    import os
    token = os.environ.get("REPLICATE_API_TOKEN", "")
    if not token:
        print("  REPLICATE_API_TOKEN not set — skipping")
        return False

    try:
        import replicate
    except ImportError:
        print("  replicate not installed")
        return False

    # length must be one of [97,129,161,193,225,257]; 193 ≈ 8s @ 24fps
    length_frames = 193

    REPLICATE_VERSION = "8c47da666861d081eeb4d1261853087de23923a268a69b63febdf5dc1dee08e4"

    print(f"  Replicate LTX-Video...", end="", flush=True)
    try:
        # Upload image to Replicate Files API
        with open(image_path, "rb") as f:
            up = requests.post(
                "https://api.replicate.com/v1/files",
                headers={"Authorization": f"Bearer {token}"},
                files={"content": (Path(image_path).name, f, "image/jpeg")},
                timeout=60
            )
        if up.status_code not in (200, 201):
            print(f" upload failed ({up.status_code})")
            return False
        image_url = up.json()["urls"]["get"]

        # Create prediction via REST API
        pred = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={
                "version": REPLICATE_VERSION,
                "input": {
                    "prompt": motion_prompt,
                    "image": image_url,
                    "length": length_frames,
                    "target_size": LTX_WIDTH,
                    "aspect_ratio": "9:16",
                    "cfg": 3,
                    "steps": 30,
                    "seed": SEED + clip_index,
                    "negative_prompt": "low quality, worst quality, deformed, distorted",
                }
            },
            timeout=30
        ).json()

        pred_url = pred.get("urls", {}).get("get")
        if not pred_url:
            print(f" no pred url: {pred.get('error','?')}")
            return False

        # Poll for completion (max 10 min)
        for _ in range(120):
            time.sleep(5)
            r = requests.get(pred_url,
                headers={"Authorization": f"Bearer {token}"}, timeout=30).json()
            status = r.get("status")
            if status == "succeeded":
                output_urls = r.get("output", [])
                url = output_urls[0] if output_urls else None
                if url:
                    data = requests.get(url, timeout=300).content
                    if len(data) > 100_000:
                        Path(output_path).write_bytes(data)
                        print(f" OK ({len(data)//1024} KB)")
                        return True
                print(f" too small or no url")
                return False
            elif status in ("failed", "canceled"):
                print(f" {status}: {r.get('error','?')}")
                return False
    except Exception as e:
        print(f" error: {str(e)[:200]}")

    return False


# ─── FALLBACK 2: KEN BURNS (silent, last resort) ─────────────────────────────

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
      2. Animate with LTX-Video 2.3 HF ZeroGPU (free, with native audio)
      3. Fallback to Replicate LTX-Video (paid ~$0.01, no audio)
      4. Fallback to FFmpeg Ken Burns (free, silent)

    Returns (success: bool, has_audio: bool)
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    image_path = output_path.parent / f"{output_path.stem}_ref.jpg"
    if not generate_image(image_prompt, image_path, seed=SEED + clip_index):
        return False, False

    ltx_result = generate_video_ltx(image_path, output_path, ltx_motion_prompt,
                                     clip_index=clip_index, max_retries=max_retries)
    if ltx_result is True or (isinstance(ltx_result, tuple) and ltx_result[0]):
        return True, True, "ltx_hf"

    quota_exhausted = isinstance(ltx_result, tuple) and ltx_result[1]
    if quota_exhausted:
        print("  ZeroGPU quota exhausted — trying Replicate LTX-Video")
        if generate_video_replicate(image_path, output_path, ltx_motion_prompt,
                                    clip_index=clip_index):
            return True, False, "replicate"

    print("  LTX failed — falling back to FFmpeg Ken Burns")
    ok, has_audio = generate_video_ffmpeg_fallback(image_path, output_path, clip_index=clip_index)
    return ok, has_audio, "ffmpeg" if ok else None
