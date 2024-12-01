from pygame.sprite import Group
from .ship import Ship
from ..button import Button

class ScoreBoard:
    """A class to report scoring information."""
    def __init__(self, game_instance):
        """Intializes scorekeeping attributes."""
        self.game_instance = game_instance
        self.screen = game_instance.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = game_instance.settings
        self.stats = game_instance.stats

        #Button for player win
        self.player_win_button = Button(self, 550, 150, 'yellow', 'green')
        self.player_win_button.rect.center = self.screen_rect.center

        #winning Instruction button
        self.win_instruction_button = Button(self.game_instance, 1600, 60, 'white', 'red')
        self.win_instruction_button.rect.midbottom = self.game_instance.screen_rect.midbottom
        self.win_instruction_button.rect.y = self.game_instance.screen_rect.height*3/4

    def draw_board(self):
        """Draws the buttons of the scoreboard."""
        #Player 1 ships left
        self.player_1_ships = Group()
        for player_1_number in range(self.stats.player_1_ship_left):
            player_1_ship = Ship(self.game_instance, self.game_instance.player_1_ship.right_image,
                self.game_instance.player_1_ship.left_image, self.game_instance.player_1_ship.up_image,
                self.game_instance.player_1_ship.down_image, 0)
            player_1_ship.image = self.game_instance.player_1_ship.up_image
            player_1_ship.rect = player_1_ship.image.get_rect()
            player_1_ship.rect.x = 20 + player_1_number * player_1_ship.rect.width
            self.player_1_ships.add(player_1_ship)
            self.player_1_ships.draw(self.screen)

        #Player 2 ships left
        self.player_2_ships = Group()
        for player_2_number in range(self.stats.player_2_ship_left):
            player_2_ship = Ship(self.game_instance, self.game_instance.player_2_ship.right_image,
                self.game_instance.player_2_ship.left_image, self.game_instance.player_2_ship.up_image,
                self.game_instance.player_2_ship.down_image, 0)
            player_2_ship.image = self.game_instance.player_2_ship.up_image
            player_2_ship.rect = player_2_ship.image.get_rect()
            player_2_ship.rect.x = self.screen_rect.width - player_2_ship.rect.width - player_2_number * player_2_ship.rect.width
            self.player_2_ships.add(player_2_ship)
            self.player_2_ships.draw(self.screen)