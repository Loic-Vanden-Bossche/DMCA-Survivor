import sys

import pygame
import loader
from settings import *
from level import Level


class Game:
    def __init__(self):
        # general setup
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Zelda')
        self.clock = pygame.time.Clock()

        self.level = Level()

    def run(self):
        # channel_id = 'UCQVaKQcp4OxSg1eC6SF3NTw'
        # loader.loading_loop(channel_id)
        # loader.channel_menu_loop(channel_id)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                self.level.input(event)

            self.screen.fill('black')
            self.level.run()
            pygame.display.update()
            self.clock.tick(60)


def main():
    # Palmashow : UCoZoRz4-y6r87ptDp4Jk74g
    # Les kassos : UCv88958LRDfndKV_Y7XmAnA
    # Wankil Studio : UCYGjxo5ifuhnmvhPvCc3DJQ
    # JDG : UC_yP2DpIgs5Y1uWC0T03Chw

    game = Game()
    game.run()


if __name__ == "__main__":
    main()
