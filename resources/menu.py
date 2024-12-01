import pygame

from .button import Button

class Menu:
    """A class to manage the main menu of the game."""

    def __init__(self, game_instance):
        """Initializes the attributes of the menu."""
        #Get the same screen of the game
        self.game_instance = game_instance
        self.screen = game_instance.screen
        self.window_width, self.window_height = self.screen.get_size()
        self.screen_rect = game_instance.screen.get_rect()
        self.bg_image = game_instance.bg_image
        self.bg_image_rect = game_instance.bg_image_rect

        #Button for MAIN MENU TITLE
        self.main_menu_button = Button(self.game_instance, 500, 100, 'gold', 'gold')
        self.main_menu_button.rect.midtop = self.game_instance.screen_rect.midtop
        self.main_menu_button.rect.y = 30
        


        #Button for ALIEN HUNT
        self.alien_hunt_button = Button(self.game_instance, 450, 90, (0, 150, 0), (255, 255, 255))
        self.alien_hunt_button.rect.x = 50
        self.alien_hunt_button.rect.y = self.game_instance.screen_rect.height/4
        
        

        #Button for SUN ESCAPE
        self.sun_escape_button = Button(self.game_instance, 470, 90, 'orange', 'dark red')
        self.sun_escape_button.rect.midtop = self.screen_rect.center
        
        

        #Button for MULTIPLAYER
        self.multiplayer_button = Button(self.game_instance, 500, 90, 'purple', 'light blue')
        self.multiplayer_button.rect.x = self.screen_rect.width - 530
        self.multiplayer_button.rect.y = self.screen_rect.height * 3/4
        
    def open_menu(self):
        """Opens the main menu."""
        #Draw the background image
        self.screen.blit(self.bg_image, self.bg_image_rect)

        #Load and play the background music
        pygame.mixer.music.unload()
        pygame.mixer.music.load('resources/sounds/interstellar_theme.mp3')
        pygame.mixer.music.play(-1)

        #Draw the buttons to access the game modes
        self.main_menu_button._prep_text('MAIN MENU', 56)
        self.main_menu_button.draw_button()

        self.alien_hunt_button._prep_text('ALIEN HUNT', 48)
        self.alien_hunt_button.draw_button()

        self.sun_escape_button._prep_text('SUN ESCAPE', 48)
        self.sun_escape_button.draw_button()

        self.multiplayer_button._prep_text('MULTIPLAYER', 48)
        self.multiplayer_button.draw_button()