import pygame
from pygame.sprite import Sprite
import random

class FuelTank(Sprite):
    """A class to manage the fuel tank of the doublerocket."""

    def __init__(self, game_instance):
        """Initializes the main attributes and loads the images."""
        super().__init__()
        self.screen = game_instance.screen
        self.screen_rect = game_instance.screen_rect
        self.settings = game_instance.settings

        self.right_image = pygame.image.load('resources/images/fuel_tank_right.bmp')
        self.right_image = pygame.transform.scale(self.right_image, (70, 50))
        self.right_image_rect = self.right_image.get_rect()

        self.left_image = pygame.image.load('resources/images/fuel_tank_left.bmp')
        self.left_image = pygame.transform.scale(self.left_image, (70, 50))
        self.left_image_rect = self.left_image.get_rect()

        #Let's start with the left image at the center of the screen
        self.image = self.left_image
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.left_image_rect
        self.rect.centerx = self.screen_rect.centerx
        self.rect.y = random.randrange(70, self.screen_rect.height - 70)
        self.right_image_rect.center = self.left_image_rect.center

    def update(self):
        """Updates the image"""
        if self.settings.fuel_counter % 2 == 0:
            self.image = self.left_image
            self.rect = self.left_image_rect
            self.mask = pygame.mask.from_surface(self.image)
        elif self.settings.fuel_counter % 2 == 1:
            self.image = self.right_image
            self.rect = self.right_image_rect
            self.mask = pygame.mask.from_surface(self.image)
        
        self.right_image_rect.center = self.rect.center
        self.left_image_rect.center = self.rect.center
        
        self.screen.blit(self.image, self.rect)