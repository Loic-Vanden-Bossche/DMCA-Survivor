import pygame
from player import Player
from enemy import Enemy
from settings import *


class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.visible_sprites = pygame.sprite.Group()
        self.player = Player(GOAL, [self.visible_sprites])
        self.enemies = []
        self.enemies.append(Enemy((1000, 80), [self.visible_sprites], self.player))
        self.enemies.append(Enemy((100, 650), [self.visible_sprites], self.player))
        self.enemies.append(Enemy((600, 50), [self.visible_sprites], self.player))

    def input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                print("shoot")

    def run(self):
        if len(self.visible_sprites):
            self.visible_sprites.draw(self.display_surface)
            self.visible_sprites.update()
        else:
            print('t mort')
