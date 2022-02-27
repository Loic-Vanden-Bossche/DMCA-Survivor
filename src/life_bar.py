import pygame
import utils

class LifeBar:

    def update(self):
        if self.display:
            for i, x in enumerate(self._map):
                if x:
                    pygame.display.get_surface().blit(self.filled, ((i*self.sprite_width) + (self.padding*i) + self.x, self.y))
                else:
                    pygame.display.get_surface().blit(self.unfilled, ((i*self.sprite_width) + (self.padding*i) + self.x, self.y))

    def _get_map(self, current_life, max_life):
        return [1 if x < current_life else 0 for x in range(0, max_life)]

    @property
    def current_life(self):
        return len([x for x in self._map if x == 1])

    @current_life.setter
    def current_life(self, current_life):
        max_life = len(self._map)
        current_life = self.check_current_value(current_life, max_life)
        self._map = self._get_map(current_life, max_life)

    def check_current_value(self, current, max_life):
        if current <= 0:
            current = 1
        elif current > max_life:
            current = max_life

        return current

    def __init__(self, x, y, height: float, current_life, max_life, padding=0, center=True):

        self.x = x
        self.y = y

        self.filled = utils.scale_surface_height(pygame.image.load('../graphics/heart-filled.png'), height)
        self.unfilled = utils.scale_surface_height(pygame.image.load('../graphics/heart-unfilled.png'), height)
        self.sprite_width = self.filled.get_width()
        self.padding = padding

        self.width = (self.sprite_width * max_life) + (padding * (max_life-1))
        self.height = height

        self.display = True

        if center:
            self.x = self.x - (self.width / 2)

        self._map = self._get_map(self.check_current_value(current_life, max_life), max_life)
