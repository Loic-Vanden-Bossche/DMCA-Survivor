import random

import pygame
import math
from pygame_gui.core import ObjectID
from settings import *
import pygame_gui

import utils


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, groups, player_sprite, manager, name_object):
        super().__init__(groups)
        self.image = self.load_image(name_object['id'])
        self.rect = self.image.get_rect(center=pos)
        self.target = player_sprite
        self.exploding = False
        self.collision = 0
        self.life = 5
        self.direction = 0

        self.life_bar = pygame_gui.elements.UIStatusBar(pygame.Rect((0, 0), (self.image.get_width(), 8)),
                                                        manager,
                                                        percent_method=self.get_life,
                                                        sprite=self,
                                                        object_id=ObjectID('#health_bar'))

        self.timer_bar = pygame_gui.elements.UIStatusBar(pygame.Rect((0, 0), (self.image.get_width(), 8)),
                                                         manager,
                                                         percent_method=self.get_timer,
                                                         sprite=self,
                                                         object_id=ObjectID('#timer_bar'))

        self.font = pygame.font.SysFont("Arial", 20)
        self.label = self.font.render(name_object['name'], True, 'white')

    def load_image(self, img_id):
        def load():
            try:
                return pygame.image.load(f"../graphics/pictures/{img_id}.jpg")
            except Exception:
                return pygame.image.load(f"../graphics/placeholder/enemy.jpg")

        return utils.scale_surface_height(load().convert_alpha(), random.randint(90, 140))

    def set_direction(self):
        self.direction = (GOAL_X-self.rect.x, GOAL_Y-self.rect.y)
        length = math.hypot(*self.direction)
        if length == 0.0:
            self.direction = (0, -1)
        else:
            self.direction = (self.direction[0]/length, self.direction[1]/length)

    def get_life(self):
        return self.life/5

    def get_timer(self):
        if not self.exploding:
            return 0
        else:
            return (pygame.time.get_ticks()-self.collision)/3000

    def move(self):
        self.rect = self.rect.move(self.direction[0]*ENEMY_SPEED, self.direction[1]*ENEMY_SPEED)
        pygame.display.get_surface().blit(self.label, pygame.Rect((self.rect.x, self.rect.y - 40), (self.label.get_width(), self.label.get_height())))

    def check_collision(self):
        return pygame.sprite.collide_rect(self, self.target)

    def take_damage(self):
        self.life -= 1

    def update(self):
        if not self.check_collision() and not self.exploding:
            self.set_direction()
            self.move()

        elif not self.exploding:
            self.collision = pygame.time.get_ticks()
            self.exploding = True

        elif self.exploding and pygame.time.get_ticks() >= self.collision + 3000:
            self.target.take_damage()
            self.life_bar.kill()
            self.timer_bar.kill()
            self.kill()

        if not self.life:
            self.life_bar.kill()
            self.timer_bar.kill()
            self.kill()
            del self
