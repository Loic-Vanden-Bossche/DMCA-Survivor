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

            pygame.display.get_surface().fill('black')
            self.level.update(time_delta)
            pygame.display.update()

    def __init__(self, difficulty, names):
        self.running = True
        self.clock = pygame.time.Clock()

        self.level = Level(difficulty, names)
