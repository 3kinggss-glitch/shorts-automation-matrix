import os
import requests
import random
import subprocess
import asyncio
import time
import datetime
from google import genai
import edge_tts

# Initialize client
client = genai.Client()
PEXELS_KEY = os.environ.get("PEXELS_API_KEY")

# Yoruba states rotation logic
YORUBA_STATES = ["Oyo", "Osun", "Ogun", "Ekiti", "Lagos", "Ondo", "Kwara", "Kogi"]

def get_daily_state():
    """Cycles through states based on the day of the year."""
    day_of_year = datetime.datetime.now().timetuple().tm_yday
    return YORUBA_STATES[day_of_year % len(YORUBA_STATES)]

def generate_viral_script():
    """Generates a state-specific script with aggressive backoff to avoid 429 errors."""
    state = get_daily_state()
    prompt = f"Write a 45-second script about {state}, Nigeria. Hook, cultural fact, conclusion. No intro. Output text only."
    
    # Retry logic: Try 5 times with increasing delay
    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            # Ensure we have text to return
            if response.text:
                return response.text.strip(), state
        except Exception as e:
            if "429" in str(e):
                wait_time = (attempt + 1) * 20 # Increased wait to be safer
                print(f"⚠️ API Limit hit. Waiting {wait_time}s to cool down...")
                time.sleep(wait_time)
            else:
                raise e
    raise Exception("API Quota exceeded after 5 attempts.")

def fetch_free_background_video():
    query = random.choice(["nature nigeria", "city life", "african landscape", "vibrant culture"])
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=10&orientation=portrait"
    headers = {"Authorization": PEXELS_KEY}
    try:
        response = requests.get(url, headers=headers, timeout=10).json()
        video_list = response.get("videos", [])
        if video_list:
            selected = random.choice(video_list)
            for f in selected.get("video_files", []):
                if f.get("width") == 720:
                    return f.get("link")
    except Exception as e:
        print(f"⚠️ Pexels fetch failed, using fallback: {e}")
    return "https://player.vimeo.com/external/371433846.sd.mp4?s=236da2f3c054ba2d11c300078a635811c08e92cb&profile_id=165"

async def generate_voiceover(text, output_path):
    communicate = edge_tts.Communicate(text, "en-US-ChristopherNeural", rate="-5%")
    await communicate.save(output_path)

def render_final_video(video_url, audio_path, script_text, output_path):
    print("📥 Downloading video asset...")
    with open("raw_input.mp4", "wb") as f:
        f.write(requests.get(video_url, timeout=20).content)
        
    with open("quote.txt", "w", encoding="utf-8") as f:
        words = script_text.split()
        for i in range(0, len(words), 5):
            f.write(" ".join(words[i:i+5]) + "\n")

    print("🎬 Rendering video...")
    # Clean up old output if it exists
    if os.path.exists(output_path):
        os.remove(output_path)

    cmd = [
        "ffmpeg", "-y",
        "-i", "raw_input.mp4",
        "-i", audio_path,
        "-filter_complex", 
        "[0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,drawtext=textfile='quote.txt':fontcolor=white:fontsize=30:box=1:boxcolor=black@0.5:boxborderw=15:x=(w-text_w)/2:y=(h-text_h)/2[v]",
        "-map", "[v]",
        "-map", "1:a",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-shortest",
        output_path
    ]
    subprocess.run(cmd, check=True)

def assemble_and_publish():
    print("🚀 Starting Production Engine...")
    try:
        script, state = generate_viral_script()
        video_url = fetch_free_background_video()
        
        audio_file = "voiceover.mp3"
        final_output = "output.mp4"
        
        asyncio.run(generate_voiceover(script, audio_file))
        render_final_video(video_url, audio_file, script, final_output)
        
        tag = f"Exploring {state} #YorubaHeritage #Nigeria"
        print(f"✨ Production Complete! Uploading for {state}...")
        
        # This is the command that triggers the actual upload
        subprocess.run(["python3", "cli.py", "upload", "--user", "ancient_discipline", "-v", "output.mp4", "-t", tag], check=True)
        
    except Exception as e:
        print(f"❌ Production failed: {e}")
        # Re-raise to ensure GitHub Actions flags the run as failed
        raise e 

if __name__ == "__main__":
    assemble_and_publish()
