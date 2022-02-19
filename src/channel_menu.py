import random
import sys
import pygame
from src import utils, loader

class Background:

    def update(self, time_delta):
        self._window_surface.blit(self._background, (0, 0))
        for carrousel in self._carrousels:
            carrousel.update(time_delta)

        self._window_surface.blit(self._foreground, (0, 0))

    def _get_image_files(self, folder, rows):
        files = utils.getFiles(folder, 'img_carrousel_')
        for idx in range(0, rows - 1):
            if f'img_carrousel_{idx}.png' not in files:
                raise FileNotFoundError

        return files

    def _generate_carrousels(self):
        carrousel_height = self._window_surface.get_height() / self._row_count
        folder = f'cache/{self._channel_id}/background_cache'

        return [
            Carrousel(path,
                      carrousel_height,
                      random.uniform(10, 20),
                      index * carrousel_height,
                      'left' if index % 2 else 'right')
            for index, path in enumerate([f'{folder}/{file}' for file in self._get_image_files(folder, self._row_count)])
        ]

    def __init__(self, channel_id, row_count):
        self._window_surface = pygame.display.get_surface()
        self._channel_id = channel_id
        self._row_count = row_count
        self._background = pygame.Surface(utils.get_dims_from_surface(self._window_surface))
        self._background.fill(pygame.Color('#000000'))
        self._foreground = self._background.copy()
        self._foreground.set_alpha(128)
        self._carrousels = self._generate_carrousels()


class Carrousel:

    def _get_right(self):
        if self._direction == 'right':
            return -self._image.get_width()
        elif self._direction == 'left':
            return 0

    def _get_left(self):
        if self._direction == 'right':
            return 0
        elif self._direction == 'left':
            return self._image.get_width()

    def _move(self, time_delta):
        speed = (self._speed * time_delta)

        if self._direction == 'right':
            self._left += speed
            self._right += speed
        elif self._direction == 'left':
            self._left -= speed
            self._right -= speed

    def update(self, time_delta):

        self._move(time_delta)

        if self._direction == 'right':
            if round(self._right) == 0:
                self._right = self._get_right()

            if round(self._left) == self._image.get_width():
                self._left = self._get_left()
        elif 'left':
            if round(self._right) == -self._image.get_width():
                self._right = self._get_right()

            if round(self._left) == 0:
                self._left = self._get_left()

        self._window_surface.blit(self._image, (self._left, self._y_pos))
        self._window_surface.blit(self._image, (self._right, self._y_pos))

    def __init__(self, montage_path, height, speed, y_pos=0, direction='right'):
        img = pygame.image.load(montage_path)
        self._window_surface = pygame.display.get_surface()
        self._image = pygame.transform.smoothscale(img, (height * (img.get_width() / img.get_height()), height))
        self._speed = speed
        self._direction = direction
        self._left = self._get_left()
        self._right = self._get_right()
        self._y_pos = y_pos


def channel_menu_loop(data):
    is_display_menu = True

    pygame.display.set_caption('Channel menu')

    loader.load_music(data)

    menu_back = Background(data, 8)

    clock = pygame.time.Clock()

    while is_display_menu:
        time_delta = clock.tick(120) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        menu_back.update(time_delta)

        pygame.display.update()
