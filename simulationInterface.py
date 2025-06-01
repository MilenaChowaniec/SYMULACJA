import pygame as p
import game as g
import simulation as s

class SimulationInterface:
    def __init__(self, screen, game, settings, width, height):
        self.screen = screen
        self.game = game
        self.SCREEN_WIDTH = width
        self.SCREEN_HEIGHT = height
        self._init_colors()
        self._init_var()
        self._init_text()
        self._init_shapes()
        self.simulation = s.Simulation(self.screen, settings, width, height, self.SIM_SIZE, self.DIST_FROM_EDGE)
    
    def _init_var(self):
        self.SIM_SIZE = 640
        self.DIST_FROM_EDGE = 20
        self.sim_x = self.SCREEN_WIDTH - self.SIM_SIZE - self.DIST_FROM_EDGE
        self.sim_y = self.SCREEN_HEIGHT - self.SIM_SIZE - self.DIST_FROM_EDGE
        self.BACK_HOVERED = False

    def _init_colors(self):
        self.BLACK = (0,0,0)
        self.GREY = (170,170,170)
        self.WHITE =  (255, 255, 255)

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

    def draw(self):
        p.draw.rect(self.screen, self.BLACK, self.sim_rect, 1)
        p.draw.rect(self.screen, self.WHITE, self.left_white)
        p.draw.rect(self.screen, self.WHITE, self.up_white)
        p.draw.rect(self.screen, self.WHITE, self.right_white)
        p.draw.rect(self.screen, self.WHITE, self.down_white)
        if self.BACK_HOVERED:
            p.draw.rect(self.screen, self.GREY, self.back_button_hovered)
        self.screen.blit(self.back_text, self.back_text_coords)
        p.draw.rect(self.screen, self.BLACK, self.back_button_rect, 1)

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

    # TO JEST WYWOLYWANE W GAME
    def render(self):
        self.screen.fill(self.WHITE)
        self.simulation.perform_actions()
        self.draw()
        self.simulation.draw_stats()

    # I TO  
    def update(self):
        p.display.flip()

