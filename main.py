import math
import os
import pprint
from youtube_transcript_api import YouTubeTranscriptApi
from multiprocessing.pool import ThreadPool
import functools

from youtubesearchpython import *
import youtube_dl

import yt_dlp as dlp

from pytimeparse.timeparse import timeparse

import pygame
import pygame_gui
import skimage

import random
import spacy

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

pp = pprint.PrettyPrinter(indent=4)

t_lang = 'fr'

isDebug = True

def debug(*args):
    if isDebug: pp.pprint(*args)


def get_progress(curr, total):
    return f'{str(curr).zfill(len(str(total)))}/{total}'


def format_channel_infos(infos):
    return {'name': infos['name'], 'thumb': infos['thumbnails'][-1], 'link': infos['link'], 'id': infos['id']}

def format_video_infos(infos):
    return infos

def get_full_video_list_from_yt(channel_id):
    playlist = Playlist(playlist_from_channel_id(channel_id))
    while playlist.hasMoreVideos:
        playlist.getNextVideos()

    return {
        'channel': format_channel_infos(playlist.info['info']['channel']),
        'videos': dict({
            item["id"]: item["title"] for item in
            sorted([
                x for x in
                ThreadPool(len(playlist.videos)).imap_unordered(Video.get, [v["id"] for v in playlist.videos])
            ], key=lambda x: int(x['viewCount']['text']), reverse=True)[0:100]
        })
    }


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
            debug(f'{get_progress(i, len(videos_data))} ->'
                  f' {"" if transcription else "FAILED"} ->'
                  f' {videos_data.get(video_id)}')
            yield data


def getFiles(folder, start='data_'):
    return [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and f.startswith(start)]


def get_data_from_file(channel_id, folder):
    file = next((x for x in getFiles(folder) if x == 'data_' + channel_id), None)

    if file:
        try:
            with open(f'{folder}/{file}', 'r', encoding='utf-8') as f:
                return eval(f.read())
        except SyntaxError:
            debug('Invalid data ... deleting')
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
    channel_data, video_list = get_full_video_list_from_yt(channel_id).values()
    return save_data({'channel': channel_data,
                      'videos': {video_id: transcription for video_id, transcription in
                                 get_transcriptions_from_ytb(video_list)}}, channel_id, 'channel_cache')


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
    return list(dict.fromkeys(arr))


def set_lang(lang):
    global t_lang
    t_lang = lang


def get_parted_names(nlp, tag_name, parted_str):
    return [ent.text.strip() for ent in nlp(parted_str).ents if ent.label_ == tag_name]


def print_progress(i, n, text, data):
    prefix, suffix = text
    i += 1
    debug(f'{prefix} -> {get_progress(i, n)} -> {suffix}')
    return data


def get_people_names(channel_id, lang):
    try:
        return get_data_from_file(channel_id, 'names_cache')
    except FileNotFoundError:

        nlp, model, tag_name, lang = spacy_init(lang)
        set_lang(lang)

        parted_str = part_str(get_transcriptions_str(channel_id), 100)

        debug(f'No cache found, creating with model {model} ...')

        return save_data(get_unique(flatten(
            [
                print_progress(i, len(parted_str), ('people resolver', 'chunk processed'), data) for
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

        try:
            spacy.cli.info(model_name)
        except Exception:
            spacy.cli.download(model_name)

        return spacy.load(model_name), model_name, tag_name, lang
    except KeyError:
        debug('Language not supported, using default')
        return spacy.load('en_core_web_lg'), 'PERSON', 'en'


window_dims = (1280, 720)

pygame.init()
window_surface = pygame.display.set_mode(window_dims)


def part_array(arr, n):
    chunk_len = len(arr) // n
    return [arr[idx: idx + chunk_len] for idx in range(0, len(arr), chunk_len)]


class Background:

    def display(self):
        for carrousel in self.carrousels:
            carrousel.display()

    def get_image_files(self, folder, rows):
        files = getFiles(folder, 'img_carrousel_')
        for idx in range(0, rows - 1):
            if f'img_carrousel_{idx}.png' not in files:
                raise FileNotFoundError

        return files

    def make_montage(self, folder, data):
        index, arr = data
        img = f'{folder}/img_carrousel_{index}.png'
        skimage.io.imsave(img, skimage.util.montage([
            skimage.io.imread(f'https://img.youtube.com/vi/{video_id}/0.jpg') for
            video_id in
            arr
        ], channel_axis=3, grid_shape=(1, len(arr))))
        return img

    def generate_images(self, folder, rows):
        arrays = part_array(list(get_transcriptions_data(self.channel_id)['videos'].keys()), rows)[:-1]

        if not os.path.exists(folder):
            os.makedirs(folder)

        return [
            print_progress(index, len(arrays), ('montage', 'processed'), img) for index, img in
            enumerate(ThreadPool(len(arrays)).imap_unordered(functools.partial(self.make_montage, folder),
                                                             [(i, arr) for i, arr in enumerate(arrays)]))
        ]

    def generate_carrousels(self):
        carrousel_height = window_surface.get_height() / self.row_count
        folder = f'background_cache/{self.channel_id}'

        try:
            res = [f'{folder}/{file}' for file in self.get_image_files(folder, self.row_count)]
        except FileNotFoundError:
            res = self.generate_images(folder, self.row_count)

        return [
            Carrousel(path,
                      carrousel_height,
                      random.uniform(0.01, 0.05),
                      index * carrousel_height,
                      'left' if index % 2 else 'right')
            for index, path in enumerate(res)
        ]

    def __init__(self, channel_id, row_count):
        self.channel_id = channel_id
        self.row_count = row_count
        self.carrousels = self.generate_carrousels()


class Carrousel:

    def get_right(self):
        if self.direction == 'right':
            return -self.image.get_width()
        elif self.direction == 'left':
            return 0

    def get_left(self):
        if self.direction == 'right':
            return 0
        elif self.direction == 'left':
            return self.image.get_width()

    def move(self):
        if self.direction == 'right':
            self.left += self.speed
            self.right += self.speed
        elif self.direction == 'left':
            self.left -= self.speed
            self.right -= self.speed

    def display(self):

        self.move()

        if self.direction == 'right':
            if round(self.right) == 0:
                self.right = self.get_right()

            if round(self.left) == self.image.get_width():
                self.left = self.get_left()
        elif 'left':
            if round(self.right) == -self.image.get_width():
                self.right = self.get_right()

            if round(self.left) == 0:
                self.left = self.get_left()

        window_surface.blit(self.image, (self.left, self.y_pos))
        window_surface.blit(self.image, (self.right, self.y_pos))

    def __init__(self, montage_path, height, speed, y_pos=0, direction='right'):
        img = pygame.image.load(montage_path)
        self.image = pygame.transform.smoothscale(img, (height * (img.get_width() / img.get_height()), height))
        self.speed = speed
        self.direction = direction
        self.left = self.get_left()
        self.right = self.get_right()
        self.y_pos = y_pos


def get_musics(channel_id):
    channel, _ = get_transcriptions_data(channel_id).values()

    if not os.path.exists('musics_cache'):
        os.makedirs('musics_cache')

    if os.path.exists(f'musics_cache/{channel_id}.mp3'):
        return

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

    def my_hook(d):
        print(d['status'])
        if d['status'] == 'finished':
            print('Done downloading, now converting ...')

    while not completed:
        try:
            video_url = res[i]['link']
            print(video_url)
            video_info = dlp.YoutubeDL().extract_info(
                url=video_url, download=False
            )
            filename = f"musics_cache/{channel_id}.webm"
            options = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'keepvideo': False,
                'progress_hooks': [my_hook],
                'outtmpl': filename,
            }

            i += 1

            with dlp.YoutubeDL(options) as ydl:
                ydl.download([video_info['webpage_url']])

            completed = True
            print("Download complete... {}".format(filename))
        except youtube_dl.utils.DownloadError:
            debug('retrying ...')


def main():
    # Palamashow : UCoZoRz4-y6r87ptDp4Jk74g
    # Les kassos : UCv88958LRDfndKV_Y7XmAnA
    # Wankil Studio : UCYGjxo5ifuhnmvhPvCc3DJQ
    # JDG : UC_yP2DpIgs5Y1uWC0T03Chw

    channel_id = 'UCYGjxo5ifuhnmvhPvCc3DJQ'

    get_people_names('UCYGjxo5ifuhnmvhPvCc3DJQ', 'fr')

    get_musics(channel_id)

    back = Background(channel_id, 8)

    pygame.display.set_caption('Game')

    background = pygame.Surface(window_dims)
    background.fill(pygame.Color('#000000'))

    foreground = background.copy()
    foreground.set_alpha(128)

    is_running = True

    pygame.mixer.music.load(f'musics_cache/{channel_id}.mp3')
    pygame.mixer.music.play()
    pygame.mixer.music.set_volume(0.6)

    while is_running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

        window_surface.blit(background, (0, 0))
        back.display()
        window_surface.blit(foreground, (0, 0))
        pygame.display.update()


if __name__ == "__main__":
    main()
