class SimulationSettings:
    def __init__(self):
        self.sensors_num = 0
        self.poi_num = 0
        self.sensors_range = 0
        self.sensors_battery = 0
    
    def set_snum(self, num):
        self.sensors_num = num

    def set_pnum(self, num):
        self.poi_num = num

    def set_srange(self, num):
        self.sensors_range = num

    def set_sbattery(self, num):
        self.sensors_battery = num

    def get_snum(self):
        return self.sensors_num
     
    def get_pnum(self):
        return self.poi_num
    
    def get_srange(self):
        return self.sensors_range
    
    def get_sbattery(self):
        return self.sensors_battery