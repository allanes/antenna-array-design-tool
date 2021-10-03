import numpy as np
import math
from dask.distributed import Client
import dask.delayed

import antenna_core_functions as core_functions
from antenna_geometric_patterns_generators import GeometryArray
import utilities as utils
import antenna_plotting_tools as plotting_tools

def array_evaluation_process(distribution_type, separation, param1, param2, aiming, plot=False):
    geometrical_array = GeometryArray(distribution_type=distribution_type)
    geometrical_array.populate_array(
        separation=separation, 
        param1= param1, 
        param2=param2
    )
    individual_element_pattern = [core_functions.quarter_wave_monopole_pattern()]
    
    arreglo = core_functions.AntennaArray(
        positions=geometrical_array.positions,
        excitations=geometrical_array.excitations,
        pattern=individual_element_pattern
    )

    arreglo.aiming(
        phi=math.radians(aiming['phi']),
        theta=math.radians(aiming['theta'])
    )

    [elevation_width, azimut_width, directividad] = arreglo.get_beam_width(plot=plot)
    if plot: arreglo.plot_3D()

    return {'elevation':elevation_width, 'azimut': azimut_width}


def stage_one(cfg):
    """
    ETAPA 1. Genera datos para Heatmap
    """
    current_pass = 0
    delayed_widths = []
    for aux_param1 in range(cfg.get_param1_initial_value(), cfg.get_param1_final_value()):
        
        for aux_param2 in range(cfg.get_param2_initial_value(), cfg.get_param2_final_value()):
            width = dask.delayed(array_evaluation_process)(
                distribution_type=cfg.distribution,
                separation=cfg.separation,
                param1=aux_param1,
                param2=aux_param2,
                aiming=cfg.aiming,
                plot=False
            )

            delayed_widths.append(width)            
            current_pass += 1
            print(f'Evaluating pass {current_pass}/{cfg.get_max_passes()}...')
    
    # dask.visualize(*delayed_widths) # Generates 'mydask.png' Task Graph 
    widths = dask.compute(*delayed_widths)
    
    return widths


def stage_two(config):
    """
    ETAPA 2. Evalua la respuesta en frecuencia    
    """    
    rango_frecuencias = [config.design_frequency,2e6,3e6,4e6,5e6,6e6,7e6,8e6,9e6,10e6,11e6,12e6,13e6,14e6,15e6] # ,16e6,17e6,18e6,19e6,20e6
    freq = np.array(rango_frecuencias)
    Dn = core_functions.denormalise_frequencies(
        frequencies_list=freq, 
        distance_reference=config.separation
    )
    
    # Recalculo los anchos para las frecuencias desnormalizadas
    delayed_widths = []
    denormalising_params = []
    current_pass = 0
    for index in range(len(Dn)):
        width = dask.delayed(array_evaluation_process)(
            distribution_type=config.distribution, 
            separation=Dn[index], 
            param1=config.parameter1, 
            param2=config.parameter2,
            aiming=config.aiming,
            plot=False
        )
        denormalising_params.append({
            'distance': Dn[index],
            'frequency': freq[index]
        })
        delayed_widths.append(width)

        current_pass += 1
        print(f'Evaluating pass {current_pass}/{len(Dn)}')
    
    # dask.visualize(*delayed_widths) # Generates 'mydask.png' Task Graph 
    widths = dask.compute(*delayed_widths)
    
    return widths, denormalising_params


def just_plot(config):
    filename = config.configure_log(option=3)
    
    array_evaluation_process(
        distribution_type=config.distribution, 
        separation=config.separation,
        param1=config.parameter1, 
        param2=config.parameter2,
        aiming=config.aiming,
        plot=True
        )

    return filename


def main():
    client = Client()
    config = utils.InputConfig()
    option = config.main_menu()
    
    if option==1:
        dataset = config.configure_log(option=option)
        widths = stage_one(config)
        config.log_widths(option, widths=widths)
        plotting_tools.plot_option_one(filename=dataset)
    
    elif option==2:
        dataset = config.configure_log(option=option)
        widths, denorm_params = stage_two(config)
        config.log_widths(option, widths=widths, extra_params=denorm_params)
        plotting_tools.plot_option_two(filename=dataset)
    
    elif option == 3: 
        just_plot(config)
    
    elif option == 4: 
        config.configure_params()


if __name__ == '__main__':
    main()