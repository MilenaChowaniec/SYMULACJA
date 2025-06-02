import pygame as p
import random as r

class Poi:
    """
    Represents a Point of Interest (POI) in the sensor network simulation.
    Each POI can generate data and be observed by a sensor.
    """
    def __init__(self, coords: tuple, screen):
        """
        Initializes the POI at given coordinates.

        :param coords: Tuple of (x, y) screen coordinates.
        :param screen: Pygame surface for rendering.
        """
        self.coords = coords
        self.screen = screen
        self._init_var()
        self._init_shapes()

    def _init_var(self):
        """Initializes POI variables such as data, size, and reliability."""
        self.DOT_SIZE = 10 # Size of the POI dot on the screen
        self.observed_by = None # Sensor currently observing this POI (if any)

        self.buffer = []  # Buffer to store generated data packets
        self.data_range = (15.0, 35.0)   # Temperature range for simulated data
        self.reliability = r.uniform(0.8, 1.0)   # Random reliability score between 0.8 and 1.0

    def _init_shapes(self):
        """Initializes the visual representation (rectangle) of the POI."""
        x, y = self.coords
        self.dot = p.Rect(x, y, self.DOT_SIZE, self.DOT_SIZE)
    
    def generate_data(self, prob):
        """
        Simulates data generation based on a probability threshold.

        :param prob: Float in [0, 1] indicating the chance of data generation.
        """
        if r.random() < prob:
            measurement = {
                "temperature": round(r.uniform(*self.data_range), 2),
                "timestamp": p.time.get_ticks(),
                "poi_coords": self.coords,
                "reliability": self.reliability
            }
            self.buffer.append(measurement)

    def release_data(self):
        """
        Releases all stored data packets and clears the buffer.

        :return: List of generated data packets.
        """
        packets = self.buffer.copy()
        self.buffer.clear()
        return packets

    def draw(self):
        """Draws the POI as a small purple square on the screen."""
        color = (153, 100, 153)
        p.draw.rect(self.screen, color, self.dot, 0, border_radius=2)

    def get_coords(self):
        """
        Returns the (x, y) coordinates of the POI.

        :return: Tuple with POI coordinates.
        """
        return self.coords