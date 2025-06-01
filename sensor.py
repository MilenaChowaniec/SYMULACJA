import pygame as p
from enum import Enum
import math as m
import random as r

class LifeBattery(Enum):
    GREEN = (102, 255, 102)
    YELLOW = (255, 255, 0)
    RED = (255, 51, 51)
    SLEEP = (0,0,0)

class State(Enum):
    ACTIVE = 1
    SLEEP = 2
    DEAD = 3

class Sensor:
    def __init__(self, coords: tuple, radius: int, screen, central=False):
        self.is_central = central       
        self.coords = coords
        self.radius = radius
        self.max_battery = 100
        self.screen = screen
        self.skip_sending = False
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
        self.visible_pois = set()
        self.next_hop = None
        self.state = State.ACTIVE
        self.in_path = True

        self.data_packets = []  # lista pakietów (zamiast liczby)
        self.old_packets_len = 0
        self.lost_packets = 0
        self.last_packet_receive_poi = 0

    def _init_colors(self):
        self.CRICLE = (100, 100, 100)
        self.CIRCLE_CENTRAL = (255, 128, 0)

    def _init_shapes(self):
        self.x, self.y = self.coords
        self.dot = p.Rect(self.x, self.y, self.DOT_SIZE, self.DOT_SIZE)
        self.circle = p.Rect(self.x + self.dot.width / 2 - self.radius / 2,
                             self.y + self.dot.width / 2 - self.radius / 2,
                             self.radius, self.radius)

    def set_battery_color(self):
        if self.state == State.SLEEP:
            self.color_battery = LifeBattery.SLEEP.value
        elif self.curr_battery >= self.max_battery / 2:
            self.color_battery = LifeBattery.GREEN.value
        elif self.curr_battery >= self.max_battery / 5:
            self.color_battery = LifeBattery.YELLOW.value
        else:
            self.color_battery = LifeBattery.RED.value
        return self.color_battery
    
    def scan_pois(self, pois):
        if self.state == State.DEAD:
            return
        for poi in pois:
            xp, yp = poi.get_coords()
            dist = m.sqrt((self.x - xp)**2 + (self.y - yp)**2)
            if dist < self.radius / 2:
                if poi.observed_by is None:
                    self.state = State.ACTIVE
                    self.curr_battery = 100
                    poi.observed_by = self
                    self.visible_pois.add(poi)

    def get_packet_poi(self, battery_receive):
        self.curr_battery -= battery_receive
        for poi in self.visible_pois:
            packets = poi.release_data()
            self.data_packets.extend(packets)

    def forward_packet(self, battery_send, battery_receive, log_file):
        if self.is_central or self.next_hop.state != State.ACTIVE:
            return

        if self.skip_sending:
            print(f"Sensor {self.coords} pomija wysyłanie danych.")
            return

        # symulacja utraty pakietów – losowo usuwamy kilka przed przekazaniem
        total_packets = len(self.data_packets)
        if total_packets == 0:
            return
        
        lost = r.randint(0, int(0.2 * total_packets))  # max 20% strat
        self.lost_packets += lost
        forwarded = self.data_packets[lost:]

        if self.next_hop is not None:
            if self.next_hop.is_central == True:
                log_file.write(f"[CENTRAL] Received {len(forwarded)} packets\n")
                print(f"[CENTRAL] Received {len(forwarded)} packets")

                for dp in forwarded:
                    time_sec = dp['timestamp'] / 1000  # konwersja na sekundy
                    log_line = f"From POI {dp['poi_coords']} at {time_sec:.2f}s - temp: {dp['temperature']}C\n"
                    #print(log_line, end='')  # end='' żeby nie dublować nowej linii
                    log_file.write(log_line)

            self.next_hop.data_packets.extend(forwarded)
            self.curr_battery -= battery_send
            self.next_hop.curr_battery -= battery_receive

        self.data_packets.clear()
    
    def reduce_battery_idle(self, battery_idle):
        self.curr_battery -= battery_idle
    
    def sleep(self):
        self.state = State.SLEEP
                
    def if_pois_observed(self):
        return len(self.visible_pois) > 0
    
    def draw(self):
        p.draw.rect(self.screen, self.set_battery_color(), self.dot, border_radius=self.DOT_SIZE)

        if self.is_central:
            p.draw.rect(self.screen, self.CIRCLE_CENTRAL, self.circle, 1, border_radius=self.radius)
        elif self.state == State.ACTIVE:
            p.draw.rect(self.screen, self.CRICLE, self.circle, 1, border_radius=self.radius)

    def draw_path_to_next_hop(self):
        if self.next_hop is not None and self.next_hop.state != State.ACTIVE:
            return
        if self.next_hop and not self.is_central:
            p.draw.line(self.screen, (240, 240, 240),
                        (self.X + self.DOT_SIZE / 2, self.Y + self.DOT_SIZE / 2),
                        (self.next_hop.X + self.DOT_SIZE / 2, self.next_hop.Y + self.DOT_SIZE / 2), 2)

    def perform_action(self, log_file, min_packets=10, battery_idle=0.01, battery_send=0.2, battery_receive=0.1):
        self.draw()

        if self.state == State.SLEEP or self.state == State.DEAD:
            return

        #jesli bateria padla, to sensor umiera
        if self.curr_battery <= 0:
            self.state = State.DEAD
        
        # jesli sensor jest dead, to przestaje obserwowac wszystkie poois
        if self.state == State.DEAD:
            for pois in self.visible_pois:
                    pois.observed_by = None
            self.visible_pois.clear()
            return

        self.draw_path_to_next_hop()
        if self.is_central == False: self.reduce_battery_idle(battery_idle)

        current_time = p.time.get_ticks()

        if not self.is_central and len(self.data_packets) >= min_packets:
            self.forward_packet(battery_send, battery_receive, log_file)

        if current_time - self.last_packet_receive_poi >= 5000:
            self.get_packet_poi(battery_receive)
            self.last_packet_receive_poi = current_time

    def get_coords(self):
        return self.coords

