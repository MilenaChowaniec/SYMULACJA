import pygame as p
import sensor as s
import random as r
import poi
import math as m
import liveGraph as graph

class Simulation:
    def __init__(self, screen, settings, width, height, sim_size, dist):
        """
        Initialize the simulation environment.

        :param screen: pygame Surface to draw on.
        :param settings: Simulation settings/configuration object.
        :param width: Width of the window.
        :param height: Height of the window.
        :param sim_size: Size (width and height) of the simulation area.
        :param dist: Distance from edges of the window to the simulation area.
        """
        self.SIM_SIZE = sim_size
        self.DIST_FROM_EDGE = dist
        self.screen = screen
        self.settings = settings
        self.SCREEN_WIDTH = width
        self.SCREEN_HEIGHT = height

        self._init_consts()
        self._init_var()
        self._init_pois_coords()
        self._init_sensors_coords()
        # Initialize live plot for sensor activity visualization
        self.live_plot = graph.LivePlot(self.screen,p.Rect(50, 520, 400, 150), "Sensor activity over time", max_points=80)
        self.create_stats() # Initialize simulation statistics display


    def _init_consts(self):
        """
        Initialize constants and main attributes used throughout the simulation.
        """
        self.SIM_WIN_X = self.SCREEN_WIDTH - self.SIM_SIZE - self.DIST_FROM_EDGE
        self.SIM_WIN_Y = self.SCREEN_HEIGHT - self.SIM_SIZE - self.DIST_FROM_EDGE
        self.MIN_DIST_SENSORS = 7
        self.MIN_DIST_POI_FROM_SENSOR = 20
        self.MIN_DIST_POIS = self.settings.get_srange() / 3
        self.sensors = [] # List containing all sensor objects
        self.pois = [] # List containing all POI objects
        self.STOP_SIM = False # Flag to stop simulation when conditions are met

    def _init_var(self):
        """
        Initialize runtime parameters and variables controlling sensor behavior.
        """
        self.last_gen_packet_time = 0
        self.prob_gen_packet = 0.7
        self.min_packet_to_send = 10
        self.battery_drain_idle = 0.02
        self.battery_drain_send = 2
        self.battery_drain_receive = 6

    # spr czy odlelgosc od elementow jest odpowiednia
    def is_far_enough(self, new_x: int, new_y: int, min_dist: int, tab):
        """
        Check if the point (new_x, new_y) is at least min_dist away from all elements in tab.

        :param new_x: X coordinate of the new point.
        :param new_y: Y coordinate of the new point.
        :param min_dist: Minimum required distance from other elements.
        :param tab: List of objects that have get_coords() method returning (x, y).
        :return: True if new point is far enough from all elements, False otherwise.
        """
        for elem in tab:
            x, y = elem.get_coords()
            if m.hypot(new_x - x, new_y - y) < min_dist:
                return False
        return True

    def _init_sensors_coords(self):
        """
        Initialize sensor positions:
        - One sensor placed centrally and active.
        - One sensor placed near each POI.
        - Remaining sensors placed randomly within simulation window,
          respecting minimum distance constraints.
        """
        # Place central sensor in the middle of simulation window
        self.sensors.append(s.Sensor((self.SIM_WIN_X + self.SIM_SIZE // 2, self.SIM_WIN_Y + self.SIM_SIZE // 2), self.settings.get_srange(), self.screen, True))
        self.central = self.sensors[0]
        sensor_range = self.settings.get_srange()
        num_sensors = self.settings.get_snum()
        max_attempts = 1000

        # 1. Place one sensor near each POI (within 80% of sensor range)
        for poi_obj in self.pois:
            placed = False
            for _ in range(max_attempts):
                angle = r.uniform(0, 2 * m.pi)
                radius = r.uniform(0, sensor_range * 0.8)
                x_offset = int(poi_obj.get_coords()[0] + radius * m.cos(angle))
                y_offset = int(poi_obj.get_coords()[1] + radius * m.sin(angle))

                if self.is_far_enough(x_offset, y_offset, self.MIN_DIST_SENSORS, self.sensors):
                    sensor = s.Sensor((x_offset, y_offset), sensor_range, self.screen)
                    self.sensors.append(sensor)
                    placed = True
                    break
            if not placed:
                print("Nie udało się umieścić sensora przy POI.")

        # 2. Place remaining sensors randomly in the simulation area
        remaining = num_sensors - len(self.sensors)
        for _ in range(remaining):
            for _ in range(max_attempts):
                x = r.randint(self.SIM_WIN_X, self.SIM_WIN_X + self.SIM_SIZE)
                y = r.randint(self.SIM_WIN_Y, self.SIM_WIN_Y + self.SIM_SIZE)
                if self.is_far_enough(x, y, self.MIN_DIST_SENSORS, self.sensors):
                    self.sensors.append(s.Sensor((x, y), self.settings.get_srange(), self.screen))
                    break

    def _init_pois_coords(self):
        """
        Initialize POI positions randomly inside the simulation window,
        respecting minimum distance constraints between POIs and sensors.
        """
        max_attempts = 1000
        for _ in range(self.settings.get_pnum()):
            for _ in range(max_attempts):
                x = r.randint(self.SIM_WIN_X, self.SIM_WIN_X + self.SIM_SIZE)
                y = r.randint(self.SIM_WIN_Y, self.SIM_WIN_Y + self.SIM_SIZE)
                if self.is_far_enough(x, y, self.MIN_DIST_POIS, self.pois) and self.is_far_enough(x, y, self.MIN_DIST_POI_FROM_SENSOR, self.sensors):
                    self.pois.append(poi.Poi((x, y), self.screen))
                    break

    def find_path_to_central(self):
        """
        For each sensor that is active or sleeping, compute a path to the central sensor.
        The path is built based on sensor proximity (edges between sensors within half their radius).
        Sensors outside of communication range have no path (None).
        """
        sensor_graph = {}

        # Only consider active or sleeping sensors for graph edges
        active_sensors = [se for se in self.sensors if se.state == s.State.ACTIVE or se.state == s.State.SLEEP]

        # Ensure central sensor is included in graph
        if self.central not in active_sensors:
            active_sensors.append(self.central)

        # Build adjacency list for sensor graph
        for sensor in active_sensors:
            sensor_graph[sensor] = []
            for other in active_sensors:
                if sensor == other:
                    continue
                x1, y1 = sensor.get_coords()
                x2, y2 = other.get_coords()
                dist = m.hypot(x1 - x2, y1 - y2)
                if dist <= sensor.radius / 2:
                    sensor_graph[sensor].append(other)

        self.paths_to_central = {}

        # BFS to find shortest path from each sensor to central sensor
        for sensor in self.sensors:
            if sensor not in sensor_graph:
                self.paths_to_central[sensor] = None
                sensor.in_path = False
                continue

            if sensor == self.central:
                self.paths_to_central[sensor] = [self.central]
                sensor.next_hop = None
                continue

            visited = set()
            queue = [(sensor, [sensor])]
            found = False

            while queue:
                current, path = queue.pop(0)
                if current in visited:
                    continue
                visited.add(current)

                for neighbor in sensor_graph.get(current, []):
                    if neighbor == self.central:
                        self.paths_to_central[sensor] = path + [self.central]
                        sensor.next_hop = self.paths_to_central[sensor][1]
                        found = True
                        break
                    else:
                        queue.append((neighbor, path + [neighbor]))

                if found:
                    break

            if not found:
                self.paths_to_central[sensor] = None
                sensor.in_path = False

    def sleep_idle_sensors(self):
        """
        Put sensors to sleep if they are not observing any POI and are not part of any critical path.
        Sensors without own path and not in others’ paths are also put to sleep.
        """
        for sensor in self.sensors:
            if sensor.state == s.State.DEAD:
                return
            if sensor.if_pois_observed(): 
                continue # Sensor observes POIs, stays awake
            has_own_path = self.paths_to_central.get(sensor) is not None
            in_other_path = any(sensor in path for s, path in self.paths_to_central.items() if path and s != sensor)
            # Sleep sensors with no own path and not in others’ paths
            if not has_own_path and not in_other_path:
                sensor.sleep()
                continue

            # Sleep if not critical: not in path to sensor that observes POIs
            is_critical = any(sensor in path for s, path in self.paths_to_central.items()
                              if s != sensor and path and s.if_pois_observed())
            if not is_critical:
                sensor.sleep()
            else:
                sensor.state = s.State.ACTIVE

    def generate_packets_in_pois(self, prob):
        """
        Generate data packets in each POI with probability `prob`.

        :param prob: Probability that a POI generates a packet during this call.
        """
        for dot in self.pois:
            dot.generate_data(prob)

    def scan_pois(self):
        """
        Each sensor scans the POIs in range to update which POIs it observes.
        """
        for sensor in self.sensors:
            sensor.scan_pois(self.pois)

    def create_stats(self):
        """
        Compute statistics about the network:
        - Average battery level of active sensors
        - Number of active, sleeping, dead, failed sensors
        - Number of packets in network and at central node
        - Number of lost packets
        Update the live plot with average battery level.
        If no active sensors remain, stop simulation.
        """
        active_sensors = sum(1 for se in self.sensors if se.state == s.State.ACTIVE)
        if active_sensors == 0: 
            self.STOP_SIM = True
            return
        
        avg_battery = sum(se.curr_battery for se in self.sensors if se.state == s.State.ACTIVE) / active_sensors
        sleeping_sensors = sum(1 for se in self.sensors if se.state == s.State.SLEEP) - 1
        total_packets = sum(len(se.data_packets) for se in self.sensors)
        dead_sensors = sum(1 for se in self.sensors if se.state == s.State.DEAD)
        lost_packets = sum(se.lost_packets for se in self.sensors)
        failed_sensors = sum(1 for se in self.sensors if se.state == s.State.FAILURE)
        self.live_plot.update(avg_battery)
        self.stats = [
            f"Average battery level: {avg_battery:.1f}%",
            f"Active sensors: {active_sensors}",
            f"Sleeping sensors: {sleeping_sensors}",
            f"Dead sensors: {dead_sensors}",
            f"Packets in the network: {total_packets}",
            f"Packets at the central node: {len(self.central.data_packets)}",
            f"Lost packets: {lost_packets}",
            f"Failed sensors: {failed_sensors}",
        ]

    def draw_stats(self):
        """
        Render the current simulation statistics on the screen.
        """
        font = p.font.SysFont('Tahoma', 20)
        for i, text in enumerate(self.stats):
            img = font.render(text, True, (0,0,0))
            self.screen.blit(img, (25,50 + i * 30))

    def draw_sensors_pois(self):
        """
        Draw all sensors and POIs on the screen.
        """
        for sensor in self.sensors:
            sensor.draw()
        for poi in self.pois:
            poi.draw()

    def perform_actions(self):
        """
        Execute a simulation step:
        - Scan POIs for sensors
        - Update paths to central sensor
        - Put idle sensors to sleep
        - Check if any POI is unobserved, stop simulation if so
        - Update sensor states (battery, failure)
        - Generate new data packets periodically
        """
        current_time = p.time.get_ticks()
        
        if not self.STOP_SIM:
            self.scan_pois()
            self.find_path_to_central()
            self.sleep_idle_sensors()

            # Stop simulation if any POI is not observed
            for poi in self.pois:
                if poi.observed_by == None:
                    self.STOP_SIM = True
                    return

            failed_sensors = sum(1 for se in self.sensors if se.state == s.State.FAILURE)
            active_sensors = sum(1 for se in self.sensors if se.state == s.State.ACTIVE)

            if active_sensors == 0: 
                self.STOP_SIM = True
                return

            failure_prob = 0.00001
            if failed_sensors / active_sensors > 0.5:
                failure_prob = 0  # Disable failures if too many sensors failed

            for sensor in self.sensors:
                sensor.perform_action(self.min_packet_to_send, self.battery_drain_idle, self.battery_drain_receive, failure_prob)
            self.create_stats()

            # Generate packets in POIs every 1 second (1000 ms)
            if current_time - self.last_gen_packet_time >= 1000:
                self.generate_packets_in_pois(self.prob_gen_packet)
                self.last_gen_packet_time = current_time
