import pygame

class SESettings:
    """Stores the game's settings."""

    def __init__(self):
        """Initializes the Sun Escape mode's static settings."""
        #Doublerocket settings
        self.doublerocket_limit = 3
        self.doublerocket_wave_speed = 300
        self.doublerocket_waves_allowed = 2

        #Fuel tank settings
        self.backup_fuel_tank_limit = 5
        
        #How quickly game speeds up
        self.speedup_scale = 1.5

        #Waves settings
        self.level_1_waves = 2
        self.level_2_waves = 2
        self.level_3_waves = 4
        self.level_4_waves = 4

        #Black hole settings
        self.black_hole_speed = 150
        self.black_hole_direction = 1 #1 is down, -1 is up
        self.black_hole_hit_duration = 0.2

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """Initializes settings that change throughout the game."""
        self.num_waves = 0
        self.doublerocket_speed = 150
        self.doublerocket_max_speed = 300
        self.wave_speed = 120
        self.wave_pause = 8
        self.wave_counter = self.wave_pause
        self.fuel_counter = self.wave_pause
        self.doublerocket_fuel = 50
        self.fuel_leak = 2
        self.collision_pause = 1
        self.collision_counter = self.collision_pause
        self.black_hole_life = 350

    def increase_difficulty(self):
        """Increases speeds but decreases fuel available."""
        self.doublerocket_speed *= self.speedup_scale
        self.doublerocket_max_speed *= self.speedup_scale
        self.wave_speed *= self.speedup_scale
        self.fuel_leak += 2
        self.wave_pause -= 2