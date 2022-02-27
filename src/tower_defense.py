import pygame

import utils
from level import Level
from settings import *


class TowerDefense:
    def run(self):
        while self._running:
            time_delta = self._clock.tick(FPS)/1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    utils.exit_app()

                self._level.input(event)

            if not self._level.player.is_alive():
                self._running = False

            pygame.display.get_surface().blit(self._back, pygame.Rect((0, 0), (200, 200)))
            self._level.update(time_delta)
            pygame.display.update()

        return self._level.get_level_scores()

    def __init__(self, channel_id, difficulty, names):
        self._running = True
        self._clock = pygame.time.Clock()

        self._back = utils.scale_surface_with(pygame.image.load('../graphics/background_game.jpg'),
                                             pygame.display.get_surface().get_width())

        self._level = Level(channel_id, difficulty, names)
