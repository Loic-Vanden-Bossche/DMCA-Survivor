import pygame

from src import utils
from src.level import Level


class TowerDefense:
    def run(self):
        while self.running:
            time_delta = self.clock.tick(60)/1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    utils.exit_app()

                self.level.input(event)

            if not self.level.player.is_alive():
                self.running = False

            pygame.display.get_surface().fill('black')
            self.level.run(time_delta)
            pygame.display.update()

    def __init__(self, difficulty, names):
        self.running = True
        self.clock = pygame.time.Clock()

        self.level = Level(difficulty, names)
