from datetime import datetime
import logging
import Arreglo_Antena_2D

class ConfiguracionEntrada:
    def __init__(
        self,
        disposicion=Arreglo_Antena_2D.Disposiciones.RECTANGULAR,
        separacion=0.25, 
        parametro1=10,
        parametro2=10,
        apuntamiento=[50,30], 
        rango_parametro1 = [20,21],
        rango_parametro2 = [20,21]
        ):
        """
        
        """
        self.disposicion = disposicion
        self.separacion = separacion
        self.parametro1 = parametro1
        self.parametro2 = parametro2
        self.apuntamiento = apuntamiento
        self.rango_parametro1 = rango_parametro1
        self.rango_parametro2 = rango_parametro2

    def mostrar_configuracion(self):
        print('\nDatos configurados:')
        print(f'  Disposicion: {self.disposicion}')
        print(f'  Separacion: {self.separacion} [lambda]')
        print(f'  Elementos en X: {self.parametro1} (utilizado en Opciones 2 y 3)')
        print(f'  Elementos en Y: {self.parametro2} (utilizado en Opciones 2 y 3)')
        print(f'  Apuntamiento: phi={self.apuntamiento[0]}, theta={self.apuntamiento[1]}')

    def configurar_parametros(self):
        print('      Disposicion. 1: Rectangular, 2: Circular')
        self.disposicion = Arreglo_Antena_2D.Disposiciones.CIRCULAR if (input('     Disposicion>>')=='2') else Arreglo_Antena_2D.Disposiciones.RECTANGULAR
        self.separacion = float(input('     Separacion [lambda]>>'))     
        print('      Rango de elementos en el eje X')
        self.rango_parametro1[0] = int(input('     Valor inicial>>'))
        self.rango_parametro1[1] = int(input('     Valor final>>'))
        print('      Rango de elementos en el eje Y')
        self.rango_parametro2[0] = int(input('     Valor inicial>>'))
        self.rango_parametro2[1] = int(input('     Valor final>>'))
        self.parametro1 = int(input("     Parametro 1>>"))
        self.parametro2 = int(input("     Parametro 2>>"))
        self.apuntamiento[0] = float(input("    Phi>>"))
        self.apuntamiento[1] = float(input("    Theta>>"))

    def configurar_logging(self, etapa):
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

def etapaUno(configuracion):
    # ----ETAPA 1. Genera datos para Heatmap
    configuracion.configurar_logging(etapa=1)
    
    for aux_param1 in range(configuracion.rango_parametro1[0],configuracion.rango_parametro1[1]+1):
        logging.info(f'Cantidad de Elementos en Parametro 1: {aux_param1}')
        
        for aux_param2 in range(configuracion.rango_parametro2[0],configuracion.rango_parametro2[1]+1):
            logging.info(f'----------Cantidad de Elementos en Parametro 2: {aux_param2} -------------')
            Arreglo_Antena_2D.main(configuracion.separacion,aux_param1,aux_param2,graficar=False)
        logging.info("-------------------------------------------")

def menu_principal(config):
    print('1. Etapa 1. Calcular anchos de haz para el config normalizado')
    print('2. Etapa 2. Calcular respuesta en frecuencia para el config desnormalizado')
    print('3. Calcular y graficar el config configurado')
    print('4. Configurar config')
    
    config.mostrar_configuracion()

    return input('Seleccione una opcion>>')

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






if __name__ == '__main__':
    main()