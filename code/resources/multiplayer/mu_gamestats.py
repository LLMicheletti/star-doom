class GameStats:
    """A class to track statistics."""
    def __init__(self, game_instance):
        """Initializes statistics."""
        self.settings = game_instance.settings
        
        self.reset_stats()

    def reset_stats(self):
        """initializes statistics that can change during the game."""
        self.player_1_ship_left = self.settings.ship_limit
        self.player_2_ship_left = self.settings.ship_limit
