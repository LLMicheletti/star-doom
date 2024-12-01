import pygame

class Sun:
    """A class to manage the sun."""
    def __init__(self, game_instance):
        """Initializes the main attributes and loads the images."""
        #The screen
        self.screen = game_instance.screen
        self.screen_rect = game_instance.screen_rect
        self.game_instance = game_instance
        self.settings = game_instance.settings

        #The yellow dwarf state
        self.yellow_dwarf_image = pygame.image.load('resources/images/yellow_dwarf.png')
        self.yellow_dwarf_image = pygame.transform.scale(self.yellow_dwarf_image, (150, 150))
        self.yellow_dwarf_image_rect = self.yellow_dwarf_image.get_rect()
        self.yellow_dwarf_image_rect.right = self.screen_rect.width - 50
        self.yellow_dwarf_image_rect.centery = self.screen_rect.height/2

        #The red giant state
        self.red_giant_image = pygame.image.load('resources/images/red_giant.png')
        self.red_giant_image = pygame.transform.scale(self.red_giant_image, (300, 300))
        self.red_giant_image_rect = self.red_giant_image.get_rect()
        self.red_giant_image_rect.right = self.screen_rect.width - 30
        self.red_giant_image_rect.centery = self.screen_rect.height/2

        #The blue dwarf state
        self.blue_dwarf_image = pygame.image.load('resources/images/blue_dwarf.png')
        self.blue_dwarf_image = pygame.transform.scale(self.blue_dwarf_image, (130, 130))
        self.blue_dwarf_image_rect = self.blue_dwarf_image.get_rect()
        self.blue_dwarf_image_rect.right = self.screen_rect.width - 50
        self.blue_dwarf_image_rect.centery = self.screen_rect.height/2
        
        #The black hole state
        self.black_hole_image = pygame.image.load('resources/images/black_hole.bmp')
        self.black_hole_image_rect = self.black_hole_image.get_rect()
        self.black_hole_image_rect.right = self.screen_rect.width - 50
        self.black_hole_image_rect.centery = self.screen_rect.height/2

        #Starting with the yellow dwarf
        self.image = self.yellow_dwarf_image
        self.rect = self.yellow_dwarf_image_rect
        self.rect.right = self.screen_rect.width - 50
        self.rect.centery = self.screen_rect.height/2

        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        self.hit_time = 0

    def update(self, dt):
        """Updates the state of the sun."""
        if self.game_instance.stats.level == 1:
            self.image = self.yellow_dwarf_image
            self.rect = self.yellow_dwarf_image_rect
        elif self.game_instance.stats.level == 2:
            self.image = self.red_giant_image
            self.rect = self.red_giant_image_rect
        elif self.game_instance.stats.level == 3:
            self.image = self.blue_dwarf_image
            self.rect = self.blue_dwarf_image_rect
        elif self.game_instance.stats.level == 4:
            self.image = self.black_hole_image
            self.rect = self.black_hole_image_rect
            self.y += self.game_instance.settings.black_hole_speed * dt * self.game_instance.settings.black_hole_direction
            if round(self.y) != self.rect.y:
                self.rect.y = round(self.y)
        
            if self.hit_time > 0:
                current_time = pygame.time.get_ticks()
                if current_time - self.hit_time > self.settings.black_hole_hit_duration:
                    self.image = self.black_hole_image.copy()
                    self.hit_time = 0

    def blit_sun(self):
        """Draws the sun at its current position."""
        self.screen.blit(self.image, self.rect)

        if self.game_instance.stats.level == 4:
            #Draw life bar for black hole
            self.life_rect = pygame.Rect(0, 0, self.settings.black_hole_life, 3)
            self.life_rect.centerx = self.rect.centerx
            self.life_rect.y = self.rect.bottom
            pygame.draw.rect(self.screen, 'red', self.life_rect)

    def black_hole_hit(self):
        """"Draws a violet overlay over the black hole when hit by a doublerocket wave"""
        violet_overlay = pygame.Surface(self.black_hole_image.get_size()).convert_alpha()
        violet_overlay.fill((128, 0, 128, 192))

        self.image = self.black_hole_image.copy()
        self.image.blit(violet_overlay, (0, 0))
        self.hit_time = pygame.time.get_ticks()