import os
import subprocess

def test_check():
    print("--- Environment Test ---")
    # 1. Check if API Key exists
    key = os.environ.get("PEXELS_API_KEY")
    if key:
        print("✅ Pexels API Key found.")
    else:
        print("❌ Pexels API Key missing!")

    # 2. Check if FFmpeg is installed (required for video rendering)
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("✅ FFmpeg is installed and ready.")
    except Exception:
        print("❌ FFmpeg is not found!")

if __name__ == "__main__":
    test_check()
