import logging
import numpy as np
import math

import antenna_core_functions
from antenna_geometric_patterns_generators import GeometryArray, get_params_names
import utilities as utils
import antenna_plotting_tools as plotting_tools


def array_evaluation_process(distribution_type, separation, param1, param2, aiming, plot=False):
    geometrical_array = GeometryArray(distribution_type=distribution_type)
    geometrical_array.populate_array(
        separation=separation, 
        param1= param1, 
        param2=param2
    )
    individual_element_pattern = [antenna_core_functions.quarter_wave_monopole_pattern()]
    
    arreglo = antenna_core_functions.AntennaArray(
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

    return [elevation_width, azimut_width]


def option_one(cfg):
    """
    ETAPA 1. Genera datos para Heatmap
    """
    dataset = cfg.configure_log(option=1)
    
    [param1_name, param2_name] = get_params_names(cfg.distribution)
    progreso_maximo = cfg.get_max_progress()
    aux_progreso = 0
    for aux_param1 in range(cfg.get_param1_initial_value(), cfg.get_param1_final_value()):
        logging.info(f'Cantidad de Elementos en Parametro 1: {aux_param1}')
        for aux_param2 in range(cfg.get_param2_initial_value(), cfg.get_param2_final_value()):
            logging.info(f'----------Cantidad de Elementos en Parametro 2: {aux_param2} -------------')
            [elev_w, azim_w] = array_evaluation_process(
                distribution_type=cfg.distribution,
                separation=cfg.separation,
                param1=aux_param1,
                param2=aux_param2,
                aiming=cfg.aiming,
                plot=False
            )
            cfg.log_widths(theta=elev_w, phi=azim_w)
            aux_progreso += 1
            print(f'Progreso: {100*aux_progreso/progreso_maximo:.1f}%')
        logging.info("-------------------------------------------")

    return dataset


def option_two(config):
    """
    ETAPA 2. Evalua la respuesta en frecuencia    
    """    
    rango_frecuencias = [config.design_frequency,2e6,3e6,4e6,5e6,6e6,7e6,8e6,9e6,10e6,11e6,12e6,13e6,14e6,15e6] # ,16e6,17e6,18e6,19e6,20e6
    freq = np.array(rango_frecuencias)
    Dn,d = antenna_core_functions.denormalise_frequency(freq,config.separation)
    
    dataset = config.configure_log(option=2, separation_m=d[0])
    
    # Recalculo los anchos para las frecuencias desnormalizadas
    anchos_elevacion = []
    anchos_azimut = []
    aux_progress = 0
    for index in range(len(Dn)):
        logging.info(f"Distancia en Lambda: {Dn[index]}")
        logging.info(f"Frecuencia: {freq[index]}")
        [elev_w, azim_w] = array_evaluation_process(
            distribution_type=config.distribution, 
            separation=Dn[index], 
            param1=config.parameter1, 
            param2=config.parameter2,
            aiming=config.aiming,
            plot=False
        )

        anchos_elevacion.append(elev_w)
        anchos_azimut.append(azim_w)
        config.log_widths(theta=elev_w, phi=azim_w)
    
        aux_progress += 1
        print(f'Progreso: {100*aux_progress/len(Dn):.1f}%')
    logging.info('Fin de desnormalizacion')

    return dataset


def option_three(config):
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
    config = utils.InputConfig()
    option = ""
    
    while(option != 'q'):
        option = config.main_menu()
                
        if option == '1':
            dataset = option_one(config)
            plotting_tools.plot_option_one(dataset)
            option = 'q'

        elif option == '2':
            dataset = option_two(config)
            plotting_tools.plot_option_two(dataset)
            option = 'q'

        elif option == '3':
            option_three(config)
            option = 'q'

        elif option == '4':
            config.configure_params()
            option = 'q'
            
        elif option == '5':
            option = 'q'


if __name__ == '__main__':
    main()