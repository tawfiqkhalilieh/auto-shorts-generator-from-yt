import os
import requests

def upload_to_discord(file_path: str, webhook_url: str):
    """
    Uploads a video file to a Discord webhook.
    """
    if not webhook_url:
        print("Error: No Discord Webhook URL provided. Skipping Discord upload.")
        return False

    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return False

    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    print(f"Uploading to Discord... (File size: {file_size_mb:.2f} MB)")

    if file_size_mb > 25:
        print("Warning: File size exceeds 25MB. Discord might reject the upload depending on the server boost level.")

    with open(file_path, 'rb') as f:
        # Prepare the payload for discord
        # Using multipart/form-data to send a file
        files = {
            'file': (os.path.basename(file_path), f, 'video/mp4')
        }
        data = {
            'content': "Here is the new Short! 🚀"
        }

        try:
            response = requests.post(webhook_url, data=data, files=files)
            if response.status_code in (200, 204):
                print("Successfully uploaded to Discord!")
                return True
            else:
                print(f"Failed to upload to Discord. Status Code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with Discord: {e}")
            return False
