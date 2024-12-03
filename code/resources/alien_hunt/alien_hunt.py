import sys
from pathlib import Path
import json
import random
import threading

from .ah_menu import AlienHuntStaticMenu, AlienHuntDynamicMenu
from .rocket import Rocket
from ..projectile import ProjectileGroup
from .ufo import RedUfoFleet, GreenUfoFleet, BlueUfoFleet
from .ah_settings import AHSettings
from .gamestats import GameStats
from .ah_scoreboard import ScoreBoard
from ..explosion import ExplosionGroup
from ..planet import PlanetGroup

class AlienHunt:
    """
    A class to manage the alien hunt mode
    """

    def __init__(self, game_instance, pg):
        """
        Initializes the game's attributes
        """
        self.pg = pg

        #Same attributes of the main game
        self.clock = game_instance.clock
        self.screen = game_instance.screen
        self.screen_rect = game_instance.screen_rect

        #Load the background image and center it
        self.bg_image = self.pg.image.load('resources/images/pia23865-2.webp')
        self.bg_image = self.pg.transform.scale(
            self.bg_image, (game_instance.window_width, game_instance.window_height))
        self.bg_image_rect = self.bg_image.get_rect()
        self.bg_image_rect.center = self.screen_rect.center

        #Settings
        self.settings = AHSettings()

        #Game statistics
        self.stats = GameStats(self)

        #Scoreboard
        self.sb = ScoreBoard(self)

        #An instance of the main game
        self.main_game_instance = game_instance

        #The rocket
        self.rocket = Rocket(self)

        #The projectiles
        self.rocket_projectiles = ProjectileGroup(self, 'resources/images/star_red.bmp')
        self.ufo_projectiles = ProjectileGroup(self, 'resources/images/star_blue.bmp')

        #Planets
        self.planets = PlanetGroup(self)

        #Ufos
        self.red_ufos = RedUfoFleet(self)
        self.green_ufos = GreenUfoFleet(self)
        self.blue_ufos = BlueUfoFleet(self)
        
        #Set up a TIMER_EVENT
        self.timer_event = self.pg.USEREVENT + 1
        self.pg.time.set_timer(self.timer_event, 1000)

        #A flag to run the game
        self.game_active = False

        #A flag to temporarely pause the game
        self.game_pause = False

        #A flag for game over
        self.game_over = False

        #A flag to make certain events happen only when timer clocks
        self.timer_clocked = False
    
        #Menu
        self.static_menu = AlienHuntStaticMenu(self)
        self.dynamic_menu = AlienHuntDynamicMenu(self)

        #Explosion animations
        self.explosions = ExplosionGroup(self)

    def _create_planets_group(self):
        """Creates a group of planets randomly placed over the screen."""
        #Empty the group of previous elems
        if self.planets:
            self.planets.clear_all()
    
        self.planets.create_planets()

    def _create_fleet(self):
        """Creates a fleet of ufos."""
        #Empty the groups of the previous elems
        if self.red_ufos:
            self.red_ufos.clear_all()
        if self.green_ufos:
            self.green_ufos.clear_all()
        if self.blue_ufos:
            self.blue_ufos.clear_all()

        self.red_ufos.create_fleet(self.planets.positions, self.planets.sizes)

        self.green_ufos.create_fleet(self.planets.positions, self.planets.sizes)

        self.blue_ufos.create_fleet(self.planets.positions, self.planets.sizes)

    def run_game(self):
        """Starts the main loop for the game."""
        while self.main_game_instance.open_alien_hunt:
            #Events from keyboard and mouse
            self._check_events()
            
            self._update_screen()
            
            #Update display
            self.pg.display.flip()

            self.clock.tick(60) #framerate
            self.dt = self.clock.tick(60) / 1000.0

    def _check_events(self):
        """Events from keyboard and mouse."""
        for event in self.pg.event.get():
            if event.type == self.pg.QUIT:
                self.pg.quit()
                sys.exit()
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
                self.timer_clocked = True
                self.settings.counter -= 1
                if self.settings.counter == 0:
                    game_over_thread = threading.Thread(target=self.manage_game_over)
                    game_over_thread.daemon = True
                    game_over_thread.start()

    def _check_keydown_events(self, event):
        """Manages the keypresses."""
        #Open dynamic_menu if the player presses ESC while playing
        if event.key == self.pg.K_ESCAPE and self.game_active: 
            self.game_active = False
            self.game_pause = True
            self.pg.mouse.set_visible(True)
            self.dynamic_menu.open_alien_hunt_dynamic_menu()
        
        #Return to the static menu if the player presses ESC while in the dynamic menu
        elif event.key == self.pg.K_ESCAPE and self.game_pause:
            self.pg.mouse.set_visible(True)
            self.game_pause = False
            self.static_menu.open_alien_hunt_static_menu()

        #Return to the Space Pursuit menu if the player presses ESC while in the static menu
        elif event.key == self.pg.K_ESCAPE and not self.game_active and not self.game_over:
            self.main_game_instance.open_alien_hunt = False
            self.main_game_instance.menu.open_menu()
        
        elif event.key == self.pg.K_d:
            self.rocket.moving_right = True
        elif event.key == self.pg.K_a:
            self.rocket.moving_left = True
        elif event.key == self.pg.K_w:
            self.rocket.moving_up = True
        elif event.key == self.pg.K_s:
            self.rocket.moving_down = True
        elif (event.key == self.pg.K_SPACE and self.rocket.moving_right and
              len(self.rocket_projectiles) < self.settings.projectile_allowed):
            if self.stats.level >= self.settings.boost_level_2:
                double_fire = True
            else:
                double_fire = False
            self._fire_projectile(self.rocket_projectiles, self.rocket, "fire_right", double_fire)
            if self.stats.level >= self.settings.boost_level_1:
                self._fire_projectile(self.rocket_projectiles, self.rocket, "fire_northeast", double_fire=False)
                self._fire_projectile(self.rocket_projectiles, self.rocket, "fire_southeast", double_fire=False)
        elif (event.key == self.pg.K_SPACE and self.rocket.moving_left and 
              len(self.rocket_projectiles) < self.settings.projectile_allowed):
            if self.stats.level >= self.settings.boost_level_2:
                double_fire = True
            else:
                double_fire = False
            self._fire_projectile(self.rocket_projectiles, self.rocket, "fire_left", double_fire)
            if self.stats.level >= self.settings.boost_level_1:
                self._fire_projectile(self.rocket_projectiles, self.rocket, "fire_northwest", double_fire=False)
                self._fire_projectile(self.rocket_projectiles, self.rocket, "fire_southwest", double_fire=False)
        elif (event.key == self.pg.K_SPACE and self.rocket.moving_up and 
              len(self.rocket_projectiles) < self.settings.projectile_allowed):
            if self.stats.level >= self.settings.boost_level_2:
                double_fire = True
            else:
                double_fire = False
            self._fire_projectile(self.rocket_projectiles, self.rocket, "fire_up", double_fire)
            if self.stats.level >= self.settings.boost_level_1:
                self._fire_projectile(self.rocket_projectiles, self.rocket, "fire_northwest", double_fire=False)
                self._fire_projectile(self.rocket_projectiles, self.rocket, "fire_northeast", double_fire=False)
        elif (event.key == self.pg.K_SPACE and self.rocket.moving_down and
              len(self.rocket_projectiles) < self.settings.projectile_allowed):
            if self.stats.level >= self.settings.boost_level_2:
                double_fire = True
            else:
                double_fire = False
            self._fire_projectile(self.rocket_projectiles, self.rocket, "fire_down", double_fire)
            if self.stats.level >= self.settings.boost_level_1:
                self._fire_projectile(self.rocket_projectiles, self.rocket, "fire_southwest", double_fire=False)
                self._fire_projectile(self.rocket_projectiles, self.rocket, "fire_southeast", double_fire=False)

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
            self.rocket.moving_right = False
        elif event.key == self.pg.K_a:
            self.rocket.moving_left = False
        elif event.key == self.pg.K_w:
            self.rocket.moving_up = False
        elif event.key == self.pg.K_s:
            self.rocket.moving_down = False

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
            self.static_menu.open_alien_hunt_static_menu()

    def _check_static_play_button(self, mouse_position):
        """Starts the game if the player clicks Play"""
        if self.static_menu.play_button.rect.collidepoint(mouse_position):
            self.pg.mouse.set_visible(False)
            self.stats.reset_stats()
            self.settings.initialize_dynamic_settings()
            self.rocket_projectiles.clear_projectiles()
            self.ufo_projectiles.clear_projectiles()
            self._create_planets_group()
            self._create_fleet()
            self.rocket.place_initial()
            self.game_active = True

    def _check_static_back_button(self, mouse_position):
        """Returns to the main menu if the player clicks Back"""
        if self.static_menu.back_button.rect.collidepoint(mouse_position):
            self.main_game_instance.open_alien_hunt = False
            self.main_game_instance.menu.open_menu()

    def _update_screen(self):
        """Updates images on the screen."""
        if self.game_active:
            #Move and draw the bg_image to create a dynamic background effect
            self.screen.blit(self.bg_image, self.bg_image_rect)

            #Draw the scoreboard
            self.sb.draw_board()

            #Update rocket's position
            self.rocket.update(self.dt)

            #Update UFOs
            self._update_ufos()

            #Update and draw projectiles (get rid of old ones)
            self._update_projectiles()

            #Draw the rocket
            self.rocket.blit_rocket()
            
            #draw planets
            self.planets.draw(self.screen)

            #Draw explosions
            self.explosions.draw(self.screen)
            self.explosions.update()

        elif self.game_over:
            game_over_surf = self.pg.Surface(self.screen.get_size())
            game_over_surf.fill((0, 0, 0))  # Fill with black
            game_over_surf.set_alpha(128)

            self.sb.game_over_button._prep_text('GAME OVER!', 56)
            self.sb.game_over_button.draw_button()

    def _check_rocket_planet_collisions(self):
        """Manages collisions between rocket and planets."""
        planets = self.pg.sprite.spritecollide(self.rocket, self.planets, False, self.pg.sprite.collide_mask)
        if planets:
            for planet in planets:
                if self.rocket.moving_right:
                    self.rocket.moving_right = False
                if self.rocket.moving_left:
                    self.rocket.moving_left = False
                if self.rocket.moving_up:
                    self.rocket.moving_up = False
                if self.rocket.moving_down:
                    self.rocket.moving_down = False

    def _update_ufos(self):
        """Updates and draws UFOs"""
        #Make green UFOs move acroos the screen 
        if self.stats.level % 2 == 0:
            for green_ufo in self.green_ufos:
                green_ufo.move_horizontal = 1 * green_ufo.direction 
        elif self.stats.level % 2 == 1:
            for green_ufo in self.green_ufos:
                green_ufo.move_vertical = 1 * green_ufo.direction

        self.red_ufos.update()
        self.green_ufos.update(self.dt)
        self.blue_ufos.update()

        #Draw ufos' fleet (draws every ufo.image at ufo.rect location)
        self.red_ufos.draw(self.screen)
        self.green_ufos.draw(self.screen)
        self.blue_ufos.draw(self.screen)

        #Make blue UFOs fire projectiles at a certain rate
        if self.settings.counter % 4 == 0 and len(self.ufo_projectiles) < len(self.blue_ufos) and self.timer_clocked:
            for blue_ufo in self.blue_ufos:
                number = random.randrange(1, 9)
                if self.stats.level >= self.settings.boost_level_2:
                    double_fire = True
                else:
                    double_fire = False
                if number == 1:
                    self._fire_projectile(
                        self.ufo_projectiles, blue_ufo, "fire_right", double_fire
                    )
                elif number == 2:
                    self._fire_projectile(
                        self.ufo_projectiles, blue_ufo, "fire_left", double_fire
                    )
                elif number == 3:
                    self._fire_projectile(
                        self.ufo_projectiles, blue_ufo, "fire_up", double_fire
                    )
                elif number == 4:
                    self._fire_projectile(
                        self.ufo_projectiles, blue_ufo, "fire_down", double_fire
                    )
                elif number == 5:
                    self._fire_projectile(
                        self.ufo_projectiles, blue_ufo, "fire_northwest", double_fire=False
                    )
                elif number == 6:
                    self._fire_projectile(
                        self.ufo_projectiles, blue_ufo, "fire_northeast", double_fire=False
                    )
                elif number == 7:
                    self._fire_projectile(
                        self.ufo_projectiles, blue_ufo, "fire_southwest", double_fire=False
                    )
                elif number == 8:
                    self._fire_projectile(
                        self.ufo_projectiles, blue_ufo, "fire_southeast", double_fire=False
                    )
                
            self.timer_clocked = False
        
        self._check_green_ufo_collisions()
        self._check_rocket_ufo_collisions()
        
    def _check_green_ufo_collisions(self):
        """Invert a green UFO's direction if it collides with an element of the game"""
        
        ufos_against_planets = self.pg.sprite.groupcollide(self.green_ufos, self.planets, False, False, self.pg.sprite.collide_mask)
        ufos_against_red = self.pg.sprite.groupcollide(self.green_ufos, self.red_ufos, False, False)
        ufos_against_blue = self.pg.sprite.groupcollide(self.green_ufos, self.blue_ufos, False, False)
        
        if ufos_against_planets:
            for green_ufo in ufos_against_planets.keys():
                for planet in ufos_against_planets[green_ufo]:
                    if green_ufo.move_horizontal == 1:
                        green_ufo.x = float(planet.rect.x - green_ufo.rect.width - 1)
                    elif green_ufo.move_horizontal == -1:
                        green_ufo.x = float(planet.rect.right + 1)
                    elif green_ufo.move_vertical == 1:
                        green_ufo.y = float(planet.rect.top - green_ufo.rect.height - 1)
                    elif green_ufo.move_vertical == -1:
                        green_ufo.y = float(planet.rect.bottom + 1)
                    
                    green_ufo.direction *= -1
        
        if ufos_against_red:  
            for green_ufo in ufos_against_red.keys():
                for red_ufo in ufos_against_red[green_ufo]:
                    if green_ufo.move_horizontal == 1:
                        green_ufo.x = float(red_ufo.rect.x - green_ufo.rect.width - 1)
                    elif green_ufo.move_horizontal == -1:
                        green_ufo.x = float(red_ufo.rect.right + 1)
                    elif green_ufo.move_vertical == 1:
                        green_ufo.y = float(red_ufo.rect.top - green_ufo.rect.height - 1)
                    elif green_ufo.move_vertical == -1:
                        green_ufo.y = float(red_ufo.rect.bottom + 1)

                    green_ufo.direction *= -1

        if ufos_against_blue:
            for green_ufo in ufos_against_blue.keys():
                for blue_ufo in ufos_against_blue[green_ufo]:
                    if green_ufo.move_horizontal == 1:
                        green_ufo.x = float(blue_ufo.rect.x - green_ufo.rect.width - 1)
                    elif green_ufo.move_horizontal == -1:
                        green_ufo.x = float(blue_ufo.rect.right + 1)
                    elif green_ufo.move_vertical == 1:
                        green_ufo.y = float(blue_ufo.rect.top - green_ufo.rect.height - 1)
                    elif green_ufo.move_vertical == -1:
                        green_ufo.y = float(blue_ufo.rect.bottom + 1)

                    green_ufo.direction *= -1

        for green_ufo in self.green_ufos:
            if green_ufo.x < 0:
                green_ufo.x = 1.0
                green_ufo.direction *= -1
            elif green_ufo.x > self.screen_rect.width - green_ufo.rect.width:
                green_ufo.x = float(self.screen_rect.width - green_ufo.rect.width - 1)
                green_ufo.direction *= -1
            elif green_ufo.y < 0:
                green_ufo.y = 1.0
                green_ufo.direction *= -1
            elif green_ufo.y > self.screen_rect.height - green_ufo.rect.height:
                green_ufo.y = float(self.screen_rect.height - green_ufo.rect.height - 1)
                green_ufo.direction *= -1

    def _check_rocket_ufo_collisions(self):
        """Manages crashes against the UFOs"""
        red_ufos_hit = self.pg.sprite.spritecollide(self.rocket, self.red_ufos, False)
        green_ufos_hit = self.pg.sprite.spritecollide(self.rocket, self.green_ufos, False)
        blue_ufos_hit = self.pg.sprite.spritecollide(self.rocket, self.blue_ufos, False)
        for red_ufo_hit in red_ufos_hit:
            self.red_ufos.remove_ufo(red_ufo_hit)
            explosion_sound = self.pg.mixer.Sound('resources/sounds/explosion_sound.mp3')
            self.pg.mixer.Sound.play(explosion_sound)
            explosion = self.explosions.create_explosion(red_ufo_hit.rect.center)
            self.explosions.add(explosion)
            self._rocket_hit()
        for green_ufo_hit in green_ufos_hit:
            self.green_ufos.remove_ufo(green_ufo_hit)
            explosion_sound = self.pg.mixer.Sound('resources/sounds/explosion_sound.mp3')
            self.pg.mixer.Sound.play(explosion_sound)
            explosion = self.explosions.create_explosion(green_ufo_hit.rect.center)
            self.explosions.add(explosion)
            self._rocket_hit()
        for blue_ufo_hit in blue_ufos_hit:
            self.blue_ufos.remove_ufo(blue_ufo_hit)
            explosion_sound = self.pg.mixer.Sound('resources/sounds/explosion_sound.mp3')
            self.pg.mixer.Sound.play(explosion_sound)
            explosion = self.explosions.create_explosion(blue_ufo_hit.rect.center)
            self.explosions.add(explosion)
            self._rocket_hit()

    def _update_projectiles(self):
        """Updates the position, gets rid of the old ones and draws projectiles."""
        #Update projectile's position
        self.rocket_projectiles.update(self.dt, self.settings.projectile_speed)
        self.ufo_projectiles.update(self.dt, self.settings.projectile_speed)

        #Delete out-of-boundaries projectiles and blit projectiles all in one loop
        for projectile in self.rocket_projectiles:
            if (projectile.rect.bottom <= 0 or projectile.rect.left >= self.screen_rect.width or
                projectile.rect.top >= self.screen_rect.height or projectile.rect.right <= 0):
                self.rocket_projectiles.remove_projectile(projectile)
            else:
                self.screen.blit(projectile.image, projectile.rect)

        for projectile in self.ufo_projectiles:
            if (projectile.rect.bottom <= 0 or projectile.rect.left >= self.screen_rect.width or
                projectile.rect.top >= self.screen_rect.height or projectile.rect.right <= 0):
                self.ufo_projectiles.remove_projectile(projectile)
            else:
                self.screen.blit(projectile.image, projectile.rect)

        self._check_rocket_projectile_ufo_collisions()
        self._check_projectile_planet_collisions(self.rocket_projectiles)
        self._check_projectile_planet_collisions(self.ufo_projectiles)
        self._check_ufo_projectile_rocket_collisions()
        self._check_ufo_projectile_ufo_collisions()

    def _check_rocket_projectile_ufo_collisions(self):
        """Responds to projectile-ufos collisions."""
        #Remove any ufos hit
        red_collisions = self.pg.sprite.groupcollide(self.rocket_projectiles, self.red_ufos, False, False)
        green_collisions = self.pg.sprite.groupcollide(self.rocket_projectiles, self.green_ufos, False, False)
        blue_collisions = self.pg.sprite.groupcollide(self.rocket_projectiles, self.blue_ufos, False, False)
        if red_collisions:
            explosion_sound = self.pg.mixer.Sound('resources/sounds/explosion_sound.mp3')
            self.pg.mixer.Sound.play(explosion_sound)
            for redufos in red_collisions.values():
                for redufo in redufos:
                    self.red_ufos.remove_ufo(redufo)
                    explosion = self.explosions.create_explosion(redufo.rect.center)
                    self.explosions.add(explosion)
                self.stats.score += self.settings.red_ufo_points * len(redufos)
        if green_collisions:
            explosion_sound = self.pg.mixer.Sound('resources/sounds/explosion_sound.mp3')
            self.pg.mixer.Sound.play(explosion_sound)
            for greenufos in green_collisions.values():
                for greenufo in greenufos:
                    self.green_ufos.remove_ufo(greenufo)
                    explosion = self.explosions.create_explosion(greenufo.rect.center)
                    self.explosions.add(explosion)
                self.stats.score += self.settings.green_ufo_points * len(greenufos)
        if blue_collisions:
            explosion_sound = self.pg.mixer.Sound('resources/sounds/explosion_sound.mp3')
            self.pg.mixer.Sound.play(explosion_sound)
            for blueufos in blue_collisions.values():
                for blueufo in blueufos:
                    self.blue_ufos.remove_ufo(blueufo)
                    explosion = self.explosions.create_explosion(blueufo.rect.center)
                    self.explosions.add(explosion)
                self.stats.score += self.settings.blue_ufo_points * len(blueufos)
        if self.stats.score >= self.stats.record:
            path = Path('resources/alien_hunt/record.json')
            new_record = json.dumps(self.stats.score)
            path.write_text(new_record)

        #If all the ufos have been destroyed, restart the game 
        if not self.red_ufos and not self.green_ufos and not self.blue_ufos:
            self.stats.level += 1
            self.settings.increase_difficulty()
            self.ufo_projectiles.empty()
            self.rocket_projectiles.empty()
            self.rocket.place_initial()
            self._create_planets_group()
            self._create_fleet()

    def _check_projectile_planet_collisions(self, group):
        """Deletes the projectile if it hits a planet"""
        projectiles = self.pg.sprite.groupcollide(group, self.planets, False, False)
        for projectile in projectiles:
            group.remove_projectile(projectile)
        
    def _check_ufo_projectile_rocket_collisions(self):
        """Manages collisions between ufo projectiles and rocket."""
        projectiles = self.pg.sprite.spritecollide(self.rocket, self.ufo_projectiles, False)
        if projectiles:
            explosion_sound = self.pg.mixer.Sound('resources/sounds/explosion_sound.mp3')
            self.pg.mixer.Sound.play(explosion_sound)
            explosion = self.explosions.create_explosion(self.rocket.rect.center)
            self.explosions.add(explosion)
            self._rocket_hit()
            for projectile in projectiles:
                self.ufo_projectiles.remove_projectile(projectile)

    def _rocket_hit(self):
        """Responds to the ship crashing against an UFOs or being hit by projectiles."""
        #Decrement rockets left
        self.stats.rocket_left -= 1
        if not self.stats.rocket_left:
            game_over_thread = threading.Thread(target=self.manage_game_over)
            game_over_thread.daemon = True
            game_over_thread.start()
        self.settings.counter += 5

    def _check_ufo_projectile_ufo_collisions(self):
        """"Remove a projectile fired by a blue UFO if it hits another UFO"""
        projectiles_against_red = self.pg.sprite.groupcollide(self.ufo_projectiles, self.red_ufos, False, False)
        projectiles_against_green = self.pg.sprite.groupcollide(self.ufo_projectiles, self.green_ufos, False, False)
        for projectile in projectiles_against_red:
            self.ufo_projectiles.remove_projectile(projectile)
        for projectile in projectiles_against_green:
            self.ufo_projectiles.remove_projectile(projectile)

    def manage_game_over(self):
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
            self.main_game_instance.open_alien_hunt = False
            self.main_game_instance.menu.open_menu()