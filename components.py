from data_io.load_case import load_case 
from collections import defaultdict
import itertools as iter
import sys



class Lines(object):
    def __init__(self, loaded_data_file):
        self.data = loaded_data_file
        self.bus = loaded_data_file["bus"]
        self.lines = loaded_data_file["branch"]
        self.baseMVA = float(loaded_data_file['baseMVA']['baseMVA'][0])

    ##DEMAND PYOMO DICTIONARY DEFINITIONS
    #Demand Identifiers (for Set D)
    def identifiers(self):
        return [line_name for line_name in self.lines['name']]

    def bus_line_in(self):
        bus_branch = defaultdict(list)
        # Populate the dictionary with branches
        for bus_name, name in self.lines.groupby('to_busname')['name'].agg(list).items():
            bus_branch[bus_name] = name
        # Ensure every bus has an entry in the dictionary
        for bus in self.bus['name']:
            bus_branch[bus]  # Since bus_branch is a defaultdict, this will automatically create an empty list if the bus is not found
        return (dict(bus_branch))

    def bus_line_out(self):
        bus_branch = defaultdict(list)
        # Populate the dictionary with branches
        for bus_name, name in self.lines.groupby('from_busname')['name'].agg(list).items():
            bus_branch[bus_name] = name
        # Ensure every bus has an entry in the dictionary
        for bus in self.bus['name']:
            bus_branch[bus]  # Since bus_branch is a defaultdict, this will automatically create an empty list if the bus is not found
        return (dict(bus_branch))

    def line_buses(self):
        return dict(zip(self.lines['name'], zip(self.lines['from_busname'], self.lines['to_busname'])))

    def continuous_rating(self):
        return self.lines.set_index('name')['ContinousRating'] / self.baseMVA

    def susceptance(self):
        return self.lines[['name', 'b']].set_index('name')['b'].T.to_dict()

    def reactance(self):
        return self.lines[['name', 'x']].set_index('name')['x'].T.to_dict()

class Transformers(object):
    def __init__(self, loaded_data_file):
        self.data = loaded_data_file
        self.transformer = loaded_data_file["transformer"]
        self.bus = loaded_data_file["bus"]
        self.baseMVA = float(loaded_data_file['baseMVA']['baseMVA'][0])

    ##TRANSFORMER PYOMO DICTIONARY DEFINITIONS
    #Transformer Identifiers (for Set TRANSF)
    def identifiers(self):
        return [transformer_name for transformer_name in self.transformer['name']]
    
    #Transformer Originating Bus
    def from_bus(self):
        return self.transformer[['name', 'from_busname']].set_index('name')['from_busname'].T.to_dict()
    
    #Transformer Destination Bus
    def to_bus(self):
        return self.transformer[['name', 'to_busname']].set_index('name')['to_busname'].T.to_dict()
    
    #Transformer Type
    def type(self):
        return self.transformer[['name', 'type']].set_index('name')['type'].T.to_dict()
    
    '''
    Storing for later
    ###Creates a dictionary with the bus as the key, and values as buses set as transformer destinations that originate at this bus
    def bustransformer_destinations(self):
        return self.branch.groupby('from_busname')['name'].agg(list).to_dict()
    
    ###Creates a dictionary with the bus as the key, and values as buses set as transformer origins that have the bus as a destination
    def bustransformer_origins(self):
        return self.branch.groupby('to_busname')['name'].agg(list).to_dict()
    '''

    ###Creates a dictionary with the bus as the key, and transformers that feed to the bus as dictionary values
    def bus_transformer_in(self):
        bus_branch = defaultdict(list)
        # Populate the dictionary with transformers
        for bus_name, name in self.transformer.groupby('to_busname')['name'].agg(list).items():
            bus_branch[bus_name] = name
        # Ensure every bus has an entry in the dictionary
        for bus in self.bus['name']:
            bus_branch[bus] # Since bus_branch is a defaultdict, this will automatically create an empty list if the bus is not found
        return(dict(bus_branch))
    
    #Creates a dictionary with the bus as the key, with transformers fed from the bus as the dictionary values
    def bus_transformer_out(self):
        bus_branch = defaultdict(list)
        # Populate the dictionary with transformers
        for bus_name, name in self.transformer.groupby('from_busname')['name'].agg(list).items():
            bus_branch[bus_name] = name
        # Ensure every bus has an entry in the dictionary
        for bus in self.bus['name']:
            bus_branch[bus] # Since bus_branch is a defaultdict, this will automatically create an empty list if the bus is not found
        return(dict(bus_branch))

    ##Create a dictionary with transformer as the key, and a tuple of from_bus name and to_busname as the value
    def transformer_buses(self):
        return dict(zip(self.transformer['name'], zip(self.transformer['from_busname'], self.transformer['to_busname'])))

    #Transformer Resistance (R)
    def resistance(self):
        return self.transformer[['name', 'r']].set_index('name')['to_r'].T.to_dict()
    
    #Transformer Reactance (X)
    def reactance(self):
        return self.transformer[['name', 'x']].set_index('name')['x'].T.to_dict()

    #Transformer Susceptance (B) (for Set BLT)
    def susceptance(self):
        return self.transformer[['name', 'b']].set_index('name')['b'].T.to_dict()

    #Transformer Short Term Voltage Rating
    def short_term_rating(self):
        # return self.transformer[['name', 'ShortTermRating']].set_index('name')['ShortTermRating'].T.to_dict()
        return self.transformer.set_index('name')['ShortTermRating'] / self.baseMVA   

    #Transformer Continuous Voltage Rating (for Set SLmaxT)
    def continuous_rating(self):
        # return self.transformer[['name', 'ContinousRating']].set_index('name')['ContinousRating'].T.to_dict()
        return self.transformer.set_index('name')['ContinousRating'] / self.baseMVA   

    #Transformer Minimum Voltage Angle (Lower Bound)
    def voltage_angle_minimum(self):
        return self.transformer[['name', 'angLB']].set_index('name')['angLB'].T.to_dict()

    #Transformer Maximum Voltage Angle (Upper Bound)
    def voltage_angle_maximum(self):
        return self.transformer[['name', 'angUB']].set_index('name')['angUB'].T.to_dict()
    
    #Transformer Phase Shift
    def phase_shift(self):
        return self.transformer[['name', 'PhaseShift']].set_index('name')['PhaseShift'].T.to_dict()
    
    #Transformer Tap Ratio
    def tap_ratio(self):
        return self.transformer[['name', 'TapRatio']].set_index('name')['TapRatio'].T.to_dict()
    
    #Transformer Tap Ratio Minimum (Lower Bound)
    def tap_ratio_minimum(self):
        return self.transformer[['name', 'TapLB']].set_index('name')['TapLB'].T.to_dict()
    
    #Transformer Tap Ratio Maximum (Upper Bound)
    def tap_ratio_maximum(self):
        return self.transformer[['name', 'TapUB']].set_index('name')['TapUB'].T.to_dict()

    #Transformer Contingency
    def contingency(self):
        return self.transformer[['name', 'contingency']].set_index('name')['contingency'].T.to_dict()

    #Transformer Failure Rate (1/year)
    def probability(self):
        return self.transformer[['name', 'probablity']].set_index('name')['probablity'].T.to_dict()

    def __init__(self, loaded_data_file):
        self.data = loaded_data_file
        self.bus = loaded_data_file["bus"]
        self.demand = loaded_data_file["demand"]
        self.baseMVA = float(loaded_data_file['baseMVA']['baseMVA'][0])

    ##DEMAND PYOMO DICTIONARY DEFINITIONS
    #Demand Identifiers (for Set D)
    def identifiers(self):
        return [demand_name for demand_name in self.demand['name']]

    '''
    Storing for Later
    
    #Demand Bus Mapping (for Set Dbs)
    # 
    # Pyomo mapping sets require a set of tuples for the index.
    #  
    # def bus_mapping(self):
    #     tuples = zip(self.demand['busname'], self.demand['name']) #creates iterator of tuples
    #     return tuples

    #Demand Bus Mapping (for Set Dbs)
    def bus_mapping(self):
        # tuples = zip(self.demand['busname'], self.demand['name']) #creates iterator of tuples
        # return tuples
            return self.demand.groupby('name')['busname'].agg(list).to_dict()

    '''

    def negatives(self):
        negatives = self.demand[self.demand['real'] < 0]
        return [negatives_name for negatives_name in negatives['name']]

    ###Demand Bus Mapping
    def bus_mapping(self):
        bus_demand = defaultdict(list)
        # Populate the dictionary with demands
        for bus_name, name in self.demand.groupby('busname')['name'].agg(list).items():
            bus_demand[bus_name] = name
        # Ensure every bus has an entry in the dictionary
        for bus in self.bus['name']:
            bus_demand[bus] # Since bus_branch is a defaultdict, this will automatically create an empty list if the bus is not found
        return(dict(bus_demand))

    #Real Power Demand (for Parameter PD, Real Power Demand)
    def real_demand(self):
        return self.demand.set_index('name')['real'] / self.baseMVA    

    #Reactive Power Demand
    def reactive_demand(self):
        return self.demand.set_index('name')['reactive'] / self.baseMVA   
    
    #Demand Value of Lost Load (for Parameter VOLL, Volume of Lost Load)
    def VOLL(self):
        return self.demand[['name', 'VOLL']].set_index('name')['VOLL'].T.to_dict()