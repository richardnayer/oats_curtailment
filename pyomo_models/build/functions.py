from pyomo.environ import *
from functools import reduce
from operator import mul
from typing import List, Dict, Tuple, Union


def add_sets_to_instance(instance: object, sets_dict_obj: dict):
    '''
    Function to add sets to a pyomo model instance.
    '''
    for set_name, set_def in sets_dict_obj.blocks.items():
        set_type = set_def.get('type', 'flat')
        dimen = set_def.get('dimen', 1)
        index = set_def.get('index', None)
        within = set_def.get('within', None)
        initialize = set_def.get('initialize')()

        print(set_name, set_type, dimen, within, initialize)

        #TODO - Buid iterative addition of sets into the instance.

        if index:
            instance.add_component(
                set_name,
                Set(
                    getattr(instance, index) if index else None,
                    within = reduce(mul, (getattr(instance,index_set) for index_set in within)) if isinstance(within, tuple) else getattr(instance,within) if isinstance(within, str) else None,  # handle tuple or Set or None
                    initialize=initialize,
                    ordered=False,
                    validate=None,
                    dimen=dimen,
                )
            )

        else:
            instance.add_component(
                set_name,
                Set(
                    within = reduce(mul, (getattr(instance,index_set) for index_set in within)) if isinstance(within, tuple) else getattr(instance,within) if isinstance(within, str) else None,  # handle tuple or Set or None
                    initialize=initialize,
                    ordered=False,
                    validate=None,
                    dimen=dimen,
                )
            )
