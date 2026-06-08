import os
import subprocess

def run_diagnostic():
    print(f"--- Running Diagnostic ---")
    print(f"Current Working Directory: {os.getcwd()}")
    print(f"Files in current directory: {os.listdir('.')}")
    
    # 1. Check for API Keys
    if os.environ.get("PEXELS_API_KEY"):
        print("✅ Pexels API Key found in environment.")
    else:
        print("❌ Pexels API Key MISSING.")

    # 2. Check for FFmpeg
    try:
        version = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        print("✅ FFmpeg is installed.")
    except FileNotFoundError:
        print("❌ FFmpeg NOT FOUND.")

if __name__ == "__main__":
    run_diagnostic()
