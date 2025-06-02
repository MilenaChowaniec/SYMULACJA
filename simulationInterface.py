import pygame as p
import game as g
import simulation as s
import sensor as se

class SimulationInterface:
    def __init__(self, screen, game, settings, width, height):
        """
        Initialize the SimulationInterface.

        :param screen: The pygame display surface where everything is drawn.
        :param game: The game controller object to manage scenes.
        :param settings: Settings object containing simulation parameters.
        :param width: Width of the screen.
        :param height: Height of the screen.
        """
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
        """
        Initialize variables for layout, sizes, and state flags.
        """
        self.SIM_SIZE = 640
        self.DIST_FROM_EDGE = 20
        self.sim_x = self.SCREEN_WIDTH - self.SIM_SIZE - self.DIST_FROM_EDGE
        self.sim_y = self.SCREEN_HEIGHT - self.SIM_SIZE - self.DIST_FROM_EDGE
        self.BACK_HOVERED = False
        self.SENSOR_SIZE = 7
        self.POI_SIZE = 10

    def _init_colors(self):
        """
        Initialize color constants used in rendering.
        """
        self.BLACK = (0,0,0)
        self.GREY = (170,170,170)
        self.WHITE = (255, 255, 255)
        self.RED = (100,0,0)

    def _init_text(self):
        """
        Initialize rendered text surfaces for buttons and messages.
        """
        self.back_text = p.font.SysFont('Tahoma', 20).render('go back', True, self.BLACK)
        self.stop_sim_text = p.font.SysFont('Tahoma', 22).render('POIs are not covered. Simulation has been stopped.', True, self.RED)
        self.start_again_txt = p.font.SysFont('Tahoma', 22).render('Go back to start again.', True, self.RED)

    def _init_shapes(self):
        """
        Initialize pygame Rect objects for UI elements positions and sizes.
        """
        self.sim_rect = p.Rect(self.sim_x, self.sim_y, self.SIM_SIZE, self.SIM_SIZE)
        self.left_white = p.Rect(0, 0, self.SCREEN_WIDTH - self.SIM_SIZE - self.DIST_FROM_EDGE, self.SCREEN_HEIGHT)
        self.up_white = p.Rect(0, 0, self.SCREEN_WIDTH, self.sim_y)
        self.right_white = p.Rect(self.sim_x + self.SIM_SIZE, 0, self.DIST_FROM_EDGE, self.SCREEN_HEIGHT)
        self.down_white = p.Rect(0, self.sim_y + self.SIM_SIZE, self.SCREEN_WIDTH, self.DIST_FROM_EDGE)
        self.back_text_coords = p.Rect(30, 10, 80, 30)
        self.back_button_rect = p.Rect(25, 10, 80, 30)
        self.back_button_hovered = self.back_button_rect
        self.stop_sim_text_coords = p.Rect(25,300,50, 50)
        self.start_again_text_coords = p.Rect(25,325,50, 50)

    def draw(self):
        """
        Draw the main simulation interface elements including background boxes and buttons.
        """
        p.draw.rect(self.screen, self.BLACK, self.sim_rect, 1)
        p.draw.rect(self.screen, self.WHITE, self.left_white)
        p.draw.rect(self.screen, self.WHITE, self.up_white)
        p.draw.rect(self.screen, self.WHITE, self.right_white)
        p.draw.rect(self.screen, self.WHITE, self.down_white)
        if self.BACK_HOVERED:
            p.draw.rect(self.screen, self.GREY, self.back_button_hovered)
        self.screen.blit(self.back_text, self.back_text_coords)
        p.draw.rect(self.screen, self.BLACK, self.back_button_rect, 1)

    def draw_legend(self):
        """
        Draw the legend explaining sensor battery states and POI representation.
        """
        p.draw.rect(self.screen, se.LifeBattery.GREEN.value, (self.sim_x, self.sim_y - 15, self.SENSOR_SIZE, self.SENSOR_SIZE), border_radius=self.SENSOR_SIZE)
        self.screen.blit(p.font.SysFont('Tahoma', 15).render('sensor battery above 50%', True, self.BLACK), p.Rect(self.sim_x + 15, self.sim_y - 20, 80, 30))
        p.draw.rect(self.screen, se.LifeBattery.YELLOW.value, (self.sim_x, self.sim_y - 35, self.SENSOR_SIZE, self.SENSOR_SIZE), border_radius=self.SENSOR_SIZE)
        self.screen.blit(p.font.SysFont('Tahoma', 15).render('sensor battery below 50%', True, self.BLACK), p.Rect(self.sim_x + 15, self.sim_y - 40, 80, 30))
        p.draw.rect(self.screen, se.LifeBattery.RED.value, (self.sim_x + 200, self.sim_y - 15, self.SENSOR_SIZE, self.SENSOR_SIZE), border_radius=self.SENSOR_SIZE)
        self.screen.blit(p.font.SysFont('Tahoma', 15).render('sensor battery below 20%', True, self.BLACK), p.Rect(self.sim_x + 15+200, self.sim_y - 20, 80, 30))
        p.draw.rect(self.screen, se.LifeBattery.SLEEP.value, (self.sim_x + 200, self.sim_y - 35, self.SENSOR_SIZE, self.SENSOR_SIZE), border_radius=self.SENSOR_SIZE)
        self.screen.blit(p.font.SysFont('Tahoma', 15).render('sensor in sleep mode', True, self.BLACK), p.Rect(self.sim_x + 15 + 200, self.sim_y - 40, 80, 30))
        p.draw.rect(self.screen, se.LifeBattery.FAILURE.value, (self.sim_x + 400, self.sim_y - 15, self.SENSOR_SIZE, self.SENSOR_SIZE), border_radius=self.SENSOR_SIZE)
        self.screen.blit(p.font.SysFont('Tahoma', 15).render('sensor failed', True, self.BLACK), p.Rect(self.sim_x + 15 + 400, self.sim_y - 20, 80, 30))
        p.draw.rect(self.screen, (153, 100, 153), p.Rect(self.sim_x + 400, self.sim_y - 35, self.POI_SIZE, self.POI_SIZE), 0, border_radius=2)
        self.screen.blit(p.font.SysFont('Tahoma', 15).render('POI', True, self.BLACK), p.Rect(self.sim_x + 15 + 400, self.sim_y - 40, 80, 30))

    def simulation_stop(self):
        """
        Stop the simulation, display stop messages and save stats to a log file.
        """
        self.screen.blit(self.stop_sim_text, self.stop_sim_text_coords)
        self.screen.blit(self.start_again_txt, self.start_again_text_coords)
        sim_stats = self.simulation.stats
        with open("stats_log.txt", "w") as file:
            for line in sim_stats:
                file.write(line + "\n")

    def handle_mouse_hovered(self, event):
        """
        Handle mouse hover events, changing cursor and button state.

        :param event: pygame event for mouse motion
        """
        if self.back_button_rect.collidepoint(event.pos):
            self.BACK_HOVERED = True
            p.mouse.set_cursor(p.SYSTEM_CURSOR_HAND)
        else: 
            self.BACK_HOVERED = False
            p.mouse.set_cursor(p.SYSTEM_CURSOR_ARROW)

    def handle_mouse_pressed(self, event):
        """
        Handle mouse press events, particularly the back button click.

        :param event: pygame event for mouse button down
        """
        if event.button == 1:
            if self.back_button_rect.collidepoint(event.pos):
                self.simulation.STOP_SIM = False
                p.mouse.set_cursor(p.SYSTEM_CURSOR_ARROW)
                self.simulation_stop()
                self.game.change_scene(g.Scene.MENU)

    def handle_event(self, event):
        """
        Handle general pygame events including quit, mouse button, and mouse motion.

        :param event: pygame event to handle
        """
        if event.type == p.QUIT:
            self.simulation_stop()
            p.quit()
            quit()
        if event.type == p.MOUSEBUTTONDOWN:
            self.handle_mouse_pressed(event)
        if event.type == p.MOUSEMOTION:
            self.handle_mouse_hovered(event)

    def render(self):
        """
        Render the simulation interface and simulation elements, or stop screen if simulation stopped.
        """
        if self.simulation.STOP_SIM == False:
            self.screen.fill(self.WHITE)
            self.simulation.draw_sensors_pois()
            self.draw()
            self.simulation.perform_actions()
            self.draw_legend()
            self.simulation.draw_stats()
            self.simulation.live_plot.draw()
        else:
            self.simulation.live_plot.paused = True
            self.simulation_stop()

    def update(self):
        """
        Update the pygame display with rendered changes.
        """
        p.display.flip()

