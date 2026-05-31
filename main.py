import os
import requests
import random
import subprocess
import asyncio
import time
import datetime
import glob # Added for cleanup
from google import genai
import edge_tts

# ... (Keep all your existing setup, get_daily_state, generate_viral_script, 
# fetch_free_background_video, generate_voiceover, and render_final_video functions exactly as they are) ...

def assemble_and_publish():
    lock_file = f"api_lock_{datetime.date.today()}.txt"
    if os.path.exists(lock_file):
        print("🛑 API limit already hit today. Skipping.")
        return

    try:
        print(f"🚀 Starting automation for {datetime.date.today()}")
        script, state = generate_viral_script()
        video_url = fetch_free_background_video()
        
        asyncio.run(generate_voiceover(script, "voiceover.mp3"))
        render_final_video(video_url, "voiceover.mp3", script, "output.mp4")
        
        tag = f"Exploring {state} #YorubaHeritage #Nigeria"
        # The upload process
        subprocess.run(["python3", "cli.py", "upload", "-v", "output.mp4", "-t", tag], check=True)
        print("✅ Success: Video uploaded.")

    except subprocess.CalledProcessError as e:
        print(f"❌ Upload failed: {e}")
        raise e
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "Quota exceeded" in error_str:
            print("🛑 Quota limit reached. Locking
