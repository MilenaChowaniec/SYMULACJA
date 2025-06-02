import pygame as p
from enum import Enum
import menu
import simulationInterface as interface

# Enum representing different screen sizes
class Size(Enum):
    HEIGHT_OPT = 600 # Height for the menu screen
    LENGTH_OPT = 600 # Width for the menu screen
    HEIGHT_SIM = 700 # Height for the simulation screen
    LENGTH_SIM = 1200 # Width for the simulation screen

# Enum representing possible scenes/states of the game
class Scene(Enum):
    MENU = 1 # Menu scene
    SIMULATION = 2  # Simulation scene

class Game:
    """
    Main game class that handles scene management, event polling, and game loop.
    """
    def __init__(self):
        """
        Initializes the game by setting up the window and the initial scene.
        """
        p.init()
        self.screen = p.display.set_mode((Size.LENGTH_OPT.value, Size.HEIGHT_OPT.value))
        p.display.set_caption("Menu")
        self._init_scenes() # Set up initial scenes

    def _init_scenes(self):
        """
        Initializes available scenes and sets the current scene to the menu.
        """
        self.curr_scene = Scene.MENU # Start with the menu scene
        self.menu = menu.Menu(self.screen, self)

        self.scenes = {
            Scene.MENU : self.menu,
            # Simulation will be added dynamically when needed
        }

    def change_scene(self, scene: Scene, simulation_settings = None):
        """
        Changes the current scene to the given one. Dynamically loads simulation if needed.

        :param scene: Scene to switch to
        :param simulation_settings: Optional settings for simulation scene
        """
        if scene == Scene.MENU:
            self.screen = p.display.set_mode((Size.LENGTH_OPT.value, Size.HEIGHT_OPT.value))
            p.display.set_caption("Menu")
        else:
            self.screen = p.display.set_mode((Size.LENGTH_SIM.value, Size.HEIGHT_SIM.value))
            p.display.set_caption("Simulation")
            # Lazy-load simulation interface when switching to simulation scene
            self.scenes[Scene.SIMULATION] = interface.SimulationInterface(self.screen, self, simulation_settings, Size.LENGTH_SIM.value, Size.HEIGHT_SIM.value)

        self.curr_scene = scene

    def _poll_events(self):
        """
        Polls all Pygame events and delegates them to the current scene for handling.
        """
        for event in p.event.get():
            self.scenes[self.curr_scene].handle_event(event)

    def play(self):
        """
        Starts the main game loop. Continuously polls events, updates, and renders the current scene.
        """
        while True:
            self._poll_events() # Handle input/events
            self.scenes[self.curr_scene].render()
            self.scenes[self.curr_scene].update()
    