import os
import requests
import random
import subprocess
import asyncio
import time  # NEW: Added for handling retry delays
from google import genai
import edge_tts

# Initialize client
client = genai.Client()
PEXELS_KEY = os.environ.get("PEXELS_API_KEY")

def generate_viral_script():
    """Generates a script with a retry loop to handle 429 errors."""
    prompt = (
        "Write a 60-second video script about Stoic resilience. "
        "1. Start with a 3-second 'Hook' that is bold or controversial. "
        "2. Keep sentences short and conversational. "
        "3. Output ONLY the text of the script."
    )
    
    # Retry logic: Try 3 times if we hit a limit
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            if "429" in str(e):
                wait_time = (attempt + 1) * 5  # Wait 5, 10, 15 seconds
                print(f"⚠️ API busy. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise e # If it's not a 429, fail immediately
    raise Exception("Failed to generate script after 3 attempts due to API limits.")

# ... [Keep your fetch_free_background_video, generate_voiceover, and render_final_video exactly as they were] ...

def assemble_and_publish():
    print("🚀 Starting Production Engine...")
    try:
        script = generate_viral_script()
        video_url = fetch_free_background_video()
        
        audio_file = "voiceover.mp3"
        final_output = "output.mp4"
        
        asyncio.run(generate_voiceover(script, audio_file))
        render_final_video(video_url, audio_file, script, final_output)
        
        print("✨ Production Complete! Uploading...")
        subprocess.run(["python3", "cli.py", "upload", "--user", "ancient_discipline", "-v", "output.mp4", "-t", "Stoic Wisdom #motivation"], check=True)
    except Exception as e:
        print(f"❌ Production failed: {e}")

if __name__ == "__main__":
    assemble_and_publish()
