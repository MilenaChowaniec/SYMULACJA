import pygame as p
import random as r

class Poi:
    def __init__(self, coords: tuple, screen):
        self.coords = coords
        self.screen = screen
        self._init_var()
        self._init_shapes()

    def _init_var(self):
        self.DOT_SIZE = 10
        self.observed_by = None

        self.buffer = []  # bufor przechowujący pakiety danych (np. temperaturę)
        self.data_range = (15.0, 35.0)  # przykładowy zakres temperatur
        self.reliability = r.uniform(0.8, 1.0)  # losowa niezawodność/czujność punktu

    def _init_shapes(self):
        x, y = self.coords
        self.dot = p.Rect(x, y, self.DOT_SIZE, self.DOT_SIZE)
    
    # Generuje losowy pakiet danych środowiskowych (np. temperatura)
    def generate_data(self, prob):
        if r.random() < prob:
            measurement = {
                "temperature": round(r.uniform(*self.data_range), 2),
                "timestamp": p.time.get_ticks(),
                "poi_coords": self.coords,
                "reliability": self.reliability
            }
            self.buffer.append(measurement)

    # Zwraca wszystkie zgromadzone dane i czyści bufor
    def release_data(self):
        packets = self.buffer.copy()
        self.buffer.clear()
        return packets

    def draw(self):
        color = (153, 100, 153)
        p.draw.rect(self.screen, color, self.dot, 0, border_radius=2)

    def perform_action(self):
        self.draw()

    def get_coords(self):
        return self.coords