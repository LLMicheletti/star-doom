import threading
import random

from .mu_menu import MultiplayerStaticMenu, MultiplayerDynamicMenu, Player1Menu, Player2Menu
from .playermenu import Player1Menu, Player2Menu
from .ship import Ship
from ..projectile import ProjectileGroup
from .mu_settings import MUSettings
from .mu_gamestats import GameStats
from ..explosion import ExplosionGroup
from .mu_scoreboard import ScoreBoard
from ..planet import PlanetGroup

class Multiplayer:
    """A class to manage the alien hunt mode."""

    def __init__(self, game_instance, pygame):
        """Initializes the game's attributes."""
        self.pg = pygame

        #Same attributes of the main game
        self.clock = game_instance.clock
        self.screen = game_instance.screen
        self.window_width = game_instance.window_width
        self.window_height = game_instance.window_height
        self.screen_rect = game_instance.screen_rect

        #Load the background image and center it
        self.bg_image = self.pg.image.load('resources/images/universe_3.bmp')
        self.bg_image = self.pg.transform.scale(self.bg_image, (game_instance.window_width, game_instance.window_height))
        self.bg_image_rect = self.bg_image.get_rect()
        self.bg_image_rect.center = self.screen_rect.center

        #Flags to run the game
        self.game_active = False
        self.game_pause = False
        self.player1menu_active = False
        self.player2menu_active = False
        self.player_1_win = False
        self.player_2_win = False
        self.player_1_hit = False
        self.player_2_hit = False
    
        #Menu
        self.static_menu = MultiplayerStaticMenu(self)
        self.dynamic_menu = MultiplayerDynamicMenu(self)
        self.player1menu = Player1Menu(self)
        self.player2menu = Player2Menu(self)

        #An instance of the main game
        self.main_game_instance = game_instance

        #Settings
        self.settings = MUSettings()

        #Gamestats
        self.stats = GameStats(self)

        #Scoreboard
        self.sb = ScoreBoard(self)

        #Planets
        self.planets = PlanetGroup(self)

        #The projectiles
        self.player_1_projectiles = ProjectileGroup(self, 'resources/images/star_red.bmp')
        self.player_2_projectiles = ProjectileGroup(self, 'resources/images/star_blue.bmp')

        #Explosion animations
        self.explosions = ExplosionGroup(self)

    def _create_planets_group(self):
        """Creates a group of planets randomly placed over the screen."""
        #Empty the group of previous elems
        if self.planets:
            self.planets.clear_all()
        
        self.planets.create_planets()

    def run_game(self):
        """Starts the main loop for the game."""
        while self.main_game_instance.open_multiplayer:
            #Events from keyboard and mouse
            self._check_events()
            
            self._update_screen()

            #Update the display
            self.pg.display.flip()
            self.clock.tick(60) #framerate
            self.dt = self.clock.tick(60) / 1000.0

    def _check_events(self):
        """Events from keyboard and mouse."""
        for event in self.pg.event.get():
            if event.type == self.pg.QUIT:
                self.pg.quit()
            elif event.type == self.pg.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == self.pg.KEYUP:
                self._check_keyup_events(event)
            elif event.type == self.pg.MOUSEBUTTONDOWN and self.game_pause:
                mouse_position = self.pg.mouse.get_pos()
                self._check_dynamic_resume_button(mouse_position)
                self._check_dynamic_exit_button(mouse_position)
            elif (event.type == self.pg.MOUSEBUTTONDOWN and not self.game_active and not 
                  self.player1menu_active and not self.player2menu_active and not self.game_pause):
                mouse_position = self.pg.mouse.get_pos()
                self._check_static_play_button(mouse_position)
                self._check_static_back_button(mouse_position)
            elif (event.type == self.pg.MOUSEBUTTONDOWN and not self.game_active and 
                  self.player1menu_active and not self.player2menu_active):
                mouse_position = self.pg.mouse.get_pos()
                self._check_ship_1_choice(mouse_position)
            elif (event.type == self.pg.MOUSEBUTTONDOWN and not self.game_active and 
                  self.player2menu_active and not self.player1menu_active):
                mouse_position = self.pg.mouse.get_pos()
                self._check_ship_2_choice(mouse_position)

    def _check_keydown_events(self, event):
        """Manages the keypresses."""
        #Open dynamic_menu if the player presses ESC while playing
        if event.key == self.pg.K_ESCAPE and self.game_active: 
            self.game_active = False
            self.game_pause = True
            self.pg.mouse.set_visible(True)
            self.dynamic_menu.open_multiplayer_dynamic_menu()

        #Return to the static menu if the player presses ESC while in the dynamic menu
        elif event.key == self.pg.K_ESCAPE and self.game_pause:
            self.pg.mouse.set_visible(True)
            self.game_pause = False
            self.static_menu.open_multiplayer_static_menu()

        elif (event.key == self.pg.K_ESCAPE and not self.game_active and 
              self.player1menu_active and not self.player2menu_active):
            self.player1menu_active = False
            self.pg.mouse.set_visible(True)
            self.game_pause = False
            self.static_menu.open_multiplayer_static_menu()

        elif (event.key == self.pg.K_ESCAPE and not self.game_active and not
              self.player1menu_active and self.player2menu_active):
            self.player2menu_active = False
            self.player1menu_active = True
            self.player1menu.open_player_1_menu()

        elif (event.key == self.pg.K_ESCAPE and not self.game_active and not 
              self.player1menu_active and not self.player2menu_active and not self.player_1_win and not self.player_2_win):
            self.main_game_instance.open_multiplayer = False
            self.main_game_instance.menu.open_menu()

        if event.key == self.pg.K_d and self.game_active:
            self.player_1_ship.moving_right = True
        if event.key == self.pg.K_a and self.game_active:
            self.player_1_ship.moving_left = True
        if event.key == self.pg.K_w and self.game_active:
            self.player_1_ship.moving_up = True
        if event.key == self.pg.K_s and self.game_active:
            self.player_1_ship.moving_down = True
        if (event.key == self.pg.K_SPACE and self.player_1_ship.moving_right and
              len(self.player_1_projectiles) < self.settings.projectile_allowed and self.game_active):
            if self.stats.player_2_ship_left <= 1:
                double_fire = True
            else:
                double_fire = False
            self._fire_projectile(self.player_1_projectiles, self.player_1_ship, "fire_right", double_fire)
            if self.stats.player_2_ship_left <= 3:
                self._fire_projectile(self.player_1_projectiles, self.player_1_ship, "fire_northeast", double_fire=False)
                self._fire_projectile(self.player_1_projectiles, self.player_1_ship, "fire_southeast", double_fire=False)
            
        if (event.key == self.pg.K_SPACE and self.player_1_ship.moving_left and 
              len(self.player_1_projectiles) < self.settings.projectile_allowed and self.game_active):
            if self.stats.player_2_ship_left <= 1:
                double_fire = True
            else:
                double_fire = False
            self._fire_projectile(self.player_1_projectiles, self.player_1_ship, "fire_left", double_fire)
            if self.stats.player_2_ship_left <= 3:
                self._fire_projectile(self.player_1_projectiles, self.player_1_ship, "fire_northwest", double_fire=False)
                self._fire_projectile(self.player_1_projectiles, self.player_1_ship, "fire_southwest", double_fire=False)

        if (event.key == self.pg.K_SPACE and self.player_1_ship.moving_up and 
              len(self.player_1_projectiles) < self.settings.projectile_allowed and self.game_active):
            if self.stats.player_2_ship_left <= 1:
                double_fire = True
            else:
                double_fire = False
            self._fire_projectile(self.player_1_projectiles, self.player_1_ship, "fire_up", double_fire)
            if self.stats.player_2_ship_left <= 3:
                self._fire_projectile(self.player_1_projectiles, self.player_1_ship, "fire_northwest", double_fire=False)
                self._fire_projectile(self.player_1_projectiles, self.player_1_ship, "fire_northeast", double_fire=False)

        if (event.key == self.pg.K_SPACE and self.player_1_ship.moving_down and
              len(self.player_1_projectiles) < self.settings.projectile_allowed and self.game_active):
            if self.stats.player_2_ship_left <= 1:
                double_fire = True
            else:
                double_fire = False
            self._fire_projectile(self.player_1_projectiles, self.player_1_ship, "fire_down", double_fire)
            if self.stats.player_2_ship_left <= 3:
                self._fire_projectile(self.player_1_projectiles, self.player_1_ship, "fire_southwest", double_fire=False)
                self._fire_projectile(self.player_1_projectiles, self.player_1_ship, "fire_southeast", double_fire=False)

        if event.key == self.pg.K_RIGHT and self.game_active:
            self.player_2_ship.moving_right = True
        if event.key == self.pg.K_LEFT and self.game_active:
            self.player_2_ship.moving_left = True
        if event.key == self.pg.K_UP and self.game_active:
            self.player_2_ship.moving_up = True
        if event.key == self.pg.K_DOWN and self.game_active:
            self.player_2_ship.moving_down = True
        if (event.key == self.pg.K_RETURN and self.player_2_ship.moving_right and
              len(self.player_2_projectiles) < self.settings.projectile_allowed and self.game_active):
            if self.stats.player_1_ship_left <= 1:
                double_fire = True
            else:
                double_fire = False
            self._fire_projectile(self.player_2_projectiles, self.player_2_ship, "fire_right", double_fire)
            if self.stats.player_2_ship_left <= 3:
                self._fire_projectile(self.player_2_projectiles, self.player_2_ship, "fire_northeast", double_fire=False)
                self._fire_projectile(self.player_2_projectiles, self.player_2_ship, "fire_southeast", double_fire=False)

        if (event.key == self.pg.K_RETURN and self.player_2_ship.moving_left and 
              len(self.player_2_projectiles) < self.settings.projectile_allowed and self.game_active):
            if self.stats.player_1_ship_left <= 1:
                double_fire = True
            else:
                double_fire = False
            self._fire_projectile(self.player_2_projectiles, self.player_2_ship, "fire_left", double_fire)
            if self.stats.player_2_ship_left <= 3:
                self._fire_projectile(self.player_2_projectiles, self.player_2_ship, "fire_northwest", double_fire=False)
                self._fire_projectile(self.player_2_projectiles, self.player_2_ship, "fire_southwest", double_fire=False)

        if (event.key == self.pg.K_RETURN and self.player_2_ship.moving_up and 
              len(self.player_2_projectiles) < self.settings.projectile_allowed and self.game_active):
            if self.stats.player_1_ship_left <= 1:
                double_fire = True
            else:
                double_fire = False
            self._fire_projectile(self.player_2_projectiles, self.player_2_ship, "fire_up", double_fire)
            if self.stats.player_2_ship_left <= 3:
                self._fire_projectile(self.player_2_projectiles, self.player_2_ship, "fire_northwest", double_fire=False)
                self._fire_projectile(self.player_2_projectiles, self.player_2_ship, "fire_northeast", double_fire=False)

        if (event.key == self.pg.K_RETURN and self.player_2_ship.moving_down and
              len(self.player_2_projectiles) < self.settings.projectile_allowed and self.game_active):
            if self.stats.player_1_ship_left <= 1:
                double_fire = True
            else:
                double_fire = False
            self._fire_projectile(self.player_2_projectiles, self.player_2_ship, "fire_down", double_fire)
            if self.stats.player_2_ship_left <= 3:
                self._fire_projectile(self.player_2_projectiles, self.player_2_ship, "fire_southwest", double_fire=False)
                self._fire_projectile(self.player_2_projectiles, self.player_2_ship, "fire_southeast", double_fire=False)
    
    def _fire_projectile(self, group, obj, direction_flag, double_fire):
        """Creates a new projectile and adds it to the projectile's group."""
        fire_sound = self.pg.mixer.Sound('resources/sounds/hit_sound.mp3')
        self.pg.mixer.Sound.play(fire_sound)
        new_projectile_1 = group.create_projectile(obj.rect.center)
        if double_fire:
            if direction_flag in ("fire_right", "fire_left"):
                new_projectile_1.y = float(obj.rect.top)
            else:
                new_projectile_1.x = float(obj.rect.left)
        setattr(new_projectile_1, direction_flag, True)
        group.add(new_projectile_1)
        if double_fire:
            new_projectile_2 = group.create_projectile(obj.rect.center)
            setattr(new_projectile_2, direction_flag, True)
            if direction_flag in ("fire_right", "fire_left"):
                new_projectile_2.y = float(obj.rect.bottom)
            else:
                new_projectile_2.x = float(obj.rect.right)
            group.add(new_projectile_2)

    def _check_keyup_events(self, event):
        """Manages key releases."""
        if event.key == self.pg.K_d:
            self.player_1_ship.moving_right = False
        if event.key == self.pg.K_a:
            self.player_1_ship.moving_left = False
        if event.key == self.pg.K_w:
            self.player_1_ship.moving_up = False
        if event.key == self.pg.K_s:
            self.player_1_ship.moving_down = False
        if event.key == self.pg.K_RIGHT:
            self.player_2_ship.moving_right = False
        if event.key == self.pg.K_LEFT:
            self.player_2_ship.moving_left = False
        if event.key == self.pg.K_UP:
            self.player_2_ship.moving_up = False
        if event.key == self.pg.K_DOWN:
            self.player_2_ship.moving_down = False

    def _check_dynamic_resume_button(self, mouse_position):
        """Returns to the game play if the player clicks RESUME"""
        if self.dynamic_menu.resume_button.rect.collidepoint(mouse_position):
            self.pg.mouse.set_visible(False)
            self.game_active = True
            self.game_pause = False

    def _check_dynamic_exit_button(self, mouse_position):
        """Returns to the static mode if the player clicks EXIT"""
        if self.dynamic_menu.exit_button.rect.collidepoint(mouse_position):
            self.pg.mouse.set_visible(True)
            self.game_pause = False
            self.static_menu.open_multiplayer_static_menu()

    def _check_static_play_button(self, mouse_position):
        """Starts the game if the player clicks Play"""
        if self.static_menu.play_button.rect.collidepoint(mouse_position):
            self.player2menu_active = False
            self.player1menu_active = True
            self.stats.reset_stats()
            self.settings.initialize_dynamic_settings()
            self._create_planets_group()
            self.player_1_projectiles.clear_projectiles()
            self.player_2_projectiles.clear_projectiles()
            self.player1menu.open_player_1_menu()

    def _check_static_back_button(self, mouse_position):
        """Returns to the main menu if the player clicks Back"""
        if self.static_menu.back_button.rect.collidepoint(mouse_position):
            self.main_game_instance.open_multiplayer = False
            self.main_game_instance.menu.open_menu()

    def _check_ship_1_choice(self, mouse_position):
        """Confirms the choice and opens Player 2 choosing menu."""
        if self.player1menu.ship_1_button.rect.collidepoint(mouse_position):
            self.player_1_ship = Ship(self, self.player1menu.ship_1_right_image,
                self.player1menu.ship_1_left_image, self.player1menu.ship_1_up_image,
                self.player1menu.ship_1_down_image, self.screen_rect.left)
            
            self.player1menu_active = False
            self.player2menu_active = True
            self.player2menu.open_player_2_menu() 

        elif self.player1menu.ship_2_button.rect.collidepoint(mouse_position):
            self.player_1_ship = Ship(self, self.player1menu.ship_2_right_image,
                self.player1menu.ship_2_left_image, self.player1menu.ship_2_up_image,
                self.player1menu.ship_2_down_image, self.screen_rect.left)
            
            self.player1menu_active = False
            self.player2menu_active = True
            self.player2menu.open_player_2_menu()

        elif self.player1menu.ship_3_button.rect.collidepoint(mouse_position):
            self.player_1_ship = Ship(self, self.player1menu.ship_3_right_image,
                self.player1menu.ship_3_left_image, self.player1menu.ship_3_up_image,
                self.player1menu.ship_3_down_image, self.screen_rect.left) 
        
            self.player1menu_active = False
            self.player2menu_active = True
            self.player2menu.open_player_2_menu()

    def _check_ship_2_choice(self, mouse_position):
        """Confirms the choice and starts the game."""
        if self.player2menu.ship_1_button.rect.collidepoint(mouse_position):
            self.player_2_ship = Ship(self, self.player2menu.ship_1_right_image,
                self.player2menu.ship_1_left_image, self.player2menu.ship_1_up_image,
                self.player2menu.ship_1_down_image, self.screen_rect.right-self.player2menu.ship_1_up_image.get_width()) 
            
            self.player2menu_active = False
            self.game_active = True
            self.pg.mouse.set_visible(False)

        elif self.player2menu.ship_2_button.rect.collidepoint(mouse_position):
            self.player_2_ship = Ship(self, self.player2menu.ship_2_right_image,
                self.player2menu.ship_2_left_image, self.player2menu.ship_2_up_image,
                self.player2menu.ship_2_down_image, self.screen_rect.right-self.player2menu.ship_2_up_image.get_width())
            
            self.player2menu_active = False
            self.game_active = True
            self.pg.mouse.set_visible(False)

        elif self.player2menu.ship_3_button.rect.collidepoint(mouse_position):
            self.player_2_ship = Ship(self, self.player2menu.ship_3_right_image,
                self.player2menu.ship_3_left_image, self.player2menu.ship_3_up_image,
                self.player2menu.ship_3_down_image, self.screen_rect.right-self.player2menu.ship_3_up_image.get_width()) 

            self.player2menu_active = False
            self.game_active = True
            self.pg.mouse.set_visible(False)

    def _update_screen(self):
        """Updates images on the screen."""
        if self.game_active:
            #Move and draw the bg_image to create a dynamic background effect
            self.screen.blit(self.bg_image, self.bg_image_rect)

            if not self.player_1_hit and not self.player_2_hit:
                #Update the two ships' positions
                self.player_1_ship.update(self.dt)
                self.player_2_ship.update(self.dt)
                self._check_ship_planet_collisions()

                #Update projectiles
                self._update_projectiles()

            #Draw the two ships on the screen
            self.player_1_ship.blit_ship()
            self.player_2_ship.blit_ship()

            #Draw explosions
            self.explosions.draw(self.screen)
            self.explosions.update()

            self.planets.draw(self.screen)

            #Draw scoreboard
            self.sb.draw_board()
        
        elif self.player_2_win:
            game_over_surf = self.pg.Surface(self.screen.get_size())
            game_over_surf.fill((0, 0, 0))  # Fill with black
            game_over_surf.set_alpha(128)

            self.sb.player_win_button._prep_text('PLAYER 2 WINS!', 46)
            self.sb.player_win_button.draw_button()

            self.sb.win_instruction_button._prep_text("You overwhelmed your enemy thanks to your superior skills. You saved the stars from their doom!", 16)
            self.sb.win_instruction_button.draw_button()

        elif self.player_1_win:
            game_over_surf = self.pg.Surface(self.screen.get_size())
            game_over_surf.fill((0, 0, 0))  # Fill with black
            game_over_surf.set_alpha(128)

            self.sb.player_win_button._prep_text('PLAYER 1 WINS!', 46)
            self.sb.player_win_button.draw_button()

            self.sb.win_instruction_button._prep_text("You overwhelmed your enemy thanks to your superior skills. You saved the stars from their doom!", 16)
            self.sb.win_instruction_button.draw_button()

    def _check_ship_planet_collisions(self):
        """Manages collisions between rocket and planets."""
        planets = self.pg.sprite.spritecollide(self.player_1_ship, self.planets, False, self.pg.sprite.collide_mask)
        if planets:
            for planet in planets:
                if self.player_1_ship.moving_right:
                    self.player_1_ship.moving_right = False
                if self.player_1_ship.moving_left:
                    self.player_1_ship.moving_left = False
                if self.player_1_ship.moving_up:
                    self.player_1_ship.moving_up = False
                if self.player_1_ship.moving_down:
                    self.player_1_ship.moving_down = False

        planets = self.pg.sprite.spritecollide(self.player_2_ship, self.planets, False, self.pg.sprite.collide_mask)
        if planets:
            for planet in planets:
                if self.player_2_ship.moving_right:
                    self.player_2_ship.moving_right = False
                if self.player_2_ship.moving_left:
                    self.player_2_ship.moving_left = False
                if self.player_2_ship.moving_up:
                    self.player_2_ship.moving_up = False
                if self.player_2_ship.moving_down:
                    self.player_2_ship.moving_down = False

    def _update_projectiles(self):
        """Updates the position, gets rid of the old ones and draws projectiles."""
        #Update projectile's position
        self.player_1_projectiles.update(self.dt, self.settings.projectile_speed)
        self.player_2_projectiles.update(self.dt, self.settings.projectile_speed)

        #Remove projectiles out of the screen from the Group
        for projectile in self.player_1_projectiles:
            if (projectile.rect.bottom <= 0 or projectile.rect.left >= self.screen_rect.width or
                projectile.rect.top >= self.screen_rect.height or projectile.rect.right <= 0):
                self.player_1_projectiles.remove_projectile(projectile)
            else:
                self.screen.blit(projectile.image, projectile.rect)
        for projectile in self.player_2_projectiles:
            if (projectile.rect.bottom <= 0 or projectile.rect.left >= self.screen_rect.width or
                projectile.rect.top >= self.screen_rect.height or projectile.rect.right <= 0):
                self.player_2_projectiles.remove_projectile(projectile)
            else:
                self.screen.blit(projectile.image, projectile.rect)

        #Check for collisions
        try:
            if not player_1_collision_thread.is_alive():
                player_1_collision = self.pg.sprite.spritecollide(self.player_1_ship, self.player_2_projectiles, True)
                if player_1_collision:
                    player_1_collision_thread = threading.Thread(target=self._manage_player_1_ship_collisions)
                    player_1_collision_thread.daemon = True
                    player_1_collision_thread.start()
        except UnboundLocalError:
            player_1_collision = self.pg.sprite.spritecollide(self.player_1_ship, self.player_2_projectiles, True)
            if player_1_collision:
                player_1_collision_thread = threading.Thread(target=self._manage_player_1_ship_collisions)
                player_1_collision_thread.daemon = True
                player_1_collision_thread.start()
        else:
            pass

        try:
            if not player_2_collision_thread.is_alive():
                player_2_collision = self.pg.sprite.spritecollide(self.player_2_ship, self.player_1_projectiles, True)
                if player_2_collision:
                    player_2_collision_thread = threading.Thread(target=self._manage_player_2_ship_collisions)
                    player_2_collision_thread.daemon = True
                    player_2_collision_thread.start()
        except UnboundLocalError:
            player_2_collision = self.pg.sprite.spritecollide(self.player_2_ship, self.player_1_projectiles, True)
            if player_2_collision:
                player_2_collision_thread = threading.Thread(target=self._manage_player_2_ship_collisions)
                player_2_collision_thread.daemon = True
                player_2_collision_thread.start()
        else:
            pass

        if not self.stats.player_1_ship_left:
            player_2_win_thread = threading.Thread(target=self._manage_player_2_win)
            player_2_win_thread.daemon = True
            player_2_win_thread.start()

        if not self.stats.player_2_ship_left:
            player_1_win_thread = threading.Thread(target=self._manage_player_1_win)
            player_1_win_thread.daemon = True
            player_1_win_thread.start()

        self._check_projectile_planet_collisions(self.player_1_projectiles)
        self._check_projectile_planet_collisions(self.player_2_projectiles)

    def _manage_player_1_ship_collisions(self):
        """Manages the Player 1 being hit by a projectile fired by Player 2."""
        self.player_1_hit = True
        explosion_sound = self.pg.mixer.Sound('resources/sounds/explosion_sound.mp3')
        self.pg.mixer.Sound.play(explosion_sound)
        explosion = self.explosions.create_explosion(self.player_1_ship.rect.center)
        self.explosions.add(explosion)
            
        #Decrement Player 1 ships left
        self.stats.player_1_ship_left -= 1

        while self.explosions:
            self.pg.time.wait(100)
            
        if not self.explosions:
            self.settings.increase_difficulty()
            self.player_1_hit = False
            self.settings.planet_counter = 0
            self._create_planets_group()
            self.player_1_projectiles.clear_projectiles()
            self.player_2_projectiles.clear_projectiles()
            self.player_1_ship.place_initial(self.screen_rect.left)
            self.player_2_ship.place_initial(self.screen_rect.right-self.player2menu.ship_2_up_image.get_width())
                
    def _manage_player_2_ship_collisions(self):
        """Manages the Player 2 being hit by a projectile fired by Player 1."""
        self.player_2_hit = True
        explosion_sound = self.pg.mixer.Sound('resources/sounds/explosion_sound.mp3')
        self.pg.mixer.Sound.play(explosion_sound)
        explosion = self.explosions.create_explosion(self.player_2_ship.rect.center)
        self.explosions.add(explosion)
            
        #Decrement Player 2 ships left
        self.stats.player_2_ship_left -= 1

        while self.explosions:
            self.pg.time.wait(100)
            
        if not self.explosions:
            self.settings.increase_difficulty()
            self.player_2_hit = False
            self.settings.planet_counter = 0
            self._create_planets_group()
            self.player_1_projectiles.clear_projectiles()
            self.player_2_projectiles.clear_projectiles()
            self.player_1_ship.place_initial(self.screen_rect.left)
            self.player_2_ship.place_initial(self.screen_rect.right-self.player2menu.ship_2_up_image.get_width())

    def _check_projectile_planet_collisions(self, group):
        """Deletes the projectile if it hits a planet"""
        projectiles = self.pg.sprite.groupcollide(group, self.planets, False, False)
        for projectile in projectiles:
            group.remove_projectile(projectile)

    def _manage_player_2_win(self):
        """Handles the end of the game in favour of player 2. Updates the game state and flags for main thread."""
        print("Game over triggered in thread.")
        
        # Set the game as inactive
        self.game_active = False
        self.player_2_win = True
        
        # Play the game over music (make sure this is safe to call from a thread)
        self.pg.mixer.music.load('resources/sounds/revelation_and_awe.mp3')
        self.pg.mixer.music.play()

        # Flag to signal that the game is over
        print("Game over music started, waiting for it to finish.")
        
        # Wait for the music to finish (use a timer or sleep instead of self.pg's event loop)
        while self.pg.mixer.music.get_busy():
            self.pg.time.wait(100)  # Sleep for short periods to avoid locking the thread

        print("Game over music finished.")

        if not self.pg.mixer.music.get_busy():
            # Mark that the game over process is complete
            self.player_2_win = False

            self.pg.mouse.set_visible(True)
            self.main_game_instance.open_multiplayer = False
            self.main_game_instance.menu.open_menu()

    def _manage_player_1_win(self):
        """Handles the end of the game in favour of player 2. Updates the game state and flags for main thread."""
        print("Game over triggered in thread.")
        
        # Set the game as inactive
        self.game_active = False
        self.player_1_win = True
        
        # Play the game over music (make sure this is safe to call from a thread)
        self.pg.mixer.music.load('resources/sounds/revelation_and_awe.mp3')
        self.pg.mixer.music.play()

        # Flag to signal that the game is over
        print("Game over music started, waiting for it to finish.")
        
        # Wait for the music to finish (use a timer or sleep instead of self.pg's event loop)
        while self.pg.mixer.music.get_busy():
            self.pg.time.wait(100)  # Sleep for short periods to avoid locking the thread

        print("Game over music finished.")

        if not self.pg.mixer.music.get_busy():
            # Mark that the game over process is complete
            self.player_1_win = False

            self.pg.mouse.set_visible(True)
            self.main_game_instance.open_multiplayer = False
            self.main_game_instance.menu.open_menu()