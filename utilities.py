from datetime import datetime
import logging

from antenna_geometric_patterns_generators import Disposiciones as disposition_types

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

    def menu_principal(self):
        print('*Menu Principal*')
        print('1. Etapa 1. Calcular anchos de haz para el config normalizado')
        print('2. Etapa 2. Calcular respuesta en frecuencia para el config desnormalizado')
        print('3. Calcular y graficar el config configurado')
        print('4. Configurar arreglo')
        
        self.mostrar_configuracion()
        return input('\nSeleccione una opcion>>')