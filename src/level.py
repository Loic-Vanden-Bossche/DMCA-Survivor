import pygame
from player import Player
from enemy import Enemy
from bullet import Bullet
from settings import *
import pygame_gui
from random import *


def sprite_alive(sprite):
    return sprite.alive()


class Level:
    def __init__(self, difficulty, names):
        self._manager = pygame_gui.UIManager((WIDTH, HEIGHT), '../themes/game.json')
        self.display_surface = pygame.display.get_surface()
        self.visible_sprites = pygame.sprite.Group()
        self.player = Player(GOAL, [self.visible_sprites], difficulty)
        self.enemies = []
        self.bullets = []
        self.wave = 1
        self.enemiesFactor = 10
        self.enemiesSpawnOffset = 3000
        self.timeToEnemySpawn = None
        self.inFight = True
        self.enemiesSpawned = 0
        self.enemiesNames = names

    def input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.player.is_alive():
                self.bullets.append(Bullet([self.visible_sprites]))

    def spawn_enemy(self):
        if choice([0, 1]):
            x_position = randint(-30, WIDTH+30)
            y_position = choice([randint(-30, 0), randint(HEIGHT, HEIGHT+30)])

        else:
            x_position = choice([randint(-30, 0), randint(WIDTH, WIDTH+30)])
            y_position = randint(-30, HEIGHT+30)

        self.enemies.append(Enemy(
            (x_position, y_position),
            [self.visible_sprites],
            self.player,
            self._manager,
            choice(self.enemiesNames)))
        self.enemiesSpawned += 1

    def run(self, time_delta):
        self.bullets = list(filter(sprite_alive, self.bullets))
        self.enemies = list(filter(sprite_alive, self.enemies))

        if len(self.visible_sprites):
            if not self.player.is_alive():
                self.inFight = False

            if self.inFight and (self.enemiesSpawned < self.wave * self.enemiesFactor):
                if self.timeToEnemySpawn:
                    if pygame.time.get_ticks() >= self.timeToEnemySpawn + self.enemiesSpawnOffset:
                        self.timeToEnemySpawn = pygame.time.get_ticks()
                        self.spawn_enemy()
                else:
                    self.timeToEnemySpawn = pygame.time.get_ticks()
                    self.spawn_enemy()

            elif self.inFight and not len(self.enemies):
                print(f"You've reached end of wave {self.wave}")
                self.enemiesSpawnOffset = self.enemiesSpawnOffset * 0.85
                self.wave += 1
                self.enemiesFactor += ENEMIES_FACTOR_AUGMENTATION

            for bullet in self.bullets:
                bullet.check_collision(self.enemies)

            self.visible_sprites.draw(self.display_surface)
            self._manager.draw_ui(self.display_surface)
            self.visible_sprites.update()
            self._manager.update(time_delta)
