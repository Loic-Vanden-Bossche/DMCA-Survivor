from settings import *
import pygame

from life_bar import LifeBar
import utils


class Player(pygame.sprite.Sprite):
    def __init__(self, channel_id, pos, groups, life):
        super().__init__(groups)
        self._thumb = utils.scale_surface_height(self._load_image(channel_id), 100).convert_alpha()
        self._arms = [utils.scale_surface_height(pygame.image.load(f'../graphics/{img}.png'), 80) for img in
                      ['left', 'right']]
        self.image = pygame.image.load('../graphics/transparent.png')
        self.image = pygame.transform.smoothscale(
            self.image,
            (self._thumb.get_width() + (self._arms[0].get_width() * 2), self._thumb.get_height())
        )

        self.image.blit(self._thumb,
                         ((self.image.get_width() / 2) - (self._thumb.get_width() / 2),
                          (self.image.get_height() / 2) - (self._thumb.get_height() / 2)))
        self._attach_arms()
        self._base_image = self.image.copy()
        self.rect = self.image.get_rect(center=pos)
        self._life = life
        self._bar = LifeBar(self.rect.x + (self.rect.width / 2),
                            self.rect.y + self.rect.height + 10, 20, self.life, 3, 10)

    @property
    def life(self):
        return self._life

    @life.setter
    def life(self, value):
        self._bar.current_life = value
        self._life = value

    def take_damage(self):
        self.life -= 1

    def _load_image(self, channel_id):
        try:
            return pygame.image.load(f'../cache/{channel_id}/thumb.jpg')
        except Exception:
            return pygame.image.load('../graphics/placeholder/character.jpg').convert_alpha()

    def is_alive(self):
        return bool(self.life)

    def _attach_arms(self):
        left, right = self._arms

        self.image.blit(left, (self._thumb.get_rect().x, 20))
        self.image.blit(right, (self._thumb.get_rect().x + self._thumb.get_width() + right.get_width(), 20))

    def update(self):
        self._bar.update()

        mouse_position = pygame.mouse.get_pos()
        angle = utils.get_angle_from_pos_to_pos(mouse_position, (GOAL_X, GOAL_Y))

        self.image = pygame.transform.rotate(self._base_image, angle + 90)
        self.rect = self.image.get_rect(center=self.image.get_rect(center=(GOAL_X, GOAL_Y)).center)

        if self.life == 0:
            self.kill()
