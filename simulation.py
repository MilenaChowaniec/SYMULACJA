import pygame as p
import sensor as s
import random as r
import game as g
import poi
import math as m

class Simulation:
    def __init__(self, screen, game, settings, width, height):
        self.screen = screen
        self.game = game
        self.settings = settings
        self.SCREEN_WIDTH = width
        self.SCREEN_HEIGHT = height
        self._init_colors()
        self._init_var()
        self._init_sensors_coords()
        self._init_pois_coords()
        self._init_text()
        self._init_shapes()
    
    def _init_var(self):
        self.SIM_SIZE = 640
        self.DIST_FROM_EDGE = 20
        self.sim_x = self.SCREEN_WIDTH - self.SIM_SIZE - self.DIST_FROM_EDGE
        self.sim_y = self.SCREEN_HEIGHT - self.SIM_SIZE - self.DIST_FROM_EDGE
        self.min_dist_sensors = self.settings.get_srange() / 2
        self.min_dist_pois = self.settings.get_srange() / 4
        self.sensors = []
        self.pois = []
        self.main_sensor = None
        self.BACK_HOVERED = False

    def _init_colors(self):
        self.BLACK = (0,0,0)
        self.GREY = (170,170,170)
        self.WHITE =  (255, 255, 255)

    def is_far_enough(self, new_x: int, new_y: int, min_dist: int):
        for sensor in self.sensors:
            x, y = sensor.get_coords()
            dist = m.hypot(new_x - x, new_y - y)
            if dist < min_dist:
                return False
        return True

    def _init_sensors_coords(self):
        max_attempts = 1000
        placed_sensors = 0
        for _ in range(self.settings.get_snum()):
            attempts = 0
            while attempts < max_attempts:
                x = r.randint(self.sim_x + self.DIST_FROM_EDGE // 2, self.sim_x + self.SIM_SIZE - self.DIST_FROM_EDGE // 2)
                y = r.randint(self.sim_y + self.DIST_FROM_EDGE //  2, self.sim_y + self.SIM_SIZE - self.DIST_FROM_EDGE // 2)
                if self.is_far_enough(x, y, self.min_dist_sensors):
                    self.sensors.append(s.Sensor((x, y), self.settings.get_srange(), self.settings.get_sbattery(), self.screen))
                    placed_sensors += 1
                    break
                attempts += 1

        # losowe ustawienie reszty sensorow
        for _ in range(placed_sensors, self.settings.get_snum()):
                x = r.randint(self.sim_x + self.DIST_FROM_EDGE // 2, self.sim_x + self.SIM_SIZE - self.DIST_FROM_EDGE // 2)
                y = r.randint(self.sim_y + self.DIST_FROM_EDGE // 2, self.sim_y + self.SIM_SIZE - self.DIST_FROM_EDGE // 2)
                self.sensors.append(s.Sensor((x, y), self.settings.get_srange(), self.settings.get_sbattery(), self.screen))

    def _init_pois_coords(self):
        max_attempts = 1200
        placed_pois = 0
        for _ in range(self.settings.get_pnum()):
            attempts = 0
            while attempts < max_attempts:
                x = r.randint(self.sim_x + self.DIST_FROM_EDGE // 2, self.sim_x + self.SIM_SIZE - self.DIST_FROM_EDGE // 2)
                y = r.randint(self.sim_y + self.DIST_FROM_EDGE // 2, self.sim_y + self.SIM_SIZE - self.DIST_FROM_EDGE // 2)
                if self.is_far_enough(x, y, self.min_dist_pois):
                    self.pois.append(poi.Poi((x, y), self.screen))
                    placed_pois += 1
                    break
                attempts += 1

        for _ in range(placed_pois, self.settings.get_pnum()):
                x = r.randint(self.sim_x + self.DIST_FROM_EDGE // 2, self.sim_x + self.SIM_SIZE - self.DIST_FROM_EDGE // 2)
                y = r.randint(self.sim_y + self.DIST_FROM_EDGE // 2, self.sim_y + self.SIM_SIZE - self.DIST_FROM_EDGE // 2)
                self.pois.append(poi.Poi((x, y), self.screen))

    def _init_text(self):
        self.back_text = p.font.SysFont('Tahoma', 20).render('go back', True, self.BLACK)

    def _init_shapes(self):
        self.sim_rect = p.Rect(self.sim_x, self.sim_y, self.SIM_SIZE, self.SIM_SIZE)
        self.left_white = p.Rect(0, 0, self.SCREEN_WIDTH - self.SIM_SIZE - self.DIST_FROM_EDGE, self.SCREEN_HEIGHT)
        self.up_white = p.Rect(0, 0, self.SCREEN_WIDTH, self.sim_y)
        self.right_white = p.Rect(self.sim_x + self.SIM_SIZE, 0, self.DIST_FROM_EDGE, self.SCREEN_HEIGHT)
        self.down_white = p.Rect(0, self.sim_y + self.SIM_SIZE, self.SCREEN_WIDTH, self.DIST_FROM_EDGE)
        self.back_text_coords = p.Rect(30, 10, 80, 30)
        self.back_button_rect = p.Rect(25, 10, 80, 30)
        self.back_button_hovered = self.back_button_rect

    def handle_mouse_hovered(self, event):
        if self.back_button_rect.collidepoint(event.pos):
            self.BACK_HOVERED = True
            p.mouse.set_cursor(p.SYSTEM_CURSOR_HAND)
        else: 
            self.BACK_HOVERED = False
            p.mouse.set_cursor(p.SYSTEM_CURSOR_ARROW)

    def handle_mouse_pressed(self, event):
        if event.button == 1:
            if self.back_button_rect.collidepoint(event.pos):
                p.mouse.set_cursor(p.SYSTEM_CURSOR_ARROW)
                self.game.change_scene(g.Scene.MENU)

    def handle_event(self, event):
        if event.type == p.QUIT:
            p.quit()
            quit()
        if event.type == p.MOUSEBUTTONDOWN:
            self.handle_mouse_pressed(event)
        if event.type == p.MOUSEMOTION:
            self.handle_mouse_hovered(event)

    def draw(self):
        p.draw.rect(self.screen, self.BLACK, self.sim_rect, 1)
        for dot in self.pois:
            dot.draw()
        for dot in self.sensors:
            dot.draw()
        p.draw.rect(self.screen, self.WHITE, self.left_white)
        p.draw.rect(self.screen, self.WHITE, self.up_white)
        p.draw.rect(self.screen, self.WHITE, self.right_white)
        p.draw.rect(self.screen, self.WHITE, self.down_white)
        if self.BACK_HOVERED:
            p.draw.rect(self.screen, self.GREY, self.back_button_hovered)
        self.screen.blit(self.back_text, self.back_text_coords)
        p.draw.rect(self.screen, self.BLACK, self.back_button_rect, 1)

    def render(self):
        self.screen.fill(self.WHITE)
        self.draw()

    def update(self):
        p.display.flip()