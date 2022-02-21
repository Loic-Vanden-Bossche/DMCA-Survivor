import pygame

from src.channel_menu import ChannelMenu
from src.loader import LoadingScreen


class Game:
    def __init__(self):
        # general setup
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption('Zelda')
        self.clock = pygame.time.Clock()

    def start_session(self, channel_id):
        names = LoadingScreen(channel_id).run()
        difficulty = ChannelMenu(channel_id, len(names)).run()

        print(len(names), difficulty)

    def run(self):
        self.start_session('UCYGjxo5ifuhnmvhPvCc3DJQ')


def main():
    # Palamashow : UCoZoRz4-y6r87ptDp4Jk74g
    # Les kassos : UCv88958LRDfndKV_Y7XmAnA
    # Wankil Studio : UCYGjxo5ifuhnmvhPvCc3DJQ
    # JDG : UC_yP2DpIgs5Y1uWC0T03Chw

    game = Game()
    game.run()


if __name__ == "__main__":
    main()
