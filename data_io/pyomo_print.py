import pandas as pd
import matplotlib.pyplot as plt
import math


def all_island_iterations_summary_df(case, output):
    #----------------------#
    # Create Summary Page  #
    #----------------------#
    summary_df = pd.DataFrame()

    for iteration in case.iterations:
        output_data = output.get(iteration).get('dcopf')
        baseMVA = case.baseMVA

        row = pd.DataFrame([
            iteration,
            sum(output_data.PD.values()) * baseMVA,
            sum(output_data.pD.values()) * baseMVA,
            sum(output_data.pG[g] for g in output_data.G_s) * baseMVA,
            sum(output_data.PGmax[g] for g in output_data.G_ns) * baseMVA,
            sum(output_data.pG[g] for g in output_data.G_ns) * baseMVA,
            sum(output_data.PGmax[g] - output_data.pG[g] for g in output_data.G_ns) * baseMVA,
            (output_data.V_Surplus + output_data.V_SNSP + output_data.V_MUON) * baseMVA,
            output_data.V_Surplus * baseMVA,
            output_data.V_SNSP * baseMVA,
            output_data.V_MUON * baseMVA,
            output_data.V_Constraint * baseMVA,
            ]
        ).T
        summary_df = pd.concat([summary_df, row], ignore_index=True)

    summary_df.columns=[
        "iteration",
        "demand (MW)",
        "demand met (MW)",
        "synchronous generation (MW)",
        "non-synchronous availability (MW)",
        "non-synchronous generation (MW)",
        "dispatch down (MW)",
        "total curtailment (MW)",
        "SURPLUS curtailment (MW)",
        "SNSP curtailment (MW)",
        "MUON curtailment (MW)",
        "constraint (MW)"
    ]

    return summary_df
    #


def df_summarised_by_bus(case, output, sub_output, param, param_index, multiplier = None):
    #Creates a dataframe of output values summed to busses
    df = pd.DataFrame()
    if multiplier == None:
        multiplier = 1

    param_by_bus = getattr(case, param_index).groupby('busname')['name'].apply(list).to_dict()

    for iteration in case.iterations:
        #Define Output of interest
        output_data = output.get(iteration).get(sub_output)

        row = pd.DataFrame([iteration]+[sum(getattr(output_data, param)[index] for index in param_by_bus[bus])*multiplier for bus in param_by_bus]).T
        df = pd.concat([df, row], ignore_index=True)

    df.columns = ['iteration'] + [bus for bus in param_by_bus]
    return df


def df_by_own_index(case, output, sub_output, param, multiplier = None):
    #Creates a dataframe of output values broken down as per their index
    df = pd.DataFrame()
    if multiplier == None:
        multiplier = 1

    for iteration in case.iterations:
        #Define Output of interest
        output_data = output.get(iteration).get(sub_output)

        row = pd.DataFrame([iteration]+[value*multiplier for value in getattr(output_data, param).values()]).T
        df = pd.concat([df, row], ignore_index=True)
    
    df.columns = ['iteration'] + [key for key in getattr(output_data, param)]
    return df


def all_island_timeseries_to_excel(case, output):
    sheets_dict = {}
    
    #Add Initial Summary Page
    sheets_dict['summary'] = all_island_iterations_summary_df(case, output)

    #Define which parameters to summarise on a buswise basis:
    summarised_by_bus_outputs = {
        'PD': {'sub_output':'copper_market',
                      'param':'PD',
                      'param_index':'demands',
                      'multiplier':case.baseMVA
                      },
        'pG': {'sub_output':'dcopf',
                      'param':'pG',
                      'param_index':'generators',
                      'multiplier':case.baseMVA
                      },
        'PGmax': {'sub_output':'dcopf',
                      'param':'PGmax',
                      'param_index':'generators',
                      'multiplier':case.baseMVA
                      },
        'Surplus': {'sub_output':'dcopf',
                      'param':'v_Surplus_g',
                      'param_index':'generators',
                      'multiplier':case.baseMVA
                      },
        'SNSP': {'sub_output':'dcopf',
                      'param':'v_SNSP_g',
                      'param_index':'generators',
                      'multiplier':case.baseMVA
                      },
        'MUON': {'sub_output':'dcopf',
                      'param':'v_MUON_g',
                      'param_index':'generators',
                      'multiplier':case.baseMVA
                      },  
        'Constraint': {'sub_output':'dcopf',
                      'param':'v_Constraint_g',
                      'param_index':'generators',
                      'multiplier':case.baseMVA
                      },                         
    }

    #Add buswise summarised sheets into sheets_df
    for name, config in summarised_by_bus_outputs.items():
        sheets_dict[name+'_buswise'] = df_summarised_by_bus(case,
                                               output,
                                               config.get('sub_output'),
                                               config.get('param'),
                                               config.get('param_index'),
                                               config.get('multiplier'))

    #Define which parameters to summarise on a self indexed basis:
    by_own_index_outputs = {
        'pD_d': {'sub_output':'dcopf',
                      'param':'PD',
                      'multiplier':case.baseMVA
                      }, 
        'alpha_d': {'sub_output':'dcopf',
                      'param':'alpha',
                      'multiplier':None
                      },
        'bus_angle': {'sub_output':'dcopf',
                      'param':'delta',
                      'multiplier':180/math.pi
                      },
        'line_delta': {'sub_output':'dcopf',
                      'param':'deltaL',
                      'multiplier':180/math.pi
                      },
        'transf_delta': {'sub_output':'dcopf',
                      'param':'deltaLT',
                      'multiplier':180/math.pi
                      },
        'line_flow': {'sub_output':'dcopf',
                      'param':'pL',
                      'multiplier':case.baseMVA
                      },
        'transf_flow': {'sub_output':'dcopf',
                      'param':'pL',
                      'multiplier':case.baseMVA
                      },
        'pG': {'sub_output':'dcopf',
                      'param':'pG',
                      'multiplier':case.baseMVA
                      },
        'PG_MARKET': {'sub_output':'dcopf',
                      'param':'PG_MARKET',
                      'multiplier':case.baseMVA
                      },
        'PG_SECURE': {'sub_output':'dcopf',
                      'param':'PG_SECURE',
                      'multiplier':case.baseMVA
                      },  
        'Surplus': {'sub_output':'dcopf',
                      'param':'v_Surplus_g',
                      'multiplier':case.baseMVA
                      },
        'SNSP': {'sub_output':'dcopf',
                      'param':'v_SNSP_g',
                      'multiplier':case.baseMVA
                      },
        'MUON': {'sub_output':'dcopf',
                      'param':'v_MUON_g',
                      'multiplier':case.baseMVA
                      },  
        'Constraint': {'sub_output':'dcopf',
                      'param':'v_Constraint_g',
                      'multiplier':case.baseMVA
                      },                             
    }

    #Add parameters on a self indexed basis to sheets dataframe
    for name, config in by_own_index_outputs.items():
        sheets_dict[name] = df_by_own_index(case,
                                               output,
                                               config.get('sub_output'),
                                               config.get('param'),
                                               config.get('multiplier'))
        
    #Create Excel Page
    with pd.ExcelWriter('results.xlsx', engine ='xlsxwriter') as writer:
        for sheet_id, sheet in sheets_dict.items():
            sheet.to_excel(writer, sheet_name = sheet_id, index = False)

    ...
















def demand_ns_plot(case, output):

    #Create DataFrame Summing Maximum Possible Wind GEneration At Each Bus
    wind_by_bus_per_iter = pd.DataFrame()
    #Dictionary of WIND generators at each bus
    wind_by_bus = {bus: case.generators.loc[
                                                (case.generators['busname'] == bus) &
                                                (case.generators['FuelType'] == 'Wind')]['name'].to_list()
                                                for bus in case.busses['name']
                                                }
    #Create iteration by iteration rows of data
    for iteration in case.iterations:
        row = pd.DataFrame([iteration]+
                           [sum(case.ts_PGUB.loc[iteration, wind_by_bus[bus]].to_list()) for bus in case.busses['name']]).T
        wind_by_bus_per_iter = pd.concat([wind_by_bus_per_iter, row], ignore_index=True)
    #Add columns to df.
    wind_by_bus_per_iter.columns = ['iteration'] + case.busses['name'].to_list()

    #Create DataFrame Summing Demand Bus
    demand_by_bus_per_iter = pd.DataFrame()
    #Dictionary of demands at each bus
    demand_by_bus = {bus: case.demands.loc[(case.demands['busname'] == bus)]['name'].to_list()
                                            for bus in case.busses['name']
                                                }
    #Create iteration by iteration rows of data
    for iteration in case.iterations:
        row = pd.DataFrame([iteration]+
                           [sum(case.ts_PD.loc[iteration, demand_by_bus[bus]].to_list()) for bus in case.busses['name']]).T
        demand_by_bus_per_iter = pd.concat([demand_by_bus_per_iter, row], ignore_index=True)
    #Add columns to df.
    demand_by_bus_per_iter.columns = ['iteration'] + case.busses['name'].to_list()



    # #Create Plot
    # x = wind_by_bus_per_iter['iteration']
    # colors = plt.cm.tab10.colors

    # for i, col in enumerate(wind_by_bus_per_iter.columns[1:]):  # skip 'iteration'
    #     # solid line for df1
    #     plt.plot(x, wind_by_bus_per_iter[col], label=f"Bus {col}", color=colors[i])
    #     # dotted line for df2
    #     plt.plot(x, demand_by_bus_per_iter[col], color=colors[i], linestyle="--")
    
    # plt.xticks(rotation=45)
    # plt.xlabel("Iteration")
    # plt.ylabel("Demand/Generation (MW)")
    # plt.legend()
    # plt.tight_layout()
    # plt.show()
    # ...
        



