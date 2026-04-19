import shutil
import os
from pathlib import Path

BASE_DIR   = Path(os.environ.get("PIPELINE_BASE_DIR", "."))
OUTPUT_DIR = BASE_DIR / "output"
TEMP_DIR   = OUTPUT_DIR / "temp"

KEEP_LAST_N = 12
MIN_FREE_GB = 2.0

def get_free_gb():
    path = str(BASE_DIR.drive) + "\\" if BASE_DIR.drive else "/"
    _, _, free = shutil.disk_usage(path)
    return free / (1024 ** 3)

def clean_temp():
    if TEMP_DIR.exists():
        count = len(list(TEMP_DIR.iterdir()))
        if count > 0:
            shutil.rmtree(TEMP_DIR)
            TEMP_DIR.mkdir()
            print(f"  Temp: wiped {count} file(s)")
    else:
        TEMP_DIR.mkdir(parents=True)

def clean_outputs():
    outputs = sorted(OUTPUT_DIR.glob("short_*.mp4"), key=lambda f: f.stat().st_mtime)
    keep = KEEP_LAST_N if get_free_gb() >= MIN_FREE_GB else 4
    for f in outputs[:-keep] if len(outputs) > keep else []:
        f.unlink()

def step_index(s):
    steps = ["idle","videos_selected","clip_0_done","clip_1_done","clip_2_done","merged","encoded","uploaded","done"]
    try: return steps.index(s)
    except ValueError: return 0

def check_temp_integrity(checkpoint):
    state = checkpoint.get("state", "idle")
    merge_file = OUTPUT_DIR / "temp" / "merged.mp4"
    encoded_file = checkpoint.get("output_file")
    if encoded_file: encoded_file = Path(encoded_file)

    if state in ("encoded", "uploaded"):
        if encoded_file and not encoded_file.exists():
            state = "merged"
    if state == "merged":
        if not merge_file.exists():
            state = "clip_2_done"
    for i in range(2, -1, -1):
        norm = OUTPUT_DIR / "temp" / f"norm_{i}.mp4"
        if step_index(state) >= step_index(f"clip_{i}_done"):
            if not norm.exists():
                state = f"clip_{i-1}_done" if i > 0 else "videos_selected"

    if state != checkpoint.get("state"):
        return False, state
    return True, state

def startup_check(checkpoint):
    state = checkpoint.get("state", "idle")
    if state in ("idle", "done", "uploaded"):
        return checkpoint
    print(f"\n  Resuming from checkpoint: {state}")
    is_clean, corrected = check_temp_integrity(checkpoint)
    if not is_clean:
        print(f"  Checkpoint corrected: {state} -> {corrected}")
        checkpoint["state"] = corrected
    return checkpoint
