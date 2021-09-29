from datetime import datetime
import logging
import numpy as np
import math

import antenna_core_functions
import antenna_geometric_patterns_generators
from antenna_geometric_patterns_generators import GeometryArray
from antenna_geometric_patterns_generators import Disposiciones as disposition_types
import graficar_etapa1
import graficar_etapa2

class ConfiguracionEntrada:
    def __init__(self):
        """
        
        """
        self.disposicion = disposition_types.STAR.value
        self.separacion = 0.25
        self.parametro1 = 10
        self.parametro2 = 15
        self.apuntamiento = {'phi':50, 'theta':30}
        self.rango_parametro1 = [10,12]
        self.rango_parametro2 = [10,13]
        self.frecuencia_disenio = 5e6

    def mostrar_configuracion(self):
        print('\nArreglo configurado:')
        print(f'  Disposicion: {disposition_types(self.disposicion).name}')
        print(f'  Separacion: {self.separacion} [lambda]')
        print(f'  Apuntamiento: phi={self.apuntamiento["phi"]},')
        print(f'                theta={self.apuntamiento["theta"]}')
        print(f'  Rango de elementos para X: {self.rango_parametro1}')
        print(f'  Rango de elementos para Y: {self.rango_parametro2}')
        print(f'  Frecuencia de disenio: {self.frecuencia_disenio}')
        print(f'  Elementos en X: {self.parametro1} (utilizado en Opciones 2 y 3)')
        print(f'  Elementos en Y: {self.parametro2} (utilizado en Opciones 2 y 3)')

    def __configurar_parametros_principal(self):
        print("Configuracion del Arreglo de Antenas")
        print("    1. Config. gral: Disposicion, Apuntamiento, Separacion")
        print("    2. Config. etapa 1: Rangos para generar arreglos")
        print("    3. Config. etapa 2: Frecuencia y cantidad de elementos para desnormalizar")
        print("    4. Volver")
        return input("\nQue desea configurar? >>")
    
    def configurar_parametros(self):
        opcion_configuracion = ""

        while(opcion_configuracion != 'q'):
            opcion_configuracion = self.__configurar_parametros_principal()

            if opcion_configuracion == '1':
                # Configuracion general (disposicion, apuntamiento,separacion)
                print('      Disposiciones:')
                for index, disp in enumerate(disposition_types):
                    print(f'{index}. {disp}')
                self.disposicion = int(input('Disposicion>>'))
                self.apuntamiento['phi'] = float(input("    Apuntamiento Phi>>"))
                self.apuntamiento['theta'] = float(input("    Apuntamiento Theta>>"))
                self.separacion = float(input('    Separacion [lambda]>>'))

            elif opcion_configuracion == '2':
                # Configuracion de etapa 1 (parametro 1, parametro 2)
                print('      Rango de elementos de Parametro 1')
                self.rango_parametro1[0] = int(input('     Valor inicial>>'))
                self.rango_parametro1[1] = int(input('     Valor final>>'))
                print('      Rango de elementos de Parametro 2')
                self.rango_parametro2[0] = int(input('     Valor inicial>>'))
                self.rango_parametro2[1] = int(input('     Valor final>>'))

            elif opcion_configuracion == '3':
                # Configuracion de etapa 2 (frec_disenio, elementos en x, elementos en y)
                self.parametro1 = int(input("     Parametro 1>>"))
                self.parametro2 = int(input("     Parametro 2>>"))
                self.frecuencia_disenio = float(input("     Frecuencia de disenio>>"))

            elif opcion_configuracion == '4':
                opcion_configuracion = 'q'

            self.mostrar_configuracion()

    def get_param1_initial_value(self):
        return self.rango_parametro1[0]
   
    def get_param1_final_value(self):
        return self.rango_parametro1[1] + 1
    
    def get_param2_initial_value(self):
        return self.rango_parametro2[0]
    
    def get_param2_final_value(self):
        return self.rango_parametro2[1] + 1

    def get_max_progress(self):
        return(
            (self.get_param1_initial_value() - self.get_param1_final_value()) * 
            (self.get_param2_initial_value() - self.get_param2_final_value())
        )

    def configurar_log(self, etapa, separacion_metros=0):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename=f'logs/log_etapa{etapa}_{timestamp}.log'
        logging.basicConfig(
            filename=filename,
            level=logging.INFO,
            # handlers=logging.StreamHandler(),
            format='%(asctime)s - %(message)s',
        )
        print(f'Archivo creado: {filename}')
        # Logueo los datos:
        if etapa == 1:
            logging.info(f'Iniciando Etapa 1. Obtencion de datos para evaluar ancho de haz en funcion de lambda. Configuracion inicial:')
            logging.info(f'Arreglo tipo {self.disposicion}')
            logging.info(f'  -Separacion: {self.separacion} [lambda]')

        elif etapa == 2:
            logging.info(f'Iniciando Etapa 2. Obtencion de datos para evaluar la respuesta en frecuencia. Configuracion inicial:')
            logging.info(f'Arreglo tipo {self.disposicion}')
            logging.info(f'Separacion entre elementos: {self.separacion} [lambda]')
            logging.info(f"Separacion entre elementos: {separacion_metros} [m]")
            logging.info(f'Desnormalizando para frecuencia de disenio f = {self.frecuencia_disenio} [Hz]')
            logging.info(f'Desnormalizando para {self.parametro1} elementos en Parametro 1 y {self.parametro2} elementos en Parametro 2')
            logging.info('----------------Seccion de Datos Generados----------------')

        return filename

    def log_widths(self, theta, phi):
        logging.info('Resultados:')
        logging.info(f' -Ancho de Elevacion  = {theta}')
        logging.info(f' -Ancho de Azimuth = {phi}')

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


def menu_principal(config):
    print('*Menu Principal*')
    print('1. Etapa 1. Calcular anchos de haz para el config normalizado')
    print('2. Etapa 2. Calcular respuesta en frecuencia para el config desnormalizado')
    print('3. Calcular y graficar el config configurado')
    print('4. Configurar arreglo')
    
    config.mostrar_configuracion()
    return input('\nSeleccione una opcion>>')


def main():    
    config = ConfiguracionEntrada()
    opcion = ""
    
    while(opcion != 'q'):
        opcion = menu_principal(config)
                
        if opcion == '1':
            dataset = etapaUno(config)
            graficar_etapa1.main(dataset)
            opcion = ''

        elif opcion == '2':
            dataset = etapaDos(config)
            graficar_etapa2.main(dataset)
            opcion = ''

        elif opcion == '3':
            opcionTres(config)
            opcion = ''

        elif opcion == '4':
            config.configurar_parametros()
            opcion = ''
            
        elif opcion == '5':
            opcion = 'q'


if __name__ == '__main__':
    main()