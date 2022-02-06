import math
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


def get_youtube():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "secrets/code_secret_client_818316336553-0okberju6cmr65vs4qqdtuq5tmgmplsp.apps.googleusercontent.com.json"

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
    credentials = flow.run_console()
    return googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)


def getFiles():
    return [f for f in os.listdir('channel_cache') if os.path.isfile(os.path.join('channel_cache', f)) and f.startswith('data_')]


def get_transcription_data(channel_id):
    channel = next((x for x in getFiles() if x == 'data_' + channel_id), None)

    if channel:
        try:
            with open('channel_cache/' + channel, 'r', encoding='utf-8') as f:
                return eval(f.read())
        except SyntaxError:
            print('Invalid data ... deleting')
            os.remove('channel_cache/' + channel)

    return get_data_from_youtube(channel_id)

def save_data(data, channel_id):
    with open('channel_cache/data_' + channel_id, 'w', encoding='utf-8') as f:
        f.write(str(data))

    return data

def get_data_from_youtube(channel_id):
    return save_data({video_id: transcription for video_id, transcription in get_transcriptions(get_full_video_list(channel_id, get_youtube()))}, channel_id)


def searchString(query, channel_id):
    return [f'https://youtu.be/{video_id}?t={math.floor(transcription["start"])}' for video_id, transcriptions in get_transcription_data(channel_id).items() if transcriptions for transcription in transcriptions if query.lower() in transcription['text'].lower()]


def print_search_results(search_response):
    for link in search_response:
        print(link)

def main():

    print_search_results(searchString("motifs indiens", 'UCoZoRz4-y6r87ptDp4Jk74g'))


if __name__ == "__main__":
    main()
