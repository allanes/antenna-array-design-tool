from datetime import datetime
import logging
from tkinter import *
from tkinter import ttk
from tkinter.font import names

from antenna_geometric_patterns_generators import Distributions, get_params_names
from antenna_design import main as initialize_dask
from antenna_design import just_plot, stage_one, stage_two
import antenna_plotting_tools as plotting_tools

class InputConfig():
    def __init__(self):
        """
        
        """
        self.distribution = Distributions.STAR.value
        self.separation = 0.25
        self.parameter1 = 10
        self.parameter2 = 15
        self.aiming = {'phi':50, 'theta':30}
        self.parameter1_range = {'from': 10, 'to': 12}
        self.parameter2_range = {'from': 10, 'to': 13}
        self.design_frequency = 5e6

    def get_param1_initial_value(self):
        return self.parameter1_range['from']
   
    def get_param1_final_value(self):
        return self.parameter1_range['to'] + 1
    
    def get_param2_initial_value(self):
        return self.parameter2_range['from']
    
    def get_param2_final_value(self):
        return self.parameter2_range['to'] + 1

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
        self.config = InputConfig()
        self.current_option = None        
        # Setup main app window
        root = Tk()
        root.title('Antenna Design Utility')
        root.geometry('500x500')
        # Creates Main Content Frame
        mainframe = ttk.Frame(root)
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        # Add image
        image = PhotoImage(file='title.gif')
        ttk.Label(mainframe, image=image).grid(column=0, row=0, sticky=(W,E,N,S))
        # Create Tab Control
        tab_control = ttk.Notebook(mainframe, width=400, height=200)
        tab_control.grid(column=0, row=1)
        tab_control.bind('<<NotebookTabChanged>>', func=self.set_current_option)
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

    def set_current_option(self, obj):
        notebook = obj.widget
        indexed_tab = notebook.index(notebook.select())
        self.current_option = indexed_tab

    def _calculate(self):
        # Setup config object with current values
        self.config.distribution = self.distribution_var.get()
        self.config.separation = self.separation_var.get()
        self.config.parameter1 = self.parameter1_var.get()
        self.config.parameter2 = self.parameter2_var.get()
        self.config.aiming = {
            'phi': float(self.aiming_phi_var.get()),
            'theta': float(self.aiming_theta_var.get())
            }
        self.config.parameter1_range = {
            'from': self.param1_from_var.get(),
            'to': self.param1_to_var.get()
            }
        self.config.parameter2_range = {
            'from': self.param2_from_var.get(),
            'to': self.param2_to_var.get()
            }
        self.config.design_frequency = 5e6
        #--
        initialize_dask()
        if self.current_option == 0: # Plot Only
            print('Plot Only')
            just_plot(self.config)
            pass
        elif self.current_option == 1: # Stage One
            print('Evaluate Stage 1')
            dataset = self.config.configure_log(option=1)
            widths = stage_one(self.config)
            self.config.log_width_results(option=1, widths=widths)
            plotting_tools.plot_option_one(filename=dataset)
            
        elif self.current_option == 2: # Stage Two
            print('Evaluate Stage 2')
            dataset = self.config.configure_log(option=2)
            widths, denorm_params = stage_two(self.config)
            self.config.log_width_results(2, widths=widths, extra_params=denorm_params)
            plotting_tools.plot_option_two(filename=dataset)
    
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
        # Declare entries
        distribution_entry = ttk.Combobox(base_frame, width=10, textvariable=self.distribution_var)
        distribution_entry['values'] = [Distributions(index).name for index, dist in enumerate(Distributions)]
        distribution_entry.state(['readonly'])
        distribution_entry.bind('<<ComboboxSelected>>', self.set_parameters_names)
        separation_entry = ttk.Entry(base_frame, width=10, textvariable=self.separation_var)
        aiming_phi_entry = ttk.Entry(base_frame, width=5, textvariable=self.aiming_phi_var)
        aiming_theta_entry = ttk.Entry(base_frame, width=5, textvariable=self.aiming_theta_var)
        # Place entries
        distribution_entry.grid(column=1, row=1, columnspan=3, sticky=(N,S,W,E))
        separation_entry.grid(column=1, row=2, columnspan=2)
        aiming_phi_entry.grid(column=2, row=3)
        aiming_theta_entry.grid(column=4, row=3)
        # Declare and place action and defaults Buttons
        evaluate_button = ttk.Button(base_frame, text="Evaluate", command=self._calculate)
        evaluate_button.grid(column=1, row=10, sticky=(N, S, W, E), rowspan=2, columnspan=3)
        defaults_button = ttk.Button(base_frame, text="Defaults", command=self.set_all_defaults)
        defaults_button.grid(column=1, row=12, sticky=(N, S, W, E), rowspan=2, columnspan=3)

        return base_frame

    def add_param1_and_param2(self, frame):
        ttk.Label(frame, text='Parameter 1').grid(column=0, row=4)
        ttk.Label(frame, text='Parameter 2').grid(column=0, row=5)
        ttk.Label(frame, textvariable=self.param1_name_var).grid(column=3, row=4, columnspan=3)
        ttk.Label(frame, textvariable=self.param2_name_var).grid(column=3, row=5, columnspan=3)
        parameter1_entry = ttk.Entry(frame, width=10, textvariable=self.parameter1_var)
        parameter2_entry = ttk.Entry(frame, width=10, textvariable=self.parameter2_var)
        parameter1_entry.grid(column=1, row=4, columnspan=2)
        parameter2_entry.grid(column=1, row=5, columnspan=2)

    def set_all_defaults(self):
        self.distribution_var.set(Distributions(self.config.distribution).name)
        self.separation_var.set(value=self.config.separation)
        self.aiming_phi_var.set(value=self.config.aiming['phi'])
        self.aiming_theta_var.set(value=self.config.aiming['theta'])
        self.parameter1_var.set(value=self.config.parameter1)
        self.parameter2_var.set(value=self.config.parameter2)
        self.set_parameters_names()
        # Stage-One-Only
        self.param1_from_var.set(value=self.config.parameter1_range['from'])
        self.param1_to_var.set(value=self.config.parameter1_range['to'])
        self.param2_from_var.set(value=self.config.parameter2_range['from'])
        self.param2_to_var.set(value=self.config.parameter2_range['to'])
        # Stage-Two-Only
        self.design_frequency_var.set(value=self.config.design_frequency)

    def add_plot_frame(self, parent_frame):
        base_frame = self.add_base_frame(parent_frame, col=0, row=0)
        self.add_param1_and_param2(frame=base_frame)
        return base_frame

    def add_stage_one_frame(self, parent_frame):
        base_frame = self.add_base_frame(parent_frame, col=1, row=0)
        
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
        self.add_param1_and_param2(frame=base_frame)
        # Declare and place labels
        ttk.Label(base_frame, text="Design Frequency").grid(column=0, row=6)
        # Declare entries
        design_freq_entry = ttk.Entry(base_frame, width=5, textvariable=self.design_frequency_var)
        # Place entries
        design_freq_entry.grid(column=1, row=6, columnspan=3, sticky=(N,S,E,W))
        
        return base_frame


if __name__ == '__main__':
    icfg = InputConfigGUI()