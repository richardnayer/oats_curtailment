from load_case import load_case 
from collections import defaultdict
import itertools as iter
import sys


class Buses(object):
    def __init__(self, loaded_data_file):
        self.data = loaded_data_file
        self.bus = loaded_data_file['bus']

    #Bus Identifiers (Set B)
    def identifiers(self):
        return [bus_name for bus_name in self.bus['name']]
    
    #Slack Bus Identifier (Set b0)
    def slack_buses(self):
        slacks = self.bus[self.bus['type'] == 3] #take busses equal to 3
        return [slack_name for slack_name in slacks['name']]
    
    #Bus Base kV Data
    def basekV(self):
        return self.bus[['name', 'baseKV']].set_index('name')['baseKV'].T.to_dict()

    #Bus Base Type
    def type(self):
        return self.bus[['name', 'type']].set_index('name')['type'].T.to_dict()
    
    #Bus Zone
    def zone(self):
        return self.bus[['name', 'zone']].set_index('name')['zone'].T.to_dict()
    
    #Bus Voltage Lower Bound
    def voltage_max(self):
        return self.bus[['name', 'VNUB']].set_index('name')['VNUB'].T.to_dict()
    
    #Bus Voltage Upper Bound
    def voltage_min(self):
        return self.bus[['name', 'VNUB']].set_index('name')['VNUB'].T.to_dict()

class Generators(object):
    def __init__(self, loaded_data_file):
        self.data = loaded_data_file
        self.generators = loaded_data_file['generator']
        self.bus = loaded_data_file['bus']
        self.baseMVA = float(loaded_data_file['baseMVA']['baseMVA'][0])

    ##GENERATOR SHEET PYOMO DICTIONARY DEFINITIONS
    #Generator Identifiers (for Set G)
    def identifiers(self):
        '''
        Returns a list of all generator names
        '''
        return [generator_name for generator_name in self.generators['name']]

    '''
    Storing for Later
      
    def bus_mapping(self):
        tuples = zip(self.generators['busname'], self.generators['name']) #creates iterator of tuples
        return tuples #creates dictionary with 'keys' as dictionary key, and other item as value(s)
    '''

    #Generator Bus Mapping (for Set Gbs) - Pyomo mapping sets require a set of tuples for the indexg
    def bus_mapping(self):
        '''
        Function creates a map of generators against each bus. It returns a dictionary with the buses (name of each bus) 
        as the keys, with a list of generators assigned to each bus as the value.
        '''
        bus_generator = defaultdict(list)
        # Populate the dictionary with generators at each bus
        for bus_name, name in self.generators.groupby('busname')['name'].agg(list).items():
            bus_generator[bus_name] = name
        # Ensure every bus has an entry in the dictionary
        for bus in self.bus['name']:
            bus_generator[bus] # Since bus_branch is a defaultdict, this will automatically create an empty list if the bus is not found
        return(dict(bus_generator))
    
    #Generator Real Power Set POint (p.u)
    def real_power(self):
        '''
        Returns a dictionary of all generators as keys, and the real power set-point as the value.
        '''
        return self.generators.set_index('name')['PG'] / self.baseMVA
    
    #Generator Minimum Real Power (for Set PGmin) in p.u
    def real_power_min(self):
        '''
        Returns a dictionary of all generators as keys, and the minimum real power as the value.
        '''
        return self.generators.set_index('name')['PGLB'] / self.baseMVA
    
    #Generator Maximum Real Power (fir Set PGmax) in p.u
    def real_power_max(self):
        '''
        Returns a dictionary of all generators as keys, and the maximum real power as the value.
        '''
        return self.generators.set_index('name')['PGUB'] / self.baseMVA
    
    def all_ireland_mingen(self):
        '''
        Returns a dictionary of all generators as keys, and PGMINGEN as the minimum real power as the value.
        '''
        return self.generators.set_index('name')['PGMINGEN'] / self.baseMVA

    #Generator Reactive Power Set Point in p.u
    def reactive_power(self):
        '''
        Returns a dictionary of all generators as keys, and the reactive power set-point as the value.
        '''
        return self.generators.set_index('name')['QG'] / self.baseMVA
    
    #Generator Minimum Reactive Power in p.u
    def reactive_power_min(self):
        '''
        Returns a dictionary of all generators as keys, and the minimum reactive power as the value.
        '''
        return self.generators.set_index('name')['QGLB'] / self.baseMVA
    
    #Generator Maximum Reactive Power in p.u
    def reactive_power_max(self):
        '''
        Returns a dictionary of all generators as keys, and the maximum reactive power as the value.
        '''
        return self.generators.set_index('name')['QGUB'] / self.baseMVA
    
    #Generator Cost c0
    def cost_c0(self):
        '''
        Returns a dictionary of all generators as keys, and the fixed cost coefficient as the value.
        '''
        return self.generators[['name', 'costc0']].set_index('name')['costc0'].T.to_dict()
    
    #Generator Cost c1
    def cost_c1(self):
        '''
        Returns a dictionary of all generators as keys, and the linear cost coefficient as the value.
        '''
        return self.generators[['name', 'costc1']].set_index('name')['costc1'].T.to_dict()
    
    #Generator Cost c2
    def cost_c2(self):
        '''
        Returns a dictionary of all generators as keys, and the quadratic cost coefficient as the value.
        '''
        return self.generators[['name', 'costc2']].set_index('name')['costc2'].T.to_dict()

    #Generator Bid Price
    def bid(self):
        '''
        Returns a dictionary of all generators as keys, and the bid cost as the value.
        '''
        return self.generators[['name', 'bid']].set_index('name')['bid'].T.to_dict()
    
    #Generator Offer Price
    def offer(self):
        '''
        Returns a dictionary of all generators as keys, and the offer cost as the value.
        '''
        return self.generators[['name', 'offer']].set_index('name')['offer'].T.to_dict()

    #Generators Failure Probability (1/year failure rate)
    def probability(self):
        '''
        Returns a dictionary of all generators as keys, and the failure_rate of each generator as the value.
        '''
        return self.generators[['name', 'failure_rate(1/yr)']].set_index('name')['failure_rate(1/yr)'].T.to_dict()

    #Wind Contingency
    def contingency(self):
        '''
        Returns a dictionary of all generators as keys, and the contingency of each generator as the value.
        '''
        return self.generators[['name', 'contingency']].set_index('name')['contingency'].T.to_dict()
    
    ###### Curtailment Policies Data Managmenet #######
    ### Individual Policy
    def individual_EER_policy(self):
        '''
        Returns a list of all generators that have freedom to manage export individually.
        '''
        return [generator_name for generator_name in self.generators[self.generators['export_policy'] == "Individual"]['name']]
    
    ### Uncontrollable
    def uncontrollable_EER_policy(self):
        '''
        Returns a list of all generators that cannot be export controlled (i.e. they will operate at their maximum). In reality this represents older generation
        assets, of smaller export capacities, that do not have DNO control systems at site, and cannot be included in a smart curtailment system.
        '''
        return [generator_name for generator_name in self.generators[self.generators['export_policy'] == "Uncontrollable"]['name']]

    ### Pro-Rata Policy
    def prorata_EER_policy(self):
        '''
        Returns a list of all generators that have Pro-Rata Enfored Export Reduction (EER) policies
        '''
        return [generator_name for generator_name in self.generators[self.generators['export_policy'] == "Pro-Rata"]['name']]
    
    ### Non-Synchronous Generators Set
    def non_synchronous_gen(self):
        '''
        Returns a list of all generators that are non-synchronous generators.
        '''
        return [generator_name for generator_name in self.generators[self.generators['synchronous'] == "No"]['name']]
    
    ### Synchronous Generators Set
    def synchronous_gen(self):
        '''
        Returns a list of all generators that are synchronous generators.
        '''
        return [generator_name for generator_name in self.generators[self.generators['synchronous'] == "Yes"]['name']]


    def prorata_groups(self):
        '''
        Returns a list of all pro-rata constraint groups
        '''
        prorata_groups = self.generators["prorata_groups"].dropna().str.split(',').explode().tolist()
        prorata_groups = list(set(cg.strip() for cg in prorata_groups)) #Convert to set of unique values only

        return prorata_groups

    def prorata_cg_map(self):
        '''
        FOR GENERATORS WITH PRO-RATA ENFORCED EXPORT REDUCTION POLICY ONLY
        Returns a dictionary of generators curtailed using pro-rata as keys, with a tuple of all constraint groups to which the generator belongs as the value.
        '''
        #Note to self [RN, 21/08] - Add drop of items that don't have any?
        pro_rata_gens = self.generators[self.generators['export_policy'] == "Pro-Rata"]
        return {k: tuple([cg.strip() for cg in v.split(',')]) for k, v in pro_rata_gens[['name', 'prorata_groups']].set_index('name')['prorata_groups'].items()}
    
    ### LIFO Policy
    def LIFO_EER_policy(self):
        '''
        Returns a list of all generators that have Last-In-First-Out (LIFO) Enfored Export Reduction (EER) policies
        '''
        return [generator_name for generator_name in self.generators[self.generators['export_policy'] == "LIFO"]['name']]

    def LIFO_groups(self):
        None

    def LIFO_combinations(self):
        LIFO_gens = self.generators[self.generators['export_policy'] == "LIFO"]
        lst = (LIFO_gens.sort_values(['lifo_group','lifo_position'],ascending=True).groupby('lifo_group').name.apply(lambda x: list(iter.combinations(x,2))).to_list())
        lst = [x for x in lst if x!=[]] #remove empty lists, units with single LIFO results in empty lists
        flat_lst = [x for x1 in lst for x in x1] #flatten the list
        return flat_lst

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