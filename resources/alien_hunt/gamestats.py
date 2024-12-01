from pathlib import Path
import json

class GameStats:
    """A class to track statistics."""
    def __init__(self, game_instance):
        """Initializes statistics."""
        self.settings = game_instance.settings
        
        self.reset_stats()

    def reset_stats(self):
        """initializes statistics that can change during the game."""
        self.rocket_left = self.settings.rocket_limit
        self.score = 0
        self.level = 1
        path = Path('resources/alien_hunt/record.json')
        try:
            content = path.read_text()
        except FileNotFoundError:
            content = str(0)
        self.record = json.loads(content)
