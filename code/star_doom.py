import pygame as pg
import sys

import resources as rs

class StarDoom:
    """The main class that manages the game."""

    def __init__(self, pg):
        """Initializes the game."""
        self.pg = pg
        self.pg.init()

        #Clock
        self.clock = pg.time.Clock()
        
        #Screen mode
        self.screen = pg.display.set_mode()
        self.window_width, self.window_height = self.screen.get_size()
        self.screen_rect = self.screen.get_rect()

        self.pg.display.set_caption("*Star Doom*")

        #Load the background image and center it
        self.bg_image = pg.image.load('resources/images/universe_bg.bmp')

        self.bg_image = pg.transform.scale(self.bg_image, (self.window_width, self.window_height))
        self.bg_image_rect = self.bg_image.get_rect()
        self.bg_image_rect.center = self.screen_rect.center

        #Menu
        #Start the main menu
        self.menu = rs.menu.Menu(self)
        self.menu.open_menu()

        #Flags to open the modes
        self.open_alien_hunt = False
        self.open_sun_escape = False
        self.open_multiplayer = False

        self.pg.mixer.init()

        self.alien_hunt_mode = rs.AlienHunt(self, self.pg)
        self.sun_escape_mode = rs.SunEscape(self, self.pg)
        self.multiplayer_mode = rs.Multiplayer(self, self.pg)

    def run_game(self):
        """Starts the main loop for the game."""
        while True:
            #Events from keyboard and mouse
            self._check_events()
            
            if self.open_alien_hunt:
                self.alien_hunt_mode.static_menu.open_alien_hunt_static_menu()
                self.alien_hunt_mode.run_game()
            elif self.open_sun_escape:
                self.sun_escape_mode.static_menu.open_sun_escape_static_menu()
                self.sun_escape_mode.run_game()
            elif self.open_multiplayer:
                self.multiplayer_mode.static_menu.open_multiplayer_static_menu()
                self.multiplayer_mode.run_game()

            pg.display.flip()
            self.clock.tick(60) #framerate

    def _check_events(self):
        """Events from keyboard and mouse."""
        for event in self.pg.event.get():
            if event.type == self.pg.QUIT:
                self.pg.quit()
                sys.exit()
            elif event.type == self.pg.KEYDOWN:
                if event.key == self.pg.K_ESCAPE:
                    self.pg.quit()
                    sys.exit()
            elif event.type == self.pg.MOUSEBUTTONDOWN and not self.open_alien_hunt and not self.open_sun_escape and not self.open_multiplayer:
                mouse_position = self.pg.mouse.get_pos()
                self._choose_mode(mouse_position)

    def _choose_mode(self, mouse_position):
        """Manages the pressing of the mode buttons."""
        if self.menu.alien_hunt_button.rect.collidepoint(mouse_position):
            self.open_alien_hunt = True
        elif self.menu.sun_escape_button.rect.collidepoint(mouse_position):
            self.open_sun_escape = True
        elif self.menu.multiplayer_button.rect.collidepoint(mouse_position):
            self.open_multiplayer = True

if __name__ == '__main__':
    #Instance of the game
    sd = StarDoom(pg=pg)
    sd.run_game()