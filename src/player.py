import pygame

from life_bar import LifeBar
import utils


class Player(pygame.sprite.Sprite):
    def __init__(self, channel_id, pos, groups, life):
        super().__init__(groups)
        self.image = utils.scale_surface_height(self.load_image(channel_id), 100)
        self.rect = self.image.get_rect(center=pos)
        self.arms = [utils.scale_surface_height(pygame.image.load(f'../graphics/{img}.png'), 80) for img in  ['left', 'right']]
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

    def load_image(self, channel_id):
        try:
            return pygame.image.load(f'../cache/{channel_id}/thumb.jpg')
        except Exception:
            return pygame.image.load('../graphics/placeholder/character.jpg').convert_alpha()

    def is_alive(self):
        return bool(self.life)

    def update_arms(self):
        left, right = self.arms
        pygame.display.get_surface().blit(left, pygame.Rect(self.rect.x - left.get_width(), self.rect.y + 30, 0, 0))
        pygame.display.get_surface().blit(right, pygame.Rect(self.rect.x + self.rect.width, self.rect.y + 30, 0, 0))

    def update(self):
        self.bar.update()
        self.update_arms()

        if self.life == 0:
            self.kill()
