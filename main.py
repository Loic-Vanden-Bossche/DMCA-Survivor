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

t_lang = 'en'


def get_progress(curr, total):
    return f'{str(curr).zfill(len(str(total)))}/{total}'


def get_full_video_list_from_yt(channel_id, youtube, pg_token=None):
    pg_data = youtube.search().list(
        part="id, snippet",
        channelId=channel_id,
        maxResults=50,
        pageToken=pg_token
    ).execute()

    return dict(
        {
            item["id"]["videoId"]: item["snippet"]["title"] for
            item in pg_data["items"] if item["id"]["kind"] == "youtube#video"
        },
        **(get_full_video_list_from_yt(channel_id, youtube, pg_data.get("nextPageToken"))
           if pg_data.get("nextPageToken")
           else {})
    )


def get_transcription_from_yt(video_id):
    try:
        return video_id, YouTubeTranscriptApi.get_transcript(video_id, [t_lang])
    except (ValueError, Exception):
        return video_id, None


def get_transcriptions_from_ytb(videos_data):
    i = 0
    with ThreadPool(len(videos_data)) as pool:
        for data in pool.imap_unordered(get_transcription_from_yt, videos_data.keys()):
            i += 1
            video_id, transcription = data
            print(f'{get_progress(i, len(videos_data))} ->'
                  f' {"" if transcription else "FAILED"} ->'
                  f' {videos_data.get(video_id)}')
            yield data


def get_ytb():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "secrets/code_secret_client_818316336553-0okberju6cmr65vs4qqdtuq5tmgmplsp.apps.googleusercontent.com.json"

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
    credentials = flow.run_console()
    return googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)


def getFiles(folder):
    return [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and f.startswith('data_')]


def get_data_from_file(channel_id, folder):
    file = next((x for x in getFiles(folder) if x == 'data_' + channel_id), None)

    if file:
        try:
            with open(f'{folder}/{file}', 'r', encoding='utf-8') as f:
                return eval(f.read())
        except SyntaxError:
            print('Invalid data ... deleting')
            os.remove(f'{folder}/{file}')

    raise FileNotFoundError('File not found or invalid data')


def get_transcriptions_data(channel_id):
    try:
        return get_data_from_file(channel_id, 'channel_cache')
    except FileNotFoundError:
        return get_transcriptions_data_from_ytb(channel_id)


def save_data(data, channel_id, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

    with open(f'{folder}/data_{channel_id}', 'w', encoding='utf-8') as f:
        f.write(str(data))

    return data


def get_transcriptions_data_from_ytb(channel_id):
    return save_data({video_id: transcription for video_id, transcription in
                      get_transcriptions_from_ytb(get_full_video_list_from_yt(channel_id, get_ytb()))}, channel_id,
                     'channel_cache')


def searchString(query, channel_id):
    return [f'https://youtu.be/{video_id}?t={math.floor(transcription["start"])}' for video_id, transcriptions in
            get_transcriptions_data(channel_id).items() if transcriptions for transcription in transcriptions if
            query.lower() in transcription['text'].lower()]


def flatten(t):
    return [item for sublist in t for item in sublist]


def part_str(f_str, n):
    chunk_len = len(f_str) // n
    return [f_str[idx: idx + chunk_len] for idx in range(0, len(f_str), chunk_len)]


def get_transcriptions_str(channel_id):
    return functools.reduce(lambda a, b: a + f' {b}',
                            [
                                i['text'] for i in
                                flatten([t for t in get_transcriptions_data(channel_id).values() if t is not None])
                            ])


def get_unique(arr):
    return list(dict.fromkeys(arr))


def set_lang(lang):
    global t_lang
    t_lang = lang


def get_parted_names(nlp, tag_name, parted_str):
    return [ent.text.strip() for ent in nlp(parted_str).ents if ent.label_ == tag_name]


def get_people_names(channel_id, lang):
    try:
        return get_data_from_file(channel_id, 'names_cache')
    except FileNotFoundError:

        def print_progress(i, n, data):
            i += 1
            print(get_progress(i, n))
            return data

        nlp, tag_name, lang = spacy_init(lang)
        set_lang(lang)

        parted_str = part_str(get_transcriptions_str(channel_id), 100)

        return save_data(get_unique(flatten(
            [
                print_progress(i, len(parted_str), data) for
                i, data in
                enumerate(ThreadPool(len(parted_str)).imap_unordered(
                    functools.partial(get_parted_names, nlp, tag_name), parted_str)
                )
            ]
        )), channel_id, 'names_cache')


def spacy_init(lang='en'):
    try:
        lang = lang.lower()
        model_name, tag_name = {
            'en': ('en_core_web_lg', 'PERSON'),
            'fr': ('fr_core_news_lg', 'PER')
        }[lang]
        print(f'No cache found, creating with model {model_name} ...')
        return spacy.load(model_name), tag_name, lang
    except KeyError:
        print('Language not supported, using default')
        return spacy.load('en_core_web_lg'), 'PERSON', 'en'


def main():
    # Palamashow : UCoZoRz4-y6r87ptDp4Jk74g
    # Les kassos : UCv88958LRDfndKV_Y7XmAnA
    # Wankil Studio : UCYGjxo5ifuhnmvhPvCc3DJQ
    # JDG : UC_yP2DpIgs5Y1uWC0T03Chw

    for name in get_people_names('UCoZoRz4-y6r87ptDp4Jk74g', 'fr'):
        print(name)


if __name__ == "__main__":
    main()
