import pygame
from pygame.sprite import Group
from numba import njit
import numpy as np
from typing import Literal

@njit
def calculate_new_position(
    x, y, moving_right, moving_left, moving_up, moving_down, moving_northwest, moving_northeast, moving_southwest, moving_southeast,
    speed, dt
    ):
    """Calculate the new position based on movement flags and elapsed time."""
    direction = np.array([0.0, 0.0])
    if moving_right:
        direction[0] += 1
    if moving_left:
        direction[0] -= 1
    if moving_up:
        direction[1] -= 1
    if moving_down:
        direction[1] += 1
    if moving_northwest:
        direction[0] -= 1
        direction[1] -= 1
    if moving_northeast:
        direction[0] += 1
        direction[1] -= 1
    if moving_southwest:
        direction[0] -= 1
        direction[1] += 1
    if moving_southeast:
        direction[0] += 1
        direction[1] += 1
    
    # Normalize the direction vector and scale by speed
    if np.linalg.norm(direction) > 0:
        direction = direction / np.linalg.norm(direction) * speed
    
    # Calculate new position based on direction and delta time
    new_x = x + direction[0] * dt
    new_y = y + direction[1] * dt
    
    return new_x, new_y

class ProjectileGroup(Group):
    """A class to manage the projectiles fired from the ship."""
    
    def __init__(self, game_instance, image_path):
        """Creates a projectile object at the rocket's current position."""
        super().__init__()
        self.screen = game_instance.screen
        self.settings = game_instance.settings
        self.pg = game_instance.pg
        self.image_path = image_path
        self.rect_positions = np.zeros((100, 2), dtype=np.int32)
        self.exact_positions = np.zeros((100, 2), dtype=np.float32)
        
        self.game_instance = game_instance
        
        self.image, self.rect = self.preload_images()

    def preload_images(self):
        """
        Preloads images to prevent repeated slow disk access.
        """
        self.image = pygame.image.load(self.image_path)
        self.image = pygame.transform.scale(self.image, (15, 15))
        self.rect = self.image.get_rect()

        return self.image, self.rect
    
    def create_projectile(self, obj_center):
        """
        Creates and adds a new projectile to the group.
        """
        projectile = self.pg.sprite.Sprite()

        projectile.index = np.where((self.rect_positions == [0, 0]).all(axis=1))[0][0]

        self.rect_positions[projectile.index] = obj_center
        self.exact_positions[projectile.index] = np.float32(obj_center)

        projectile.image = self.image
        projectile.rect = self.rect.copy()

        projectile.rect.center = obj_center
        projectile.x, projectile.y = float(obj_center[0]), float(obj_center[1])

        projectile.fire_right = False
        projectile.fire_left = False
        projectile.fire_up = False
        projectile.fire_down = False
        projectile.fire_northwest = False
        projectile.fire_northeast = False
        projectile.fire_southwest = False
        projectile.fire_southeast = False

        return projectile

    def update(self, dt, projectile_speed):
        """
        Updates the projectile's position based on the movement flags.
        """
        for projectile in self.sprites():
            self.exact_positions[projectile.index] = calculate_new_position(
                projectile.x, projectile.y, projectile.fire_right, projectile.fire_left, projectile.fire_up, projectile.fire_down,
                projectile.fire_northwest, projectile.fire_northeast, projectile.fire_southwest, projectile.fire_southeast, projectile_speed, dt
                )
            
            self.rect_positions[projectile.index] = np.round(self.exact_positions[projectile.index]).astype(np.int32)
            
            projectile.x, projectile.y = self.exact_positions[projectile.index]

            new_rect_x, new_rect_y = round(projectile.x), round(projectile.y)
            if projectile.rect.x != new_rect_x or projectile.rect.y != new_rect_y:
                projectile.rect.x, projectile.rect.y = new_rect_x, new_rect_y

    def blit_projectile(self):
        """Draws the projectile at its current position."""
        for projectile in self.sprites():
            self.screen.blit(projectile.image, projectile.rect)

    def remove_projectile(self, projectile):
        """Removes the projectile from the group."""
        self.remove(projectile)
        index = np.where((self.rect_positions == [projectile.rect.x, projectile.rect.y]).all(axis=1))[0][0]
        self.rect_positions[index] = [0, 0]
        self.exact_positions[index] = [0, 0]

    def clear_projectiles(self):
        """Clears all projectiles from the group."""
        self.empty()
        self.rect_positions = np.zeros((100, 2), dtype=np.int32)
        self.exact_positions = np.zeros((100, 2), dtype=np.float32)