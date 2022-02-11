import math
import os
import pprint
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from youtube_transcript_api import YouTubeTranscriptApi
from multiprocessing.pool import ThreadPool
import functools

import spacy

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

pp = pprint.PrettyPrinter(indent=4)

def get_full_video_list_from_yt(channel_id, youtube, pg_token=None):
    pg_data = youtube.search().list(
        part="id, snippet",
        channelId=channel_id,
        maxResults=50,
        pageToken=pg_token
    ).execute()

    return dict({item["id"]["videoId"]: item["snippet"]["title"] for item in pg_data["items"] if item["id"]["kind"] == "youtube#video"}, **(get_full_video_list_from_yt(channel_id, youtube, pg_data.get("nextPageToken")) if pg_data.get("nextPageToken") else {}))


def get_transcription_from_yt(video_id):
    try:
        return video_id, YouTubeTranscriptApi.get_transcript(video_id, ['fr'])
    except (ValueError, Exception):
        return video_id, None


def get_transcriptions_from_ytb(videos_data):
    i = 0
    with ThreadPool(len(videos_data)) as pool:
        for data in pool.imap_unordered(get_transcription_from_yt, videos_data.keys()):
            i += 1
            video_id, transcription = data
            print(f'{str(i).zfill(len(str(len(videos_data))))}/{len(videos_data)} -> {"" if transcription else "FAILED"} -> {videos_data.get(video_id)}')
            yield data


def get_ytb():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "secrets/code_secret_client_818316336553-0okberju6cmr65vs4qqdtuq5tmgmplsp.apps.googleusercontent.com.json"

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
    credentials = flow.run_console()
    return googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)


def getFiles():
    return [f for f in os.listdir('channel_cache') if os.path.isfile(os.path.join('channel_cache', f)) and f.startswith('data_')]


def get_transcriptions_data(channel_id):
    channel = next((x for x in getFiles() if x == 'data_' + channel_id), None)

    if channel:
        try:
            with open('channel_cache/' + channel, 'r', encoding='utf-8') as f:
                return eval(f.read())
        except SyntaxError:
            print('Invalid data ... deleting')
            os.remove('channel_cache/' + channel)

    return get_data_from_ytb(channel_id)


def save_data(data, channel_id):
    with open('channel_cache/data_' + channel_id, 'w', encoding='utf-8') as f:
        f.write(str(data))

    return data


def get_data_from_ytb(channel_id):
    return save_data({video_id: transcription for video_id, transcription in get_transcriptions_from_ytb(get_full_video_list_from_yt(channel_id, get_ytb()))}, channel_id)


def searchString(query, channel_id):
    return [f'https://youtu.be/{video_id}?t={math.floor(transcription["start"])}' for video_id, transcriptions in get_transcriptions_data(channel_id).items() if transcriptions for transcription in transcriptions if query.lower() in transcription['text'].lower()]


def flatten(t):
    return [item for sublist in t for item in sublist]


def part_str(str, n):
    return [str[i:i+n] for i in range(0, len(str), n)]


def get_transcriptions_str(channel_id):
    return functools.reduce(lambda a, b: a + f' {b}', [i['text'] for i in flatten([t for t in get_transcriptions_data(channel_id).values() if t is not None])])


def get_unique(arr):
    return list(dict.fromkeys(arr))


def get_people_names(channel_id, nlp, max_str_size=1000000):
    return get_unique(flatten([[ent.text.strip() for ent in nlp(s).ents if ent.label_ == 'PER'] for s in part_str(get_transcriptions_str(channel_id), max_str_size)]))


def main():

    # Palamashow : UCoZoRz4-y6r87ptDp4Jk74g
    # Les kassos : UCv88958LRDfndKV_Y7XmAnA
    # JDG : UC_yP2DpIgs5Y1uWC0T03Chw

    for name in get_people_names('UCoZoRz4-y6r87ptDp4Jk74g', spacy.load("fr_core_news_lg")):
        print(name)


if __name__ == "__main__":
    main()
