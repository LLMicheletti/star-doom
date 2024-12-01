import pygame

from resources.button import Button

class AlienHuntStaticMenu:
    """A class to manage the initial menu of Alien Hunt mode."""

    def __init__(self, game_instance):
        """Initializes the attributes of the menu."""
        #Get the same screen of the game
        self.game_instance = game_instance
        self.screen = game_instance.screen
        self.screen_rect = game_instance.screen.get_rect()
        self.bg_image = game_instance.bg_image
        self.bg_image_rect = game_instance.bg_image_rect

        #PLAY button
        self.play_button = Button(self.game_instance, 300, 100, 'purple', 'yellow')
        self.play_button.rect.midtop = self.game_instance.screen_rect.midtop
        self.play_button.rect.y = self.game_instance.screen_rect.height/4

        #BACK button 
        self.back_button = Button(self.game_instance, 300, 100, 'red', 'white')
        self.back_button.rect.midtop = self.game_instance.screen_rect.midtop
        self.back_button.rect.y = self.game_instance.screen_rect.height/2

        #Instruction button
        self.instruction_button = Button(self.game_instance, 700, 60, 'white', 'white')
        self.instruction_button.rect.midbottom = self.game_instance.screen_rect.midbottom
        self.instruction_button.rect.y = self.game_instance.screen_rect.height*3/4
        
    def open_alien_hunt_static_menu(self):
        """Opens the main menu of Alien Hunt."""
        pygame.display.set_caption("*Alien Hunt*")
        #Draw the background image
        self.screen.blit(self.bg_image, self.bg_image_rect)

        #Load and play the background music
        pygame.mixer.music.unload()
        pygame.mixer.music.load('resources/sounds/running_out.mp3')
        pygame.mixer.music.play(-1)

        #Draw PLAY button
        self.play_button._prep_text('PLAY', 56)
        self.play_button.draw_button()

        #Draw BACK button 
        self.back_button._prep_text('BACK', 56)
        self.back_button.draw_button()

        #Draw Instruction button
        self.instruction_button._prep_text('Destroy all the UFOs before the time expires!', 16)
        self.instruction_button.draw_button()

class AlienHuntDynamicMenu:
    """A class to manage the main menu of Alien Hunt mode."""

    def __init__(self, game_instance):
        """Initializes the attributes of the menu."""
        #Get the same screen of the game
        self.game_instance = game_instance
        self.screen = game_instance.screen
        self.screen_rect = game_instance.screen.get_rect()
        self.bg_image = game_instance.bg_image
        self.bg_image_rect = game_instance.bg_image_rect

        #Instruction button
        self.instruction_button = Button(self.game_instance, 700, 60, 'white', 'white')
        self.instruction_button.rect.midbottom = self.game_instance.screen_rect.midbottom
        self.instruction_button.rect.y = self.game_instance.screen_rect.height/4

        #RESUME button 
        self.resume_button = Button(self.game_instance, 400, 100, 'purple', 'yellow')
        self.resume_button.rect.midtop = self.game_instance.screen_rect.midtop
        self.resume_button.rect.y = self.game_instance.screen_rect.height/2

        #EXIT button 
        self.exit_button = Button(self.game_instance, 300, 100, 'red', 'white')
        self.exit_button.rect.midtop = self.game_instance.screen_rect.midtop
        self.exit_button.rect.y = self.game_instance.screen_rect.height*3/4

    def open_alien_hunt_dynamic_menu(self):
        """Opens the dyanmic menu of Alien Hunt."""
        #Draw the background image
        self.screen.blit(self.bg_image, self.bg_image_rect)

        #Draw Instruction button
        self.instruction_button._prep_text('Use W-A-S-D to move and SPACE to fire while moving', 16)
        self.instruction_button.draw_button()

        #Draw RESUME button 
        self.resume_button._prep_text('RESUME', 56)
        self.resume_button.draw_button()

        #Draw EXIT button 
        self.exit_button._prep_text('EXIT', 56)
        self.exit_button.draw_button()