# Auto Short Generator

A Python script that automatically downloads a segment of a YouTube video, crops it into a 9:16 vertical video format suitable for Shorts/TikTok, and then automatically uploads it to both Discord (via Webhook) and YouTube Shorts.

## Features

- **Download & Crop**: Utilizes `yt-dlp` to efficiently download only the required segment of the video and `ffmpeg` to process it into a 1080x1920 (9:16) format.
- **Discord Upload**: Posts the generated Short directly to a Discord channel via a Webhook.
- **YouTube Upload**: Uploads the generated Short directly to your YouTube channel as a Short, utilizing the YouTube Data API v3.

## Requirements

- Python 3.7+
- FFmpeg (Must be installed on your system and available in your PATH)
- A Discord Webhook URL (for Discord upload)
- Google Cloud Console Project with YouTube Data API v3 enabled and OAuth 2.0 Credentials (for YouTube upload)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd auto-short-generator
    ```

2.  **Set up a virtual environment (recommended):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

### Discord Webhook

1.  Create a `.env` file based on the example:
    ```bash
    cp .env.example .env
    ```
2.  Open the `.env` file and set your `DISCORD_WEBHOOK_URL`.

### YouTube API Authentication

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new project or select an existing one.
3.  Enable the **YouTube Data API v3**.
4.  Navigate to **APIs & Services > Credentials**.
5.  Create **OAuth client ID** credentials (choose "Desktop app" as the application type).
6.  Download the JSON file and rename it to `client_secret.json`.
7.  Place the `client_secret.json` file in the root directory of this project.

*Note: On your first run, a browser window will open to authenticate the app with your Google account. It will save a `token.pickle` file for subsequent runs.*

## Usage

Run the main script from your terminal:

```bash
python main.py <URL> <START_TIME> <END_TIME> [OPTIONS]
```

### Examples

**Basic usage (Download, crop, and upload to both Discord and YouTube):**
```bash
python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" "01:00" "01:30"
```

**Custom Title, Description, and Privacy (for YouTube):**
```bash
python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" "60" "120" --title "My Cool Short" --description "Check out this clip!" --privacy public
```

**Skip Discord and keep the local file:**
```bash
python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" "01:00" "01:15" --skip-discord --keep-file
```

### Available Options

```
positional arguments:
  url                   The URL of the YouTube video to process.
  start_time            Start time for the clip (e.g., '01:30' or '90').
  end_time              End time for the clip (e.g., '02:00' or '120').

options:
  -h, --help            show this help message and exit
  --title TITLE         Title for the YouTube Short.
  --description DESCRIPTION
                        Description for the YouTube Short.
  --privacy {public,private,unlisted}
                        Privacy status for YouTube upload.
  --discord-webhook DISCORD_WEBHOOK
                        Discord Webhook URL for uploading. Overrides .env DISCORD_WEBHOOK_URL.
  --skip-discord        Skip Discord upload.
  --skip-youtube        Skip YouTube upload.
  --keep-file           Keep the processed video file after uploading.
```
