import os
import sys
from threading import Thread
import pygame


class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        print(type(self._target))
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        return self._return


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


def scale_surface_height(surface: pygame.Surface, height: int):
    return pygame.transform.smoothscale(surface, (height * (surface.get_width() / surface.get_height()), height))


def getFiles(folder, start='data_'):
    return [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and f.startswith(start)]

def part_array(arr, n):
    chunk_len = len(arr) // n
    return [arr[idx: idx + chunk_len] for idx in range(0, len(arr), chunk_len)]


def chunk_array(arr, n):
    return [arr[i * n:(i + 1) * n] for i in range((len(arr) + n - 1) // n )]

def exit_app():
    pygame.quit()
    sys.exit()