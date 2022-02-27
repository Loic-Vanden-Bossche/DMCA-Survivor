import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIWindow, UILabel

import loader
import utils
from dynamic_background import Background
from life_bar import LifeBar
from settings import *
from scores import *
from tower_defense import TowerDefense


class LevelSummaryWindow(UIWindow):
    def __init__(self, ui_manager, wave, difficulty):
        window_width, window_height = pygame.display.get_window_size()
        width = window_width / 3
        height = window_height / 5

        score_updated = set_best_scores(wave, difficulty)

        super().__init__(
            pygame.Rect((window_width / 2) - (width / 2), (window_height / 2) - (height / 2), width, height),
            ui_manager,
            window_display_title='Session summary',
        )

        UILabel(pygame.Rect(0, 20, self.relative_rect.width, 50),
                f'You reached wave {wave} !',
                ui_manager,
                self, object_id=ObjectID('#30_text'))

        if score_updated:
            UILabel(pygame.Rect(0, 60, self.relative_rect.width, 20),
                    'Well done ! You beat your best score.',
                    ui_manager,
                    self, object_id=ObjectID('#10_text'))

        UILabel(pygame.Rect(0, 80, self.relative_rect.width, 50),
                f'Your best score is {get_best_scores_for_difficulty(difficulty)} for difficulty {difficulty}',
                ui_manager,
                self, object_id=ObjectID('#20_text'))

        self.set_blocking(True)


class ChannelMenu:
    def run(self):
        while self.running:
            time_delta = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    utils.exit_app()

                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.start_button:
                        self.summary_window = LevelSummaryWindow(
                            self.manager,
                            TowerDefense(self.channel_data['id'], self.get_life_from_dropdown_value(), self.names).run(),
                            self.difficulty
                        )
                        self.life_bar.display = False

                    if event.ui_element == self.quit_button:
                        self.running = False

                if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and event.ui_element == self.dropdown:
                    self.difficulty = self.dropdown.selected_option
                    self.life_bar.current_life = self.get_life_from_dropdown_value()

                if event.type == pygame_gui.UI_WINDOW_CLOSE and event.ui_element == self.summary_window:
                    self.life_bar.display = True

                self.manager.process_events(event)

            self.manager.update(time_delta)
            self.background.update(time_delta)

            self.manager.draw_ui(pygame.display.get_surface())
            self.life_bar.update()
            pygame.display.update()

    def init_ui_manager(self):
        return pygame_gui.UIManager(utils.get_dims_from_surface(pygame.display.get_surface()), '../themes/menu.json')

    def init_main_panel(self):
        return pygame_gui.elements.UIPanel(relative_rect=utils.get_centered_rect(400, 600),
                                           starting_layer_height=4,
                                           manager=self.manager,
                                           object_id=ObjectID('#panel'))

    def init_button(self, text, width, height, y_offset):
        return pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.panel.relative_rect.w / 2 - (width / 2), self.panel.relative_rect.h - y_offset,
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
                                    self.channel_data['name'],
                                    self.manager,
                                    self.panel)

        pygame_gui.elements.UILabel(pygame.Rect(0, 190, self.panel.relative_rect.w, 30),
                                    f'{len(self.names)} enemies loaded !',
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

    def __init__(self, channel_id, names):
        self.channel_data = loader.get_transcriptions_data(channel_id)['channel']
        self.names = names
        utils.set_game_title(self.channel_data['name'])
        loader.load_music(f'../cache/{channel_id}/music.mp3')
        self.running = True

        self.difficulties = difficulties
        self.difficulty = 'medium'

        self.background = Background(channel_id, 8)

        self.manager = self.init_ui_manager()

        self.panel = self.init_main_panel()

        self.summary_window = None

        self.start_button = self.init_button('start game', 200, 30, 120)
        self.quit_button = self.init_button('return to main menu', 200, 30, 80)

        self.thumb = utils.scale_surface_height(pygame.image.load(f'../cache/{channel_id}/thumb.jpg'), 100)

        self.dropdown = self.init_dropdown()

        self.life_bar = LifeBar(self.panel.rect.x + (self.panel.rect.w/2), self.dropdown.rect.y + 60, 20, 3, 3, 10)
        self.life_bar.current_life = self.get_life_from_dropdown_value()

        self.init_static_content()

        self.clock = pygame.time.Clock()
