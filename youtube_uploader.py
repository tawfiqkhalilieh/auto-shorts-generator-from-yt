import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import pickle

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google Cloud Console at
# https://cloud.google.com/console.
# Please ensure that you have enabled the YouTube Data API for your project.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


def get_authenticated_service():
    credentials = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
            
    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print("Refreshing access token...")
            credentials.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRETS_FILE):
                print(f"Error: {CLIENT_SECRETS_FILE} not found. Please place it in the project root to enable YouTube uploads.")
                return None

            print("Starting OAuth flow. A browser window will open to authenticate.")
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)

    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


def initialize_upload(youtube, file_path: str, title: str, description: str, category: str="22", privacyStatus: str="private"):
    tags = ["shorts", "auto-generated"]
    
    print(f"Uploading file: {file_path} to YouTube as a Short...")
    
    body = dict(
        snippet=dict(
            title=title,
            description=description,
            tags=tags,
            categoryId=category
        ),
        status=dict(
            privacyStatus=privacyStatus
        )
    )

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
    )

    response = None
    error = None
    retry = 0
    while response is None:
        try:
            status, response = insert_request.next_chunk()
            if status:
                print(f"Uploaded {int(status.progress() * 100)}%.")
        except HttpError as e:
            if e.resp.status in [500, 502, 503, 504]:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
            else:
                raise
        except Exception as e:
            error = "A retriable error occurred: %s" % e

        if error is not None:
            print(error)
            retry += 1
            if retry > 10:
                print("No longer attempting to retry.")
                break
            import time
            time.sleep(1)
            error = None

    if response:
        print(f"Video uploaded successfully to YouTube! Video ID: {response.get('id')}")
        return response.get('id')
    else:
        print("Failed to complete YouTube upload.")
        return None


def upload_to_youtube(file_path: str, title: str, description: str, privacy: str = "private"):
    """
    Orchestrates the YouTube authentication and upload process.
    """
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return None

    youtube = get_authenticated_service()
    if youtube is None:
        print("YouTube service could not be authenticated. Skipping upload.")
        return None

    try:
        video_id = initialize_upload(youtube, file_path, title, description, privacyStatus=privacy)
        return video_id
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
        return None
