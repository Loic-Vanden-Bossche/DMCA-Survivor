import pygame
import math
from settings import *


class Bullet(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load('../graphics/placeholder/bullet.jpg').convert_alpha()
        self.rect = self.image.get_rect(center=GOAL)
        self.target = []

        mouse_position = pygame.mouse.get_pos()
        self.direction = (mouse_position[0]-GOAL_X, mouse_position[1]-GOAL_Y)

        length = math.hypot(*self.direction)
        if length == 0.0:
            self.direction = (0, -1)
        else:
            self.direction = (self.direction[0]/length, self.direction[1]/length)

        angle = math.degrees(math.atan2(-self.direction[1], self.direction[0]))
        self.image = pygame.transform.rotate(self.image, angle-90)

    def move(self):
        self.rect = self.rect.move(self.direction[0]*BULLET_SPEED, self.direction[1]*BULLET_SPEED)

    def check_collision(self, enemies):
        for i in enemies:
            if pygame.sprite.collide_rect(self, i):
                i.take_damage()
                self.kill()

    def update(self):
        self.move()

        height = range(-20, HEIGHT+20)
        width = range(-20, WIDTH+20)
        if self.rect.x not in width or self.rect.y not in height:
            self.kill()
