import pygame

from life_bar import LifeBar


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, life):
        super().__init__(groups)
        self.image = pygame.image.load('../graphics/placeholder/character.jpg').convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self._life = life
        self.bar = LifeBar(self.rect.x + (self.rect.width / 2),
                           self.rect.y + self.rect.height + 10, 20, self.life, 3, 10)

    @property
    def life(self):
        return self._life

    @life.setter
    def life(self, value):
        self.bar.current_life = value
        self._life = value

    def take_damage(self):
        self.life -= 1

    def is_alive(self):
        return bool(self.life)

    def update(self):
        self.bar.update()
        if self.life == 0:
            self.kill()
