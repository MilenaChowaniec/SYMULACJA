import pygame as p
import sensor as s
import random as r
import poi
import math as m

class Simulation:
    def __init__(self, screen, settings, width, height, sim_size, dist):
        self.SIM_SIZE = sim_size
        self.DIST_FROM_EDGE = dist
        self.screen = screen
        self.settings = settings
        self.SCREEN_WIDTH = width
        self.SCREEN_HEIGHT = height

        self._init_consts()
        self._init_var()
        self._init_sensors_coords()
        self._init_pois_coords()

    # stale, ktore nigdy nie ulegna zmianie w trakcie dzialania symulacji
    def _init_consts(self):
        self.SIM_WIN_X = self.SCREEN_WIDTH - self.SIM_SIZE - self.DIST_FROM_EDGE
        self.SIM_WIN_Y = self.SCREEN_HEIGHT - self.SIM_SIZE - self.DIST_FROM_EDGE        
        self.MIN_DIST_SENSORS = 7
        self.MIN_DIST_POI_FROM_SENSOR = 20 # minimalny dystans poi od sensora
        self.MIN_DIST_POIS = self.settings.get_srange() / 3
        self.sensors = []
        self.pois = []
    
    def _init_var(self):
        self.last_gen_packet_time = 0 # do mierzenia sekundy w generowaniu pakietu
        self.last_packet_receive_poi = 0
        self.last_packet_forwarded = 0
        self.prob_gen_packet = 0.7 # p-stwo wygenerowania pakietu w poi

        self.min_packet_to_send = 100

        self.battery_drain_idle = 0.001
        self.battery_drain_send = 0.002
        self.battery_drain_receive = 0.005

    def is_far_enough(self, new_x: int, new_y: int, min_dist: int, tab):
        for elem in tab:
            x, y = elem.get_coords()
            dist = m.hypot(new_x - x, new_y - y)
            if dist < min_dist:
                return False
        return True

    def _init_sensors_coords(self):
        self.sensors.append(s.Sensor((self.SIM_WIN_X + self.SIM_SIZE // 2, self.SIM_WIN_Y + self.SIM_SIZE // 2), self.settings.get_srange(), self.settings.get_sbattery(), self.screen, True))
        max_attempts = 2000
        placed_sensors = 0
        for _ in range(self.settings.get_snum()):
            attempts = 0
            while attempts < max_attempts:
                x = r.randint(self.SIM_WIN_X + self.DIST_FROM_EDGE // 2, self.SIM_WIN_X + self.SIM_SIZE - self.DIST_FROM_EDGE // 2)
                y = r.randint(self.SIM_WIN_Y + self.DIST_FROM_EDGE // 2, self.SIM_WIN_Y + self.SIM_SIZE - self.DIST_FROM_EDGE // 2)
                if self.is_far_enough(x, y, self.MIN_DIST_SENSORS, self.sensors):
                    self.sensors.append(s.Sensor((x, y), self.settings.get_srange(), self.settings.get_sbattery(), self.screen))
                    placed_sensors += 1
                    break
                attempts += 1

        # losowe ustawienie reszty sensorow
        for _ in range(placed_sensors, self.settings.get_snum()):
                x = r.randint(self.SIM_WIN_X + self.DIST_FROM_EDGE // 2, self.SIM_WIN_X + self.SIM_SIZE - self.DIST_FROM_EDGE // 2)
                y = r.randint(self.SIM_WIN_Y + self.DIST_FROM_EDGE // 2, self.SIM_WIN_Y + self.SIM_SIZE - self.DIST_FROM_EDGE // 2)
                self.sensors.append(s.Sensor((x, y), self.settings.get_srange(), self.settings.get_sbattery(), self.screen))

    def _init_pois_coords(self):
        max_attempts = 1000
        placed_pois = 0
        for _ in range(self.settings.get_pnum()):
            attempts = 0
            while attempts < max_attempts:
                x = r.randint(self.SIM_WIN_X + self.DIST_FROM_EDGE // 2, self.SIM_WIN_X + self.SIM_SIZE - self.DIST_FROM_EDGE // 2)
                y = r.randint(self.SIM_WIN_Y + self.DIST_FROM_EDGE // 2, self.SIM_WIN_Y + self.SIM_SIZE - self.DIST_FROM_EDGE // 2)
                if self.is_far_enough(x, y, self.MIN_DIST_POIS, self.pois) and self.is_far_enough(x, y, self.MIN_DIST_POI_FROM_SENSOR, self.sensors):
                    self.pois.append(poi.Poi((x, y), self.screen))
                    placed_pois += 1
                    break
                attempts += 1

        for _ in range(placed_pois, self.settings.get_pnum()):
                x = r.randint(self.SIM_WIN_X + self.DIST_FROM_EDGE // 2, self.SIM_WIN_X + self.SIM_SIZE - self.DIST_FROM_EDGE // 2)
                y = r.randint(self.SIM_WIN_Y + self.DIST_FROM_EDGE // 2, self.SIM_WIN_Y + self.SIM_SIZE - self.DIST_FROM_EDGE // 2)
                self.pois.append(poi.Poi((x, y), self.screen))

    def find_path_to_central(self):
        central = self.sensors[0]
        sensor_graph = {sensor: [] for sensor in self.sensors} # klucz jest sensorem, a wartosciami lista jego sasiadow

        # dla kazdego sensora znajduje jego sasiadow w promieniu sensor.radius
        for sensor in self.sensors:
            for other in self.sensors:
                if sensor == other:
                    continue
                x1, y1 = sensor.get_coords()
                x2, y2 = other.get_coords()
                dist = m.hypot(x1 - x2, y1 - y2)
                if dist <= sensor.radius:
                    sensor_graph[sensor].append(other)

        self.paths_to_central = {} # kluczem jest sensor, a wartoscia sciezka od tego sensora do centralnego

        for sensor in self.sensors:
            if sensor == central: # dla centralnego, jego sciezka to on sam
                self.paths_to_central[sensor] = [central]
                continue               
            # BFS
            visited = set() # sensory, ktore zostaly juz odwiedzone w jednej iteracji
            queue = [(sensor, [sensor])] # tu bedzie zapisana sciezka dla konkretnej iteracji
            while queue:
                # current - obecnie sprawdzany sensor, path - sciezka tego sensora do centalnego
                current, path = queue.pop(0)
                if current in visited:
                    continue
                visited.add(current)
                
                for neighbor in sensor_graph[current]:
                    if neighbor == central:
                        self.paths_to_central[sensor] = path + [central]
                        break
                    else:
                        queue.append((neighbor, path + [neighbor]))
                if sensor in self.paths_to_central:
                    if sensor == central: sensor.next_hope = central
                    else: sensor.next_hop = self.paths_to_central[sensor][1]
                    break

            if sensor not in self.paths_to_central:
                self.paths_to_central[sensor] = None
                sensor.in_path = False

    def sleep_idle_sensors(self):
        for sensor in self.sensors:
            # jesli sensor obserwuje jakies poi, nie mozna go uspic
            if sensor.if_pois_observed(): continue

            # bool, sprawdzamy czy sensor posiada sciezke do centrali
            has_own_path = self.paths_to_central.get(sensor) is not None
            # bool, sprawdzamy czy sensor znajduje sie w jakiejs innej sciezce do centrali
            in_other_path = any(sensor in path for s, path in self.paths_to_central.items()
                                if path is not None and s != sensor)
            
            if not has_own_path and not in_other_path:
                # nie ma zadnej sciezki i nie obserwuje poi usypiamy
                sensor.sleep()
                continue

            is_critical = False
            for other_sensor, path in self.paths_to_central.items():
                if other_sensor == sensor or path is None:
                    continue
                if not other_sensor.if_pois_observed():
                    continue
                if sensor in path:
                    is_critical = True
                    break
            
            if not is_critical:
                sensor.sleep()
    
    # co sekunde, kazde poi bedzie generowac jeden pakiet
    def generate_packets_in_pois(self, prob):
        for dot in self.pois:
            dot.generate_data(prob)

    def draw(self):
        for dot in self.pois:
            dot.draw()
        for dot in self.sensors:
            dot.draw()

    def scan_pois(self):
        for sensor in self.sensors:
            sensor.scan_pois(self.pois)

    def perform_actions(self):
        current_time = p.time.get_ticks()

        for sensor in self.sensors:
            sensor.perform_action(self.min_packet_to_send, self.battery_drain_idle)
        for poi in self.pois:
            poi.perform_action()

        self.scan_pois()
        self.find_path_to_central()
        self.sleep_idle_sensors()

        # co 1 sekunde generowane sa pakiety w pois
        if current_time - self.last_gen_packet_time >= 1000:
            self.generate_packets_in_pois(self.prob_gen_packet)
            self.last_gen_packet_time = current_time
        
        
        
