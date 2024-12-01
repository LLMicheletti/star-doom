import pygame

class AHSettings:
    """Stores the game's settings."""

    def __init__(self):
        """Initializes the Alien Hunt mode static settings."""
        #Rocket settings
        self.rocket_limit = 3

        #Alien Hunt mode playtime
        self.playtime = 50
        
        #Red ufos settings
        self.red_ufo_increase = 1

        #Green ufos settings
        self.green_ufo_increase = 2
        self.green_ufo_speed = 150

        #Blue ufos settings
        self.blue_ufo_increase = 3

        #How quickly game speeds up
        self.speedup_scale = 1.2

        #How quickly score increases
        self.score_scale = 1.5

        #How many planets to generate
        self.planet_limit = 5

        #Levels at witch the firepower is boosted
        self.boost_level_1 = 1
        self.boost_level_2 = 1

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """Initializes settings that change throughout the game."""
        self.rocket_speed = 150
        self.projectile_allowed = 10
        self.projectile_speed = 300
        self.red_ufo_limit = 5
        self.green_ufo_limit = 3
        self.blue_ufo_limit = 2
        self.counter = self.playtime
        self.green_ufo_counter = 0
        self.blue_ufo_counter = 0
        self.planet_counter = 0
        self.red_ufo_points = 20
        self.green_ufo_points = 30
        self.blue_ufo_points = 50
    
    def increase_difficulty(self):
        """Increases speed settings the number of ufos generated."""
        self.rocket_speed *= self.speedup_scale
        self.projectile_allowed += self.red_ufo_increase
        self.projectile_speed *= self.speedup_scale
        self.red_ufo_limit += self.red_ufo_increase
        self.green_ufo_limit += self.green_ufo_increase
        self.blue_ufo_limit += self.blue_ufo_increase
        self.counter = self.playtime - self.blue_ufo_limit
        self.red_ufo_counter = 0
        self.green_ufo_counter = 0
        self.blue_ufo_counter = 0
        self.planet_counter = 0
        self.red_ufo_points = int(self.red_ufo_points * self.score_scale)
        self.green_ufo_points = int(self.green_ufo_points * self.score_scale)
        self.blue_ufo_points = int(self.blue_ufo_points * self.score_scale)