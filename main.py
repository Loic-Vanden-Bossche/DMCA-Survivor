import os
import pprint
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from youtube_transcript_api import YouTubeTranscriptApi
from multiprocessing.pool import ThreadPool

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

pp = pprint.PrettyPrinter(indent=4)


def get_full_video_list(channel_id, youtube, pg_token=None):
    pg_data = youtube.search().list(
        part="id, snippet",
        channelId=channel_id,
        maxResults=50,
        pageToken=pg_token
    ).execute()

    return dict({item["id"]["videoId"]: item["snippet"]["title"] for item in pg_data["items"] if item["id"]["kind"] == "youtube#video"}, **(get_full_video_list(channel_id, youtube, pg_data.get("nextPageToken")) if pg_data.get("nextPageToken") else {}))


def getTranscription(video_id):
    try:
        return video_id, YouTubeTranscriptApi.get_transcript(video_id, ['fr'])
    except (ValueError, Exception):
        return video_id, None

def get_transcriptions(videos_data):
    i = 0
    with ThreadPool(len(videos_data)) as pool:
        for data in pool.imap_unordered(getTranscription, videos_data.keys()):
            i += 1
            video_id, transcription = data
            print(f'{str(i).zfill(len(str(len(videos_data))))}/{len(videos_data)} -> {"" if transcription else "FAILED"} -> {videos_data.get(video_id)}')
            yield data


def main():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "secrets/code_secret_client_818316336553-0okberju6cmr65vs4qqdtuq5tmgmplsp.apps.googleusercontent.com.json"

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    dict = {video_id: transcription for video_id, transcription in get_transcriptions(get_full_video_list("UCoZoRz4-y6r87ptDp4Jk74g", youtube))}
    pp.pprint(dict)


if __name__ == "__main__":
    main()
