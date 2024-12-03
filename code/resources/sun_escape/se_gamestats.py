class GameStats:
    """A class to track statistics."""
    def __init__(self, game_instance):
        """Initializes statistics."""
        self.settings = game_instance.settings
        
        self.reset_stats()

    def reset_stats(self):
        """initializes statistics that can change during the game."""
        self.doublerocket_left = self.settings.doublerocket_limit
        self.backup_fuel_tank_left = self.settings.backup_fuel_tank_limit
        self.level = 1