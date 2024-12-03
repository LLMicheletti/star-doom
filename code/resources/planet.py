from pygame.sprite import Group
import random
import numpy as np
from numba import njit, prange


@njit(parallel=True)
def check_overlap(positions, sizes, planet_size, planet_position):
    """
    Checks for overlapping with other planets.
    """
    overlaps = False
    for i in prange(len(positions)):
        pos = positions[i]
        size = sizes[i]
        x1_min, y1_min = pos[0], pos[1]
        x1_max, y1_max = x1_min + size[0], y1_min + size[1]
        x2_min, y2_min = planet_position[0], planet_position[1]
        x2_max, y2_max = x2_min + planet_size[0], y2_min + planet_size[1]

        x_overlap = (x1_min <= x2_max) and (x1_max >= x2_min)
        y_overlap = (y1_min <= y2_max) and (y1_max >= y2_min)

        if x_overlap and y_overlap:
            overlaps = True
            
    return overlaps

check_overlap.parallel_diagnostics(level=4)

class PlanetGroup(Group):
    """A class to manage planets."""
    
    def __init__(self, game_instance):
        """
        Initializes the planet and set its starting position.
        """
        super().__init__()
        self.screen = game_instance.screen
        self.screen_rect = game_instance.screen_rect
        self.pg = game_instance.pg
        self.settings = game_instance.settings
        self.positions = np.zeros((self.settings.planet_limit, 2), dtype=np.int32)
        self.sizes = np.zeros((self.settings.planet_limit, 2), dtype=np.int32)

        # Usage
        self.preloaded_images = self.preload_images()

    def preload_images(self):
        """
        Preloads images to prevent repeated slow disk access.
        """
        images = {}
        for i in range(1, 8):
            try:
                img = self.pg.image.load(f'resources/images/planet{i}.png')
                dimension = random.randrange(50, 200)
                img = self.pg.transform.scale(img, (dimension, dimension))
                images[i] = {"image": img, "dimension" : [dimension, dimension]}
            except self.pg.error as e:
                print(f"Error loading image: planet{i}.png - {e}")
                images[i] = None  # Placeholder for missing images
        return images
    
    def create_planets(self):
        """
        Create a specified number of planets and add them to the group.
        """
        n = 0
        while n < self.settings.planet_limit:
            planet_image_info = self.preloaded_images.get(random.randrange(1, 8))
            planet_size = planet_image_info.get("dimension")
            planet_position = random.randint(0, self.screen_rect.width - planet_size[0]), random.randint(250, self.screen_rect.height - planet_size[1])
            if not check_overlap(self.positions, self.sizes, planet_size=planet_size, planet_position=planet_position):
                self.positions[n] = planet_position
                self.sizes[n] = planet_size
                self.add(self._create_planet(planet_image=planet_image_info.get("image"), planet_position=planet_position))
                n += 1
            else:
                continue

    def _create_planet(self, planet_image, planet_position):
        """
        Create a single planet sprite.
        """
        planet = self.pg.sprite.Sprite()
        planet.image = planet_image
        planet.rect = planet.image.get_rect()

        planet.rect.x, planet.rect.y = planet_position[0], planet_position[1]

        # Add a collision mask
        planet.mask = self.pg.mask.from_surface(planet.image)

        return planet

    def remove_planet(self, planet):
        """
        Remove a specific planet from the group.
        """
        self.remove(planet)

    def clear_all(self):
        """
        Remove all planets from the group.
        """
        self.empty()