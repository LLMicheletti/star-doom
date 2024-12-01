import pygame
from pygame.sprite import Group
from pathlib import Path
import json

from resources.button import Button
from resources.sun_escape.fuel_tank import FuelTank

class ScoreBoard:
    """A class to report scoring information."""
    def __init__(self, game_instance):
        """Intializes scorekeeping attributes."""
        self.game_instance = game_instance
        self.screen = game_instance.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = game_instance.settings
        self.stats = game_instance.stats

        #Button for game over
        self.game_over_button = Button(self, 500, 150, 'black', 'purple')
        self.game_over_button.rect.center = self.screen_rect.center

        #Button for game victory
        self.game_win_button = Button(self, 500, 150, 'black', 'purple')
        self.game_win_button.rect.center = self.screen_rect.center

        #winning Instruction button
        self.win_instruction_button = Button(self.game_instance, 900, 60, 'white', 'white')
        self.win_instruction_button.rect.midbottom = self.game_instance.screen_rect.midbottom
        self.win_instruction_button.rect.y = self.game_instance.screen_rect.height*3/4

    def draw_board(self):
        """Draws the buttons of the scoreboard."""
        #Button for level
        pygame.draw.circle(self.screen, 'white', (self.screen_rect.width -70, 70), 30, 2)
        self.font = pygame.font.Font('resources/font/Dune_Rise.otf', 40)
        self.font.set_underline(True)
        self.text_image = self.font.render(str(self.stats.level), True, 'red', None)
        self.text_image_rect = self.text_image.get_rect()
        self.text_image_rect.center = (self.screen_rect.width - 70, 70)
        self.screen.blit(self.text_image, self.text_image_rect)

        #Fuel tanks left
        self.backup_fuel_tanks = Group()
        for fuel_tank_number in range(self.stats.backup_fuel_tank_left):
            backup_fuel_tank = FuelTank(self.game_instance)
            backup_fuel_tank.image = backup_fuel_tank.left_image
            backup_fuel_tank.rect = backup_fuel_tank.left_image_rect
            backup_fuel_tank.rect.x = fuel_tank_number * 40
            backup_fuel_tank.rect.y = 0
            self.backup_fuel_tanks.add(backup_fuel_tank)
            self.backup_fuel_tanks.draw(self.screen)