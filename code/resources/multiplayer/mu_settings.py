class MUSettings:
    """Stores the game's settings."""
    def __init__(self):
        """Initializes the Multiplayer settings."""
        self.ship_limit = 5

        self.ship_speed = 180

        self.projectile_allowed = 6
        
        self.projectile_speed = 500

        self.planet_limit = 5

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """Initializes settings that change throughout the game."""
        self.planet_counter = 0

    def increase_difficulty(self):
        """Increases the speed of ships, projectiles and allows more projectiles"""
        self.ship_speed *= 1.2
        self.projectile_speed *= 1.2
        self.projectile_allowed += 2