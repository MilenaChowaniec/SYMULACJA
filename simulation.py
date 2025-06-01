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
        self.log_file = open("central_data_log.txt", "w")  # otwieramy plik na start
        self.font = p.font.SysFont('Tahoma', 20)

    def _init_consts(self):
        self.SIM_WIN_X = self.SCREEN_WIDTH - self.SIM_SIZE - self.DIST_FROM_EDGE
        self.SIM_WIN_Y = self.SCREEN_HEIGHT - self.SIM_SIZE - self.DIST_FROM_EDGE
        self.MIN_DIST_SENSORS = 7
        self.MIN_DIST_POI_FROM_SENSOR = 20
        self.MIN_DIST_POIS = self.settings.get_srange() / 3
        self.sensors = [] # lista wszystkich sensorow
        self.pois = [] # lista wszystkich pois

    def _init_var(self):
        self.last_gen_packet_time = 0
        self.last_sa_time = 0
        self.sa_interval = 1000
        self.sa_trials = 50
        self.prob_gen_packet = 0.7
        self.min_packet_to_send = 10
        self.battery_drain_idle = 0.001
        self.battery_drain_send = 1
        self.battery_drain_receive = 5

    # spr czy odlelgosc od elementow jest odpowiednia
    def is_far_enough(self, new_x: int, new_y: int, min_dist: int, tab):
        for elem in tab:
            x, y = elem.get_coords()
            if m.hypot(new_x - x, new_y - y) < min_dist:
                return False
        return True

    # inicjacja koords sensorow
    def _init_sensors_coords(self):
        self.sensors.append(s.Sensor((self.SIM_WIN_X + self.SIM_SIZE // 2, self.SIM_WIN_Y + self.SIM_SIZE // 2), self.settings.get_srange(), self.screen, True))
        max_attempts = 2000
        for _ in range(self.settings.get_snum()):
            for _ in range(max_attempts):
                x = r.randint(self.SIM_WIN_X, self.SIM_WIN_X + self.SIM_SIZE)
                y = r.randint(self.SIM_WIN_Y, self.SIM_WIN_Y + self.SIM_SIZE)
                if self.is_far_enough(x, y, self.MIN_DIST_SENSORS, self.sensors):
                    self.sensors.append(s.Sensor((x, y), self.settings.get_srange(), self.screen))
                    break

    # inicjacja koords pois
    def _init_pois_coords(self):
        max_attempts = 1000
        for _ in range(self.settings.get_pnum()):
            for _ in range(max_attempts):
                x = r.randint(self.SIM_WIN_X, self.SIM_WIN_X + self.SIM_SIZE)
                y = r.randint(self.SIM_WIN_Y, self.SIM_WIN_Y + self.SIM_SIZE)
                if self.is_far_enough(x, y, self.MIN_DIST_POIS, self.pois) and self.is_far_enough(x, y, self.MIN_DIST_POI_FROM_SENSOR, self.sensors):
                    self.pois.append(poi.Poi((x, y), self.screen))
                    break

    # kazdemu aktywnemu sensorowi przypisujemy sciezke
    def find_path_to_central(self):
        self.central = self.sensors[0]
        sensor_graph = {}

        # Tworzymy graf tylko z aktywnych i żywych sensorów
        active_sensors = [se for se in self.sensors if se.state == s.State.ACTIVE and se.curr_battery > 0]

        # Dodajemy centralny sensor niezależnie od stanu (bo do niego prowadzą ścieżki)
        if self.central not in active_sensors:
            active_sensors.append(self.central)

        for sensor in active_sensors:
            sensor_graph[sensor] = []
            for other in active_sensors:
                if sensor == other:
                    continue
                x1, y1 = sensor.get_coords()
                x2, y2 = other.get_coords()
                dist = m.hypot(x1 - x2, y1 - y2)
                if dist <= sensor.radius:
                    sensor_graph[sensor].append(other)

        self.paths_to_central = {}

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
        for sensor in self.sensors:
            if sensor.state == s.State.DEAD:
                return
            if sensor.if_pois_observed(): 
                continue
            has_own_path = self.paths_to_central.get(sensor) is not None
            in_other_path = any(sensor in path for s, path in self.paths_to_central.items() if path and s != sensor)
            # jesli nie ma swojej sciezki, albo nie jest w zadnej to go usypiamy
            if not has_own_path and not in_other_path:
                sensor.sleep()
                continue

            #sprawdza, czy jest w sciezce do sensora ktory obserwuje jakies poi, jesli tak to usypiamy
            is_critical = any(sensor in path for s, path in self.paths_to_central.items()
                              if s != sensor and path and s.if_pois_observed())
            if not is_critical:
                sensor.sleep()

    # po prostu wywoluje generowanie pakietow
    def generate_packets_in_pois(self, prob):
        for dot in self.pois:
            dot.generate_data(prob)

    # skanowanie pois
    def scan_pois(self):
        for sensor in self.sensors:
            sensor.scan_pois(self.pois)

    def reactivate_sensors_for_uncovered_pois(self):
        for poi in self.pois:
            if poi.observed_by is None:
                best_sensor = None
                min_dist = float('inf')
                for sensor in self.sensors:
                    if sensor.state == s.State.SLEEP and sensor.curr_battery > 0:
                        dist = m.dist(sensor.get_coords(), poi.get_coords())
                        if dist < sensor.radius and dist < min_dist:
                            best_sensor = sensor
                            min_dist = dist
                if best_sensor:
                    best_sensor.state = s.State.ACTIVE
                    poi.observed_by = best_sensor
                    best_sensor.visible_pois.add(poi)

    def filter_redundant_data(self):
        THRESHOLD_DISTANCE = self.settings.get_srange()  # max dystans do sąsiada
        TEMP_DIFF_THRESHOLD = 0.5  # różnica temperatury uznana za podobną

        for sensor in self.sensors:
            sensor.skip_sending = False

        for sensor in self.sensors:
            if not sensor.data_packets:
                continue
            
            # Weź ostatni pakiet z tego sensora
            last_packet = sensor.data_packets[-1]
            last_temp = last_packet.get("temperature", None)
            if last_temp is None:
                continue

            similar_data_count = 0
            for neighbor in self.sensors:
                if neighbor == sensor or not neighbor.data_packets:
                    continue
                
                # Dystans między sensorami
                distance = m.dist(sensor.get_coords(), neighbor.get_coords())
                if distance > THRESHOLD_DISTANCE:
                    continue
                
                neighbor_last_packet = neighbor.data_packets[-1]
                neighbor_temp = neighbor_last_packet.get("temperature", None)
                if neighbor_temp is None:
                    continue
                
                # Sprawdź, czy temperatury są podobne
                if abs(last_temp - neighbor_temp) < TEMP_DIFF_THRESHOLD:
                    similar_data_count += 1
            
            # Jeśli co najmniej 2 sąsiadów ma podobne dane - sensor może pominąć wysyłanie
            if similar_data_count >= 2:
                sensor.skip_sending = True
                half = len(sensor.data_packets) // 2
                sensor.data_packets = sensor.data_packets[half:]
                print(f"[SKIP] Sensor at {sensor.get_coords()} skipping. Similar neighbors: {similar_data_count}, packets left: {len(sensor.data_packets)}")
            else:
                sensor.skip_sending = False

    def create_stats(self):
        
        active_sensors = sum(1 for se in self.sensors if se.state == s.State.ACTIVE)
        avg_battery = sum(se.curr_battery for se in self.sensors if se.state == s.State.ACTIVE) / active_sensors
        sleeping_sensors = sum(1 for se in self.sensors if se.state == s.State.SLEEP) - 1
        total_packets = sum(len(se.data_packets) for se in self.sensors)
        dead_sensors = sum(1 for se in self.sensors if se.state == s.State.DEAD)
        lost_packets = sum(se.lost_packets for se in self.sensors)
        
        self.stats = [
            f"Average battery level: {avg_battery:.1f}%",
            f"Active sensors: {active_sensors}",
            f"Sleeping sensors: {sleeping_sensors}",
            f"Dead sensors: {dead_sensors}",
            f"Packets in the network: {total_packets}",
            f"Packets at the central node: {len(self.central.data_packets)}",
            f"Lost packets: {lost_packets}",
        ]
    
    def draw_stats(self):
        for i, text in enumerate(self.stats):
            img = self.font.render(text, True, (0,0,0))
            self.screen.blit(img, (25,100 + i * 30))

    def perform_actions(self):
        current_time = p.time.get_ticks()


        self.scan_pois()
        self.find_path_to_central()
        self.sleep_idle_sensors()
        self.reactivate_sensors_for_uncovered_pois()


        for sensor in self.sensors:
            sensor.perform_action(self.log_file, self.min_packet_to_send, self.battery_drain_idle, self.battery_drain_receive)
        for poi in self.pois:
            poi.perform_action()
        self.filter_redundant_data()
        self.create_stats()

        if current_time - self.last_gen_packet_time >= 1000:
            self.generate_packets_in_pois(self.prob_gen_packet)
            self.last_gen_packet_time = current_time
        if current_time - self.last_sa_time >= self.sa_interval:
            self.last_sa_time = current_time
