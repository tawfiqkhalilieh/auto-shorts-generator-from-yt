import argparse
import os
import sys
from dotenv import load_dotenv

# Import our custom modules
from video_processor import process_video
from discord_uploader import upload_to_discord
from youtube_uploader import upload_to_youtube

def main():
    parser = argparse.ArgumentParser(description="Auto Short Generator: Download, crop, and post YouTube Shorts.")
    parser.add_argument("url", help="The URL of the YouTube video to process.")
    parser.add_argument("start_time", help="Start time for the clip (e.g., '01:30' or '90').")
    parser.add_argument("end_time", help="End time for the clip (e.g., '02:00' or '120').")
    
    parser.add_argument("--title", default="Auto Generated Short #Shorts", help="Title for the YouTube Short.")
    parser.add_argument("--description", default="Generated automatically using Python and FFmpeg.", help="Description for the YouTube Short.")
    parser.add_argument("--privacy", choices=["public", "private", "unlisted"], default="private", help="Privacy status for YouTube upload.")
    
    parser.add_argument("--discord-webhook", help="Discord Webhook URL for uploading. Overrides .env DISCORD_WEBHOOK_URL.")
    
    parser.add_argument("--skip-discord", action="store_true", help="Skip Discord upload.")
    parser.add_argument("--skip-youtube", action="store_true", help="Skip YouTube upload.")
    parser.add_argument("--keep-file", action="store_true", help="Keep the processed video file after uploading.")

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()
    
    discord_webhook_url = args.discord_webhook or os.getenv("DISCORD_WEBHOOK_URL")

    print(f"--- Auto Short Generator ---")
    print(f"Video URL: {args.url}")
    print(f"Time Range: {args.start_time} - {args.end_time}")
    
    # 1. Process Video
    cropped_video_path = None
    try:
        cropped_video_path = process_video(args.url, args.start_time, args.end_time)
        print(f"Video processed successfully: {cropped_video_path}")
    except Exception as e:
        print(f"Failed to process video: {e}")
        sys.exit(1)

    # 2. Upload to Discord
    if not args.skip_discord:
        if discord_webhook_url:
            print("\n--- Uploading to Discord ---")
            upload_to_discord(cropped_video_path, discord_webhook_url)
        else:
            print("\n--- Skipping Discord Upload ---")
            print("No Discord Webhook URL provided in arguments or .env file.")

    # 3. Upload to YouTube
    if not args.skip_youtube:
        print("\n--- Uploading to YouTube Shorts ---")
        try:
            # YouTube module will handle checking for client_secret.json
            upload_to_youtube(
                file_path=cropped_video_path,
                title=args.title,
                description=args.description,
                privacy=args.privacy
            )
        except Exception as e:
            print(f"Failed to upload to YouTube: {e}")

    # 4. Cleanup
    if not args.keep_file:
        if os.path.exists(cropped_video_path):
            os.remove(cropped_video_path)
            print(f"\nCleaned up processed video file: {cropped_video_path}")
    else:
        print(f"\nKept processed video file: {cropped_video_path}")

    print("\nAll tasks completed!")

if __name__ == "__main__":
    main()
