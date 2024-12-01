import pygame
from pygame.sprite import Group, Sprite
import random
from numba import njit, prange
import numpy as np

@njit
def calculate_new_position(x, y, speed, move_horizontal, move_vertical, dt):
    """Calculate the new position based on movement flags and elapsed time."""
    direction = np.array([0.0, 0.0], dtype=np.float32)
    direction[0] += move_horizontal
    direction[1] += move_vertical
    
    # Normalize the direction vector and scale by speed
    if np.linalg.norm(direction) > 0:
        direction = direction / np.linalg.norm(direction) * np.float32(speed)
    
    # Calculate new position based on direction and delta time
    
    new_position = np.array([0, 0], dtype=np.float32)
    new_position[0] = x + direction[0] * np.float32(dt)
    new_position[1] = y + direction[1] * np.float32(dt)

    return new_position

@njit(parallel=True)
def check_overlap(ufo_size, ufo_position, planets_positions, planets_sizes):
    """
    Checks for overlapping with planets.
    """
    overlaps = False  # Initialize the overlap flag
    for i in prange(len(planets_positions)): 
        pos = planets_positions[i]
        size = planets_sizes[i]

        x1_min, y1_min = pos[0], pos[1]
        x1_max, y1_max = x1_min + size[0], y1_min + size[1]
        x2_min, y2_min = ufo_position[0], ufo_position[1]
        x2_max, y2_max = x2_min + ufo_size[0], y2_min + ufo_size[1]

        x_overlap = (x1_min <= x2_max) & (x1_max >= x2_min)
        y_overlap = (y1_min <= y2_max) & (y1_max >= y2_min)

        if x_overlap and y_overlap:
            overlaps = True

    return overlaps

class RedUfoFleet(Group):
    """A class o represent a single red ufo in the fleet."""

    def __init__(self, game_instance):
        """Initializes the ufo and set its starting position."""
        super().__init__()
        self.screen = game_instance.screen
        self.screen_rect = game_instance.screen_rect
        self.game_instance = game_instance
        self.pg = game_instance.pg
        self.settings = game_instance.settings
        self.positions = np.zeros((100, 2), dtype=np.int32)

        # Usage
        self.red_image_right, self.red_image_left, self.red_rect_right, self.red_rect_left = self.preload_images()

        #Default image and rect
        self.size = self.red_rect_right.size

    def preload_images(self):
        """
        Preloads images to prevent repeated slow disk access.
        """
        self.red_image_right = pygame.image.load('resources/images/red_ufo_right.bmp')
        self.red_rect_right = self.red_image_right.get_rect()

        self.red_image_left = pygame.image.load('resources/images/red_ufo_left.bmp')
        self.red_rect_left = self.red_image_left.get_rect()

        return self.red_image_right, self.red_image_left, self.red_rect_right, self.red_rect_left

    def create_fleet(self, planets_positions, planets_sizes):
        """
        Create a specified number of ufos and add them to the group.
        """
        n = 0
        while n < self.settings.red_ufo_limit:
            ufo_position = random.randrange(0, self.screen_rect.width - self.red_rect_right.width), random.randrange(250, self.screen_rect.height - self.red_rect_right.height)
            if not check_overlap(ufo_position=ufo_position, ufo_size=self.size, planets_positions=planets_positions, planets_sizes=planets_sizes):
                self.positions[n] = ufo_position
                self.add(self._create_ufo(ufo_position))
                n += 1
            else:
                continue

    def _create_ufo(self, ufo_position):
        """
        Create a single ufo sprite.
        """
        red_ufo = self.pg.sprite.Sprite()
        red_ufo.red_image_right = self.red_image_right
        red_ufo.red_rect_right = self.red_rect_right
        red_ufo.red_image_left = self.red_image_left
        red_ufo.red_rect_left = self.red_rect_left

        for rect in (red_ufo.red_rect_right, red_ufo.red_rect_left):
            rect.x, rect.y = ufo_position

        red_ufo.image = red_ufo.red_image_right
        red_ufo.rect = red_ufo.red_rect_right

        return red_ufo

    def update(self):
        """Updates the image and position of each UFO."""
        for i, sprite in enumerate(self.sprites()):
            # Update the sprite image and rect based on the counter
            if self.game_instance.settings.counter % 2 == 0:
                sprite.image = sprite.red_image_right
                sprite.rect = sprite.red_rect_right.copy()  # Use a copy to avoid shared reference issues
            else:
                sprite.image = sprite.red_image_left
                sprite.rect = sprite.red_rect_left.copy()

            # Update the rect position from self.positions
            sprite.rect.topleft = (int(self.positions[i][0]), int(self.positions[i][1])) 

    def remove_ufo(self, ufo):
        """
        Remove a specific ufo from the group.
        """
        try:
            index = self.sprites().index(ufo)  # Find the index of the UFO in the group
        except ValueError:
            pass
        else:
            self.positions = np.delete(self.positions, index, axis=0)  # Remove position from array
            self.remove(ufo)

    def clear_all(self):
        """
        Remove all ufos from the group.
        """
        self.empty()
        self.positions = np.zeros((100, 2), dtype=np.int32)

class GreenUfoFleet(Group):
    """A class o represent a single green ufo in the fleet."""

    def __init__(self, game_instance):
        """Initializes the ufo and set its starting position."""
        super().__init__()
        self.screen = game_instance.screen
        self.screen_rect = game_instance.screen_rect
        self.game_instance = game_instance
        self.settings = game_instance.settings
        self.pg = game_instance.pg
        self.rect_positions = np.zeros((100, 2), dtype=np.int32)
        self.exact_positions = np.zeros((100, 2), dtype=np.float32)

        self.green_image_right, self.green_image_left, self.green_rect_right, self.green_rect_left = self.preload_images()

        self.size = self.green_rect_right.size

    def preload_images(self):
        """
        Preloads images to prevent repeated slow disk access.
        """
        self.green_image_right = pygame.image.load('resources/images/green_ufo_right.bmp')
        self.green_rect_right = self.green_image_right.get_rect()

        self.green_image_left = pygame.image.load('resources/images/green_ufo_left.bmp')
        self.green_rect_left = self.green_image_left.get_rect()

        return self.green_image_right, self.green_image_left, self.green_rect_right, self.green_rect_left

    def create_fleet(self, planets_positions, planets_sizes):
        """
        Create a specified number of ufos and add them to the group.
        """
        n = 0
        while n < self.settings.green_ufo_limit:
            ufo_position = random.randrange(0, self.screen_rect.width - self.green_rect_right.width), random.randrange(250, self.screen_rect.height - self.green_rect_right.height)
            if not check_overlap(ufo_position=ufo_position, ufo_size=self.size, planets_positions=planets_positions, planets_sizes=planets_sizes):
                self.rect_positions[n] = ufo_position
                self.exact_positions[n] = np.float32(ufo_position)
                self.add(self._create_ufo(ufo_position))
                n += 1
            else:
                continue

    def _create_ufo(self, ufo_position):
        """
        Create a single ufo sprite.
        """
        green_ufo = self.pg.sprite.Sprite()
        green_ufo.green_image_right = self.green_image_right
        green_ufo.green_rect_right = self.green_rect_right
        green_ufo.green_image_left = self.green_image_left
        green_ufo.green_rect_left = self.green_rect_left

        for rect in (green_ufo.green_rect_right, green_ufo.green_rect_left):
            rect.x, rect.y = ufo_position

        green_ufo.x, green_ufo.y = float(ufo_position[0]), float(ufo_position[1])

        green_ufo.image = green_ufo.green_image_right
        green_ufo.rect = green_ufo.green_rect_right

        green_ufo.move_horizontal = 0
        green_ufo.move_vertical = 0

        green_ufo.direction = 1

        green_ufo.mask = self.pg.mask.from_surface(green_ufo.image)

        return green_ufo

    def update(self, dt):
        """Updates the image."""
        for i, sprite in enumerate(self.sprites()):
            # Update position
            self.exact_positions[i] = calculate_new_position(
                self.exact_positions[i][0], self.exact_positions[i][1], self.settings.green_ufo_speed, sprite.move_horizontal, sprite.move_vertical, dt
                )
            
            self.rect_positions[i] = np.round(self.exact_positions[i])
            
            if sprite.direction == 1:
                sprite.image = sprite.green_image_right
                sprite.rect = sprite.green_rect_right.copy()
            elif sprite.direction == -1:
                sprite.image = sprite.green_image_left
                sprite.rect = sprite.green_rect_left.copy()
            
            sprite.x, sprite.y = float(self.exact_positions[i][0]), float(self.exact_positions[i][1])

            # Update rect position
            sprite.rect.topleft = (int(self.rect_positions[i][0]), int(self.rect_positions[i][1]))

            sprite.mask = pygame.mask.from_surface(sprite.image)

            # Update all image rects
            for img_rect in [sprite.green_rect_right, sprite.green_rect_left]:
                img_rect.center = sprite.rect.center

    def remove_ufo(self, ufo):
        """
        Remove a specific ufo from the group.
        """
        try:
            index = self.sprites().index(ufo)  # Find the index of the UFO in the group
        except ValueError:
            pass
        else:
            self.rect_positions = np.delete(self.rect_positions, index, axis=0)  # Remove position from array
            self.exact_positions = np.delete(self.exact_positions, index, axis=0)
            self.remove(ufo)

    def clear_all(self):
        """
        Remove all ufos from the group.
        """
        self.empty()
        self.rect_positions = np.zeros((100, 2), dtype=np.int32)
        self.exact_positions = np.zeros((100, 2), dtype=np.float32)

class BlueUfoFleet(Group):
    """A class o represent a single blue ufo in the fleet."""

    def __init__(self, game_instance):
        """Initializes the ufo and set its starting position."""
        super().__init__()
        self.screen = game_instance.screen
        self.screen_rect = game_instance.screen_rect
        self.game_instance = game_instance
        self.pg = game_instance.pg
        self.settings = game_instance.settings
        self.positions = np.zeros((100, 2), dtype=np.int32)

        self.blue_image_right, self.blue_image_left, self.blue_rect_right, self.blue_rect_left = self.preload_images()

        self.size = self.blue_rect_right.size

    def preload_images(self):
        """
        Preloads images to prevent repeated slow disk access.
        """
        self.blue_image_right = pygame.image.load('resources/images/blue_ufo_right.bmp')
        self.blue_rect_right = self.blue_image_right.get_rect()

        self.blue_image_left = pygame.image.load('resources/images/blue_ufo_left.bmp')
        self.blue_rect_left = self.blue_image_left.get_rect()

        return self.blue_image_right, self.blue_image_left, self.blue_rect_right, self.blue_rect_left

    def create_fleet(self, planets_positions, planets_sizes):
        """
        Create a specified number of ufos and add them to the group.
        """
        n = 0
        while n < self.settings.blue_ufo_limit:
            ufo_position = random.randrange(0, self.screen_rect.width - self.blue_rect_right.width), random.randrange(250, self.screen_rect.height - self.blue_rect_right.height)
            if not check_overlap(ufo_position=ufo_position, ufo_size=self.size, planets_positions=planets_positions, planets_sizes=planets_sizes):
                self.positions[n] = ufo_position
                self.add(self._create_ufo(ufo_position))
                n += 1
            else:
                continue

    def _create_ufo(self, ufo_position):
        """
        Create a single ufo sprite.
        """
        blue_ufo = self.pg.sprite.Sprite()
        blue_ufo.blue_image_right = self.blue_image_right
        blue_ufo.blue_rect_right = self.blue_rect_right
        blue_ufo.blue_image_left = self.blue_image_left
        blue_ufo.blue_rect_left = self.blue_rect_left

        for rect in (blue_ufo.blue_rect_right, blue_ufo.blue_rect_left):
            rect.x, rect.y = ufo_position

        blue_ufo.image = blue_ufo.blue_image_right
        blue_ufo.rect = blue_ufo.blue_rect_right

        return blue_ufo

    def update(self):
        """Updates the image and position of each UFO."""
        for i, sprite in enumerate(self.sprites()):
            # Update the sprite image and rect based on the counter
            if self.game_instance.settings.counter % 2 == 0:
                sprite.image = sprite.blue_image_right
                sprite.rect = sprite.blue_rect_right.copy()  # Use a copy to avoid shablue reference issues
            else:
                sprite.image = sprite.blue_image_left
                sprite.rect = sprite.blue_rect_left.copy()

            # Update the rect position from self.positions
            sprite.rect.topleft = (int(self.positions[i][0]), int(self.positions[i][1]))

    def remove_ufo(self, ufo):
        """
        Remove a specific ufo from the group.
        """
        try:
            index = self.sprites().index(ufo)  # Find the index of the UFO in the group
        except ValueError:
            pass
        else:
            self.positions = np.delete(self.positions, index, axis=0)  # Remove position from array
            self.remove(ufo)

    def clear_all(self):
        """
        Remove all ufos from the group.
        """
        self.empty()
        self.positions = np.zeros((100, 2), dtype=np.int32)