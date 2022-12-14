import numpy as np
import math
from dask.distributed import Client
import dask.delayed

import arreglo_antenas_core.antenna_core_functions as core_functions
from arreglo_antenas_core.antenna_geometric_patterns_generators import GeometryArray


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

    (elevation_width, azimut_width) = arreglo.get_beam_width(plot=plot)
    origin = [0,0,0]
    if geometrical_array.distribution_name == 0:
        dx = separation*(param1 - 1) / 2
        dy = separation*(param2 - 1) / 2
        origin = [dx, dy, 0]
    
    if plot: arreglo.plot_3D(origin)

    return {'elevation':elevation_width, 'azimut': azimut_width}


def stage_one(config):
    """
    ETAPA 1. Genera datos para Heatmap
    """
    current_pass = 0
    delayed_widths = []
    for aux_param1 in range(config.get_param1_initial_value(), config.get_param1_final_value()):
        
        for aux_param2 in range(config.get_param2_initial_value(), config.get_param2_final_value()):
            width = dask.delayed(array_evaluation_process)(
                distribution_type=config.distribution,
                separation=config.separation,
                param1=aux_param1,
                param2=aux_param2,
                aiming=config.aiming,
                plot=False
            )

            delayed_widths.append(width)            
            current_pass += 1
            print(f'Evaluating pass {current_pass}/{config.get_max_passes()}...')
    
    # dask.visualize(*delayed_widths) # Generates 'mydask.png' Task Graph 
    widths = dask.compute(*delayed_widths)
    
    return widths


def stage_two(config):
    """
    ETAPA 2. Evalua la respuesta en frecuencia    
    """    
    rango_frecuencias = [config.design_frequency,2e6,3e6,4e6,5e6,6e6,7e6,8e6,9e6,10e6,11e6,12e6,13e6,14e6,15e6, 16e6,17e6,18e6,19e6,20e6]
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
    
    array_evaluation_process(
        distribution_type=config.distribution, 
        separation=config.separation,
        param1=config.parameter1, 
        param2=config.parameter2,
        aiming=config.aiming,
        plot=True
        )


def main():
    client = Client()
    # client = Client(processes=False)
    
