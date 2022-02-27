import pygame
from pygame_gui.core import ObjectID

from player import Player
from enemy import Enemy
from bullet import Bullet
from settings import *
import pygame_gui
from random import *
import utils


class Names:

    def get_cursor(self):
        if self._cursor >= len(self._names):
            self._cursor = -1

        self._cursor += 1
        return self._cursor

    @property
    def current(self):
        return self._names[self.get_cursor()]

    def __init__(self, names):
        self._cursor = -1

        shuffle(names)
        self._names = names

class StatusBar(pygame_gui.elements.UIPanel):

    @property
    def wave(self):
        return self._status_text.text

    @wave.setter
    def wave(self, wave):
        self._status_text.set_text(f'Wave {wave}')

    def __init__(self, width, manager):
        super().__init__(pygame.Rect(pygame.display.get_surface().get_width() - width, 0, width, 75), 1, manager)

        self._status_text = pygame_gui.elements.UILabel(
            pygame.Rect(0, 0, self.relative_rect.w, self.relative_rect.h),
            'Wave 1', self.ui_manager, container=self, object_id=ObjectID('#wave_text'))


def sprite_alive(sprite):
    return sprite.alive()


class Level:
    def __init__(self, channel_id,  difficulty, names):
        self._manager = pygame_gui.UIManager((WIDTH, HEIGHT), '../themes/game.json')
        self._display_surface = pygame.display.get_surface()
        self._visible_sprites = pygame.sprite.Group()
        self.player = Player(channel_id, GOAL, (self._visible_sprites,), difficulty)
        self._enemies = []
        self._bullets = []
        self._wave = 1
        self._enemiesFactor = 10
        self._enemiesSpawnOffset = 3000
        self._timeToEnemySpawn = None
        self._inFight = True
        self._enemiesSpawned = 0
        self._enemiesNames = Names(names)
        self._channel_thumbs = [
            f'../cache/{channel_id}/video_thumbs/{video_file}' for video_file
            in utils.getFiles(f'../cache/{channel_id}/video_thumbs', '')
        ]
        self._status_bar = StatusBar(200, self._manager)

    def input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.player.is_alive():
                self._bullets.append(Bullet(self._channel_thumbs, (self._visible_sprites,)))

    def get_level_scores(self):
        return self._wave

    def spawn_enemy(self):
        if choice([False, True]):
            x_position = randint(-30, WIDTH + 30)
            y_position = choice([randint(-30, 0), randint(HEIGHT, HEIGHT + 30)])

        else:
            x_position = choice([randint(-30, 0), randint(WIDTH, WIDTH + 30)])
            y_position = randint(-30, HEIGHT + 30)

        self._enemies.append(Enemy(
            (x_position, y_position),
            (self._visible_sprites,),
            self.player,
            self._manager,
            self._enemiesNames.current))
        self._enemiesSpawned += 1

    def update(self, time_delta):
        self._bullets = list(filter(sprite_alive, self._bullets))
        self._enemies = list(filter(sprite_alive, self._enemies))

        if len(self._visible_sprites):
            if not self.player.is_alive():
                self._inFight = False

            if self._inFight and (self._enemiesSpawned < self._wave * self._enemiesFactor):
                if self._timeToEnemySpawn:
                    if pygame.time.get_ticks() >= self._timeToEnemySpawn + self._enemiesSpawnOffset:
                        self._timeToEnemySpawn = pygame.time.get_ticks()
                        self.spawn_enemy()
                else:
                    self._timeToEnemySpawn = pygame.time.get_ticks()
                    self.spawn_enemy()

            elif self._inFight and not len(self._enemies):
                self._enemiesSpawnOffset = self._enemiesSpawnOffset * 0.85
                self._wave += 1
                self._status_bar.wave = self._wave
                self._enemiesFactor += ENEMIES_FACTOR_AUGMENTATION

            for bullet in self._bullets:
                bullet.check_collision(self._enemies)

            self._visible_sprites.draw(self._display_surface)
            self._manager.draw_ui(self._display_surface)
            self._visible_sprites.update()
            self._manager.update(time_delta)
