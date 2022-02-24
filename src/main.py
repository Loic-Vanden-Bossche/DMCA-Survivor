import pygame

from src.main_menu import MainMenu
from settings import *

class Game(MainMenu):
    def __init__(self):
        # general setup
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Zelda')
        super().__init__()


if __name__ == "__main__":
    Game().run()
