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
        self.buffer = 0

    def _init_shapes(self):
        x, y = self.coords
        self.dot = p.Rect(x, y, self.DOT_SIZE, self.DOT_SIZE)
    
    # jest prob szans ze poi wygeneruje pakiet, ta funkcja bedzie wywolywana co sekunde
    def generate_data(self, prob):
        if r.random() < prob: self.buffer += 1

    # funkcja bedzie odpalana gdy sensor bedzie odpalal skanowanie pakietow co stale 3 sekundy
    def release_data(self):
        packets = self.buffer
        self.buffer = 0
        return packets

    def draw(self):
        p.draw.rect(self.screen, (153,100,153), self.dot, 0, border_radius= 2)

    def perform_action(self):
        self.draw()
    
    def get_coords(self):
        return self.coords
    