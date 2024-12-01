import pygame
from pygame.sprite import Group

from resources.button import Button
from resources.alien_hunt.rocket import Rocket

class ScoreBoard:
    """A class to report scoring information."""
    def __init__(self, game_instance):
        """Intializes scorekeeping attributes."""
        self.game_instance = game_instance
        self.screen = game_instance.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = game_instance.settings
        self.stats = game_instance.stats

        #Timer button
        self.timer_button = Button(game_instance, 100, 100, 'white', 'white')
        self.timer_button.rect.midtop = game_instance.screen_rect.midtop
        self.timer_button.rect.y = 20

        #Button for score
        self.score_button = Button(game_instance, 400, 100, 'white', 'white')
        self.score_button.rect.right = self.screen_rect.right - 20
        self.score_button.rect.top = 20

        #Button for Record
        self.record_button = Button(game_instance, 400, 100, 'white', 'red')
        self.record_button.rect.left = self.screen_rect.left + 20
        self.record_button.rect.top = 20

        #Button for game over
        self.game_over_button = Button(self, 500, 150, 'red', 'white')
        self.game_over_button.rect.center = self.screen_rect.center

    def draw_board(self):
        """Draws the buttons of the scoreboard."""
        self.timer_button._prep_text(str(self.settings.counter), 50)
        self.timer_button.draw_button()
        rounded_score = round(self.stats.score, -1)
        score_str = f"{rounded_score:,}"
        self.score_button._prep_text(score_str, 40)
        self.score_button.draw_button()
        rounded_record = round(self.stats.record, -1)
        record_str = f"{rounded_record:,}"
        self.record_button._prep_text(record_str, 40)
        self.record_button.draw_button()
        
        #Button for level
        pygame.draw.circle(self.screen, 'white', (self.screen_rect.width -110, 190), 50, 2)
        self.font = pygame.font.Font('resources/font/Dune_Rise.otf', 40)
        self.font.set_underline(True)
        self.text_image = self.font.render(str(self.stats.level), True, 'red', None)
        self.text_image_rect = self.text_image.get_rect()
        self.text_image_rect.center = (self.screen_rect.width -110, 190)
        self.screen.blit(self.text_image, self.text_image_rect)

        #Rockets left
        self.rockets = Group()
        for rocket_number in range(self.stats.rocket_left):
            rocket = Rocket(self.game_instance)
            rocket.image = rocket.up_image
            rocket.rect = rocket.up_image_rect
            rocket.rect.x = 20 + rocket_number * rocket.rect.width
            rocket.rect.y = 150
            self.rockets.add(rocket)
            self.rockets.draw(self.screen)

        #if self.game_instance.game_over:
            #Draw game over button
            #self.game_over_button._prep_text('GAME OVER!', 56)
            #self.game_over_button.draw_button()
