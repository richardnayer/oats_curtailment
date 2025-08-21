from pyomo.environ import *
import pandas as pd

class InstanceCache:
    def __init__(self, result, data_to_cache, options=None):
        self.result = result
        self.data_to_cache = data_to_cache
        self.headers = None
        self.options = options
        self.obj = 0

    #Add objective to object
    def obj_value(self, instance):
        # setattr(self, "obj",  )
        obj_val = value(getattr(instance, "OBJ"))
        setattr(self, "obj", obj_val)

    #Add Parameters to Object
    def param(self, instance):
        '''
        Function iterates through parameters in the model, and adds data indexed in a dictionary for each parameter.
        Default is to cache all parameters, unless a specific parameter list is given in data_to_cache then this is extracted, 
        '''
        #Default is to cache all parameters unless specifics noted
        if self.data_to_cache["Param"] == [None]:
            # print("none 1")
            return        
        if not self.data_to_cache["Param"]:
            # print("not none 2")
            param_list = instance.component_objects(Param, active=True)
        else:
            # print("not none 3")
            param_list = self.data_to_cache["Param"]

        #Iterator through all params in param_list, extract value and add to object
        for p in param_list:
            paramobject = getattr(instance, str(p))
            # print(paramobject)
            
            # Use a generator to assign index-value pairs directly to the attribute
            setattr(self, str(p), {index: paramobject[index].value if "pyomo" in str(type(paramobject[index])) else paramobject[index]
                                    for index in paramobject})
    
    #Add Variables to Object
    def var(self, instance):
        '''
        Function iterates through variables in the model, and adds data indexed in a dictionary for each variable.
        Default is to cache all variables, unless a specific variable list is given in data_to_cache then this is extracted, 
        '''       
        if self.data_to_cache["Var"] == [None]:
            return
        if not self.data_to_cache["Var"]:
            var_list = instance.component_objects(Var, active=True)
        else:
            var_list = self.data_to_cache["Var"]

        #Iterator through all variables in var_list, extract value and add to object
        for v in var_list:
            varobject = getattr(instance, str(v))
            # print(str(v), {index: varobject[index].value if "pyomo" in str(type(varobject[index])) else varobject[index]
            #                        for index in varobject})
            # Use a generator to assign index-value pairs directly to the attribute
            setattr(self, str(v), {index: varobject[index].value if "pyomo" in str(type(varobject[index])) else varobject[index]
                                   for index in varobject})
               
    #Add Sets to Object
    def set(self, instance):
        '''
        Function iterates through sets in the model, and adds data indexed in a dictionary for each sets.
        Default is to cache all sets, unless a specific sets list is given in data_to_cache then this is extracted, 
        '''
        if self.data_to_cache["Set"] == [None]:
            return       
        if not self.data_to_cache["Set"]:
            set_list = instance.component_objects(Set, active=True)
        else:
            set_list = self.data_to_cache["Set"]

        #Iterator through all sets in set_list, extract data and add to object
        for s in set_list:
            setobject = getattr(instance, str(s))
            setattr(self, str(s), setobject.data())
            
        results = {}
        for v in instance.component_data_objects(Var, active=True):
            try:
                if v.value is not None:
                    split_key = str(v).split("[")
                    results[split_key[0]][split_key[1][:-1]] =  value(v)
                
            except:
                results[split_key[0]] = {}
            
        headers_list = []
        if table_list == None:
            table_list = []
            
            
            for main_v in results:
                results_table = pd.DataFrame.from_dict([results[main_v]])
                table_list.append(results_table) 
                headers_list.append(main_v)   
            
        else:
            # print(len(table_list))
            for counter, main_v in enumerate(results):
                results_table = pd.DataFrame.from_dict([results[main_v]])
                table_list[counter] = pd.concat([table_list[counter], results_table], ignore_index=True)
                headers_list.append(main_v)  
 
        
        self.headers = headers_list
        
        return table_list