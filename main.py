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

YORUBA_STATES = ["Oyo", "Osun", "Ogun", "Ekiti", "Lagos", "Ondo", "Kwara", "Kogi"]

def get_daily_state():
    day_of_year = datetime.datetime.now().timetuple().tm_yday
    return YORUBA_STATES[day_of_year % len(YORUBA_STATES)]

def generate_viral_script():
    state = get_daily_state()
    # Optimized prompt with Call-to-Action
    prompt = (
        f"Write a 30-second script about {state}, Nigeria. "
        "1. Start with a high-energy, shocking hook. "
        "2. Provide 2 fascinating, lesser-known cultural facts. "
        "3. End with a clear call to action: 'Subscribe to see more of our Yoruba heritage!' "
        "Use an enthusiastic, conversational tone. No intro. Output text only."
    )
    
    for attempt in range(6):
        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            if response.text:
                return response.text.strip(), state
        except Exception as e:
            if "429" in str(e):
                wait_time = (attempt + 1) * 30
                print(f"⚠️ API busy. Cooldown {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise e
    raise Exception("API Quota exceeded.")

def fetch_free_background_video():
    query = random.choice(["nigeria scenery", "african life", "lagos city", "cultural heritage"])
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=5&orientation=portrait"
    headers = {"Authorization": PEXELS_KEY}
    try:
        response = requests.get(url, headers=headers, timeout=10).json()
        video_list = response.get("videos", [])
        if video_list:
            selected = random.choice(video_list)
            for f in selected.get("video_files", []):
                if f.get("width") == 720:
                    return f.get("link")
    except:
        pass
    return "https://player.vimeo.com/external/371433846.sd.mp4?s=236da2f3c054ba2d11c300078a635811c08e92cb&profile_id=165"

async def generate_voiceover(text, output_path):
    communicate = edge_tts.Communicate(text, "en-US-ChristopherNeural", rate="-5%")
    await communicate.save(output_path)

def render_final_video(video_url, audio_path, script_text, output_path):
    with open("raw_input.mp4", "wb") as f:
        f.write(requests.get(video_url, timeout=20).content)
    with open("quote.txt", "w", encoding="utf-8") as f:
        words = script_text.split()
        for i in range(0, len(words), 5):
            f.write(" ".join(words[i:i+5]) + "\n")

    cmd = [
        "ffmpeg", "-y", "-i", "raw_input.mp4", "-i", audio_path,
        "-filter_complex", "[0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,drawtext=textfile='quote.txt':fontcolor=white:fontsize=30:box=1:boxcolor=black@0.5:boxborderw=15:x=(w-text_w)/2:y=(h-text_h)/2[v]",
        "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-shortest", output_path
    ]
    subprocess.run(cmd, check=True)

def assemble_and_publish():
    # Stop if we already failed today
    lock_file = f"api_lock_{datetime.date.today()}.txt"
    if os.path.exists(lock_file):
        print("🛑 Already hit limit today. Skipping.")
        return

    try:
        script, state = generate_viral_script()
        video_url = fetch_free_background_video()
        asyncio.run(generate_voiceover(script, "voiceover.mp3"))
        render_final_video(video_url, "voiceover.mp3", script, "output.mp4")
        
        tag = f"Exploring {state} #YorubaHeritage #Nigeria"
        subprocess.run(["python3", "cli.py", "upload", "-v", "output.mp4", "-t", tag], check=True)
    except Exception as e:
        with open(lock_file, "w") as f: f.write("failed")
        raise e

if __name__ == "__main__":
    assemble_and_publish()
