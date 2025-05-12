import pygame as p
import game
import simulationSettings as settings
import sliderDot as slider

class Menu:
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self._init_text()
        self._init_buttons()
        self._init_colors()
        self._init_var()
        self._init_sliders()

    def _init_var(self):
        self.GEN_HOVERED = False
        self.curr_slider = None
        
        self.LINE_LENGTH = 400
        self.CIRCLE_RADIUS = 15

        self.settings = settings.SimulationSettings()

    def _init_text(self):
        self.generate = p.font.SysFont('Tahoma', 30).render('GENERATE', True, (0, 0, 0))

    def _init_colors(self):
        self.BLACK = (0,0,0)
        self.GREY = (170,170,170)
        self.WHITE = (255, 255, 255)

    def _init_buttons(self):
        self.generate_button = p.Rect(self.screen.get_width() / 2 - self.generate.get_width() / 2 - 10, 500 - 3, self.generate.get_width() + 20, self.generate.get_height() + 6)
    
    def _init_sliders(self):
        self.sliders = {
            "snum": slider.SliderDot('number of sensors', self.screen, 70, '10', '30'),
            "pnum": slider.SliderDot('number of POIs', self.screen, 170, '10', '30'),
            "srange": slider.SliderDot('sensors range', self.screen, 270, '150', '300'),
            "sbattery": slider.SliderDot('sensors battery life', self.screen, 370, '30', '160')
        }

    def handle_mouse_hovered(self):
        if self.generate_button.collidepoint(p.mouse.get_pos()): 
            self.GEN_HOVERED = True
            p.mouse.set_cursor(p.SYSTEM_CURSOR_HAND)
        else: 
            self.GEN_HOVERED = False
            p.mouse.set_cursor(p.SYSTEM_CURSOR_ARROW)
    
    def handle_mouse_pressed(self, event, x):
        if event.button == 1:
            if self.generate_button.collidepoint(event.pos):
                self.settings.set_snum(self.sliders["snum"].get_settings())
                self.settings.set_pnum(self.sliders["pnum"].get_settings())
                self.settings.set_sbattery(self.sliders["sbattery"].get_settings())
                self.settings.set_srange(self.sliders["srange"].get_settings())
                self.GEN_HOVERED = False
                p.mouse.set_cursor(p.SYSTEM_CURSOR_ARROW)
                self.game.change_scene(game.Scene.SIMULATION, self.settings)
            
            for slider in self.sliders:
                if self.sliders[slider].get_dot_rect().collidepoint(event.pos):
                    self.sliders[slider].drag(x)
                    self.curr_slider = self.sliders[slider]
                    p.mouse.set_cursor(p.SYSTEM_CURSOR_HAND)
                    break


    def handle_mouse_motion(self, x):
        if self.curr_slider is not None and self.curr_slider.get_if_drag():
            self.curr_slider.move(x)
            p.mouse.set_cursor(p.SYSTEM_CURSOR_HAND)

    def handle_mouse_released(self, x):
        if self.curr_slider is not None:
             self.curr_slider.drag(x)
             self.curr_slider = None
             p.mouse.set_cursor(p.SYSTEM_CURSOR_ARROW)


    def handle_event(self, event):
        mouse_x, mouse_y = p.mouse.get_pos()
        if event.type == p.QUIT:
            p.quit()
            quit()
        if event.type == p.MOUSEMOTION:
            self.handle_mouse_hovered()
        if event.type == p.MOUSEBUTTONDOWN:
            self.handle_mouse_pressed(event, mouse_x)
        if event.type == p.MOUSEMOTION:
            self.handle_mouse_motion(mouse_x)
        if event.type == p.MOUSEBUTTONUP:
            self.handle_mouse_released(mouse_x)


    def draw(self):
        if self.GEN_HOVERED == True:    
            p.draw.rect(self.screen, self.GREY, self.generate_button)
        self.screen.blit(self.generate, (self.screen.get_width() / 2 - self.generate.get_width() / 2, 500))
        p.draw.rect(self.screen, self.BLACK, (self.screen.get_width() / 2 - self.generate.get_width() / 2 - 10, 500 - 3, self.generate.get_width() + 20, self.generate.get_height() + 6), 1)

        for slider in self.sliders:
            self.sliders[slider].draw()
        
    def render(self):
        self.screen.fill(self.WHITE)
        self.draw()

    def update(self):
        p.display.flip()