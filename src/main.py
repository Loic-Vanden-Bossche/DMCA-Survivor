import pygame

from main_menu import MainMenu
from settings import *
import utils


class Game(MainMenu):
    def __init__(self):
        # general setup
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        utils.set_game_title('Init')
        super().__init__()


if __name__ == "__main__":
    Game().run()
