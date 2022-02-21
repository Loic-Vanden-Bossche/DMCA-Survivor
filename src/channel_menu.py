import sys
import pygame
import pygame_gui
from pygame_gui.core import ObjectID

from src import utils, loader

from dynamic_background import Background
from src.life_bar import LifeBar


class ChannelMenu:
    def run(self):
        while self.running:
            time_delta = self.clock.tick(120) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.start_button:
                        self.running = False

                if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and event.ui_element == self.dropdown:
                    self.difficulty = self.dropdown.selected_option
                    self.life_bar.current_life = self.get_life_from_dropdown_value()

                self.manager.process_events(event)

            self.manager.update(time_delta)
            self.background.update(time_delta)

            self.manager.draw_ui(pygame.display.get_surface())
            self.life_bar.update()
            pygame.display.update()

        return self.get_life_from_dropdown_value()

    def init_ui_manager(self):
        return pygame_gui.UIManager(utils.get_dims_from_surface(pygame.display.get_surface()), 'themes/menu.json')

    def init_main_panel(self):
        return pygame_gui.elements.UIPanel(relative_rect=utils.get_centered_rect(400, 600),
                                           starting_layer_height=4,
                                           manager=self.manager,
                                           object_id=ObjectID('#panel'))

    def init_button(self, text, width, height):
        return pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.panel.relative_rect.w / 2 - (width / 2), self.panel.relative_rect.h - 90,
                                      width,
                                      height),
            text=text,
            manager=self.manager,
            container=self.panel,
            object_id=ObjectID('#start_button'))

    def init_dropdown(self):
        return pygame_gui.elements.UIDropDownMenu(self.difficulties, self.difficulty,
                                           pygame.Rect(self.panel.relative_rect.w / 2 - (200 / 2), 300,
                                                       200, 30),
                                           self.manager,
                                           container=self.panel)

    def init_static_content(self):
        pygame_gui.elements.UILabel(pygame.Rect(0, 140, self.panel.relative_rect.w, 30),
                                    loader.get_transcriptions_data(self.channel_id)['channel']['name'],
                                    self.manager,
                                    self.panel)

        pygame_gui.elements.UILabel(pygame.Rect(0, 190, self.panel.relative_rect.w, 30),
                                    f'{self.loaded_count} enemies loaded !',
                                    self.manager,
                                    self.panel)

        pygame_gui.elements.ui_image.UIImage(
            self.thumb.get_rect().move(self.panel.relative_rect.w / 2 - (self.thumb.get_width() / 2), 30),
            self.thumb,
            self.manager,
            self.panel)

        pygame_gui.elements.UILabel(
            pygame.Rect(self.dropdown.relative_rect.x, self.dropdown.relative_rect.y - 30,
                        self.dropdown.relative_rect.w, 30),
            f'difficulty',
            self.manager,
            container=self.panel)

    def get_life_from_dropdown_value(self):
        return len(self.difficulties) - self.difficulties.index(self.difficulty)

    def __init__(self, channel_id, loaded_count):
        self.channel_id = channel_id
        self.loaded_count = loaded_count
        pygame.display.set_caption('Channel menu')
        loader.load_music(channel_id)
        self.running = True

        self.difficulties = ['easy', 'medium', 'hard']
        self.difficulty = 'medium'

        self.background = Background(channel_id, 8)

        self.manager = self.init_ui_manager()

        self.panel = self.init_main_panel()

        self.start_button = self.init_button('start game', 200, 30)

        self.thumb = utils.scale_surface_height(pygame.image.load(f'cache/{channel_id}/thumb.jpg'), 100)

        self.dropdown = self.init_dropdown()

        self.life_bar = LifeBar(self.panel.rect.x + (self.panel.rect.w/2), self.dropdown.rect.y + 60, 20, 3, 3, 10)
        self.life_bar.current_life = self.get_life_from_dropdown_value()

        self.init_static_content()

        self.clock = pygame.time.Clock()
