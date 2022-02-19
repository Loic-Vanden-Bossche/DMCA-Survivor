import pygame

from src.channel_menu import channel_menu_loop
from src.loader import loading_loop

class Game:
    def __init__(self):
        # general setup
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption('Zelda')
        self.clock = pygame.time.Clock()

    def run(self):
        channel_id = 'UC_yP2DpIgs5Y1uWC0T03Chw'

        loading_loop(channel_id)
        channel_menu_loop(channel_id)


def main():
    # Palamashow : UCoZoRz4-y6r87ptDp4Jk74g
    # Les kassos : UCv88958LRDfndKV_Y7XmAnA
    # Wankil Studio : UCYGjxo5ifuhnmvhPvCc3DJQ
    # JDG : UC_yP2DpIgs5Y1uWC0T03Chw

    game = Game()
    game.run()


if __name__ == "__main__":
    main()
