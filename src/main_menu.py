import math

import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIWindow, UITextEntryLine

from src import utils, loader
from src.channel_menu import ChannelMenu
from src.loader import LoadingScreen


class SeamLessBackground:

    def update(self):
        for y in range(0, self.lines):
            for x in range(0, self.rows):
                self.window.blit(self.image, (self.image.get_width() * x, self.image.get_height() * y))

    def __init__(self, texture_path, layer_height):
        self.image = utils.scale_surface_height(pygame.image.load(texture_path), layer_height)
        self.window = pygame.display.get_surface()
        self.lines = math.ceil(self.window.get_height() / self.image.get_height())
        self.rows = math.ceil(self.window.get_width() / self.image.get_width())


class SearchResult(pygame_gui.elements.UIPanel):
    def __init__(self, padding, height, width, index, y_offset, manager, container):
        super().__init__(pygame.Rect((0 + padding, ((index * height) + (index * y_offset)) + padding), (width, height)),
                         5, manager, container=container)


class ScrollablePanel(pygame_gui.elements.UIPanel):

    @property
    def scroll_height(self):
        return self._scroll_height

    @scroll_height.setter
    def scroll_height(self, height):
        self._scroll_height = height
        self.container.set_scrollable_area_dimensions((self.container.relative_rect.w - 30, self._scroll_height))

    def __init__(self, rect, ui_manager, panel):
        super().__init__(rect, 0, manager=ui_manager, container=panel)

        self.container = pygame_gui.elements.UIScrollingContainer(pygame.Rect(0, 0, self.relative_rect.w - 4,
                                                                              self.relative_rect.h - 4),
                                                                  ui_manager, container=self)

        self._scroll_height = 0
        self.scroll_height = 0


class SearchResults(ScrollablePanel):

    @property
    def results(self):
        return self._results

    @results.setter
    def results(self, results):
        self._results = [
            SearchResult(self._entry_padding,
                         self._entry_height,
                         self._entry_width, i,
                         self._entry_y_offset,
                         self._manager,
                         self.container)
            for i, result in enumerate(results)
        ]
        self.scroll_height = self._entry_padding + \
                             (self._entry_height * len(results)) + \
                             (self._entry_y_offset * len(results))

    def __init__(self, rect, ui_manager, panel):
        super().__init__(rect, ui_manager, panel)

        self._entry_height = 100
        self._entry_width = 250
        self._entry_padding = 10
        self._entry_y_offset = 20

        self._manager = ui_manager
        self._results = []


class SearchModule:

    @property
    def text(self):
        return self.entry.text

    @text.setter
    def text(self, status):
        self.entry.set_text(status)

    def __init__(self, pos, ui_manager, container):
        self.entry = UITextEntryLine(pygame.Rect(pos, (200, 35)),
                                     ui_manager,
                                     container=container,
                                     object_id='#search_text_entry')

        self.button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.entry.relative_rect.x + self.entry.relative_rect.w,
                                      self.entry.relative_rect.y,
                                      self.entry.relative_rect.h,
                                      self.entry.relative_rect.h),
            container=container,
            manager=ui_manager,
            object_id=ObjectID('#search_button'),
            text=''
        )


class NewGameWindow(UIWindow):

    def init_main_panel(self, padding_from_borders=0):
        calculated_rect = pygame.Rect((padding_from_borders, padding_from_borders),
                                      ((self.get_relative_rect().width / 2) - (2 * padding_from_borders),
                                       (self.rect.h - 60) - (2 * padding_from_borders)))

        return pygame_gui.elements.UIPanel(relative_rect=calculated_rect,
                                           starting_layer_height=4,
                                           manager=self._manager,
                                           container=self,
                                           object_id=ObjectID('#panel'))

    def __init__(self, ui_manager):
        window_width, window_height = pygame.display.get_window_size()
        width = window_width / 1.5
        height = window_height / 1.5

        self._manager = ui_manager

        super().__init__(
            pygame.Rect((window_width / 2) - (width / 2), (window_height / 2) - (height / 2), width, height),
            self._manager,
            window_display_title='Create a new session',
        )

        self.panel = self.init_main_panel(10)

        padding = 20

        self.results_container = SearchResults(pygame.Rect((padding, 80), (300, 300)), self._manager, self.panel)
        self.results_container.results = range(0, 10)

        self.search_module = SearchModule((padding, padding), self._manager, self.panel)

        self.set_blocking(True)


class MainMenu:
    def run(self):
        loader.load_music('../music.mp3', 0.1)

        while self.running:
            time_delta = self.clock.tick(120) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    utils.exit_app()

                if (event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED and
                        event.ui_element == self.new_game_window.search_module.entry):
                    print(event.text)

                self._manager.process_events(event)
                self.check_buttons(event)

            self._manager.update(time_delta)

            pygame.display.get_surface().blit(self.back, pygame.Rect((0, 0), (200, 200)))

            self._manager.draw_ui(pygame.display.get_surface())
            pygame.display.update()

    def check_buttons(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.quit_button:
                utils.exit_app()

            if event.ui_element == self.new_game_button:
                self.new_game_window = NewGameWindow(self._manager)

            if self.new_game_window:
                if event.ui_element == self.new_game_window.search_module.button:
                    print(self.new_game_window.search_module.text)

    def init_ui_manager(self):
        return pygame_gui.UIManager(utils.get_dims_from_surface(pygame.display.get_surface()), '../themes/main.json')

    def init_main_panel(self):
        return pygame_gui.elements.UIPanel(relative_rect=utils.get_centered_rect(500, 800),
                                           starting_layer_height=4,
                                           manager=self._manager,
                                           object_id=ObjectID('#panel'))

    def init_static_content(self):
        pygame_gui.elements.UILabel(pygame.Rect(0, 10, self.panel.relative_rect.w, 80),
                                    'DMCA - Survivor',
                                    self._manager,
                                    object_id=ObjectID('#test'),
                                    container=self.panel)

    def init_menu_button(self, label, width, height, y_offset=0):
        return pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.panel.relative_rect.w / 2 - (width / 2),
                                      self.panel.relative_rect.y + y_offset,
                                      width, height),
            text=label,
            manager=self._manager,
            container=self.panel,
            object_id=ObjectID('#start_button'))

    def init_menu_buttons(self, labels, width, height, y_offset, padding):
        return [self.init_menu_button(label, width, height, (i * height) + y_offset + (i * padding)) for i, label in
                enumerate(labels)]

    def start_session(self, channel_id):
        names = LoadingScreen(channel_id).run()
        difficulty = ChannelMenu(channel_id, len(names)).run()

        print(len(names), difficulty)

    def __init__(self):
        self.back = utils.scale_surface_height(pygame.image.load('../graphics/background.jpg'),
                                               pygame.display.get_surface().get_height())
        self.running = True

        pygame.display.set_caption('Main menu')

        self._manager = self.init_ui_manager()

        self.panel = self.init_main_panel()

        self.new_game_button, self.scores_button, self.quit_button = self.init_menu_buttons(
            ['new game', 'scores', 'quit'],
            300, 40, 100, 20
        )

        self.init_static_content()

        self.new_game_window = None

        self.clock = pygame.time.Clock()