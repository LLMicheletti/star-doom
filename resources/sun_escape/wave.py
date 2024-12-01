import random
from pygame.sprite import Group
import math


from numba import njit
import numpy as np

@njit
def calculate_sin_points(width, centerx, amplitude, frequency, phase, starting_height):
    """Calculate the initial points of the sine wave."""
    num_points = round(centerx - width)
    points = np.empty((num_points, 2), dtype=np.float32)
    x = np.linspace(width, width + num_points, num_points)
    y = starting_height + np.sin(x * frequency + phase) * amplitude
    points = np.stack((x, y), axis=1)

    return points

@njit	
def update_sin_points(points, speed, frequency, phase, starting_height, amplitude):
    """Update points for the sine wave path with optimized calculations."""
    num_points = points.shape[0]
    for i in range(num_points):
        # Move left by the speed
        points[i, 0] -=  speed
        # Update the y-coordinate based on sine function
        points[i, 1] = starting_height + np.sin(points[i, 0] * frequency + phase) * amplitude

@njit
def cubic_bezier(t, p0, p1, p2, p3):
    """Cubic Bezier curve calculation for multiple points."""
    t = np.asarray(t)  # Ensure t is a CuPy array
    one_minus_t = 1 - t
    return (one_minus_t ** 3) * p0 + \
           3 * (one_minus_t ** 2) * t * p1 + \
           3 * one_minus_t * (t ** 2) * p2 + \
           (t ** 3) * p3

@njit
def bezier_curve_points(p0, control_1, control_2, p3, num_points=101):
    """Generates points for a smooth Bezier curve."""
    t_values = np.linspace(0, 1, num_points)
    points = np.zeros((num_points, 2), dtype=np.float32)
    points[:, 0] = cubic_bezier(t_values, p0[0], control_1[0], control_2[0], p3[0])
    points[:, 1] = cubic_bezier(t_values, p0[1], control_1[1], control_2[1], p3[1])

    return points

@njit
def update_wave_points(points, speed):
    """Move each point in the wave to the left by a given speed."""
    points[:, 0] -= speed

@njit
def update_right_points(points, speed, frequency, phase, starting_height, amplitude):
    """Update points for the sine wave path with optimized calculations."""
    num_points = points.shape[0]
    for i in range(num_points):
        # Move left by the speed
        points[i, 0] += speed
        # Update the y-coordinate based on sine function
        points[i, 1] = starting_height + math.sin(points[i, 0] * frequency + phase) * amplitude

class WaveGroup(Group):
    """
    A class to manage waves
    """
    def __init__(self, game_instance):
        super().__init__()
        self.game_instance = game_instance
        self.pg = game_instance.pg
        self.screen = game_instance.screen
        self.screen_rect = game_instance.screen_rect
        self.settings = game_instance.settings

    def _calculate_control_point(self, p1, p2):
        return [(p1[0] + p2[0]) / 2, p1[1] + random.randrange(-50, 50)]
    
    def create_sin_wave(self, colour):
        """Create a new wave and add it to the group."""
        sin_wave = self.pg.sprite.Sprite()
        sin_wave.form = "sin"
        sin_wave.colour = colour
        sin_wave.amplitude = float(random.randrange(20, 140))
        sin_wave.frequency = 0.10
        sin_wave.phase = 0
        sin_wave.starting_height = random.randrange(
            int(self.screen_rect.height / 2) - 200,
            int(self.screen_rect.height / 2) + 200
        )
        sin_wave.points = calculate_sin_points(
            self.screen_rect.width - 450, self.game_instance.sun.rect.centerx,
            sin_wave.amplitude, sin_wave.frequency, sin_wave.phase, sin_wave.starting_height
        )
        sin_wave.point_0 = sin_wave.points[-1]
        sin_wave.left_point = sin_wave.points[0]
        sin_wave.right_point = sin_wave.point_0
        sin_wave.rect = self.pg.Rect(0, 0, 0, 0)

        return sin_wave
    
    def update_sin_wave(self, dt, sin_wave):
        """
        Update the sine wave's points and position.
        """
        sin_wave.phase += sin_wave.frequency  # Increment phase
        speed = self.settings.wave_speed * dt

        # Use Numba-optimized update function
        update_sin_points(
            sin_wave.points, speed, sin_wave.frequency, sin_wave.phase, sin_wave.starting_height, sin_wave.amplitude
        )

        # Update position of the sin_wave's bounding rectangle
        sin_wave.left_point = sin_wave.points[0]
        sin_wave.right_point = sin_wave.points[-1]
        sin_wave.rect.x = int(sin_wave.points[0, 0])
        sin_wave.rect.y = int(sin_wave.points[0, 1])
        sin_wave.rect.width = int(abs(sin_wave.points[0, 0] - sin_wave.points[-1, 0]))
        sin_wave.rect.height = int(abs(sin_wave.points[0, 1] - sin_wave.points[-1, 1]))

    def create_long_wave(self, colour):
        """Create a new wave and add it to the group."""
        long_wave = self.pg.sprite.Sprite()
        long_wave.form = "long"
        long_wave.colour = colour
        long_wave.point_0 = [float(self.game_instance.sun.rect.centerx), float(self.game_instance.sun.rect.centery)]
        long_wave.point_1 = [float(random.randrange(self.screen_rect.width - 250, self.screen_rect.width - 210)),
                        float(random.randrange(70, self.screen_rect.height - 70))]
        long_wave.point_2 = [float(random.randrange(self.screen_rect.width - 350, self.screen_rect.width - 250)),
                        float(random.randrange(70, self.screen_rect.height - 70))]
        long_wave.point_3 = [float(random.randrange(self.screen_rect.width - 450, self.screen_rect.width - 350)),
                        float(random.randrange(70, self.screen_rect.height - 70))]
        long_wave.control_1 = self._calculate_control_point(long_wave.point_0, long_wave.point_1)
        long_wave.control_2 = self._calculate_control_point(long_wave.point_2, long_wave.point_3)
        long_wave.points = bezier_curve_points(
            np.array(long_wave.point_0), np.array(long_wave.control_1),
            np.array(long_wave.control_2), np.array(long_wave.point_3)
        )
        long_wave.left_point = long_wave.points[0]
        long_wave.right_point = long_wave.point_0
        long_wave.rect = self.pg.Rect(0, 0, 0, 0)

        return long_wave
    
    def update_bezier_wave(self, dt, wave):
        """Update the wave position based on elapsed time."""
        speed = self.settings.wave_speed * dt
        update_wave_points(wave.points, speed)
        wave.left_point = wave.points[0]
        wave.right_point = wave.points[-1]
        wave.rect.x = int(wave.points[0, 0])
        wave.rect.y = int(wave.points[0, 1])
        wave.rect.width = int(abs(wave.points[0, 0] - wave.points[-1, 0])
        )
        wave.rect.height = int(abs(wave.points[0, 1] - wave.points[-1, 1]))

    def create_up_wave(self, colour):
        """Create a new wave and add it to the group."""
        up_wave = self.pg.sprite.Sprite()
        up_wave.form = "up"
        up_wave.colour = colour
        up_wave.point_0 = [float(self.game_instance.sun.rect.centerx), float(self.game_instance.sun.rect.centery - 40)]
        up_wave.point_1 = [float(random.randrange(self.screen_rect.width - 250, self.screen_rect.width - 210)),
                        float(random.randrange(70, int(self.screen_rect.height / 2) - 70))]
        up_wave.point_2 = [float(random.randrange(self.screen_rect.width - 350, self.screen_rect.width - 250)),
                        float(random.randrange(70, int(self.screen_rect.height / 2) - 70))]
        up_wave.point_3 = [float(random.randrange(self.screen_rect.width - 450, self.screen_rect.width - 350)),
                        float(random.randrange(70, int(self.screen_rect.height / 2) - 70))]

        up_wave.control_1 = self._calculate_control_point(up_wave.point_0, up_wave.point_1)
        up_wave.control_2 = self._calculate_control_point(up_wave.point_2, up_wave.point_3)
        up_wave.points = bezier_curve_points(
            np.array(up_wave.point_0), np.array(up_wave.control_1),
            np.array(up_wave.control_2), np.array(up_wave.point_3)
        )

        up_wave.left_point = up_wave.points[0]
        up_wave.right_point = up_wave.point_0

        up_wave.rect = self.pg.Rect(0, 0, 0, 0)

        return up_wave
    
    def create_down_wave(self, colour):
        """Create a new wave and add it to the group."""
        down_wave = self.pg.sprite.Sprite()
        down_wave.form = "down"
        down_wave.colour = colour
        down_wave.point_0 = [float(self.game_instance.sun.rect.centerx), float(self.game_instance.sun.rect.centery + 40)]
        down_wave.point_1 = [float(random.randrange(self.screen_rect.width - 250, self.screen_rect.width - 210)),
                        float(random.randrange(int(self.screen_rect.height / 2) + 70, self.screen_rect.height))]
        down_wave.point_2 = [float(random.randrange(self.screen_rect.width - 350, self.screen_rect.width - 250)),
                        float(random.randrange(int(self.screen_rect.height / 2) + 70, self.screen_rect.height))]
        down_wave.point_3 = [float(random.randrange(self.screen_rect.width - 450, self.screen_rect.width - 350)),
                        float(random.randrange(int(self.screen_rect.height / 2) + 70, self.screen_rect.height))]

        down_wave.control_1 = self._calculate_control_point(down_wave.point_0, down_wave.point_1)
        down_wave.control_2 = self._calculate_control_point(down_wave.point_2, down_wave.point_3)
        down_wave.points = bezier_curve_points(
            np.array(down_wave.point_0), np.array(down_wave.control_1),
            np.array(down_wave.control_2), np.array(down_wave.point_3)
        )

        down_wave.left_point = down_wave.points[0]
        down_wave.right_point = down_wave.point_0

        down_wave.rect = self.pg.Rect(0, 0, 0, 0)

        return down_wave
    
    def create_right_wave(self, colour):
        """Create a new wave and add it to the group."""
        right_wave = self.pg.sprite.Sprite()
        right_wave.form = "right"
        right_wave.colour = colour
        right_wave.amplitude = float(20)
        right_wave.frequency = 0.10
        right_wave.phase = 0
        right_wave.starting_height = float(self.game_instance.doublerocket.rect.centery)
        right_wave.points = calculate_sin_points(
            self.game_instance.doublerocket.rect.centerx, self.game_instance.doublerocket.rect.centerx + 100,
            right_wave.amplitude, right_wave.frequency, right_wave.phase, right_wave.starting_height
        )
        right_wave.point_0 = right_wave.points[-1]
        right_wave.left_point = right_wave.points[0]
        right_wave.right_point = right_wave.point_0
        right_wave.rect = self.pg.Rect(0, 0, 0, 0)

        return right_wave
    
    def update_right_wave(self, dt, right_wave):
        """Update the sine wave's points and position."""
        for right_wave in self.sprites():
            right_wave.phase += right_wave.frequency  # Increment phase
            speed = self.settings.wave_speed * dt

            # Use Numba-optimized update function
            update_right_points(
                right_wave.points, speed, right_wave.frequency, right_wave.phase, right_wave.starting_height, right_wave.amplitude
            )

            # Update position of the right_wave's bounding rectangle
            right_wave.left_point = right_wave.points[0]
            right_wave.right_point = right_wave.points[-1]
    
    def update(self, dt, wave):
        """
        Update the wave position based on elapsed time.
        """
        if wave.form == "sin":
            self.update_sin_wave(dt, wave)
        elif wave.form == "long" or wave.form == "up" or wave.form == "down":
            self.update_bezier_wave(dt, wave)
        elif wave.form == "right":
            self.update_right_wave(dt, wave)
    
    def _draw(self, wave):
        """
        Draw the waves
        """
        self.pg.draw.lines(self.screen, wave.colour, False, wave.points.astype(np.int32).tolist(), 3)

class SinWaveGroup(Group):
    """A class to manage a single wave emitted which changes during its path."""
    def __init__(self, game_instance):
        super().__init__()
        self.game_instance = game_instance
        self.pg = game_instance.pg
        self.screen = game_instance.screen
        self.screen_rect = game_instance.screen_rect
        self.settings = game_instance.settings

    def create_sinwave(self, colour):
        """Create a new wave and add it to the group."""
        wave = self.pg.sprites.Sprite()
        wave.colour = colour
        wave.amplitude = float(random.randrange(20, 140))
        wave.frequency = 0.10
        wave.phase = 0
        wave.starting_height = random.randrange(
            int(self.screen_rect.height / 2) - 200,
            int(self.screen_rect.height / 2) + 200
        )
        wave.points = calculate_sin_points(
            self.screen_rect.width - 450, self.game_instance.sun.rect.centerx,
            wave.amplitude, wave.frequency, wave.phase, wave.starting_height
        )
        wave.point_0 = wave.points[-1]
        wave.left_point = wave.points[0]
        wave.right_point = wave.point_0
        wave.rect = self.pg.Rect(0, 0, 0, 0)

        return wave

    def update_sinwave(self, dt):
        """
        Update the sine wave's points and position.
        """
        for wave in self.sprites():
            wave.phase += wave.frequency  # Increment phase
            speed = self.settings.wave_speed * dt

            # Use Numba-optimized update function
            update_sinpoints(
                wave.points, speed, wave.frequency, wave.phase, wave.starting_height, wave.amplitude
            )

            # Update position of the wave's bounding rectangle
            wave.left_point = wave.points[0]
            wave.right_point = wave.points[-1]
            wave.rect.x = int(wave.points[0, 0])
            wave.rect.y = int(wave.points[0, 1])
            wave.rect.width = int(abs(wave.points[0, 0] - wave.points[-1, 0]))
            wave.rect.height = int(abs(wave.points[0, 1] - wave.points[-1, 1]))

    def _draw(self):
        for wave in self.sprites():
            self.pg.draw.lines(self.screen, wave.colour, False, wave.points.astype(np.int32).tolist(), 3)

class LongWaveGroup(Group):
    """A class to manage a single wave emitted from the center."""

    def __init__(self, game_instance):
        super().__init__()
        self.game_instance = game_instance
        self.pg = game_instance.pg
        self.screen = game_instance.screen
        self.screen_rect = game_instance.screen_rect
        self.settings = game_instance.settings

    def create_long_wave(self, colour):
        """Create a new wave and add it to the group."""
        wave = self.pg.sprite.Sprite()
        wave.colour = colour
        wave.point_0 = [float(self.game_instance.sun.rect.centerx), float(self.game_instance.sun.rect.centery)]
        wave.point_1 = [float(random.randrange(self.screen_rect.width - 250, self.screen_rect.width - 210)),
                        float(random.randrange(70, self.screen_rect.height - 70))]
        wave.point_2 = [float(random.randrange(self.screen_rect.width - 350, self.screen_rect.width - 250)),
                        float(random.randrange(70, self.screen_rect.height - 70))]
        wave.point_3 = [float(random.randrange(self.screen_rect.width - 450, self.screen_rect.width - 350)),
                        float(random.randrange(70, self.screen_rect.height - 70))]
        wave.control_1 = self._calculate_control_point(wave.point_0, wave.point_1)
        wave.control_2 = self._calculate_control_point(wave.point_2, wave.point_3)
        wave.points = bezier_curve_points(
            np.array(wave.point_0), np.array(wave.control_1),
            np.array(wave.control_2), np.array(wave.point_3)
        )
        wave.left_point = wave.points[0]
        wave.right_point = wave.point_0
        wave.rect = self.pg.Rect(0, 0, 0, 0)

        return wave

    def _calculate_control_point(self, p1, p2):
        return [(p1[0] + p2[0]) / 2, p1[1] + random.randrange(-50, 50)]

    def update_long_wave(self, dt):
        """Update the wave position based on elapsed time."""
        for wave in self.sprites():
            speed = self.settings.wave_speed * dt
            update_wave_points(wave.points, speed)
            wave.left_point = wave.points[0]
            wave.right_point = wave.points[-1]
            wave.rect.x = int(wave.points[0, 0])
            wave.rect.y = int(wave.points[0, 1])
            wave.rect.width = int(abs(wave.points[0, 0] - wave.points[-1, 0])
            )
            wave.rect.height = int(abs(wave.points[0, 1] - wave.points[-1, 1]))

    def _draw(self):
        """Draws the wave using the computed Bezier curve points."""
        for wave in self.sprites():
            self.pg.draw.lines(self.screen, wave.colour, False, wave.points.astype(np.int32).tolist(), 3)

class UpWaveGroup(Group):
    """A class to manage a single up wave emitted from the top."""

    def __init__(self, game_instance):
        super().__init__()
        self.game_instance = game_instance
        self.pg = game_instance.pg
        self.screen = game_instance.screen
        self.screen_rect = game_instance.screen_rect
        self.settings = game_instance.settings

    def create_up_wave(self, colour):
        """Create a new wave and add it to the group."""
        wave = self.pg.sprite.Sprite()
        wave.colour = colour
        wave.point_0 = [float(self.game_instance.sun.rect.centerx), float(self.game_instance.sun.rect.centery - 40)]
        wave.point_1 = [float(random.randrange(self.screen_rect.width - 250, self.screen_rect.width - 210)),
                        float(random.randrange(70, int(self.screen_rect.height / 2) - 70))]
        wave.point_2 = [float(random.randrange(self.screen_rect.width - 350, self.screen_rect.width - 250)),
                        float(random.randrange(70, int(self.screen_rect.height / 2) - 70))]
        wave.point_3 = [float(random.randrange(self.screen_rect.width - 450, self.screen_rect.width - 350)),
                        float(random.randrange(70, int(self.screen_rect.height / 2) - 70))]

        wave.control_1 = self._calculate_control_point(wave.point_0, wave.point_1)
        wave.control_2 = self._calculate_control_point(wave.point_2, wave.point_3)
        wave.points = bezier_curve_points(
            np.array(wave.point_0), np.array(wave.control_1),
            np.array(wave.control_2), np.array(wave.point_3)
        )

        wave.left_point = wave.points[0]
        wave.right_point = wave.point_0

        wave.rect = self.pg.Rect(0, 0, 0, 0)

        return wave

    def _calculate_control_point(self, p1, p2):
        """Calculate the midpoint control point with a slight random offset."""
        return [(p1[0] + p2[0]) / 2, p1[1] + random.randrange(-50, 50)]

    def update(self, dt):
        """Update the wave position based on elapsed time."""
        for wave in self.sprites():
            speed = self.settings.wave_speed * dt
            update_wave_points(wave.points, speed)
            wave.left_point = wave.points[0]
            wave.right_point = wave.points[-1]
            wave.rect.x = int(wave.points[0, 0])
            wave.rect.y = int(wave.points[0, 1])
            wave.rect.width = int(abs(wave.points[0, 0] - wave.points[-1, 0]))
            wave.rect.height = int(abs(wave.points[0, 1] - wave.points[-1, 1]))

    def _draw(self):
        """Draw the wave using the computed Bezier curve points."""
        for wave in self.sprites():
            self.pg.draw.lines(self.screen, wave.colour, False, wave.points.astype(np.int32).tolist(), 3)
        
class DownWaveGroup(Group):
    """A class to manage a single down wave emitted from the bottom."""

    def __init__(self, game_instance):
        super().__init__()
        self.game_instance = game_instance
        self.pg = game_instance.pg
        self.screen = game_instance.screen
        self.screen_rect = game_instance.screen_rect
        self.settings = game_instance.settings

    def create_wave(self, colour):
        """Create a new wave and add it to the group."""
        wave = self.pg.sprite.Sprite()
        wave.colour = colour
        wave.point_0 = [float(self.game_instance.sun.rect.centerx), float(self.game_instance.sun.rect.centery + 40)]
        wave.point_1 = [float(random.randrange(self.screen_rect.width - 250, self.screen_rect.width - 210)),
                        float(random.randrange(int(self.screen_rect.height / 2) + 70, self.screen_rect.height))]
        wave.point_2 = [float(random.randrange(self.screen_rect.width - 350, self.screen_rect.width - 250)),
                        float(random.randrange(int(self.screen_rect.height / 2) + 70, self.screen_rect.height))]
        wave.point_3 = [float(random.randrange(self.screen_rect.width - 450, self.screen_rect.width - 350)),
                        float(random.randrange(int(self.screen_rect.height / 2) + 70, self.screen_rect.height))]

        wave.control_1 = self._calculate_control_point(wave.point_0, wave.point_1)
        wave.control_2 = self._calculate_control_point(wave.point_2, wave.point_3)
        wave.points = bezier_curve_points(
            np.array(wave.point_0), np.array(wave.control_1),
            np.array(wave.control_2), np.array(wave.point_3)
        )

        wave.left_point = wave.points[0]
        wave.right_point = wave.point_0

        wave.rect = self.pg.Rect(0, 0, 0, 0)

        return wave

    def _calculate_control_point(self, p1, p2):
        """Calculate the midpoint control point with a slight random offset."""
        return [(p1[0] + p2[0]) / 2, p1[1] + random.randrange(-50, 50)]

    def update(self, dt):
        """Update the wave position based on elapsed time."""
        for wave in self.sprites():
            speed = self.settings.wave_speed * dt
            update_wave_points(wave.points, speed)
            wave.left_point = wave.points[0]
            wave.right_point = wave.points[-1]
            wave.rect.x = int(wave.points[0, 0])
            wave.rect.y = int(wave.points[0, 1])
            wave.rect.width = int(abs(wave.points[0, 0] - wave.points[-1, 0]))
            wave.rect.height = int(abs(wave.points[0, 1] - wave.points[-1, 1]))

    def _draw(self):
        """Draw the wave using the computed Bezier curve points."""
        for wave in self.sprites():
            self.pg.draw.lines(self.screen, wave.colour, False, wave.points.astype(np.int32).tolist(), 3)

class RightWaveGroup(Group):
    """A class to manage a single wave fired by the doublerocket."""
    def __init__(self, game_instance):
        super().__init__()
        self.pg = game_instance.pg
        self.game_instance = game_instance
        self.screen = game_instance.screen
        self.screen_rect = game_instance.screen_rect
        self.settings = game_instance.settings

    def create_wave(self, colour):
        """Create a new wave and add it to the group."""
        wave = self.pg.sprite.Sprite()
        wave.colour = colour
        wave.amplitude = float(20)
        wave.frequency = 0.10
        wave.phase = 0
        wave.starting_height = float(self.game_instance.doublerocket.rect.centery)
        wave.points = calculate_points(
            self.game_instance.doublerocket.rect.centerx, self.game_instance.doublerocket.rect.centerx + 100,
            wave.amplitude, wave.frequency, wave.phase, wave.starting_height
        )
        wave.point_0 = wave.points[-1]
        wave.left_point = wave.points[0]
        wave.right_point = wave.point_0
        wave.rect = self.pg.Rect(0, 0, 0, 0)

        return wave

    def update(self, dt):
        """Update the sine wave's points and position."""
        for wave in self.sprites():
            wave.phase += wave.frequency  # Increment phase
            speed = self.settings.wave_speed * dt

            # Use Numba-optimized update function
            update_right_points(
                wave.points, speed, wave.frequency, wave.phase, wave.starting_height, wave.amplitude
            )

            # Update position of the wave's bounding rectangle
            wave.left_point = wave.points[0]
            wave.right_point = wave.points[-1]

    def _draw(self):
        """Draw the wave using the computed Bezier curve points."""
        for wave in self.sprites():
            self.pg.draw.lines(self.screen, wave.colour, False, wave.points.astype(np.int32).tolist(), 3)