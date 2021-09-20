import logging
import funciones_evaluacion


def main():
    logging.basicConfig(
        filename='antenas_log.log',
        level=logging.INFO,
        # handlers=logging.StreamHandler(),
        format='%(asctime)s - %(message)s',
    )

    DR = 0.25 #separacion radial entre elementos
    Nr = 10 # Num. de anillos   (Para un unico elemento Nr = 0)
    N = 10 # Num. de elementos por anillo
    Dz = 0.25 # separacion sobre el eje z
    Nz = 1 # Num de elementos sobre el eje z
    #Logueo los datos:
    logging.info(f'Datos CONSTANTES del arreglo CIRCULAR:')
    logging.info(f'  -DR = {DR}')
    logging.info(f'  -Dz = {Dz}')
    logging.info(f'  -Nz = {Nz}')

    

    for aux in range(20,21):#20):
        logging.info(f'----------Cantidad de Anillos {aux}-------------')
        for aux2 in range(20,21):
            logging.info(f'Cantidad de Elementos: {aux2}')
            funciones_evaluacion.main(DR,aux,aux2,Dz,Nz)
        logging.info("-------------------------------------------")

if __name__ == '__main__':
    main()