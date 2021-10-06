from datetime import datetime
import logging
from tkinter import *
from tkinter import ttk

from antenna_geometric_patterns_generators import Distributions as disposition_types

class InputConfig():
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

    def _log_width(self,width):
        logging.info('Resultados:')
        logging.info(f' -Ancho de Elevacion  = {width["elevation"]}')
        logging.info(f' -Ancho de Azimuth = {width["azimut"]}')            
        logging.info("-------------------------------------------")

    def log_width_results(self, option, widths, extra_params=None):
        if option==1:
            param1_total_elements = self.get_param1_final_value() - self.get_param1_initial_value()
            param2_total_elements = self.get_param2_final_value() - self.get_param2_initial_value()
            for aux_param1 in range(param1_total_elements):
                logging.info(f'Cantidad de Elementos en Parametro 1: {aux_param1+self.get_param1_initial_value()}')
                for aux_param2 in range(param2_total_elements):
                    index = aux_param1 * (param2_total_elements) + aux_param2
                    logging.info(f'----------Cantidad de Elementos en Parametro 2: {aux_param2+self.get_param2_initial_value()} -------------')
                    self._log_width(width=widths[index])
                    
        if option == 2:
            for index in range(len(extra_params)):
                logging.info(f"Distancia en Lambda: {extra_params[index]['distance']}")
                logging.info(f"Frecuencia: {extra_params[index]['frequency']}")
                self._log_width(width=widths[index])
        

    def main_menu(self):
        print('*Menu Principal*')
        print('1. Etapa 1. Calcular anchos de haz para el config normalizado')
        print('2. Etapa 2. Calcular respuesta en frecuencia para el config desnormalizado')
        print('3. Calcular y graficar el config configurado')
        print('4. Configurar arreglo')
        
        self.show_config()
        return int(input('\nSeleccione una opcion>>'))

class InputConfigGUI():
    def __init__(self):
        # Setup main app window
        root = Tk()
        root.title('Antenna Design Utility')
        # Creates Main Content Frame
        mainframe = ttk.Frame(root, padding='3 3 12 20')
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1) 
        # Creates sub Content Frames
        just_plot_frame = self.add_plot_frame(parent_frame=mainframe)
        stage_one_frame = self.add_stage_one_frame(parent_frame=mainframe)
        

        # Add some polish
        for child in mainframe.winfo_children(): 
            child.grid_configure(padx=5, pady=5)
        # Make it start the Event Loop
        root.mainloop()

    def _calculate():
        pass

    def add_base_frame(self, parent_frame):
        # Declare variables
        self.distribution = StringVar(value=disposition_types.STAR.value)
        self.separation = StringVar(value=0.25)
        self.parameter1 = StringVar(value=10)
        self.parameter2 = StringVar(value=15)
        self.aiming_phi = StringVar(value=50)
        self.aiming_theta = StringVar(value=30)
        # self.aiming = {'phi':50, 'theta':30}

        plot_frame = ttk.Frame(parent_frame, padding='3 3 12 20')
        plot_frame = plot_frame.grid(column=0, row=0)
        # Declare and place labels
        ttk.Label(plot_frame, text="Distribution").grid(column=0, row=1, sticky=(W, E))
        ttk.Label(plot_frame, textvariable="Separation").grid(column=0, row=2, sticky=(W, E))
        ttk.Label(plot_frame, text="Pointing phi").grid(column=0, row=3, sticky=(W, E))
        ttk.Label(plot_frame, text="Pointing theta").grid(column=0, row=4, sticky=(W, E))
        ttk.Label(plot_frame, text="Param 1").grid(column=0, row=5, sticky=(W, E))
        ttk.Label(plot_frame, text="Param 2").grid(column=0, row=6, sticky=(W, E))

        # Declare and place entries
        distribution_entry = ttk.Entry(plot_frame, width=7, textvariable=self.distribution)
        separation_entry = ttk.Entry(plot_frame, width=7, textvariable=self.separation)
        parameter1_entry = ttk.Entry(plot_frame, width=7, textvariable=self.parameter1)
        parameter2_entry = ttk.Entry(plot_frame, width=7, textvariable=self.parameter2)
        aiming_phi_entry = ttk.Entry(plot_frame, width=7, textvariable=self.aiming_phi)
        aiming_theta_entry = ttk.Entry(plot_frame, width=7, textvariable=self.aiming_theta)
        distribution_entry = distribution_entry.grid(column=1, row=1, sticky=(N,S))
        separation_entry = separation_entry.grid(column=1, row=2, sticky=(N,S))
        parameter1_entry = parameter1_entry.grid(column=1, row=3, sticky=(N,S))
        parameter2_entry = parameter2_entry.grid(column=1, row=4, sticky=(N,S))
        aiming_phi_entry = aiming_phi_entry.grid(column=1, row=5, sticky=(N,S))
        aiming_theta_entry = aiming_theta_entry.grid(column=1, row=6, sticky=(N,S))

        # ttk.Button(plot_frame, text="Calculate", command=self._calculate).grid(column=3, row=3, sticky=W)
        return plot_frame

    def add_plot_frame(self, parent_frame):
        base_frame = self.add_base_frame(parent_frame)
        return base_frame

    def add_stage_one_frame(self, parent_frame):
        pass


if __name__ == '__main__':
    icfg = InputConfigGUI()