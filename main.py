import os
import requests
import random
import subprocess
import asyncio
from google import genai
import edge_tts

# Initialize free Gemini client from secure GitHub Vault
client = genai.Client()
PEXELS_KEY = os.environ.get("PEXELS_API_KEY")

def generate_stoic_script():
    """Generates a high-retention quote for $0 using Gemini Flash"""
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents="Give me one short, powerful, viral Stoic quote by Marcus Aurelius or Seneca about resilience. Output ONLY the quote, no conversational intro, no hashtags, no newlines."
    )
    # Strip quotes and keep it on a clean single line
    return response.text.strip().replace('"', '').replace('\n', ' ')

def fetch_free_background_video():
    """Pulls high-definition vertical video clips completely for free"""
    query = random.choice(["nature dark", "rain aesthetic", "ocean waves", "dark moody"])
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=10&orientation=portrait"
    headers = {"Authorization": PEXELS_KEY}
    
    response = requests.get(url, headers=headers).json()
    video_list = response.get("videos", [])
    
    if video_list:
        selected_video = random.choice(video_list)
        video_files = selected_video.get("video_files", [])
        for f in video_files:
            if "mp4" in f.get("file_type", "") and f.get("width") == 720:
                return f.get("link")
    return "https://player.vimeo.com/external/371433846.sd.mp4?s=236da2f3c054ba2d11c300078a635811c08e92cb&profile_id=165"

async def generate_voiceover(text, output_audio_path):
    """Generates a deep, cinematic male voiceover completely for free"""
    communicate = edge_tts.Communicate(text, "en-US-ChristopherNeural", rate="-10%")
    await communicate.save(output_audio_path)

def render_final_video(video_url, audio_path, script_text, output_video_path):
    """Downloads assets and uses FFmpeg to burn text and combine audio"""
    print("📥 Downloading raw video asset from Pexels...")
    video_data = requests.get(video_url).content
    with open("raw_input.mp4", "wb") as f:
        f.write(video_data)
        
    print("🎬 FFmpeg Compiling: Injecting voiceover and rendering text overlay...")
    
    # Safe string cleaning for terminal execution
    clean_text = script_text.replace("'", "").replace(":", " ")

    # Standard single-line clean text injection for FFmpeg
    cmd = [
        "ffmpeg", "-y",
        "-i", "raw_input.mp4",
        "-i", audio_path,
        "-filter_complex", f"[0:v]scale=720:1280,setsar=1,drawtext=text='{clean_text}':fontcolor=white:fontsize=32:box=1:boxcolor=black@0.6:boxborderw=15:x=(w-text_w)/2:y=(h-text_h)/2:shortest=1[v]",
        "-map", "[v]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-shortest",
        output_video_path
    ]
    
    subprocess.run(cmd, check=True)

def assemble_and_publish():
    """Triggers real production pipeline and delivers it to the upload structure"""
    script_text = generate_stoic_script()
    video_url = fetch_free_background_video()
    
    print(f"--- REAL SCRIPT GENERATED ---\n{script_text}")
    print(f"--- VIDEO SOURCE LOCATED ---\n{video_url}")
    
    audio_file = "voiceover.mp3"
    final_output = "output.mp4"
    
    # Run the voice generation task
    asyncio.run(generate_voiceover(script_text, audio_file))
    
    # Compile everything into a real video file
    render_final_video(video_url, audio_file, script_text, final_output)
    
    print("✨ Video production engine finished rendering output.mp4 perfectly!")
    
    # Send it to the active upload channel environment script
    subprocess.run(["python3", "cli.py", "upload", "--user", "ancient_discipline", "-v", "output.mp4", "-t", "Daily Stoic Discipline #motivation"])

if __name__ == "__main__":
    assemble_and_publish()
