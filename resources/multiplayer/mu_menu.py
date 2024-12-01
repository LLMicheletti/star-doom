import pygame

from ..button import Button

class MultiplayerStaticMenu:
    """A class to manage the main menu of Multplayer mode."""

    def __init__(self, game_instance):
        """Initializes the attributes"""
        #Get the same screen of the game
        self.game_instance = game_instance
        self.screen = game_instance.screen
        self.screen_rect = game_instance.screen.get_rect()
        self.bg_image = pygame.image.load('resources/images/universe_3.bmp')
        self.bg_image = pygame.transform.scale(self.bg_image, (game_instance.window_width, game_instance.window_height))
        self.bg_image_rect = self.bg_image.get_rect()

        #PLAY button
        self.play_button = Button(self.game_instance, 300, 100, 'yellow', 'green')
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
        
    def open_multiplayer_static_menu(self):
        """Opens the main menu of Multiplayer."""
        #Draw the background image
        self.screen.blit(self.bg_image, self.bg_image_rect)

        #Load and play the background music
        pygame.mixer.init()
        pygame.mixer.music.load('resources/sounds/day_one.mp3')
        pygame.mixer.music.play(-1)

        #Draw PLAY button
        self.play_button._prep_text('PLAY', 56)
        self.play_button.draw_button()

        #Draw BACK button 
        self.back_button._prep_text('BACK', 56)
        self.back_button.draw_button()

        #Draw Instruction button
        self.instruction_button._prep_text('Prevail against your opponent with your skill!', 16)
        self.instruction_button.draw_button()

class MultiplayerDynamicMenu:
    """A class to manage the in-game menu of Multplayer mode."""

    def __init__(self, game_instance):
        """Initializes the attributes"""
        #Get the same screen of the game
        self.game_instance = game_instance
        self.screen = game_instance.screen
        self.screen_rect = game_instance.screen.get_rect()
        self.bg_image = pygame.image.load('resources/images/universe_3.bmp')
        self.bg_image = pygame.transform.scale(self.bg_image, (game_instance.window_width, game_instance.window_height))
        self.bg_image_rect = self.bg_image.get_rect()

        #Player 1 Instruction button
        self.instruction_1_button = Button(self.game_instance, 800, 60, 'yellow', 'green')
        self.instruction_1_button.rect.midbottom = self.game_instance.screen_rect.midbottom
        self.instruction_1_button.rect.y = self.game_instance.screen_rect.height/6

        #Player 2 Instruction button
        self.instruction_2_button = Button(self.game_instance, 800, 60, 'yellow', 'green')
        self.instruction_2_button.rect.midbottom = self.game_instance.screen_rect.midbottom
        self.instruction_2_button.rect.y = self.game_instance.screen_rect.height/3

        #RESUME button 
        self.resume_button = Button(self.game_instance, 400, 100, 'red', 'white')
        self.resume_button.rect.midtop = self.game_instance.screen_rect.midtop
        self.resume_button.rect.y = self.game_instance.screen_rect.height/2

        #EXIT button 
        self.exit_button = Button(self.game_instance, 300, 100, 'white', 'white')
        self.exit_button.rect.midtop = self.game_instance.screen_rect.midtop
        self.exit_button.rect.y = self.game_instance.screen_rect.height*3/4
        
    def open_multiplayer_dynamic_menu(self):
        """Opens the main menu of Multiplayer."""
        #Draw the background image
        self.screen.blit(self.bg_image, self.bg_image_rect)

        #Draw Player 1 Instruction button
        self.instruction_1_button._prep_text('Player 1:Use W-A-S-D to move and SPACE to fire while moving', 16)
        self.instruction_1_button.draw_button()

        #Draw Player 2 Instruction button
        self.instruction_2_button._prep_text('Player 1:Use <-^-> to move and ENTER to fire while moving', 16)
        self.instruction_2_button.draw_button()

        #Draw RESUME button 
        self.resume_button._prep_text('RESUME', 56)
        self.resume_button.draw_button()

        #Draw EXIT button 
        self.exit_button._prep_text('EXIT', 56)
        self.exit_button.draw_button()

class Player1Menu:
    """A class to manage the menu in wich Player 1 chooses his/her rocket."""
    
    def __init__(self, game_instance):
        """Intializes the main attributes."""
        #Get the same screen of the game
        self.game_instance = game_instance
        self.screen = game_instance.screen
        self.screen_rect = game_instance.screen.get_rect()
        self.bg_image = pygame.image.load('resources/images/universe_3.bmp')
        self.bg_image = pygame.transform.scale(self.bg_image, (game_instance.window_width, game_instance.window_height))
        self.bg_image_rect = self.bg_image.get_rect()

        self.ship_1_button = Button(self.game_instance, 200, 300, 'white', 'white')
        self.ship_1_button.rect.left = self.screen_rect.width/4
        self.ship_1_button.rect.centery = self.screen_rect.height/2
        self.ship_1_right_image = pygame.image.load('resources/images/rocket_right.bmp')
        self.ship_1_left_image = pygame.image.load('resources/images/rocket_left.bmp')
        self.ship_1_up_image = pygame.image.load('resources/images/rocket_up.bmp')
        self.ship_1_down_image = pygame.image.load('resources/images/rocket_down.bmp')
        self.ship_1_image = self.ship_1_up_image
        self.ship_1_rect = self.ship_1_image.get_rect()
        self.ship_1_rect.center = self.ship_1_button.rect.center

        self.ship_2_button = Button(self.game_instance, 200, 300, 'white', 'white')
        self.ship_2_button.rect.centerx = self.screen_rect.width/2
        self.ship_2_button.rect.centery = self.screen_rect.height/2
        self.ship_2_right_image = pygame.image.load('resources/images/blue_ufo_right.bmp')
        self.ship_2_left_image = pygame.image.load('resources/images/blue_ufo_left.bmp')
        self.ship_2_up_image = pygame.image.load('resources/images/blue_ufo_right.bmp')
        self.ship_2_down_image = pygame.image.load('resources/images/blue_ufo_left.bmp')
        self.ship_2_image = self.ship_2_up_image
        self.ship_2_rect = self.ship_2_image.get_rect()
        self.ship_2_rect.center = self.ship_2_button.rect.center

        self.ship_3_button = Button(self.game_instance, 200, 300, 'white', 'white')
        self.ship_3_button.rect.right = self.screen_rect.width *3/4
        self.ship_3_button.rect.centery = self.screen_rect.height/2
        self.ship_3_right_image = pygame.image.load('resources/images/green_ufo_right.bmp')
        self.ship_3_left_image = pygame.image.load('resources/images/green_ufo_left.bmp')
        self.ship_3_up_image = pygame.image.load('resources/images/green_ufo_right.bmp')
        self.ship_3_down_image = pygame.image.load('resources/images/green_ufo_left.bmp')
        self.ship_3_image = self.ship_3_up_image
        self.ship_3_rect = self.ship_3_image.get_rect()
        self.ship_3_rect.center = self.ship_3_button.rect.center

        #Instruction button
        self.instruction_button = Button(self.game_instance, 500, 60, 'white', 'white')
        self.instruction_button.rect.x = self.game_instance.screen_rect.width/5
        self.instruction_button.rect.y = self.game_instance.screen_rect.height/5

    def open_player_1_menu(self):
        """Opens the choosing menu for Player 1."""
        #Draw the background image
        self.screen.blit(self.bg_image, self.bg_image_rect)

        #Draw ship 1 button
        pygame.draw.rect(self.screen, 'white', self.ship_1_button.rect, 5)
        self.screen.blit(self.ship_1_image, self.ship_1_rect)

        #Draw ship 2 button
        pygame.draw.rect(self.screen, 'white', self.ship_2_button.rect, 5)
        self.screen.blit(self.ship_2_image, self.ship_2_rect)

        #Draw ship 3 button
        pygame.draw.rect(self.screen, 'white', self.ship_3_button.rect, 5)
        self.screen.blit(self.ship_3_image, self.ship_3_rect)

        #Draw Instruction button
        self.instruction_button._prep_text('Player 1, choose your spaceship.', 16)
        self.instruction_button.draw_button()

class Player2Menu:
    """A class to manage the menu in wich Player 2 chooses his/her rocket."""
    
    def __init__(self, game_instance):
        """Intializes the main attributes."""
        #Get the same screen of the game
        self.game_instance = game_instance
        self.screen = game_instance.screen
        self.screen_rect = game_instance.screen.get_rect()
        self.bg_image = pygame.image.load('resources/images/universe_3.bmp')
        self.bg_image = pygame.transform.scale(self.bg_image, (game_instance.window_width, game_instance.window_height))
        self.bg_image_rect = self.bg_image.get_rect()

        self.ship_1_button = Button(self.game_instance, 200, 300, 'white', 'white')
        self.ship_1_button.rect.left = self.screen_rect.width/4
        self.ship_1_button.rect.centery = self.screen_rect.height/2
        self.ship_1_right_image = pygame.image.load('resources/images/doublerocket_right.bmp')
        self.ship_1_left_image = pygame.image.load('resources/images/doublerocket_left.bmp')
        self.ship_1_up_image = pygame.image.load('resources/images/doublerocket_up.bmp')
        self.ship_1_down_image = pygame.image.load('resources/images/doublerocket_down.bmp')
        self.ship_1_image = self.ship_1_up_image
        self.ship_1_rect = self.ship_1_image.get_rect()
        self.ship_1_rect.center = self.ship_1_button.rect.center

        self.ship_2_button = Button(self.game_instance, 200, 300, 'white', 'white')
        self.ship_2_button.rect.centerx = self.screen_rect.width/2
        self.ship_2_button.rect.centery = self.screen_rect.height/2
        self.ship_2_right_image = pygame.image.load('resources/images/red_ufo_right.bmp')
        self.ship_2_left_image = pygame.image.load('resources/images/red_ufo_left.bmp')
        self.ship_2_up_image = pygame.image.load('resources/images/red_ufo_right.bmp')
        self.ship_2_down_image = pygame.image.load('resources/images/red_ufo_left.bmp')
        self.ship_2_image = self.ship_2_up_image
        self.ship_2_rect = self.ship_2_image.get_rect()
        self.ship_2_rect.center = self.ship_2_button.rect.center

        self.ship_3_button = Button(self.game_instance, 200, 300, 'white', 'white')
        self.ship_3_button.rect.right = self.screen_rect.width *3/4
        self.ship_3_button.rect.centery = self.screen_rect.height/2
        self.ship_3_right_image = pygame.image.load('resources/images/spiked_ship_right.bmp')
        self.ship_3_right_image = pygame.transform.scale(self.ship_3_right_image, (65, 52))
        self.ship_3_left_image = pygame.image.load('resources/images/spiked_ship_left.bmp')
        self.ship_3_left_image = pygame.transform.scale(self.ship_3_left_image, (65, 52))
        self.ship_3_up_image = pygame.image.load('resources/images/spiked_ship_up.bmp')
        self.ship_3_up_image = pygame.transform.scale(self.ship_3_up_image, (65, 52))
        self.ship_3_down_image = pygame.image.load('resources/images/spiked_ship_down.bmp')
        self.ship_3_down_image = pygame.transform.scale(self.ship_3_down_image, (65, 52))
        self.ship_3_image = self.ship_3_up_image
        self.ship_3_rect = self.ship_3_image.get_rect()
        self.ship_3_rect.center = self.ship_3_button.rect.center

        #Instruction button
        self.instruction_button = Button(self.game_instance, 500, 60, 'white', 'white')
        self.instruction_button.rect.x = self.game_instance.screen_rect.width*3/5
        self.instruction_button.rect.y = self.game_instance.screen_rect.height/5

    def open_player_2_menu(self):
        """Opens the choosing menu for Player 2."""
        #Draw the background image
        self.screen.blit(self.bg_image, self.bg_image_rect)

        #Draw ship 1 button
        pygame.draw.rect(self.screen, 'white', self.ship_1_button.rect, 5)
        self.screen.blit(self.ship_1_image, self.ship_1_rect)

        #Draw ship 2 button
        pygame.draw.rect(self.screen, 'white', self.ship_2_button.rect, 5)
        self.screen.blit(self.ship_2_image, self.ship_2_rect)

        #Draw ship 3 button
        pygame.draw.rect(self.screen, 'white', self.ship_3_button.rect, 5)
        self.screen.blit(self.ship_3_image, self.ship_3_rect)

        #Draw Instruction button
        self.instruction_button._prep_text('Player 2, choose your spaceship.', 16)
        self.instruction_button.draw_button()