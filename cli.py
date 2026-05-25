import os
import sys
import requests

def upload_to_tiktok(video_path, title):
    """Handles the TikTok publishing pipeline."""
    session_cookie = os.environ.get("TIKTOK_SESSION_COOKIE")
    
    if not session_cookie or session_cookie == "PLACEHOLDER":
        print("ℹ️ TikTok: No active session cookie found. Skipping.")
        return

    print("📡 TikTok: Broadcasting video packets...")
    # TikTok upload APIs are highly unstable. This is the standard endpoint.
    url = "https://www.tiktok.com/api/v1/video/upload/" 
    cookies = {"sessionid": session_cookie}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    try:
        with open(video_path, "rb") as video_file:
            files = {"video": video_file}
            data = {"title": title, "visibility": "public"}
            # Active transmission line - UNCOMMENTED
            res = requests.post(url, cookies=cookies, files=files, data=data, headers=headers, timeout=60)
            if res.status_code == 200:
                print("✨ TikTok: Video successfully deployed live!")
            else:
                print(f"❌ TikTok: Upload failed with code {res.status_code}")
    except Exception as e:
        print(f"❌ TikTok: Upload dropped: {e}")

def upload_to_youtube(video_path, title):
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")
    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    
    if not refresh_token or refresh_token == "PLACEHOLDER":
        print("ℹ️ YouTube: No OAuth tokens found. Skipping.")
        return

    print("🔄 YouTube: Refreshing Google Access Token...")
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "client_id": client_id, "client_secret": client_secret,
        "refresh_token": refresh_token, "grant_type": "refresh_token"
    }
    
    try:
        token_res = requests.post(token_url, data=token_data).json()
        access_token = token_res.get("access_token")
        if not access_token:
            print("❌ YouTube: Failed to fetch token.")
            return

        print("📡 YouTube: Uploading binary media...")
        metadata_url = "https://www.googleapis.com/upload/youtube/v3/videos?part=snippet,status"
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        metadata = {
            "snippet": {"title": title, "description": f"{title}\n\n#YorubaHeritage #Nigeria #Shorts", "categoryId": "22"},
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
        }
        
        init_res = requests.post(f"{metadata_url}&uploadType=resumable", headers=headers, json=metadata)
        upload_url = init_res.headers.get("Location")
        
        with open(video_path, "rb") as video_file:
            upload_res = requests.put(upload_url, data=video_file)
            
        if upload_res.status_code in [200, 201]:
            print("✨ YouTube: Video successfully deployed!")
        else:
            print(f"❌ YouTube: Server rejected upload: {upload_res.status_code}")
    except Exception as e:
        print(f"❌ YouTube: Upload dropped: {e}")

if __name__ == "__main__":
    if "upload" in sys.argv:
        try:
            video_file = sys.argv[sys.argv.index("-v") + 1]
            video_title = sys.argv[sys.argv.index("-t") + 1]
            upload_to_tiktok(video_file, video_title)
            upload_to_youtube(video_file, video_title)
        except (ValueError, IndexError):
            print("❌ Error: Invalid flags.")
