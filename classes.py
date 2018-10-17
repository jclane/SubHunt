            
class Harddrive:
    """Class to create objects for harddrives."""
    
    def __init__(self, part_num, brand, description, connector, capacity, speed, physical_size, height, interface, do_not_sub, subbed):
        self.part_num = part_num
        self.brand = brand
        self.description = description     
        self.connector = connector
        self.capacity = capacity
        self.speed = speed
        self.physical_size = physical_size
        self.height = height
        self.interface = interface
        self.do_not_sub = do_not_sub
        self.subbed = subbed

    
    def __str__(self):
        return self.part_num + " | " + self.brand + " | " + self.description
    
    def __eq__(self, other):
        if (isinstance(other, Harddrive)
            and self.physical_size == other.physical_size
            and self.height == other.height
            and self.connector == other.connector):
            return (self.capacity == other.capacity 
                and self.speed == other.speed 
                and self.interface == other.interface)            

    
    def __ne__(self, other):
        if (isinstance(other, Harddrive)
            and self.physical_size == other.physical_size
            and self.height == other.height
            and self.connector == other.connector):
            return (self.capacity != other.capacity 
                and self.speed != other.speed 
                and self.interface != other.interface)            
           

class SolidStateDrive(Harddrive):
    """Class to create objects for SSDs."""
    
    def __init__(self, part_num, brand, description, connector, capacity, physical_size, interface, do_not_sub, subbed):
        self.part_num = part_num
        self.brand = brand
        self.description = description
        self.connector = connector
        self.capacity = capacity
        self.physical_size = physical_size
        self.interface = interface
        self.do_not_sub = do_not_sub
        self.subbed = subbed
            
            
class Processor:
    """Class to create objects for CPUs."""
    
    def __init__(self, series, type, cores, speed, turbo_speed, cache, socket, 
                thermal_design_power, core):
        
        self.series = series
        self.type = type
        self.cores = cores
        self.speed = speed
        self.turbo_speed = turbo_speed
        self.cache = cache
        self.socket = socket
        self.thermal_design_power = thermal_design_power
        self.core = core


class Memory:
    """Class to create objects for RAM"""
    
    def __init__(self, part_num, speed, brand, connector, capacity, description, 
                do_not_sub, subbed):
                
        self.part_num = part_num
        self.brand = brand
        self.speed = speed
        self.connector = connector
        self.capacity = capacity
        self.description = description
        self.do_not_sub = do_not_sub
        self.subbed = subbed
        
    def __str__(self):
        return self.brand + " | " + self.part_num + " | " + self.capacity + " | " + self.speed + " | " + self.description    
        
    def __eq__(self, other):
        if isinstance(other, Memory) and self.connector == other.connector:
            return (self.capacity == other.capacity 
                and self.speed == other.speed) 
            
    def __ne__(self, other):
        if isinstance(other, Memory) and self.connector == other.connector:
            return (self.capacity != other.capacity 
                and self.speed != other.speed) 
