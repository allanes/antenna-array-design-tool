from datetime import datetime
import logging

from antenna_geometric_patterns_generators import Distributions as disposition_types

class InputConfig:
    def __init__(self):
        """
        
        """
        self.distribution = disposition_types.STAR.value
        self.separation = 0.25
        self.parameter1 = 10
        self.parameter2 = 15
        self.aiming = {'phi':50, 'theta':30}
        self.parameter1_range = [10,12]
        self.parameter2_range = [10,13]
        self.design_frequency = 5e6

    def show_config(self):
        print('\nArreglo configurado:')
        print(f'  Disposicion: {disposition_types(self.distribution).name}')
        print(f'  Separacion: {self.separation} [lambda]')
        print(f'  Apuntamiento: phi={self.aiming["phi"]},')
        print(f'                theta={self.aiming["theta"]}')
        print(f'  Rango de elementos para X: {self.parameter1_range}')
        print(f'  Rango de elementos para Y: {self.parameter2_range}')
        print(f'  Frecuencia de disenio: {self.design_frequency}')
        print(f'  Elementos en X: {self.parameter1} (utilizado en Opciones 2 y 3)')
        print(f'  Elementos en Y: {self.parameter2} (utilizado en Opciones 2 y 3)')

    def __params_config_menu(self):
        print("Configuracion del Arreglo de Antenas")
        print("    1. Config. gral: Disposicion, Apuntamiento, Separacion")
        print("    2. Config. etapa 1: Rangos para generar arreglos")
        print("    3. Config. etapa 2: Frecuencia y cantidad de elementos para desnormalizar")
        print("    4. Volver")
        return input("\nQue desea configurar? >>")
    
    def configure_params(self):
        opcion_configuracion = ""

        while(opcion_configuracion != 'q'):
            opcion_configuracion = self.__params_config_menu()

            if opcion_configuracion == '1':
                # Configuracion general (disposicion, apuntamiento,separacion)
                print('      Disposiciones:')
                for index, disp in enumerate(disposition_types):
                    print(f'{index}. {disp}')
                self.distribution = int(input('Disposicion>>'))
                self.aiming['phi'] = float(input("    Apuntamiento Phi>>"))
                self.aiming['theta'] = float(input("    Apuntamiento Theta>>"))
                self.separation = float(input('    Separacion [lambda]>>'))

            elif opcion_configuracion == '2':
                # Configuracion de etapa 1 (parametro 1, parametro 2)
                print('      Rango de elementos de Parametro 1')
                self.parameter1_range[0] = int(input('     Valor inicial>>'))
                self.parameter1_range[1] = int(input('     Valor final>>'))
                print('      Rango de elementos de Parametro 2')
                self.parameter2_range[0] = int(input('     Valor inicial>>'))
                self.parameter2_range[1] = int(input('     Valor final>>'))

            elif opcion_configuracion == '3':
                # Configuracion de etapa 2 (frec_disenio, elementos en x, elementos en y)
                self.parameter1 = int(input("     Parametro 1>>"))
                self.parameter2 = int(input("     Parametro 2>>"))
                self.design_frequency = float(input("     Frecuencia de disenio>>"))

            elif opcion_configuracion == '4':
                opcion_configuracion = 'q'

            self.show_config()

    def get_param1_initial_value(self):
        return self.parameter1_range[0]
   
    def get_param1_final_value(self):
        return self.parameter1_range[1] + 1
    
    def get_param2_initial_value(self):
        return self.parameter2_range[0]
    
    def get_param2_final_value(self):
        return self.parameter2_range[1] + 1

    def get_max_passes(self):
        return(
            (self.get_param1_final_value() - self.get_param1_initial_value()) * 
            (self.get_param2_final_value() - self.get_param2_initial_value())
        )

    def configure_log(self, option, separation_m=0):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename=f'logs/log_etapa{option}_{timestamp}.log'
        logging.basicConfig(
            filename=filename,
            level=logging.INFO,
            # handlers=logging.StreamHandler(),
            format='%(asctime)s - %(message)s',
        )
        print(f'Archivo creado: {filename}')
        # Logueo los datos:
        if option == 1:
            logging.info(f'Iniciando Etapa 1. Obtencion de datos para evaluar ancho de haz en funcion de lambda. Configuracion inicial:')
            logging.info(f'Arreglo tipo {self.distribution}')
            logging.info(f'  -Separacion: {self.separation} [lambda]')

        elif option == 2:
            logging.info(f'Iniciando Etapa 2. Obtencion de datos para evaluar la respuesta en frecuencia. Configuracion inicial:')
            logging.info(f'Arreglo tipo {self.distribution}')
            logging.info(f'Separacion entre elementos: {self.separation} [lambda]')
            logging.info(f"Separacion entre elementos: {separation_m} [m]")
            logging.info(f'Desnormalizando para frecuencia de disenio f = {self.design_frequency} [Hz]')
            logging.info(f'Desnormalizando para {self.parameter1} elementos en Parametro 1 y {self.parameter2} elementos en Parametro 2')
            logging.info('----------------Seccion de Datos Generados----------------')

        return filename

    def log_widths(self, option, widths, extra_params=None):
        param1_total_elements = self.get_param1_final_value() - self.get_param1_initial_value()
        param2_total_elements = self.get_param2_final_value() - self.get_param2_initial_value()
        for aux_param1 in range(param1_total_elements):
            if (option==1):logging.info(f'Cantidad de Elementos en Parametro 1: {aux_param1+self.get_param1_initial_value()}')
            for aux_param2 in range(param2_total_elements):
                index = aux_param1 * (param2_total_elements) + aux_param2
                if option == 1:
                    logging.info(f'----------Cantidad de Elementos en Parametro 2: {aux_param2+self.get_param2_initial_value()} -------------')
                    
                if option == 2:
                    logging.info(f"Distancia en Lambda: {extra_params[index]['distance']}")
                    logging.info(f"Frecuencia: {extra_params[index]['frequency']}")

                logging.info('Resultados:')
                logging.info(f' -Ancho de Elevacion  = {widths[index]["elevation"]}')
                logging.info(f' -Ancho de Azimuth = {widths[index]["azimut"]}')
            
            logging.info("-------------------------------------------")
        

    def main_menu(self):
        print('*Menu Principal*')
        print('1. Etapa 1. Calcular anchos de haz para el config normalizado')
        print('2. Etapa 2. Calcular respuesta en frecuencia para el config desnormalizado')
        print('3. Calcular y graficar el config configurado')
        print('4. Configurar arreglo')
        
        self.show_config()
        return int(input('\nSeleccione una opcion>>'))