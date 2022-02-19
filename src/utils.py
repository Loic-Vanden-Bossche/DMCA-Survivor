import os

import pygame

def get_centered_rect(w, h, y_offset=0):
    return pygame.Rect(
        ((pygame.display.get_surface().get_width() / 2) - w / 2,
         ((pygame.display.get_surface().get_height() / 2) - h / 2) + y_offset), (w, h))


def get_centered_pos_from_wh(w, h, y_offset=0):
    return (pygame.display.get_surface().get_width() / 2) - w / 2, (
                (pygame.display.get_surface().get_height() / 2) - h / 2) + y_offset


def get_dims_from_surface(surface: pygame.Surface):
    return surface.get_width(), surface.get_height()


def get_dims_from_display():
    return pygame.display.get_surface().get_width(), pygame.display.get_surface().get_height()


def getFiles(folder, start='data_'):
    return [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and f.startswith(start)]