"""
__authors__ = "Richard Nayer, Sam Hodges, Waqquas Bukhsh"
__credits__ = "University of Strathclyde"
__version__ = "1.0.1"
__status__ = "Prototype"
"""
from typing import List, Dict, Tuple
import itertools as iter
import data_feed.pyomo.helpers as helpers

### KEY DEFINITIONS
component = 'generators'

###
### GENERAL LISTS AND MAPPING
###

def identifiers(case) -> List[str]:
    '''
    Returns a list of all generator names
    '''
    return [generator_name for generator_name in case.generators['name']]

#Generator Bus Mapping (for Set Gbs) - Pyomo mapping sets require a set of tuples for the indexg
def bus_mapping(case) -> Dict[str, List[str]]:
    '''
    Function creates a map of generators against each bus. It returns a dictionary with the buses (name of each bus) 
    as the keys, with a list of generators assigned to each bus as the value.
    '''
    bus_gen_map = case.generators.groupby('busname')['name'].apply(list).to_dict()
    for bus in case.busses['name']:
        bus_gen_map.setdefault(bus, [])
    return bus_gen_map

###
### POWER CRITERIA
###

#Generator Real Power Set Point (p.u)
def real_power(case) -> Dict[str, float]:
    '''
    Returns a dictionary of all generators as keys, and the real power (scaled against baseMVA) set-point as the value.
    '''
    return helpers.get_baseMVA_param(case, component, 'name', 'PG', case.baseMVA)

#Generator Minimum Real Power (for Set PGmin) in p.u
def real_power_min(case) -> Dict[str, float]:
    '''
    Returns a dictionary of all generators as keys, and the minimum real power as the value.
    '''
    return helpers.get_baseMVA_param(case, component, 'name', 'PGLB', case.baseMVA)

#Generator Maximum Real Power (fir Set PGmax) in p.u
def real_power_max(case) -> Dict[str, float]:
    '''
    Returns a dictionary of all generators as keys, and the maximum real power as the value.
    '''
    return helpers.get_baseMVA_param(case, component, 'name', 'PGUB', case.baseMVA)

def all_ireland_mingen(case) -> Dict[str, float]:
    '''
    Returns a dictionary of all generators as keys, and PGMINGEN as the minimum real power as the value.
    '''
    return helpers.get_baseMVA_param(case, component, 'name', 'PGMINGEN', case.baseMVA)

#Generator Reactive Power Set Point in p.u
def reactive_power(case) -> Dict[str, float]:
    '''
    Returns a dictionary of all generators as keys, and the reactive power set-point as the value.
    '''
    return helpers.get_baseMVA_param(case, component, 'name', 'QG', case.baseMVA)

#Generator Minimum Reactive Power in p.u
def reactive_power_min(case) -> Dict[str, float]:
    '''
    Returns a dictionary of all generators as keys, and the minimum reactive power as the value.
    '''
    return helpers.get_baseMVA_param(case, component, 'name', 'QGLB', case.baseMVA)

#Generator Maximum Reactive Power in p.u
def reactive_power_max(case) -> Dict[str, float]:
    '''
    Returns a dictionary of all generators as keys, and the maximum reactive power as the value.
    '''
    return helpers.get_baseMVA_param(case, component, 'name', 'QGUB', case.baseMVA)


###
### COST CRITERIA
###

#Generator Cost c0
def cost_c0(case) -> Dict[str, float]:
    '''
    Returns a dictionary of all generators as keys, and the fixed cost coefficient as the value.
    '''
    return helpers.get_param(case, component, 'name', 'costc0')

#Generator Cost c1
def cost_c1(case) -> Dict[str, float]:
    '''
    Returns a dictionary of all generators as keys, and the linear cost coefficient as the value.
    '''
    return helpers.get_param(case, component, 'name', 'costc1')

#Generator Cost c2
def cost_c2(case) -> Dict[str, float]:
    '''
    Returns a dictionary of all generators as keys, and the quadratic cost coefficient as the value.
    '''
    return helpers.get_param(case, component, 'name', 'costc2')

#Generator Bid Price
def bid(case) -> Dict[str, float]:
    '''
    Returns a dictionary of all generators as keys, and the bid cost as the value.
    '''
    return helpers.get_param(case, component, 'name', 'bid')

#Generator Offer Price
def offer(case) -> Dict[str, float]:
    '''
    Returns a dictionary of all generators as keys, and the offer cost as the value.
    '''
    return helpers.get_param(case, component, 'name', 'offer')

###
### MISC. CRITERIA
###

#Generators Failure Probability (1/year failure rate)
def probability(case) -> Dict[str, float]:
    '''
    Returns a dictionary of all generators as keys, and the failure_rate of each generator as the value.
    '''
    return helpers.get_param(case, component, 'name', 'failure_rate(1/yr)')

#Wind Contingency
def contingency(case) -> Dict[str, float]:
    '''
    Returns a dictionary of all generators as keys, and the contingency of each generator as the value.
    '''
    return helpers.get_param(case, component, 'name', 'contingency')

###
### CURTAILMENT POLICY MAPPING
###

### Individual Policy
def individual_EER_policy(case) -> List[str]:
    '''
    Returns a list of all generators that have freedom to manage export individually.
    '''
    return helpers.filter_component_by_param(case, 'generators', 'export_policy', 'Individual', 'name')

### Uncontrollable
def uncontrollable_EER_policy(case) -> List[str]:
    '''
    Returns a list of all generators that cannot be export controlled (i.e. they will operate at their maximum). In reality this represents older generation
    assets, of smaller export capacities, that do not have DNO control systems at site, and cannot be included in a smart curtailment system.
    '''
    return helpers.filter_component_by_param(case, 'generators', 'export_policy', 'Uncontrollable', 'name')

### Pro-Rata Policy
def prorata_EER_policy(case) -> List[str]:
    '''
    Returns a list of all generators that have Pro-Rata Enfored Export Reduction (EER) policies
    '''
    return helpers.filter_component_by_param(case, 'generators', 'export_policy', 'Pro-Rata', 'name')

### Non-Synchronous Generators Set
def non_synchronous_gen(case) -> List[str]:
    '''
    Returns a list of all generators that are non-synchronous generators.
    '''
    return helpers.filter_component_by_param(case, 'generators', 'synchronous', 'No', 'name')

### Synchronous Generators Set
def synchronous_gen(case) -> List[str]:
    '''
    Returns a list of all generators that are synchronous generators.
    '''
    return helpers.filter_component_by_param(case, 'generators', 'synchronous', 'Yes', 'name')

def prorata_groups(case) -> List[str]:
    groups = (
        case.generators['prorata_groups']
        .dropna()
        .str.split(',')
        .explode()
        .str.strip()
        .unique()
        .tolist()
    )
    return groups

# def prorata_cg_map(case):
#     '''
#     FOR GENERATORS WITH PRO-RATA ENFORCED EXPORT REDUCTION POLICY ONLY
#     Returns a dictionary of generators curtailed using pro-rata as keys, with a tuple of all constraint groups to which the generator belongs as the value.
#     '''
#     #Note to case [RN, 21/08] - Add drop of items that don't have any?
#     pro_rata_gens = case.generators[case.generators['export_policy'] == "Pro-Rata"]
#     return {k: tuple([cg.strip() for cg in v.split(',')]) for k, v in pro_rata_gens[['name', 'prorata_groups']].set_index('name')['prorata_groups'].items()}

def prorata_cg_map(case) -> Dict[str, Tuple[str, ...]]:
    pro_rata_gens = case.generators.loc[case.generators['export_policy'] == "Pro-Rata"]
    return {
        name: tuple(cg.strip() for cg in groups.split(','))
        for name, groups in pro_rata_gens[['name', 'prorata_groups']].dropna().values
    }

### LIFO Policy
def LIFO_EER_policy(case) -> List[str]:
    '''
    Returns a list of all generators that have Last-In-First-Out (LIFO) Enfored Export Reduction (EER) policies
    '''
    return helpers.filter_component_by_param(case, 'generators', 'export_policy', 'LIFO', 'name')

def LIFO_combinations(case):
    LIFO_gens = case.generators.loc[case.generators['export_policy'] == "LIFO"]
    grouped = LIFO_gens.sort_values(['lifo_group', 'lifo_position'])
    lst = (LIFO_gens.sort_values(['lifo_group','lifo_position'],ascending=True).groupby('lifo_group').name.apply(lambda x: list(iter.combinations(x,2))).to_list())
    lst = [x for x in lst if x!=[]] #remove empty lists, units with single LIFO results in empty lists
    flat_lst = [x for x1 in lst for x in x1] #flatten the list
    return flat_lst

    # LIFO_gens = case.generators.loc[case.generators['export_policy'] == "LIFO"]
    # grouped = LIFO_gens.sort_values(['lifo_group', 'lifo_position'])
    # combos = grouped.groupby('lifo_group')['name'].apply(lambda x: list(it.combinations(x, 2))).tolist()
    # combos = [combo for sublist in combos for combo in sublist if combo]
    # return combos
