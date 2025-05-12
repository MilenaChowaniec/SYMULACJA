import pygame as p
from enum import Enum

class LifeBattery(Enum):
    GREEN = (102, 255, 102)
    YELLOW = (255, 255, 0)
    RED = (255, 51, 51)


class Sensor:
    def __init__(self, coords: tuple, radius: int, battery: int, screen):
        self.coords = coords
        self.radius = radius
        self.battery = battery
        self.screen = screen
        self._init_var()
        self._init_colors()
        self._init_shapes()

    def _init_var(self):
        self.dot_size = 7
        self.life_battery = LifeBattery.GREEN.value
    
    def _init_colors(self):
        self.CRICLE = (100,100,100)

    def _init_shapes(self):
        x, y = self.coords
        self.dot = p.Rect(x, y, self.dot_size, self.dot_size)
        self.circle = p.Rect(x + self.dot.width / 2 - self.radius / 2, y + self.dot.width / 2 - self.radius / 2, self.radius, self.radius)

    def reduce_battery(self):
        return self.life_battery

    def draw(self):
        p.draw.rect(self.screen, self.reduce_battery(), self.dot, border_radius=self.dot_size)
        p.draw.rect(self.screen, self.CRICLE, self.circle, 1, border_radius=self.radius)
    
    def get_coords(self):
        return self.coords
