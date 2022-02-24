import io
import math
from urllib.request import urlopen

import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIWindow, UITextEntryLine
from youtubesearchpython import ChannelsSearch

from src import utils, loader
from src.channel_menu import ChannelMenu
from src.loader import LoadingScreen
from src.tower_defense import TowerDefense


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
    def __init__(self, padding, height, width, index, y_offset, manager, container, channel_data):
        super().__init__(pygame.Rect((0 + padding, ((index * height) + (index * y_offset)) + padding), (width, height)),
                         5, manager, container=container)

        self.data = channel_data

        padding = 30

        pygame_gui.elements.UILabel(pygame.Rect(padding, 10, self.relative_rect.w, padding),
                                    self.data['name'],
                                    manager,
                                    self,
                                    object_id=ObjectID('#lefttext'))

        image_str = urlopen(f"https:{self.data['image']}").read()
        self.thumb = pygame.image.load(io.BytesIO(image_str))

        pygame_gui.elements.ui_image.UIImage(
            pygame.Rect((padding, 50),
                        (self.relative_rect.h - (padding * 2) - 20, self.relative_rect.h - (padding * 2) - 20)),
            utils.scale_surface_height(self.thumb, self.relative_rect.h),
            manager,
            self)

        width, height = (150, 50)

        self.button = pygame_gui.elements.UIButton(pygame.Rect(self.relative_rect.w - width - padding,
                                                               self.relative_rect.h - height - padding,
                                                               width, height),
                                                   'select',
                                                   manager,
                                                   self)


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
        for res in self._results:
            res.kill()

        self._results = [
            SearchResult(self._entry_padding,
                         self._entry_height,
                         self._entry_width, i,
                         self._entry_y_offset,
                         self._manager,
                         self.container,
                         result)
            for i, result in enumerate(results)
        ]
        self.scroll_height = self._entry_padding + \
                             (self._entry_height * len(results)) + \
                             (self._entry_y_offset * len(results))

    def __init__(self, rect, ui_manager, panel):
        super().__init__(rect, ui_manager, panel)

        self._entry_padding = 10
        self._entry_y_offset = 20
        self._entry_width = rect.w - (self._entry_padding * 2) - 30
        self._entry_height = self._entry_width * 0.4

        self._manager = ui_manager
        self._results = []


class SearchModule:

    @property
    def text(self):
        return self.entry.text

    @text.setter
    def text(self, status):
        self.entry.set_text(status)

    @property
    def results(self):
        return self.results_container.results

    @results.setter
    def results(self, results):
        self.results_container.results = results

    def __init__(self, padding, ui_manager, container):
        self.entry = UITextEntryLine(pygame.Rect((padding, padding), (200, 35)),
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

        y_offset = 80

        self.results_container = SearchResults(pygame.Rect((padding, y_offset),
                                                           (container.relative_rect.w - (padding * 2),
                                                            container.relative_rect.h - y_offset - padding)),
                                               ui_manager, container)


class SelectedPanel(pygame_gui.elements.UIPanel):
    def __init__(self, relative_rect, manager, container, image: pygame.Surface, data):
        super().__init__(relative_rect, 1, manager, container=container)

        pygame_gui.elements.UIImage(pygame.Rect(0, 0, 300, 300),
                                    image,
                                    manager,
                                    self)

        width, height, padding = (150, 50, 30)

        self.id = data['id']

        self.button = pygame_gui.elements.UIButton(pygame.Rect(self.relative_rect.w - width - padding,
                                                               self.relative_rect.h - height - padding,
                                                               width, height),
                                                   'start session', manager, self)


class NewGameWindow(UIWindow):

    def init_search_panel(self):
        return pygame_gui.elements.UIPanel(relative_rect=self.calculate_Rect(0),
                                           starting_layer_height=4,
                                           manager=self._manager,
                                           container=self,
                                           object_id=ObjectID('#panel'))

    def calculate_Rect(self, idx):

        width = (self.rect.width - 70) / 2
        height = (self.rect.h - 60) - (2 * self._padding_from_borders)

        return pygame.Rect(((self._padding_from_borders * (idx + 1)) + (idx * width), self._padding_from_borders),
                           (width, height))

    def set_selected(self, data, image):
        if self.selected_panel:
            self.selected_panel.kill()

        self.selected_panel = SelectedPanel(self.calculate_Rect(1), self._manager, self, image, data)

    def check_events(self, event):
        for res in self.search_module.results:
            if event.ui_element == res.button:
                self.set_selected(res.data, res.thumb)

        if self.selected_panel:
            if event.ui_element == self.selected_panel.button:
                names = LoadingScreen(self.selected_panel.id).run()
                difficulty = ChannelMenu(self.selected_panel.id, len(names)).run()

                TowerDefense(difficulty, names).run()

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

        self._padding_from_borders = 10

        self.panel = self.init_search_panel()
        self.search_module = SearchModule(20, self._manager, self.panel)
        self.selected_panel = None

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
                    self.on_search(event.text)

                self._manager.process_events(event)
                self.check_buttons(event)

            self._manager.update(time_delta)

            pygame.display.get_surface().blit(self.back, pygame.Rect((0, 0), (200, 200)))

            self._manager.draw_ui(pygame.display.get_surface())
            pygame.display.update()

    def on_search(self, query):
        channelsSearch = ChannelsSearch(query, limit=10)
        self.new_game_window.search_module.results = [
            {
                'id': c['id'],
                'name': c['title'],
                'image': c['thumbnails'][0]['url'],
                'sub': c['subscribers'],
                'v_count': c['videoCount']
            }
            for c in channelsSearch.result().get('result')
        ]

    def check_buttons(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.quit_button:
                utils.exit_app()

            if event.ui_element == self.new_game_button:
                self.new_game_window = NewGameWindow(self._manager)

            if self.new_game_window:
                if event.ui_element == self.new_game_window.search_module.button:
                    self.on_search(self.new_game_window.search_module.text)

            self.new_game_window.check_events(event)

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
