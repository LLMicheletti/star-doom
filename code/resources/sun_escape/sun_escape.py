import random
import threading
import numpy as np


from .se_menu import SunEscapeStaticMenu, SunEscapeDynamicMenu
from .doublerocket import Doublerocket
from .se_settings import SESettings
from .se_gamestats import GameStats
from .sun import Sun
from .wave import WaveGroup
from .fuel_tank import FuelTank
from ..explosion import ExplosionGroup
from .se_scoreboard import ScoreBoard

class SunEscape:
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
        self.bg_image = self.pg.image.load('resources/images/birthofstars.webp')
        self.bg_image = self.pg.transform.scale(self.bg_image, (self.window_width, self.window_height))
        self.bg_image_rect = self.bg_image.get_rect()
        self.bg_image_rect.center= self.screen_rect.center

        #A flag to run the game
        self.game_active = False

        #A flag to temporarely pause the game
        self.game_pause = False

        #A flag to manage when user wins
        self.game_win = False

        #A flag to manage game_over status
        self.game_over = False

        #Set up a TIMER_EVENT
        self.timer_event = self.pg.USEREVENT + 1
        self.pg.time.set_timer(self.timer_event, 1000)

        #Settings
        self.settings = SESettings()

        #Game statistics
        self.stats = GameStats(self)

        #Doublerocket
        self.doublerocket = Doublerocket(self)

        #Sun
        self.sun = Sun(self)

        #Waves
        self.waves = WaveGroup(self)
        self.doublerocket_waves = WaveGroup(self)

        #Fuel tanks
        self.fuel_tanks = self.pg.sprite.Group()

        #Menu
        self.static_menu = SunEscapeStaticMenu(self)
        self.dynamic_menu = SunEscapeDynamicMenu(self)

        #An instance of the main game
        self.main_game_instance = game_instance

        #Explosion animations
        self.explosions = ExplosionGroup(self)

        #Scoreboard
        self.sb = ScoreBoard(self)

    def run_game(self):
        """Starts the main loop for the game."""
        while self.main_game_instance.open_sun_escape:
            #Events from keyboard and mouse
            self._check_events()

            self._update_screen()

            #Update the display
            self.pg.display.flip()
            #self.clock.tick_busy_loop(60) #framerate

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
            elif event.type == self.pg.MOUSEBUTTONDOWN and not self.game_active and not self.game_pause:
                mouse_position = self.pg.mouse.get_pos()
                self._check_static_play_button(mouse_position)
                self._check_static_back_button(mouse_position)
            elif event.type == self.timer_event and self.game_active:
                self.settings.fuel_counter -= 1
                self.settings.wave_counter -= 1
                if self.settings.collision_counter < self.settings.collision_pause:
                    self.settings.collision_counter += 1
                self._check_doublerocket_fuel_level()

    def _check_keydown_events(self, event):
        """Manages the keypresses."""
        #Open dynamic_menu if the player presses ESC while playing
        if event.key == self.pg.K_ESCAPE and self.game_active: 
            self.game_active = False
            self.game_pause = True
            self.pg.mouse.set_visible(True)
            self.dynamic_menu.open_sun_escape_dynamic_menu()

        #Return to the static menu if the player presses ESC while in the dynamic menu
        elif event.key == self.pg.K_ESCAPE and self.game_pause:
            self.pg.mouse.set_visible(True)
            self.game_pause = False
            self.static_menu.open_sun_escape_static_menu()

        #Return to the Space Pursuit menu if the player presses ESC while in the static menu
        elif event.key == self.pg.K_ESCAPE and not self.game_active and not self.game_over and not self.game_win:
            self.main_game_instance.open_sun_escape = False
            self.main_game_instance.menu.open_menu()

        elif event.key == self.pg.K_d:
            self.doublerocket.moving_right = True
        elif event.key == self.pg.K_a:
            self.doublerocket.moving_left = True
        elif event.key == self.pg.K_w:
            self.doublerocket.moving_up = True
        elif event.key == self.pg.K_s:
            self.doublerocket.moving_down = True
        elif (event.key == self.pg.K_SPACE and self.doublerocket.moving_right and
              len(self.doublerocket_waves) < self.settings.doublerocket_waves_allowed):
            self._fire_wave()

    def _fire_wave(self):
        """Fires a right wave from the doublerocket at level 4"""
        if self.stats.level == 4:
            right_wave = self.doublerocket_waves.create_right_wave("yellow")
            self.doublerocket_waves.add(right_wave)

    def _check_keyup_events(self, event):
        """Manages key releases."""
        if event.key == self.pg.K_d:
            self.doublerocket.moving_right = False
        elif event.key == self.pg.K_a:
            self.doublerocket.moving_left = False
        elif event.key == self.pg.K_w:
            self.doublerocket.moving_up = False
        elif event.key == self.pg.K_s:
            self.doublerocket.moving_down = False

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
            self.static_menu.open_sun_escape_static_menu()

    def _check_static_play_button(self, mouse_position):
        """Starts the game if the player clicks Play"""
        if self.static_menu.play_button.rect.collidepoint(mouse_position):
            self.pg.mouse.set_visible(False)
            self.doublerocket.place_initial()
            self.fuel_tanks.empty()
            self.stats.reset_stats()
            self.settings.initialize_dynamic_settings()
            self.waves.empty()
            self.game_active = True

    def _check_static_back_button(self, mouse_position):
        """Returns to the main menu if the player clicks Back"""
        if self.static_menu.back_button.rect.collidepoint(mouse_position):
            self.main_game_instance.open_sun_escape = False
            self.main_game_instance.menu.open_menu()
            #self.main_game_instance.run_game()

    def _update_screen(self):
        """Updates images on the screen."""
        if self.game_active:
            #Move and draw the bg_image to create a dynamic background effect
            self.screen.blit(self.bg_image, self.bg_image_rect)

            self._update_doublerocket()

            self._update_sun()
            
            self._update_fuel_tank()

            self._update_waves()

            #Draw explosions
            self.explosions.draw(self.screen)
            self.explosions.update()

            self.sb.draw_board()

            #self._check_level()

        elif self.game_over:
            game_over_surf = self.pg.Surface(self.screen.get_size())
            game_over_surf.fill((0, 0, 0))  # Fill with black
            game_over_surf.set_alpha(128)

            self.sb.game_over_button._prep_text('GAME OVER!', 56)
            self.sb.game_over_button.draw_button()
        
        elif self.game_win:
            game_win_surf = self.pg.Surface(self.screen.get_size())
            game_win_surf.fill((0, 0, 0))  # Fill with black
            game_win_surf.set_alpha(128)

            #Draw game victory button
            self.sb.game_win_button._prep_text('YOU WIN!', 56)
            self.sb.game_win_button.draw_button()

            #Draw winning Instruction button
            self.sb.win_instruction_button._prep_text(
                'You earned the right to engrave your name among the bravest.', 16)
            self.sb.win_instruction_button.draw_button()

    def _update_doublerocket(self): 
        """Takes care of all methods concerning the doublerocket in the game"""
        self.doublerocket.update(self.dt)
        #self._check_doublerocket_fuel_level()
        self._check_doublerocket_sun_collisions()
        self.doublerocket.blit_doublerocket()

    def _check_doublerocket_fuel_level(self):
        """Updates the fuel level of the doublerocket and removes a backup fuel tank if necessary."""
        self.settings.doublerocket_fuel -= self.settings.fuel_leak
        
        if self.settings.doublerocket_fuel <= 0:
            self._remove_backup_fuel_tank()
            self.settings.doublerocket_fuel = 50

    def _check_doublerocket_sun_collisions(self):
        """Removes a backup fuel tank in case the rocket hits the star."""
        if self.doublerocket.rect.colliderect(self.sun):
            game_over_thread = threading.Thread(target=self._manage_game_over)
            game_over_thread.daemon = True
            game_over_thread.start()

    def _update_sun(self): 
        """Takes care of all methods concerning the sun in the game"""
        self.sun.update(self.dt)
        if self.stats.level == 4:
            self._check_edges()
        self.sun.blit_sun()

    def _check_edges(self):
        """Changes black hole direction if it hits an edge."""
        if self.sun.rect.bottom >= self.screen_rect.bottom or self.sun.rect.top <= self.screen_rect.top:
            self.settings.black_hole_direction *= -1

    def _update_fuel_tank(self):
        """Takes care of all methods concerning the fuel tanks in the game"""
        if self._check_level:
            self._spawn_fuel_tank()
        try:
            self.fuel_tanks.update()
        except AttributeError:
            pass
        else:
            self._check_doublerocket_fuel_tank_collisions()

    def _check_doublerocket_fuel_tank_collisions(self):
        """Refills the doublerocket fuel tank."""
        fuel_tank = self.pg.sprite.spritecollideany(self.doublerocket, self.fuel_tanks)
        if fuel_tank:
            self.fuel_tanks.remove(fuel_tank)
            self.settings.doublerocket_fuel += 25

    def _update_waves(self):
        """Takes care of all methods concerning the waves in the game"""
        if self._check_level():
            self._generate_wave()
        for wave in self.waves:
            self.waves.update(self.dt, wave)
            if wave.point_0[0] < 0:
                self.waves.remove(wave)
            else:
                self.waves._draw(wave)

            try:
                self._check_wave_doublerocket_collisions(wave)
            except UnboundLocalError:
                pass

            try:
                self._check_wave_fuel_tank_collisions(wave)
            except UnboundLocalError:
                pass
        
        for dr_wave in self.doublerocket_waves:
            self.doublerocket_waves.update(self.dt, dr_wave)
            if dr_wave.point_0[0] > self.screen_rect.width:
                self.doublerocket_waves.remove(dr_wave)
            else:
                self.doublerocket_waves._draw(dr_wave)

            try:
                self._check_wave_fuel_tank_collisions(dr_wave)
            except UnboundLocalError:
                pass

            try:
                self._check_doublerocket_waves_black_hole_collisions(dr_wave)
            except UnboundLocalError:
                pass

            try:
                self._check_doublerocket_waves_other_waves_collisions(dr_wave)
            except UnboundLocalError:
                pass

    def _check_wave_doublerocket_collisions(self, wave):
        """Manages collisions between the doublerocket and a wave."""
        #bezier_points = wave._bezier_curve()
        wave_points = wave.points.astype(np.int32).tolist()
        num_points = len(wave_points)
        for i in range(0, num_points - 1, 2):
            point1 = wave_points[i]
            point2 = wave_points[i + 1]
            if self.doublerocket.rect.clipline((point1[0], point1[1]), (point2[0], point2[1])):
                clipped_line = True  # Collision detected
                break
        if (clipped_line and self.settings.collision_counter == self.settings.collision_pause):
            explosion_sound = self.pg.mixer.Sound('resources/sounds/explosion_sound.mp3')
            self.pg.mixer.Sound.play(explosion_sound)
            explosion = self.explosions.create_explosion(self.doublerocket.rect.center)
            self.explosions.add(explosion)
            self._remove_backup_fuel_tank()
            self.settings.collision_counter = 0

    def _check_wave_fuel_tank_collisions(self, wave):
        """Removes the spawned fuel tank if hit by the wave."""
        clipped_line = False
        #bezier_points = wave._bezier_curve()
        wave_points = wave.points.astype(np.int32).tolist()
        num_points = len(wave_points)
        for i in range(0, num_points - 1, 2):
            point1 = wave_points[i]
            point2 = wave_points[i + 1]
            for fuel_tank in self.fuel_tanks:
                if fuel_tank.rect.clipline(point1, point2):
                    clipped_line = True  # Collision detected
                    break
        if clipped_line:
            explosion_sound = self.pg.mixer.Sound('resources/sounds/explosion_sound.mp3')
            self.pg.mixer.Sound.play(explosion_sound)
            explosion = self.explosions.create_explosion(fuel_tank.rect.center)
            self.explosions.add(explosion)
            self.fuel_tanks.remove(fuel_tank)

    def _check_doublerocket_waves_black_hole_collisions(self, dr_wave):
        """Reduces the life of the black hole if hit by a doublerocket wave."""
        wave_points = dr_wave.points.astype(np.int32).tolist()
        num_points = len(wave_points)
        for i in range(0, num_points - 1, 2):
            point1 = wave_points[i]
            point2 = wave_points[i + 1]
            if self.sun.rect.clipline((point1[0], point1[1]), (point2[0], point2[1])):
                clipped_line = True  # Collision detected
                break
        if clipped_line:
            self.sun.black_hole_hit()
            self.settings.black_hole_life -= 50
            self.doublerocket_waves.remove(dr_wave)
            if self.settings.black_hole_life == 0:
                game_win_thread = threading.Thread(target=self._manage_game_win)
                game_win_thread.daemon = True
                game_win_thread.start()

    def _check_doublerocket_waves_other_waves_collisions(self, dr_wave):
        wave_points = dr_wave.points.astype(np.int32).tolist()
        num_points = len(wave_points)
        for i in range(0, num_points - 1, 2):
            point1 = wave_points[i]
            point2 = wave_points[i + 1]
            for wave in self.waves:
                if wave.rect.clipline((point1[0], point1[1]), (point2[0], point2[1])):
                    clipped_line = True  # Collision detected
                    break
        if clipped_line:
            self.doublerocket_waves.remove(dr_wave)

    def _remove_backup_fuel_tank(self):
        """Removes a backup fuel tank"""
        self.stats.backup_fuel_tank_left -= 1
        if not self.stats.backup_fuel_tank_left:
            game_over_thread = threading.Thread(target=self._manage_game_over)
            game_over_thread.daemon = True
            game_over_thread.start()

    def _spawn_fuel_tank(self):
        """Makes a fuel tank spawn when generating a new wave"""
        if self.settings.fuel_counter == 0:
            if self.stats.level <= 3:
                fuel_tank = FuelTank(self)
                fuel_tank.rect.centerx = self.screen_rect.centerx
                self.fuel_tanks.add(fuel_tank)
            elif self.stats.level == 4:
                #Make a fuel tank spawn randomly at the left or right side of the screen
                number = random.randrange(1, 3)
                if number == 1:
                    fuel_tank = FuelTank(self)
                    fuel_tank.rect.centerx = 70
                    self.fuel_tanks.add(fuel_tank)
                elif number == 2:
                    fuel_tank = FuelTank(self)
                    fuel_tank.rect.centerx = self.screen_rect.centerx
                    self.fuel_tanks.add(fuel_tank)
            
            self.settings.fuel_counter = self.settings.wave_pause

    def _generate_wave(self):
        """Creates a new wave and draws it."""
        if self.settings.wave_counter == 0:
            if self.stats.level == 1:
                wave = self.waves.create_sin_wave("yellow")	
                self.waves.add(wave)

            elif self.stats.level == 2:
                wave = self.waves.create_long_wave("red")
                self.waves.add(wave)

            elif self.stats.level == 3:
                up_wave = self.waves.create_up_wave("blue")
                down_wave = self.waves.create_down_wave("blue")
                self.waves.add(up_wave, down_wave)

            elif self.stats.level == 4:
                number = random.randrange(0, 3)
                if number == 0:
                    up_wave = self.waves.create_up_wave("purple")
                    self.waves.add(up_wave)
                elif number == 1:
                    down_wave = self.waves.create_down_wave("purple")
                    self.waves.add(down_wave)
                elif number == 2:
                    long_wave = self.waves.create_long_wave("black")
                    self.waves.add(long_wave)
                elif number == 3:
                    sin_wave = self.waves.create_sin_wave("black")
                    self.waves.add(sin_wave)
                
                number = random.randrange(0, 3)
                if number == 0:
                    up_wave = self.waves.create_up_wave("purple")
                    self.waves.add(up_wave)
                elif number == 1:
                    down_wave = self.waves.create_down_wave("purple")
                    self.waves.add(down_wave)
                elif number == 2:
                    long_wave = self.waves.create_long_wave("black")
                    self.waves.add(long_wave)
                elif number == 3:
                    sin_wave = self.waves.create_sin_wave("black")
                    self.waves.add(sin_wave)
                    
            self.settings.wave_counter = self.settings.wave_pause
            self.settings.num_waves += 1

    def _check_level(self):
        """Increases the level after a certain number of waves emitted."""
        if ((self.stats.level == 1 and self.settings.num_waves < self.settings.level_1_waves) 
            or (self.stats.level == 2 and self.settings.num_waves < self.settings.level_2_waves)
            or (self.stats.level == 3 and self.settings.num_waves < self.settings.level_3_waves)
            or (self.stats.level == 4 and self.settings.num_waves < self.settings.level_4_waves)):
            return True
        elif self.stats.level == 5:
            game_over_thread = threading.Thread(target=self._manage_game_over)
            game_over_thread.daemon = True
            game_over_thread.start()
        elif self.settings.wave_counter == 0:
            self.settings.num_waves = 0
            self.fuel_tanks.empty()
            self.waves.empty()
            #self.pg.time.wait(100)
            self.stats.level += 1
            self.settings.increase_difficulty()
            self.settings.wave_counter = self.settings.wave_pause
            self.settings.fuel_counter = self.settings.wave_pause
            return False

    def _manage_game_win(self):
        """Handles the (positive) end of the game. Updates the game state and flags for main thread."""       
        # Set the game as inactive
        self.game_active = False
        self.game_win = True

        #Play song
        self.pg.mixer.music.load('resources/sounds/what_happens_now.mp3')
        self.pg.mixer.music.play()

        # Wait for the music to finish (use a timer or sleep instead of self.pg's event loop)
        while self.pg.mixer.music.get_busy():
            self.pg.time.wait(100)  # Sleep for short periods to avoid locking the thread

        if not self.pg.mixer.music.get_busy():
            # Mark that the game over process is complete
            self.game_win = False

            self.pg.mouse.set_visible(True)
            self.main_game_instance.open_sun_escape = False
            self.main_game_instance.menu.open_menu()

    def _manage_game_over(self):
        """Handles the end of the game. Updates the game state and flags for main thread."""
        # Set the game as inactive
        self.game_active = False
        self.game_over = True
        
        # Play the game over music (make sure this is safe to call from a thread)
        self.pg.mixer.music.load('resources/sounds/do_not_go_gentle_into_that_good_night.mp3')
        self.pg.mixer.music.play()

        # Wait for the music to finish (use a timer or sleep instead of self.pg's event loop)
        while self.pg.mixer.music.get_busy():
            self.pg.time.wait(100)  # Sleep for short periods to avoid locking the thread

        if not self.pg.mixer.music.get_busy():
            # Mark that the game over process is complete
            self.game_over = False

            self.pg.mouse.set_visible(True)
            self.main_game_instance.open_sun_escape = False
            self.main_game_instance.menu.open_menu()