from datetime import datetime
import logging

import numpy as np
import Arreglo_Antena_2D

class ConfiguracionEntrada:
    def __init__(self):
        """
        
        """
        self.disposicion = Arreglo_Antena_2D.Disposiciones.CIRCULAR.value
        self.separacion = 0.25
        self.parametro1 = 10
        self.parametro2 = 15
        self.apuntamiento = [50,30]
        self.rango_parametro1 = [10,15]
        self.rango_parametro2 = [10,50]
        self.frecuencia_disenio = 5e6

    def mostrar_configuracion(self):
        print('\nArreglo configurado:')
        print(f'  Disposicion: {Arreglo_Antena_2D.Disposiciones(self.disposicion).name}')
        print(f'  Separacion: {self.separacion} [lambda]')
        print(f'  Apuntamiento: phi={self.apuntamiento[0]},')
        print(f'                theta={self.apuntamiento[1]}')
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
                for index, disp in enumerate(Arreglo_Antena_2D.Disposiciones):
                    print(f'{index}. {disp}')
                self.disposicion = int(input('Disposicion>>'))
                self.apuntamiento[0] = float(input("    Apuntamiento Phi>>"))
                self.apuntamiento[1] = float(input("    Apuntamiento Theta>>"))
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
            logging.info(f'  -DR = {self.separacion}')

        elif etapa == 2:
            logging.info(f'Iniciando Etapa 2. Obtencion de datos para evaluar la respuesta en frecuencia. Configuracion inicial:')
            logging.info(f'Arreglo tipo {self.disposicion}')
            logging.info(f'Separacion entre elementos: {self.separacion} [lambda]')
            logging.info(f"Separacion entre elementos: {separacion_metros} [m]")
            logging.info(f'Desnormalizando para frecuencia de disenio f = {self.frecuencia_disenio} [Hz]')
            logging.info(f'Desnormalizando para {self.parametro1} elementos en Parametro 1 y {self.parametro2} elementos en Parametro 2')
            logging.info('----------------Seccion de Datos Generados----------------')


def etapaUno(configuracion):
    """
    ETAPA 1. Genera datos para Heatmap
    """

    configuracion.configurar_log(etapa=1)
    
    for aux_param1 in range(configuracion.rango_parametro1[0],configuracion.rango_parametro1[1]+1):
        logging.info(f'Cantidad de Elementos en Parametro 1: {aux_param1}')
        
        for aux_param2 in range(configuracion.rango_parametro2[0],configuracion.rango_parametro2[1]+1):
            logging.info(f'----------Cantidad de Elementos en Parametro 2: {aux_param2} -------------')
            Arreglo_Antena_2D.main(configuracion.disposicion,configuracion.separacion,aux_param1,aux_param2,graficar=False)
        logging.info("-------------------------------------------")


def etapaDos(configuracion):
    """
    ETAPA 2. Evalua la respuesta en frecuencia    
    """
    
    rango_frecuencias = [configuracion.frecuencia_disenio,2e6,3e6,4e6,5e6,6e6,7e6,8e6,9e6,10e6,11e6,12e6,13e6,14e6,15e6,16e6,17e6,18e6,19e6,20e6] # 
    freq = np.array(rango_frecuencias)
    Dn,d = Arreglo_Antena_2D.Unnormalisation_Freq(freq,configuracion.separacion)
    
    configuracion.configurar_log(etapa=2, separacion_metros=d[0])
    
    # Recalculo los anchos para las frecuencias desnormalizadas
    anchos_elevacion = []
    anchos_azimut = []
    for index in range(len(Dn)):
        logging.info(f"Distancia en Lambda: {Dn[index]}")
        logging.info(f"Frecuencia: {freq[index]}")
        [elev, azim] = Arreglo_Antena_2D.main(configuracion.disposicion, Dn[index], configuracion.parametro1, configuracion.parametro2,graficar=False)        
        anchos_elevacion.append(elev)
        anchos_azimut.append(azim)
    
    logging.info('Fin de desnormalizacion')


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
                
        if opcion == '4':
            config.configurar_parametros()
            
        if opcion == '5':
            opcion = 'q'

        if opcion == '1':
            etapaUno(config)
            opcion = 'q'

        if opcion == '2':
            etapaDos(config)
            opcion = 'q'

        if opcion == '3':
            config.configurar_log(etapa=3)
            Arreglo_Antena_2D.main(config.disposicion, config.separacion, config.parametro1, config.parametro2,graficar=True)
            opcion = 'q'


if __name__ == '__main__':
    main()