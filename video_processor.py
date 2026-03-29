import yt_dlp
import subprocess
import os
import uuid

def process_video(url: str, start_time: str, end_time: str) -> str:
    """
    Downloads a segment of a YouTube video and crops it to 9:16 (Shorts) format.
    Returns the path to the processed video.
    """
    temp_id = str(uuid.uuid4())
    raw_video_path = f"raw_{temp_id}.mp4"
    cropped_video_path = f"cropped_{temp_id}.mp4"

    start_seconds = yt_dlp.utils.parse_duration(start_time)
    end_seconds = yt_dlp.utils.parse_duration(end_time)

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': raw_video_path,
        'download_ranges': yt_dlp.utils.download_range_func(None, [(start_seconds, end_seconds)]),
        'force_keyframes_at_cuts': True,
    }

    print(f"Downloading {url} from {start_time} to {end_time}...")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    if not os.path.exists(raw_video_path):
        # yt-dlp might append .mkv if the merge output is not strictly mp4.
        # Let's find the file that starts with raw_{temp_id}
        for file in os.listdir('.'):
            if file.startswith(f"raw_{temp_id}"):
                raw_video_path = file
                break
                
    if not os.path.exists(raw_video_path):
        raise FileNotFoundError(f"Downloaded video file {raw_video_path} not found.")

    print("Cropping video to 9:16 aspect ratio (Shorts format)...")
    # crop=ih*9/16:ih -> center crop matching 9:16. scale=1080:1920 -> scale to 1080p vertical
    command = [
        "ffmpeg", "-y", "-i", raw_video_path,
        "-vf", "crop=ih*9/16:ih,scale=1080:1920",
        "-c:a", "aac", "-b:a", "192k",
        "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        cropped_video_path
    ]
    
    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error during processing.")
        raise e

    if os.path.exists(raw_video_path):
        os.remove(raw_video_path)

    return cropped_video_path
