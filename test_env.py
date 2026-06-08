import os
import subprocess

def quick_test():
    print("--- QUICK ENVIRONMENT TEST ---")
    
    # 1. Check for API Keys
    if os.environ.get("PEXELS_API_KEY"):
        print("✅ Pexels Key found")
    else:
        print("❌ Pexels Key missing")

    # 2. Check for FFmpeg (The heart of your video engine)
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("✅ FFmpeg is installed")
    except Exception:
        print("❌ FFmpeg is missing")

if __name__ == "__main__":
    quick_test()
