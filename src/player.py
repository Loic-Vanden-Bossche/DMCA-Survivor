import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.image.load('../graphics/placeholder/character.jpg').convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.life = 3

    def take_damage(self):
        self.life -= 1
        print(self.life)

    def update(self):
        if self.life == 0:
            print('Game Over')
            self.kill()