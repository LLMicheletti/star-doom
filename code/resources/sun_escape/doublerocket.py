from pygame.sprite import Sprite
from numba import njit
import numpy as np

@njit
def calculate_new_position(position, moving_right, moving_left, moving_up, moving_down, speed, dt):
    """Calculate the new position based on movement flags and elapsed time."""
    direction = np.array([0.0, 0.0], dtype=np.float32)
    if moving_right:
        direction[0] += 1
    if moving_left:
        direction[0] -= 1
    if moving_up:
        direction[1] -= 1
    if moving_down:
        direction[1] += 1
    
    # Normalize the direction vector and scale by speed
    if np.linalg.norm(direction) > 0:
        direction = direction / np.linalg.norm(direction) * np.float32(speed)
    
    # Calculate new position based on direction and delta time
    position[0] = position[0] + direction[0] * np.float32(dt)
    position[1] = position[1] + direction[1] * np.float32(dt)

    return position, direction

class Doublerocket(Sprite):
    """A class to manage the doublerocket."""

    def __init__(self, game_instance):
        """Initializes the attributes of the doublerocket and its starting position."""
        super().__init__()
        #Work on the same screen of the game instance
        self.screen = game_instance.screen
        self.pg = game_instance.pg
        self.screen_rect = self.screen.get_rect()
        self.game_instance = game_instance

        #Settings
        self.settings = game_instance.settings

        #Load the doublerocket images and get their rects
        #Pointing right
        self.right_image = self.pg.image.load('resources/images/doublerocket_right.bmp')
        self.right_image_rect = self.right_image.get_rect()
        
        #Pointing left
        self.left_image = self.pg.image.load('resources/images/doublerocket_left.bmp')
        self.left_image_rect = self.left_image.get_rect()
        

        #Pointing up
        self.up_image = self.pg.image.load('resources/images/doublerocket_up.bmp')
        self.up_image_rect = self.up_image.get_rect()
        

        #Pointing down
        self.down_image = self.pg.image.load('resources/images/doublerocket_down.bmp')
        self.down_image_rect = self.down_image.get_rect()
        
        self.place_initial()

        #Movement flags
        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False

    def place_initial(self):
        """Places the doublerocket at its inital position"""
        self.right_image_rect.x = 0
        self.right_image_rect.y = self.screen_rect.height/2
        self.left_image_rect.x = 0
        self.left_image_rect.y = self.screen_rect.height/2
        self.up_image_rect.x = 0
        self.up_image_rect.y = self.screen_rect.height/2
        self.down_image_rect.x = 0
        self.down_image_rect.y = self.screen_rect.height/2

        #Start with the doublerocket pointing right at the right of the screen
        self.image = self.right_image
        self.mask = self.pg.mask.from_surface(self.image)
        self.rect = self.right_image_rect
        self.position = np.array([0, self.screen_rect.height/2], dtype=np.float32)

    def update(self, dt):
        """Updates doublerocket's position based on the movement flags and elapsed time."""
        
        # Update position
        self.position, speed = calculate_new_position(
            self.position, self.moving_right, self.moving_left, self.moving_up, self.moving_down, self.settings.doublerocket_speed, dt
            )

        # Constrain to screen boundaries
        self.position[0] = np.clip(self.position[0], 0, self.screen_rect.right - self.rect.width)
        self.position[1] = np.clip(self.position[1], 0, self.screen_rect.bottom - self.rect.height)

        new_rect_x, new_rect_y = round(self.position[0]), round(self.position[1])
        if self.rect.x != new_rect_x or self.rect.y != new_rect_y:
            # Update image and mask based on movement direction
            if speed[0] > 0:
                self.image = self.right_image
                self.rect = self.right_image_rect
            elif speed[0] < 0:
                self.image = self.left_image
                self.rect = self.left_image_rect
            elif speed[1] < 0:
                self.image = self.up_image
                self.rect = self.up_image_rect
            elif speed[1] > 0:
                self.image = self.down_image
                self.rect = self.down_image_rect
            
            self.rect.x, self.rect.y = new_rect_x, new_rect_y

            self.mask = self.pg.mask.from_surface(self.image)
            
            # Update all image rects
            for img_rect in [self.right_image_rect, self.left_image_rect, self.up_image_rect, self.down_image_rect]:
                img_rect.center = self.rect.center

    def blit_doublerocket(self):
        """Draws the doublerocket at its current position."""
        self.screen.blit(self.image, self.rect)

        #Draw fuel bar
        self.fuel_rect = self.pg.Rect(0, 0, self.settings.doublerocket_fuel, 3)
        self.fuel_rect.centerx = self.rect.centerx
        self.fuel_rect.y = self.rect.y - 3
        self.pg.draw.rect(self.screen, 'yellow', self.fuel_rect)