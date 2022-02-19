import pygame
from player import Player
from enemy import Enemy
from bullet import Bullet
from settings import *
import pygame_gui


def sprite_alive(sprite):
    return sprite.alive()


class Level:
    def __init__(self):
        self._manager = pygame_gui.UIManager((WIDTH,HEIGHT), '../themes/game.json')
        self.display_surface = pygame.display.get_surface()
        self.visible_sprites = pygame.sprite.Group()
        self.player = Player(GOAL, [self.visible_sprites])
        self.enemies = []
        self.bullets = []

        self.enemies.append(Enemy((0, 0), [self.visible_sprites], self.player, self._manager))
        self.enemies.append(Enemy((-10, -10), [self.visible_sprites], self.player, self._manager))
        self.enemies.append(Enemy((100, 650), [self.visible_sprites], self.player, self._manager))
        self.enemies.append(Enemy((600, 50), [self.visible_sprites], self.player, self._manager))

    def input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.bullets.append(Bullet([self.visible_sprites]))

    def run(self, time_delta):
        self.bullets = list(filter(sprite_alive, self.bullets))
        self.enemies = list(filter(sprite_alive, self.enemies))

        if len(self.visible_sprites):
            self.visible_sprites.draw(self.display_surface)
            self._manager.draw_ui(self.display_surface)

            for bullet in self.bullets:
                bullet.check_collision(self.enemies)
            self.visible_sprites.update()
            self._manager.update(time_delta)