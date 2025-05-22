import pygame as p
from enum import Enum
import menu
import simulationInterface as interface

class Size(Enum):
    HEIGHT_OPT = 600
    LENGTH_OPT = 600
    HEIGHT_SIM = 700
    LENGTH_SIM = 1200

class Scene(Enum):
    MENU = 1
    SIMULATION = 2 

class Game:
    def __init__(self):
        p.init()
        self.screen = p.display.set_mode((Size.LENGTH_OPT.value, Size.HEIGHT_OPT.value))
        p.display.set_caption("choice")
        self._init_scenes()

    def _init_scenes(self):
        self.curr_scene = Scene.MENU
        self.menu = menu.Menu(self.screen, self)

        self.scenes = {
            Scene.MENU : self.menu,
        }

    def change_scene(self, scene: Scene, simulation_settings = None):
        if scene == Scene.MENU:
            self.screen = p.display.set_mode((Size.LENGTH_OPT.value, Size.HEIGHT_OPT.value))
            p.display.set_caption("Menu")
        else:
            self.screen = p.display.set_mode((Size.LENGTH_SIM.value, Size.HEIGHT_SIM.value))
            p.display.set_caption("Simulation")
            self.scenes[Scene.SIMULATION] = interface.SimulationInterface(self.screen, self, simulation_settings, Size.LENGTH_SIM.value, Size.HEIGHT_SIM.value)

        self.curr_scene = scene

    def _poll_events(self):
        for event in p.event.get():
            self.scenes[self.curr_scene].handle_event(event)

    def play(self):
        while True:
            self._poll_events()
            self.scenes[self.curr_scene].render()
            self.scenes[self.curr_scene].update()
    