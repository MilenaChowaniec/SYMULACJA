import pygame as p
import random as r

class Poi:
    def __init__(self, coords: tuple, screen):
        """
        Initialize a Point of Interest (POI) object.

        :param coords: Tuple containing the (x, y) coordinates of the POI.
        :param screen: Pygame screen where the POI will be drawn.
        """
        self.coords = coords
        self.screen = screen
        self._init_var()
        self._init_shapes()

    def _init_var(self):
        """
        Initialize POI internal variables.
        """
        self.DOT_SIZE = 10 # Size of the POI dot on the screen
        self.observed_by = None # Sensor currently observing this POI (if any)

        self.buffer = []  # Buffer to store generated data packets
        self.data_range = (15.0, 35.0)   # Temperature range for simulated data
        self.reliability = r.uniform(0.8, 1.0)   # Random reliability score between 0.8 and 1.0

    def _init_shapes(self):
        """
        Initialize graphical representation of the POI.
        """
        x, y = self.coords
        self.dot = p.Rect(x, y, self.DOT_SIZE, self.DOT_SIZE)
    
    def generate_data(self, prob):
        """
        Generate a data packet with a given probability.

        :param prob: Probability of generating data at this time step.
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
        Release all buffered data packets and clear the buffer.

        :return: List of data packets.
        """
        packets = self.buffer.copy()
        self.buffer.clear()
        return packets

    def draw(self):
        """
        Draw the POI on the screen.
        """
        color = (153, 100, 153)
        p.draw.rect(self.screen, color, self.dot, 0, border_radius=2)

    def get_coords(self):
        """
        Get the coordinates of the POI.

        :return: Tuple (x, y) representing the POI position.
        """
        return self.coords