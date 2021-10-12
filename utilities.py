from datetime import datetime
import logging
from tkinter import *
from tkinter import ttk
from tkinter.font import names

from antenna_geometric_patterns_generators import Distributions, get_params_names

class InputConfig():
    def __init__(self):
        """
        
        """
        self.distribution = Distributions.STAR.value
        self.separation = 0.25
        self.parameter1 = 10
        self.parameter2 = 15
        self.aiming = {'phi':50, 'theta':30}
        self.parameter1_range = [10,12]
        self.parameter2_range = [10,13]
        self.design_frequency = 5e6

    def show_config(self):
        print('\nArreglo configurado:')
        print(f'  Disposicion: {Distributions(self.distribution).name}')
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
                for index, disp in enumerate(Distributions):
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
        self.distribution = Distributions.STAR.value
        self.separation = 0.25
        self.parameter1 = 10
        self.parameter2 = 15
        self.aiming_phi = 50
        self.aiming_theta = 30
        self.aiming = {'phi':self.aiming_phi, 'theta':self.aiming_theta}
        self.parameter1_range = {'from': 10, 'to': 12}
        self.parameter2_range = {'from': 11, 'to': 14}
        self.design_frequency = 5e6
        
        # Setup main app window
        root = Tk()
        root.title('Antenna Design Utility')
        root.geometry('500x500')
        self.validate_separation_wrapper = (root.register(self.validate_separation), '%P')
        # Creates Main Content Frame
        mainframe = ttk.Frame(root)
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        # Create Tab Control
        tab_control = ttk.Notebook(mainframe, width=400, height=200)
        tab_control.grid(column=0, row=0)
        # Create linked variables
        # -Base frame variables
        self.distribution_var = StringVar()
        self.separation_var = DoubleVar()
        self.aiming_phi_var = IntVar()
        self.aiming_theta_var = IntVar()
        self.parameter1_var = IntVar()
        self.parameter2_var = IntVar()
        self.param1_name_var = StringVar()
        self.param2_name_var = StringVar()
        # -Stage one variables
        self.param1_from_var = IntVar()
        self.param1_to_var = IntVar()
        self.param2_from_var = IntVar()
        self.param2_to_var = IntVar()
        # -Stage two variables
        self.design_frequency_var = DoubleVar()
        # Add individual tabs
        plot_tab = self.add_plot_frame(parent_frame=tab_control)
        stage_one_tab = self.add_stage_one_frame(parent_frame=tab_control)
        stage_two_tab = self.add_stage_two_frame(parent_frame=tab_control)
        self.set_all_defaults()
        # Creates sub Content Frames        
        tab_control.add(plot_tab, text='Plot 3D')
        tab_control.add(stage_one_tab, text='Stage 1')
        tab_control.add(stage_two_tab, text='Stage 2')        

        # Make it start the Event Loop
        root.mainloop()

    def validate_separation(self, newval):
        print(f'New val: {newval}')
        return True

    def _calculate():
        pass

    def set_parameters_names(self, option=None):
        dist = self.distribution_var.get()
        params_names = get_params_names(Distributions[dist].value)
        self.param1_name_var.set(value=params_names[0])
        self.param2_name_var.set(value=params_names[1])

    def add_base_frame(self, parent_frame, col, row):
        # Declare base frame
        base_frame = ttk.Frame(parent_frame)
        base_frame.grid(column=col, row=row)        
        # Declare and place labels
        ttk.Label(base_frame, text="Distribution").grid(column=0, row=1)
        ttk.Label(base_frame, text="Separation").grid(column=0, row=2)
        ttk.Label(base_frame, text="Pointing:").grid(column=0, row=3)
        ttk.Label(base_frame, text="phi").grid(column=1, row=3)
        ttk.Label(base_frame, text="theta").grid(column=3, row=3)
        ttk.Label(base_frame, textvariable=self.param1_name_var).grid(column=0, row=4)
        ttk.Label(base_frame, textvariable=self.param2_name_var).grid(column=0, row=5)
        # Declare entries
        distribution_entry = ttk.Combobox(base_frame, width=10, textvariable=self.distribution_var)
        distribution_entry['values'] = [Distributions(index).name for index, dist in enumerate(Distributions)]
        distribution_entry.state(['readonly'])
        distribution_entry.bind('<<ComboboxSelected>>', self.set_parameters_names)
        separation_entry = ttk.Entry(base_frame, width=10, textvariable=self.separation_var, validate='key', validatecommand=self.validate_separation_wrapper)
        aiming_phi_entry = ttk.Entry(base_frame, width=5, textvariable=self.aiming_phi_var)
        aiming_theta_entry = ttk.Entry(base_frame, width=5, textvariable=self.aiming_theta_var)
        parameter1_entry = ttk.Entry(base_frame, width=10, textvariable=self.parameter1_var)
        parameter2_entry = ttk.Entry(base_frame, width=10, textvariable=self.parameter2_var)
        # Place entries
        distribution_entry.grid(column=1, row=1, columnspan=3, sticky=(N,S,W,E))
        separation_entry.grid(column=1, row=2, columnspan=2)
        aiming_phi_entry.grid(column=2, row=3)
        aiming_theta_entry.grid(column=4, row=3)
        parameter1_entry.grid(column=1, row=4, columnspan=2)
        parameter2_entry.grid(column=1, row=5, columnspan=2)
        # Set entries to default
       
        print("var's set")
        # Declare and place action Button
        button = ttk.Button(base_frame, text="Evaluate", command=self._calculate)
        button.grid(column=1, row=10, sticky=(N, S, W, E), rowspan=2, columnspan=3)

        return base_frame

    def set_all_defaults(self):
        self.distribution_var.set(Distributions(self.distribution).name)
        self.separation_var.set(value=self.separation)
        self.aiming_phi_var.set(value=self.aiming_phi)
        self.aiming_theta_var.set(value=self.aiming_theta)
        self.parameter1_var.set(value=self.parameter1)
        self.parameter2_var.set(value=self.parameter2)
        self.set_parameters_names()
        # Stage-One-Only
        self.param1_from_var.set(value=self.parameter1_range['from'])
        self.param1_to_var.set(value=self.parameter1_range['to'])
        self.param2_from_var.set(value=self.parameter2_range['from'])
        self.param2_to_var.set(value=self.parameter2_range['to'])
        # Stage-Two-Only
        self.design_frequency_var.set(value=self.design_frequency)

    def add_plot_frame(self, parent_frame):
        base_frame = self.add_base_frame(parent_frame, col=0, row=0)
        return base_frame

    def add_stage_one_frame(self, parent_frame):
        base_frame = self.add_base_frame(parent_frame, col=1, row=0)
        print(base_frame.winfo_children)
        
        # Declare and place labels
        ttk.Label(base_frame, text="Parameter 1").grid(column=0, row=6)
        ttk.Label(base_frame, text="from").grid(column=1, row=6)
        ttk.Label(base_frame, text="to").grid(column=3, row=6)
        ttk.Label(base_frame, text="Parameter 2").grid(column=0, row=7)
        ttk.Label(base_frame, text="from").grid(column=1, row=7)
        ttk.Label(base_frame, text="to").grid(column=3, row=7)
        # Declare entries
        param1_from_entry = ttk.Entry(base_frame, width=5, textvariable=self.param1_from_var)
        param1_to_entry = ttk.Entry(base_frame, width=5, textvariable=self.param1_to_var)
        param2_from_entry = ttk.Entry(base_frame, width=5, textvariable=self.param2_from_var)
        param2_to_entry = ttk.Entry(base_frame, width=5, textvariable=self.param2_to_var)
        # Place entries
        param1_from_entry.grid(column=2, row=6)
        param1_to_entry.grid(column=4, row=6)
        param2_from_entry.grid(column=2, row=7)
        param2_to_entry.grid(column=4, row=7)

        return base_frame

    def add_stage_two_frame(self, parent_frame):
        base_frame = self.add_base_frame(parent_frame, col=2, row=0)
        # Declare stage one exclusive variables
        
        # Declare and place labels
        ttk.Label(base_frame, text="Design Frequency").grid(column=0, row=6)
        # Declare entries
        design_freq_entry = ttk.Entry(base_frame, width=5, textvariable=self.design_frequency_var)
        # Place entries
        design_freq_entry.grid(column=1, row=6, columnspan=3, sticky=(N,S,E,W))
        
        return base_frame


if __name__ == '__main__':
    icfg = InputConfigGUI()