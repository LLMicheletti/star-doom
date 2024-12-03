import pygame.font

class Button:
    """A class to build buttons."""

    def __init__(self, game_instance, width, height, button_colour, text_colour):
        """Initializes the main attributes of a button."""
        #Match with the game screen
        self.screen = game_instance.screen
        self.screen_rect = self.screen.get_rect()

        #Dimensions
        self.width, self.height = width, height
        self.button_colour, self.text_colour = button_colour, text_colour
        
        #Build the rect
        self.rect = pygame.Rect(0, 0, self.width, self.height)
    
    def _prep_text(self, text, font_size):
        """Turns the text into a rendered image."""
        #Font
        self.font = pygame.font.Font('resources/font/Dune_Rise.otf', font_size)
        self.font.set_underline(True)

        #Render image
        self.text_image = self.font.render(text, True, self.text_colour, None)
        self.text_image_rect = self.text_image.get_rect()
        self.text_image_rect.center = self.rect.center

    def draw_button(self):
        """Draws the button to the given position of the screen."""
        pygame.draw.rect(self.screen, self.button_colour, self.rect, 5)
        self.screen.blit(self.text_image, self.text_image_rect)

