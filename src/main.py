import pygame

from src.main_menu import MainMenu


class Game(MainMenu):
    def __init__(self):
        # general setup
        pygame.init()
        self.screen = pygame.display.set_mode((1920, 1080))
        pygame.display.set_caption('Zelda')
        self.clock = pygame.time.Clock()
        super().__init__()


def main():
    # Palamashow : UCoZoRz4-y6r87ptDp4Jk74g
    # Les kassos : UCv88958LRDfndKV_Y7XmAnA
    # Wankil Studio : UCYGjxo5ifuhnmvhPvCc3DJQ
    # JDG : UC_yP2DpIgs5Y1uWC0T03Chw

    Game().run()


if __name__ == "__main__":
    main()
