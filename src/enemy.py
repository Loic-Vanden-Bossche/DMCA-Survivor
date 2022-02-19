import pygame
import math
from settings import *
import numpy as np


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, groups, player_sprite):
        super().__init__(groups)
        self.image = pygame.image.load('../graphics/placeholder/enemy.jpg').convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.target = player_sprite
        self.exploding = False
        self.x_speed = 0
        self.y_speed = 0
        self.set_movement()
        self.tickToExplode = 0

    def set_movement(self):
        x_diff = GOAL_X - self.rect.x
        y_diff = GOAL_Y - self.rect.y

        self.x_speed = x_diff/SPEED
        self.y_speed = y_diff/SPEED

    def move_to_goal(self):
        self.rect = self.rect.move(self.x_speed, self.y_speed)

    def check_collision(self):
        return pygame.sprite.collide_rect(self, self.target)

    def update(self):
        x_diff = GOAL_X - self.rect.x
        y_diff = GOAL_Y - self.rect.y
        stop_range = range(-EXPLOSION_DISTANCE, EXPLOSION_DISTANCE)

        if not self.check_collision() and not self.exploding:
            self.move_to_goal()
        elif not self.exploding:
            self.tickToExplode = pygame.time.get_ticks()+3000
            self.exploding = True
        elif self.exploding and pygame.time.get_ticks() >= self.tickToExplode:
            print('boom')
            self.target.take_damage()
            self.kill()
