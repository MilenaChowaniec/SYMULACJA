class SimulationSettings:
    """
    A configuration class for simulation parameters.

    This class encapsulates the basic settings of a sensor network simulation,
    including the number of sensors, number of points of interest (POIs),
    and the sensing range of each sensor. It provides setter and getter methods
    to allow easy access and modification of these parameters.
    """
    def __init__(self):
        self.sensors_num = 0
        self.poi_num = 0
        self.sensors_range = 0
    
    def set_snum(self, num):
        self.sensors_num = num

    def set_pnum(self, num):
        self.poi_num = num

    def set_srange(self, num):
        self.sensors_range = num

    def get_snum(self):
        return self.sensors_num
     
    def get_pnum(self):
        return self.poi_num
    
    def get_srange(self):
        return self.sensors_range
    