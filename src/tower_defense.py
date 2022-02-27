import pygame

import utils
from level import Level
from settings import *


class TowerDefense:
    def run(self):
        while self.running:
            time_delta = self.clock.tick(FPS)/1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    utils.exit_app()

                self.level.input(event)

            if not self.level.player.is_alive():
                self.running = False

            pygame.display.get_surface().blit(self.back, pygame.Rect((0, 0), (200, 200)))
            self.level.update(time_delta)
            pygame.display.update()

        return self.level.get_level_scores()

    def __init__(self, difficulty, names):
        self.running = True
        self.clock = pygame.time.Clock()

        self.back = utils.scale_surface_with(pygame.image.load('../graphics/background_game.jpg'),
                                             pygame.display.get_surface().get_width())

        self.level = Level(difficulty, names)
