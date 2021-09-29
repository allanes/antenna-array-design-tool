import logging
import numpy as np
import math

import antenna_core_functions
from antenna_geometric_patterns_generators import GeometryArray, get_params_names
import utilities as utils
import graficar_etapa1
import graficar_etapa2


def array_evaluation_process(distribution_type, separation, param1, param2, aiming, plot=False):
    geometrical_array = GeometryArray(distribution_type=distribution_type)
    geometrical_array.populate_array(
        separacion=separation, 
        param1= param1, 
        param2=param2
    )
    individual_element_pattern = [antenna_core_functions.patronMonopoloCuartoOnda()]
    
    arreglo = antenna_core_functions.ArregloGeneral(
        posiciones=geometrical_array.posiciones,
        excitaciones=geometrical_array.excitaciones,
        patron=individual_element_pattern
    )

    arreglo.apuntar(
        phi=math.radians(aiming['phi']),
        theta=math.radians(aiming['theta'])
    )

    [elevation_width, azimut_width, directividad] = arreglo.get_beam_width(plot=plot)
    if plot: arreglo.plot_3D()

    return [elevation_width, azimut_width]

def etapaUno(cfg):
    """
    ETAPA 1. Genera datos para Heatmap
    """
    dataset = cfg.configurar_log(etapa=1)
    
    [param1_name, param2_name] = get_params_names(cfg.disposicion)
    progreso_maximo = cfg.get_max_progress()
    aux_progreso = 0
    for aux_param1 in range(cfg.get_param1_initial_value(), cfg.get_param1_final_value()):
        logging.info(f'Cantidad de Elementos en Parametro 1: {aux_param1}')
        for aux_param2 in range(cfg.get_param2_initial_value(), cfg.get_param2_final_value()):
            logging.info(f'----------Cantidad de Elementos en Parametro 2: {aux_param2} -------------')
            [elev_w, azim_w] = array_evaluation_process(
                distribution_type=cfg.disposicion,
                separation=cfg.separacion,
                param1=aux_param1,
                param2=aux_param2,
                aiming=cfg.apuntamiento,
                plot=False
            )
            cfg.log_widths(theta=elev_w, phi=azim_w)
            aux_progreso += 1
            print(f'Progreso: {100*aux_progreso/progreso_maximo:.1f}%')
        logging.info("-------------------------------------------")

    return dataset


def etapaDos(configuracion):
    """
    ETAPA 2. Evalua la respuesta en frecuencia    
    """    
    rango_frecuencias = [configuracion.frecuencia_disenio,2e6,3e6,4e6,5e6,6e6,7e6,8e6,9e6,10e6,11e6,12e6,13e6,14e6,15e6] # ,16e6,17e6,18e6,19e6,20e6
    freq = np.array(rango_frecuencias)
    Dn,d = antenna_core_functions.Unnormalisation_Freq(freq,configuracion.separacion)
    
    dataset = configuracion.configurar_log(etapa=2, separacion_metros=d[0])
    
    # Recalculo los anchos para las frecuencias desnormalizadas
    anchos_elevacion = []
    anchos_azimut = []
    aux_progress = 0
    for index in range(len(Dn)):
        logging.info(f"Distancia en Lambda: {Dn[index]}")
        logging.info(f"Frecuencia: {freq[index]}")
        [elev_w, azim_w] = array_evaluation_process(
            distribution_type=configuracion.disposicion, 
            separation=Dn[index], 
            param1=configuracion.parametro1, 
            param2=configuracion.parametro2,
            aiming=configuracion.apuntamiento,
            plot=False
        )

        anchos_elevacion.append(elev_w)
        anchos_azimut.append(azim_w)
        configuracion.log_widths(theta=elev_w, phi=azim_w)
    
        aux_progress += 1
        print(f'Progreso: {100*aux_progress/len(Dn):.1f}%')
    logging.info('Fin de desnormalizacion')

    return dataset

def opcionTres(config):
    filename = config.configurar_log(etapa=3)
    
    array_evaluation_process(
        distribution_type=config.disposicion, 
        separation=config.separacion, 
        param1=config.parametro1, 
        param2=config.parametro2,
        aiming=config.apuntamiento,
        plot=True
        )

    return filename


def main():    
    config = utils.ConfiguracionEntrada()
    opcion = ""
    
    while(opcion != 'q'):
        opcion = config.menu_principal()
                
        if opcion == '1':
            dataset = etapaUno(config)
            graficar_etapa1.main(dataset)
            opcion = 'q'

        elif opcion == '2':
            dataset = etapaDos(config)
            graficar_etapa2.main(dataset)
            opcion = 'q'

        elif opcion == '3':
            opcionTres(config)
            opcion = 'q'

        elif opcion == '4':
            config.configurar_parametros()
            opcion = 'q'
            
        elif opcion == '5':
            opcion = 'q'


if __name__ == '__main__':
    main()