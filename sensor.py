import pygame as p
from enum import Enum
import math as m

class LifeBattery(Enum):
    GREEN = (102, 255, 102)
    YELLOW = (255, 255, 0)
    RED = (255, 51, 51)
    SLEEP = (0,0,0)

class State(Enum):
    ACTIVE = 1
    SLEEP = 2

class Sensor:
    def __init__(self, coords: tuple, radius: int, battery: int, screen, central = False):
        self.is_central = central       
        self.coords = coords
        self.radius = radius
        self.max_battery = 100
        if central == True: self.max_battery += 60
        self.screen = screen
        self._init_consts()
        self._init_var()
        self._init_colors()
        self._init_shapes()

    def __hash__(self):
        return hash(self.coords)
    
    def __eq__(self, other):
        return isinstance(other, Sensor) and self.coords == other.coords 

    def _init_consts(self):
        self.DOT_SIZE = 7
        self.X, self.Y = self.coords

    def _init_var(self):
        self.curr_battery = self.max_battery
        self.color_battery = LifeBattery.GREEN.value
        self.visible_pois = []
        self.next_hop = None
        self.state = State.ACTIVE
        self.in_path = True
        self.packets = 0
        # to trzeba obliczyc na podstawie czasu symulacji, ktory wybiera uzytkownik
        self.lost_packets = 0
        self.packets = 0
        self.last_packet_receive_poi = 0
    
    def _init_colors(self):
        self.CRICLE = (100,100,100)
        self.CIRCLE_CENTRAL = (255, 128, 00)

    def _init_shapes(self):
        self.x, self.y = self.coords
        self.dot = p.Rect(self.x, self.y, self.DOT_SIZE, self.DOT_SIZE)
        self.circle = p.Rect(self.x + self.dot.width / 2 - self.radius / 2, self.y + self.dot.width / 2 - self.radius / 2, self.radius, self.radius)

    def set_battery_color(self):
        if self.state == State.SLEEP:
            self.color_battery = LifeBattery.SLEEP.value
            return self.color_battery
        
        if self.curr_battery >= self.max_battery / 2:
            self.color_battery = LifeBattery.GREEN.value
        elif self.curr_battery >= self.max_battery / 5:
            self.color_battery = LifeBattery.YELLOW.value
        else:
            self.color_battery = LifeBattery.RED.value

        return self.color_battery
    
    def scan_pois(self, pois):
        for poi in pois:
            xp, yp = poi.get_coords()
            if poi.observed_by is None and m.sqrt((self.x - xp)**2 + (self.y - yp)**2) < self.radius / 2:
                poi.observed_by = self
                self.visible_pois.append(poi)

    # ta funkcja bedzie wywolywana co stale 3 sekundy i bedzie obnizac baterie
    def get_packet_poi(self, battery_receive):
        self.curr_battery -= battery_receive
        for poi in self.visible_pois:
            self.packets += poi.release_data()
    
    def get_packet_sensor(self, packets, battery_receive):
        self.curr_battery -= battery_receive
        self.packets += packets

    # sprawdza, czy osiagnieto minimalna ilosc pakietow do wyslania
    # wywoluje get_packet_sensor na next_hop
    # losuje liczbe pakietow 0-len(packets) ktora zostaje utracona
    def forward_packet(self, battery_send, battery_receive):
        self.curr_battery -= battery_send
        if self.next_hop == None:
            self.packets = 0
        else: self.next_hop.get_packet_sensor(self.packets, battery_receive)
    
        # stale wyladowywanie sie
    def reduce_battery_idle(self, battery_idle):
        self.curr_battery -= battery_idle
    
    def sleep(self):
        self.state = State.SLEEP
                
    def if_pois_observed(self):
        if len(self.visible_pois) == 0:
            return False
        return True
    
    def draw(self):
        p.draw.rect(self.screen, self.set_battery_color(), self.dot, border_radius=self.DOT_SIZE)

        if self.is_central:
            # jesli jest to centralny sensor, to ma pomaranczow okrag
            p.draw.rect(self.screen, self.CIRCLE_CENTRAL, self.circle, 1, border_radius=self.radius)
        else:
            if self.state == State.ACTIVE: 
                # jesli jest to zwykly sensor i jest aktywny, to ma czarny okrag
                p.draw.rect(self.screen, self.CRICLE, self.circle, 1, border_radius=self.radius)

    def draw_path_to_next_hop(self):
        if self.next_hop is not None and self.is_central == False and self.state == State.ACTIVE:
            p.draw.line(self.screen, (240,240,240), (self.X + self.DOT_SIZE/2, self.Y+ self.DOT_SIZE/2), (self.next_hop.X+ self.DOT_SIZE/2, self.next_hop.Y+ self.DOT_SIZE/2), 2)

    def perform_action(self, min_packets, battery_idle=0.01, battery_send=0.2, battery_receive=0.1):
        current_time = p.time.get_ticks()
        self.draw_path_to_next_hop()
        self.draw()
        self.reduce_battery_idle(battery_idle)

        if self.is_central == True:
            print(self.packets)

        # tylko 
        if self.is_central == False and self.packets >= min_packets:
            self.forward_packet(battery_send, battery_receive)

        if current_time - self.last_packet_receive_poi >= 5000:
            self.get_packet_poi(battery_receive)
            self.last_packet_receive_poi = current_time

    def get_coords(self):
        return self.coords
