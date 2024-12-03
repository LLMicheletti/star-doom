from pygame.sprite import Group

class ExplosionGroup(Group):
    """A class to manage the explosion animation."""

    def __init__(self, game_instance):
        """Initializes the attributes and loads the images."""
        super().__init__()
        self.pg = game_instance.pg
        self.images = self.preload_images()
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.counter = 0

    def preload_images(self):
        """Preloads images to prevent repeated slow disk access."""
        images = []
        for i in range(1, 7):
            img = self.pg.image.load(f'resources/images/exp{i}.bmp')
            img = self.pg.transform.scale(img, (60, 60))
            images.append(img)
        return images
    
    def create_explosion(self, obj_center): 
        """
        Creates and adds a new explosion to the group.
        """
        explosion = self.pg.sprite.Sprite()

        explosion.index = 0
        explosion.counter = 0
        explosion.images = self.images
        explosion.image = self.images[explosion.index]
        explosion.rect = self.rect.copy()
        explosion.rect.center = obj_center
        
        return explosion

    def update(self):
        """
        Changes explosions images.
        """
        for explosion in self.sprites():
            explosion_speed = 5
            explosion.counter += 1

            if explosion.counter >= explosion_speed and explosion.index < len(explosion.images) - 1:
                explosion.counter = 0
                explosion.index += 1
                explosion.image = explosion.images[explosion.index]

            if explosion.index >= len(explosion.images) - 1 and explosion.counter >= explosion_speed:
                explosion.kill()