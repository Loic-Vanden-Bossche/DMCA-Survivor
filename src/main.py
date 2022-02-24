import sys

import pygame

from src.channel_menu import ChannelMenu
from src.level import Level
from src.loader import LoadingScreen
from src.main_menu import MainMenu
from settings import *


class Game(MainMenu):
    def __init__(self):
        # general setup
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Zelda')
        self.clock = pygame.time.Clock()
        super().__init__()

        self.level = None

    def run_game(self):

        running = True

        while running:
            time_delta = self.clock.tick(60)/1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self.level.input(event)

            if not self.level.player.is_alive():
                running = False

            self.screen.fill('black')
            self.level.run(time_delta)
            pygame.display.update()

    def temp_run(self, channel_id):

        names = LoadingScreen(channel_id).run()
        difficulty = ChannelMenu(channel_id, len(names)).run()

        self.level = Level(difficulty, names)
        self.run_game()



def main():
    # Palmashow : UCoZoRz4-y6r87ptDp4Jk74g
    # Les kassos : UCv88958LRDfndKV_Y7XmAnA
    # Wankil Studio : UCYGjxo5ifuhnmvhPvCc3DJQ
    # JDG : UC_yP2DpIgs5Y1uWC0T03Chw

    #Game().temp_run('UCoZoRz4-y6r87ptDp4Jk74g')

    Game().run()


if __name__ == "__main__":
    main()
