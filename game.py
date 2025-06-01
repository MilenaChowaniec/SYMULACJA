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
    def __init__(self):
        """
        Initialize the Game object, including pygame, screen, and scenes.
        """
        p.init()
        self.screen = p.display.set_mode((Size.LENGTH_OPT.value, Size.HEIGHT_OPT.value))
        p.display.set_caption("Menu")
        self._init_scenes() # Set up initial scenes

    def _init_scenes(self):
        """
        Initialize the available scenes and set the current scene to MENU.
        """
        self.curr_scene = Scene.MENU
        self.menu = menu.Menu(self.screen, self)

        self.scenes = {
            Scene.MENU : self.menu,
            # Simulation will be added dynamically when needed
        }

    def change_scene(self, scene: Scene, simulation_settings = None):
        """
        Change the current scene (menu <-> simulation), updating the screen size and title.

        :param scene: The target scene to switch to (Scene Enum).
        :param simulation_settings: Optional settings to pass to the simulation interface.
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
        Poll and dispatch pygame events to the current scene's handler.
        """
        for event in p.event.get():
            self.scenes[self.curr_scene].handle_event(event)

    def play(self):
        """
        Main game loop: process events, render the current scene, and update logic.
        """
        while True:
            self._poll_events()
            self.scenes[self.curr_scene].render()
            self.scenes[self.curr_scene].update()
    