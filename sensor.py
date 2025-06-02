import pygame as p
from enum import Enum
import math as m
import random as r

class LifeBattery(Enum):
    """Battery color states depending on status and energy level."""
    GREEN = (102, 255, 102) # High battery
    YELLOW = (255, 255, 0) # Medium battery
    RED = (255, 51, 51) # Low battery
    SLEEP = (0,0,0) # Sleeping sensor
    FAILURE = (102, 178, 255) # Failed sensor

class State(Enum):
    """Sensor operational states."""
    ACTIVE = 1
    SLEEP = 2
    DEAD = 3
    FAILURE = 4

class Sensor:
    """
    Represents a sensor node in a WSN (Wireless Sensor Network) simulation.
    Handles observation of POIs, data collection and forwarding, and energy management.
    """
    def __init__(self, coords: tuple, radius: int, screen, central=False):
        """
        Initializes a sensor node.

        :param coords: Tuple (x, y) position on the screen.
        :param radius: Integer radius of sensing area.
        :param screen: Pygame surface to draw on.
        :param central: Boolean flag for central/base station node.
        """
        self.is_central = central       
        self.coords = coords
        self.radius = radius
        self.max_battery = 100
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
        """Initialize constant values."""
        self.DOT_SIZE = 7
        self.X, self.Y = self.coords

    def _init_var(self):
        """Initialize sensor state variables."""
        self.curr_battery = self.max_battery
        self.color_battery = LifeBattery.GREEN.value
        self.visible_pois = set()
        self.next_hop = None
        self.state = State.ACTIVE
        self.in_path = True
        self.data_packets = [] 
        self.old_packets_len = 0
        self.lost_packets = 0
        self.last_packet_receive_poi = 0

    def _init_colors(self):
        """Initialize sensor colors."""
        self.CRICLE = (100, 100, 100)
        self.CIRCLE_CENTRAL = (255, 128, 0)

    def _init_shapes(self):
        """Initialize Pygame shapes for drawing."""
        self.x, self.y = self.coords
        self.dot = p.Rect(self.x, self.y, self.DOT_SIZE, self.DOT_SIZE)
        self.circle = p.Rect(self.x + self.dot.width / 2 - self.radius / 2, self.y + self.dot.width / 2 - self.radius / 2, self.radius, self.radius)

    def set_battery_color(self):
        """Update color based on battery level and state."""
        if self.state == State.FAILURE:
            self.color_battery = LifeBattery.FAILURE.value
        elif self.state == State.SLEEP:
            self.color_battery = LifeBattery.SLEEP.value
        elif self.curr_battery >= self.max_battery / 2:
            self.color_battery = LifeBattery.GREEN.value
        elif self.curr_battery >= self.max_battery / 5:
            self.color_battery = LifeBattery.YELLOW.value
        else:
            self.color_battery = LifeBattery.RED.value
        return self.color_battery
    
    def activate_path(self):
        """Recursively activate next-hop sensors in the communication path."""
        if self.next_hop is not None:
            self.next_hop.state = State.ACTIVE
            self.next_hop.activate_path()
    
    def scan_pois(self, pois):
        """
        Scan for POIs within sensing range and start observing unobserved ones.
        :param pois: list of all POIs
        """
        if self.state == State.DEAD:
            return
        for poi in pois:
            xp, yp = poi.get_coords()
            dist = m.sqrt((self.x - xp)**2 + (self.y - yp)**2)
            if dist < self.radius / 2:
                if poi.observed_by is None:
                    self.state = State.ACTIVE
                    self.activate_path()
                    self.curr_battery = 100 # recharge on activation
                    poi.observed_by = self
                    self.visible_pois.add(poi)

    def get_packet_poi(self, battery_receive):
        """
        Collect data packets from all observed POIs.
        :param battery_receive: battery cost for receiving
        """
        self.curr_battery -= battery_receive
        for poi in self.visible_pois:
            packets = poi.release_data()
            self.data_packets.extend(packets)

    def forward_packet(self, battery_send, battery_receive):
        """
        Forward packets to next hop in the path, simulating random loss.
        :param battery_send: battery cost to send
        :param battery_receive: battery cost for next hop to receive
        """
        if self.is_central or (self.next_hop is not None and self.next_hop.state) != State.ACTIVE:
            return

        total_packets = len(self.data_packets)
        if total_packets == 0:
            return
        
        lost = r.randint(0, int(0.1 * total_packets))  # Simulate up to 10% random packet loss
        self.lost_packets += lost
        forwarded = self.data_packets[lost:]

        if self.next_hop is not None:
            self.next_hop.data_packets.extend(forwarded)
            self.curr_battery -= battery_send
            self.next_hop.curr_battery -= battery_receive
        else:
            self.lost_packets += len(forwarded)

        self.data_packets.clear()
    
    def draw(self):
        """Draw sensor and its sensing circle if active."""
        p.draw.rect(self.screen, self.set_battery_color(), self.dot, border_radius=self.DOT_SIZE)

        if self.is_central:
            p.draw.rect(self.screen, self.CIRCLE_CENTRAL, self.circle, 1, border_radius=self.radius)
        elif self.state == State.ACTIVE:
            p.draw.rect(self.screen, self.CRICLE, self.circle, 1, border_radius=self.radius)

    def draw_path_to_next_hop(self):
        """Draw a line to the next hop sensor if active."""
        if self.next_hop is not None and self.next_hop.state != State.ACTIVE:
            return
        if self.next_hop and not self.is_central:
            p.draw.line(self.screen, (240, 240, 240), (self.X + self.DOT_SIZE / 2, self.Y + self.DOT_SIZE / 2), (self.next_hop.X + self.DOT_SIZE / 2, self.next_hop.Y + self.DOT_SIZE / 2), 2)

    def perform_action(self, min_packets=10, battery_idle=0.01, battery_send=0.2, battery_receive=0.1, prob_failure=0.0001):
        """
        Perform sensor's main behavior: data collection, packet forwarding, and energy consumption.
        :param min_packets: minimum packets before forwarding
        :param battery_idle: idle energy cost
        :param battery_send: energy cost to send
        :param battery_receive: energy cost to receive
        :param prob_failure: probability of random failure
        """
        if self.state != State.ACTIVE:
            return

        # Check if battery is depleted
        if self.curr_battery <= 0:
            self.state = State.DEAD
        
        if self.state == State.DEAD:
            # Release all POIs this sensor was observing
            for pois in self.visible_pois:
                    pois.observed_by = None
            self.visible_pois.clear()
            return

        # Simulate sensor failure
        if r.random() < prob_failure:
            self.state = State.FAILURE
            return

        self.draw_path_to_next_hop()

        # Idle battery drain
        if self.is_central == False: self.curr_battery -= battery_idle

        # Forward data if enough packets
        if not self.is_central and len(self.data_packets) >= min_packets:
            self.forward_packet(battery_send, battery_receive)

        # Periodically collect data from POIs
        current_time = p.time.get_ticks()
        if current_time - self.last_packet_receive_poi >= 5000:
            self.get_packet_poi(battery_receive)
            self.last_packet_receive_poi = current_time

    def if_pois_observed(self):
        """Return True if this sensor is observing any POIs."""
        return len(self.visible_pois) > 0
    
    def sleep(self):
        """Put the sensor into sleep mode."""
        self.state = State.SLEEP

    def get_coords(self):
        """Return the sensor's coordinates."""
        return self.coords

