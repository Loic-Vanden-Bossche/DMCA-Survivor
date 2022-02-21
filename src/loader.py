import functools
import math
import os
import sys
from multiprocessing.pool import ThreadPool
from uuid import uuid5, UUID

import pygame
import pygame_gui
import requests
import skimage
import spacy
import youtube_dl
import yt_dlp as dlp
from pygame_gui.core import ObjectID
from pytimeparse.timeparse import timeparse
from youtube_transcript_api import YouTubeTranscriptApi
from youtubesearchpython import *

from src import utils
from src.scrapper import GoogleImageDownloader
from src.utils import ThreadWithReturnValue

t_lang = 'fr'

isDebug = True

progress_status = {
    'status': '',
    'title': '',
    'progress': 0
}


def debug(*args):
    if isDebug: print(*args)


def get_progress(curr, total):
    return f'{str(curr).zfill(len(str(total)))}/{total}'


def format_channel_infos(infos):
    return {'name': infos['name'], 'thumb': infos['thumbnails'][-1], 'link': infos['link'], 'id': infos['id']}


def format_video_infos(infos):
    return infos


def download_channel_thumb(channel_id, link):
    if not os.path.exists(f'cache/{channel_id}'):
        os.makedirs(f'cache/{channel_id}')

    img_data = requests.get(link).content
    with open(f'cache/{channel_id}/thumb.jpg', 'wb') as handler:
        handler.write(img_data)


def get_full_video_list_from_yt(channel_id):
    playlist = Playlist(playlist_from_channel_id(channel_id))
    while playlist.hasMoreVideos:
        playlist.getNextVideos()

    channel_data = format_channel_infos(playlist.info['info']['channel'])

    download_channel_thumb(channel_id, channel_data['thumb']['url'])

    reset_progress('videos')

    return {
        'channel': channel_data,
        'videos': dict({
            item["id"]: item["title"] for item in
            sorted([
                set_progress_status(
                    f'{get_progress(i, len(playlist.videos))} - {x["title"]}',
                    calculate_progress(i, len(playlist.videos)),
                    x)
                for i, x in
                enumerate(
                    ThreadPool(len(playlist.videos)).imap_unordered(Video.get, [v["id"] for v in playlist.videos]))
            ], key=lambda x: int(x['viewCount']['text']), reverse=True)[0:100]
        })
    }


def get_transcription_from_yt(video_id):
    try:
        return video_id, YouTubeTranscriptApi.get_transcript(video_id, [t_lang])
    except (ValueError, Exception):
        return video_id, None


def reset_progress(title):
    global progress_status
    progress_status.update(title=title, status='', progress=0)


def calculate_progress(n, total):
    return n / total


def set_progress_status(status, progress, data=None):
    global progress_status
    progress_status.update(status=status, progress=progress)
    debug(f'{progress_status.get("title")} -> {round(progress * 100, 1)}% -> {status}')
    return data


def get_transcriptions_from_ytb(videos_data):
    i = 0
    reset_progress('resolving translations')
    with ThreadPool(len(videos_data)) as pool:
        for data in pool.imap_unordered(get_transcription_from_yt, videos_data.keys()):
            i += 1
            video_id, _ = data
            yield set_progress_status(videos_data.get(video_id), calculate_progress(i, len(videos_data)), data)


def get_data_from_file(file_name, folder):
    folder = 'cache/' + folder
    try:
        with open(f'{folder}/{file_name}', 'r', encoding='utf-8') as f:
            return eval(f.read())
    except SyntaxError:
        debug('Invalid data ... deleting')
        os.remove(f'{folder}/{file_name}')

    raise FileNotFoundError('File not found or invalid data')


def get_transcriptions_data(channel_id):
    try:
        return get_data_from_file('channel_data', channel_id)
    except FileNotFoundError:
        return get_transcriptions_data_from_ytb(channel_id)


def save_data(data, file_name, folder):
    folder = 'cache/' + folder
    if not os.path.exists(folder):
        os.makedirs(folder)

    with open(f'{folder}/{file_name}', 'w', encoding='utf-8') as f:
        f.write(str(data))

    return data


def get_transcriptions_data_from_ytb(channel_id):
    channel_data, video_list = get_full_video_list_from_yt(channel_id).values()
    return save_data({'channel': channel_data,
                      'videos': {video_id: transcription for video_id, transcription in
                                 get_transcriptions_from_ytb(video_list)}}, 'channel_data', channel_id)


def searchString(query, channel_id):
    return [f'https://youtu.be/{video_id}?t={math.floor(transcription["start"])}' for video_id, transcriptions in
            get_transcriptions_data(channel_id)['videos'].items() if transcriptions for transcription in transcriptions
            if query.lower() in transcription['text'].lower()]


def flatten(t):
    return [item for sublist in t for item in sublist]


def part_str(f_str, n):
    chunk_len = len(f_str) // n
    return [f_str[idx: idx + chunk_len] for idx in range(0, len(f_str), chunk_len)]


def get_transcriptions_str(channel_id):
    return functools.reduce(lambda a, b: a + f' {b}',
                            [
                                i['text'] for i in
                                flatten([t for t in get_transcriptions_data(channel_id)['videos'].values() if
                                         t is not None])
                            ])


def get_unique(arr):
    return [{'id': str(uuid5(UUID('6bccb050-91b0-11ec-b13f-cb90244a3835'), name)), 'name': name} for name in
            list(dict.fromkeys(arr))]


def set_lang(lang):
    global t_lang
    t_lang = lang


def get_parted_names(nlp, tag_name, parted_str):
    return [ent.text.strip() for ent in nlp(parted_str).ents if ent.label_ == tag_name]


def print_progress(i, n, text, data=None):
    prefix, suffix = text
    i += 1
    debug(f'{prefix} -> {get_progress(i, n)} -> {suffix}')
    return data


def get_people_names(channel_id, lang):
    try:
        return get_data_from_file('unique_names', channel_id)
    except FileNotFoundError:

        set_lang(lang)

        parted_str = part_str(get_transcriptions_str(channel_id), 100)

        reset_progress('resolving names')

        set_progress_status('initializing spacy ...', 0)

        nlp, model, tag_name, lang = spacy_init(lang)

        debug(f'No cache found, creating with model {model} ...')
        return save_data(get_unique(flatten(
            [
                set_progress_status(
                    f'{i}%',
                    calculate_progress(i, len(parted_str) - 1),
                    data
                ) for
                i, data in
                enumerate(ThreadPool(len(parted_str)).imap_unordered(
                    functools.partial(get_parted_names, nlp, tag_name), parted_str)
                )
            ]
        )), 'unique_names', channel_id)


def spacy_init(lang='en'):
    try:
        lang = lang.lower()
        model_name, tag_name = {
            'en': ('en_core_web_lg', 'PERSON'),
            'fr': ('fr_core_news_lg', 'PER')
        }[lang]

        try:
            spacy.cli.info(model_name)
        except Exception:
            spacy.cli.download(model_name)

        return spacy.load(model_name), model_name, tag_name, lang
    except KeyError:
        debug('Language not supported, using default')
        return spacy.load('en_core_web_lg'), 'PERSON', 'en'


def get_people_pictures(names):
    reset_progress('getting people pictures')

    set_progress_status('initializing bs4 ...', 0)

    if not os.path.exists('graphics/pictures'):
        os.makedirs('graphics/pictures')

    for i, name in enumerate(ThreadPool(
            len(names)).imap_unordered(functools.partial(GoogleImageDownloader, 'graphics/pictures'),
                                       names)):
        set_progress_status(get_progress(i, len(names) - 1), calculate_progress(i, len(names) - 1))


def part_array(arr, n):
    chunk_len = len(arr) // n
    return [arr[idx: idx + chunk_len] for idx in range(0, len(arr), chunk_len)]


def make_montage(folder, data):
    index, arr = data
    img = f'{folder}/img_carrousel_{index}.png'
    if not os.path.exists(img):
        skimage.io.imsave(img, skimage.util.montage([
            skimage.io.imread(f'https://img.youtube.com/vi/{video_id}/0.jpg') for
            video_id in
            arr
        ], channel_axis=3, grid_shape=(1, len(arr))))
    return img


def generate_images(channel_id, rows):
    arrays = part_array(list(get_transcriptions_data(channel_id)['videos'].keys()), rows)[:-1]

    folder = f'cache/{channel_id}/background_cache'

    if not os.path.exists(folder):
        os.makedirs(folder)

    reset_progress('montage')

    return [
        set_progress_status(f'{get_progress(index + 1, len(arrays))} processed',
                            calculate_progress(index + 1, len(arrays)), img) for index, img in
        enumerate(ThreadPool(len(arrays)).imap_unordered(functools.partial(make_montage, folder),
                                                         [(i, arr) for i, arr in enumerate(arrays)]))
    ]


def download_music_from_channel(channel_id, channel):
    videos = eval(SearchVideos(f'{channel["name"]} Musique').result())['search_result']
    res = []
    i = 0
    while len(res) == 0:
        i += 1
        res = [
            video for video in videos
            if timeparse(video['duration']) <= 300 + (100 * i)
        ]

    completed = False

    i = 0

    def dl_hook(d):
        if d['status'] == 'downloading':
            set_progress_status(
                f'{d["_percent_str"]} - {d["_speed_str"]}', calculate_progress(d["downloaded_bytes"], d["total_bytes"]))

        elif d['status'] == 'finished':
            set_progress_status('Done downloading, now converting ...', calculate_progress(100, 100))

    while not completed:
        try:
            video_url = res[i]['link']
            print(video_url)
            video_info = dlp.YoutubeDL().extract_info(
                url=video_url, download=False
            )
            filename = f"cache/{channel_id}/music.webm"
            options = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'keepvideo': False,
                'progress_hooks': [dl_hook],
                'outtmpl': filename,
            }

            i += 1

            reset_progress('downloading music')

            with dlp.YoutubeDL(options) as ydl:
                ydl.download([video_info['webpage_url']])

            completed = True
            print("Download complete... {}".format(filename))
        except youtube_dl.utils.DownloadError:
            debug('retrying ...')


def get_musics(channel_id):
    channel, _ = get_transcriptions_data(channel_id).values()
    folder = f'cache/{channel_id}'

    if not os.path.exists(folder):
        os.makedirs(folder)

    if not os.path.exists(f'{folder}/music.mp3'):
        download_music_from_channel(channel_id, channel)


class ProgressScreen:

    @property
    def progress(self):
        return self._progress_bar.percent_full

    @progress.setter
    def progress(self, progress):
        self._progress_bar.percent_full = progress

    @property
    def status(self):
        return self._status_label.text

    @status.setter
    def status(self, status):
        self._status_label.set_text(status)

    @property
    def title(self):
        return self._status_label.text

    @title.setter
    def title(self, status):
        self._title_label.set_text(status)

    def update(self, time_delta):

        self._window_surface.blit(self._background, (0, 0))

        if self._thumb:
            self._window_surface.blit(self._thumb, utils.get_centered_pos_from_wh(
                self._thumb.get_width(),
                self._thumb.get_height(),
                -100
            ))

        self._manager.update(time_delta)
        self._set_status_from_global()
        self._manager.draw_ui(self._window_surface)

    def _set_status_from_global(self):
        global progress_status
        status, title, progress = progress_status.values()

        thumb_path = f'cache/{self._channel_id}/thumb.jpg'
        if os.path.exists(thumb_path) and not self._thumb:
            img = pygame.image.load(thumb_path)
            self._thumb = utils.scale_surface_height(img, 200)

        self.title = title
        self.status = status
        self.progress = progress

    def __init__(self, channel_id, status='', title=''):
        self._window_surface = pygame.display.get_surface()
        self._manager = pygame_gui.UIManager(utils.get_dims_from_surface(self._window_surface), 'themes/loading.json')
        self._background = pygame.Surface(utils.get_dims_from_surface(self._window_surface))
        self._background.fill(self._manager.ui_theme.get_colour('dark_bg'))

        self._thumb = None
        self._channel_id = channel_id

        height = 30

        self._progress_bar = pygame_gui.elements.UIStatusBar(utils.get_centered_rect(200, height, 100),
                                                             self._manager,
                                                             None,
                                                             object_id=ObjectID('#progress_bar'))

        self._status_label = pygame_gui.elements.UILabel(
            utils.get_centered_rect(self._window_surface.get_width(), height, 100 + height),
            status,
            self._manager,
            object_id=ObjectID('#progress_bar_label'))

        self._title_label = pygame_gui.elements.UILabel(
            utils.get_centered_rect(self._window_surface.get_width(), height, 100 - height),
            title,
            self._manager,
            object_id=ObjectID('#progress_bar_label'))


def load_music(channel_id):
    pygame.mixer.music.load(f'cache/{channel_id}/music.mp3')
    pygame.mixer.music.play()
    pygame.mixer.music.set_volume(0.3)


class LoadingScreen:
    def run(self):
        while self.running:
            time_delta = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.progress_ui.update(time_delta)

            pygame.display.update()

        return self.thread.join()

    def load_parameters_for_channel(self):
        names = get_people_names(self.channel_id, 'fr')
        get_people_pictures(names)

        generate_images(self.channel_id, 8)

        get_musics(self.channel_id)

        self.running = False
        return names

    def __init__(self, channel_id):
        self.channel_id = channel_id
        self.running = True

        pygame.display.set_caption('loading ....')

        self.thread = ThreadWithReturnValue(target=self.load_parameters_for_channel)
        self.thread.start()

        self.progress_ui = ProgressScreen(channel_id)
        self.clock = pygame.time.Clock()