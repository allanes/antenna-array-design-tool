import seaborn as sns
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt


def main():
    valores_eje_cantidad_anillos = []
    valores_eje_cantidad_elementos = []
    valores_elevacion_raw = []
    valores_azimuth_raw = []

    with open('antenas_log_bak.log', 'r') as f:
        aux_cant_anillos_actual = 0
        aux_cant_elementos_actual = 0
        aux_elevacion_actual = 0.0
        aux_azimuth_actual = 0.0
        paso_por_aca_flag = 0

        for line in f:
            if line[26:].startswith('-TT'):
                aux_cant_anillos_actual = line[58:].split()[0]
                valores_eje_cantidad_anillos.append(int(aux_cant_anillos_actual))
                paso_por_aca_flag += 1
                continue
            if line[26:].startswith('Cantidad'): #'Cantidad de Elementos'
                if (paso_por_aca_flag > 1): 
                    continue
                aux_cant_elementos_actual = line[49:].split()[0]
                if not aux_cant_anillos_actual in valores_eje_cantidad_elementos:
                    valores_eje_cantidad_elementos.append(int(aux_cant_elementos_actual))
                continue
            if line[26:].startswith(' -Ancho de E'):
                aux_elevacion_actual = line[50:].split()[0]
                valores_elevacion_raw.append(float(aux_elevacion_actual))
                continue
            if line[26:].startswith(' -Ancho de A'):
                aux_azimuth_actual = line[47:].split()[0]
                valores_azimuth_raw.append(float(aux_azimuth_actual))
                continue
        
    indice_truncar_arreglo = len(valores_eje_cantidad_anillos)*len(valores_eje_cantidad_elementos)
    valores_elevacion_raw = valores_elevacion_raw[:indice_truncar_arreglo]

    valores_elevacion = np.reshape(
            np.array(valores_elevacion_raw), 
            (len(valores_eje_cantidad_anillos), len(valores_eje_cantidad_elementos))
        )

    fig, ax = plt.subplots()
    im = ax.imshow(valores_elevacion)
    
    # Configura la grilla de la grafica
    ax.set_xticks(np.arange(len(valores_eje_cantidad_elementos)))
    ax.set_yticks(np.arange(len(valores_eje_cantidad_anillos)))
    # Configura las etiquetas de las marcas de los ejes
    ax.set_xticklabels(valores_eje_cantidad_elementos)
    ax.set_yticklabels(valores_eje_cantidad_anillos)
    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
            rotation_mode="anchor")
    # Agrega el valor del ancho a cada par de entrada x, y
    for i in range(len(valores_eje_cantidad_anillos)):
        for j in range(len(valores_eje_cantidad_elementos)):
            text = ax.text(
                j, 
                i,
                '{:.2f}'.format(valores_elevacion[i][j]),
                ha="center", 
                va="center", 
                color="w"
                )

    ax.set_title('Ancho del patrón de radiación en la coordenada/eje de Elevación')
    fig.tight_layout()
    """
    """
    plt.show()

    return

if __name__ == '__main__':
    main()
    