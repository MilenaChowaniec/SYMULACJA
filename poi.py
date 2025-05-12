import pygame as p

class Poi:
    def __init__(self, coords: tuple, screen):
        self.coords = coords
        self.screen = screen
        self._init_var()
        self._init_shapes()

    def _init_var(self):
        self.dot_size = 10

    def _init_shapes(self):
        x, y = self.coords
        self.dot = p.Rect(x, y, self.dot_size, self.dot_size)

    def draw(self):
        p.draw.rect(self.screen, (153,100,153), self.dot, 0, border_radius= 2)
    