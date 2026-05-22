import os
import requests
import random
import subprocess
import asyncio
from google import genai
import edge_tts

# Initialize client
client = genai.Client()
PEXELS_KEY = os.environ.get("PEXELS_API_KEY")

def generate_viral_script():
    """Generates a hook-based script for higher engagement."""
    prompt = (
        "Write a 60-second video script about Stoic resilience. "
        "1. Start with a 3-second 'Hook' that is bold or controversial. "
        "2. Keep sentences short and conversational. "
        "3. Output ONLY the text of the script."
    )
    response = client.models.generate_content(
        model='gemini-2.0-flash', # Updated to the latest stable model
        contents=prompt
    )
    return response.text.strip()

def fetch_free_background_video():
    query = random.choice(["nature dark", "rain aesthetic", "ocean waves", "dark moody"])
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=10&orientation=portrait"
    headers = {"Authorization": PEXELS_KEY}
    
    response = requests.get(url, headers=headers).json()
    video_list = response.get("videos", [])
    
    if video_list:
        selected = random.choice(video_list)
        for f in selected.get("video_files", []):
            if f.get("width") == 720:
                return f.get("link")
    return "https://player.vimeo.com/external/371433846.sd.mp4?s=236da2f3c054ba2d11c300078a635811c08e92cb&profile_id=165"

async def generate_voiceover(text, output_path):
    communicate = edge_tts.Communicate(text, "en-US-ChristopherNeural", rate="-5%")
    await communicate.save(output_path)

def render_final_video(video_url, audio_path, script_text, output_path):
    # 1. Download Video
    print("📥 Downloading video asset...")
    with open("raw_input.mp4", "wb") as f:
        f.write(requests.get(video_url).content)
        
    # 2. Prepare Text File for Overlay
    with open("quote.txt", "w", encoding="utf-8") as f:
        # Simple word wrap logic
        words = script_text.split()
        for i in range(0, len(words), 5):
            f.write(" ".join(words[i:i+5]) + "\n")

    # 3. Compile with FFmpeg
    print("🎬 Rendering video...")
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
    script = generate_viral_script()
    video_url = fetch_free_background_video()
    
    audio_file = "voiceover.mp3"
    final_output = "output.mp4"
    
    asyncio.run(generate_voiceover(script, audio_file))
    render_final_video(video_url, audio_file, script, final_output)
    
    print("✨ Production Complete! Uploading...")
    # Trigger upload
    subprocess.run(["python3", "cli.py", "upload", "--user", "ancient_discipline", "-v", "output.mp4", "-t", "Stoic Wisdom #motivation"])

if __name__ == "__main__":
    assemble_and_publish()
