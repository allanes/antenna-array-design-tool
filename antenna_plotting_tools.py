import numpy as np
from matplotlib import pyplot as plt
import heatmap


def plot_option_one(filename=""):
    param1_values = []
    param2_values = []
    elevation_values_raw = []
    azimut_values_raw = []
    
    if filename == "": 
        filename = 'logs/log_etapa1_20210922_132302.log'

    with open(filename, 'r') as f:
        current_param1 = 0
        current_param2 = 0
        current_elev = 0.0
        current_azim = 0.0
        flag = 0

        for line in f:
            if 'Parametro 1' in line:
                current_param1 = line[64:].split()[0]
                param1_values.append(int(current_param1))
                flag += 1
            
            elif 'Parametro 2' in line:
                if (flag > 1): 
                    continue
                current_param2 = line[74:].split()[0]
                if not current_param1 in param2_values:
                    param2_values.append(int(current_param2))
            
            elif ' Elevacion' in line:
                current_elev = line[50:].split()[0]
                elevation_values_raw.append(float(current_elev))
            
            elif ' Azimut' in line:
                current_azim = line[47:].split()[0]
                azimut_values_raw.append(float(current_azim))
        
    # Reacomodo un poco los datos
    indice_truncar_arreglo = len(param1_values)*len(param2_values)
    elevation_values_raw = elevation_values_raw[:indice_truncar_arreglo]
    azimut_values_raw = azimut_values_raw[:indice_truncar_arreglo]

    elevation_values = np.reshape(
            np.array(elevation_values_raw), 
            (len(param1_values), len(param2_values))
        )

    azimut_values = np.reshape(
            np.array(azimut_values_raw), 
            (len(param1_values), len(param2_values))
        )

    fig, ax = plt.subplots()
    im = ax.imshow(elevation_values)
    
    im, cbar = heatmap.heatmap(
        data=elevation_values,
        row_labels=param1_values,
        col_labels=param2_values,
        ax=ax,
        cmap="YlGn", 
        cbarlabel="ancho_theta"
    )
    texts = heatmap.annotate_heatmap(im, valfmt="{x:.1f}")
    
    # Configura la grilla de la grafica
    ax.set_xlabel('Parametro 2')
    ax.set_ylabel('Parametro 1')
    ax.set_title('Ancho del patrón de radiación en Elevación')
    fig.tight_layout()
    # ---------------
    fig_az, ax_az = plt.subplots()
    im_az = ax_az.imshow(azimut_values)
    
    im_az, cbar = heatmap.heatmap(
        data=azimut_values,
        row_labels=param1_values,
        col_labels=param2_values,
        ax=ax_az,
        cmap="YlGn", 
        cbarlabel="ancho_phi"
    )
    texts = heatmap.annotate_heatmap(im_az, valfmt="{x:.1f}")
    
    # Configura la grilla de la grafica
    ax_az.set_title('Ancho del patrón de radiación en Azimuth')
    ax_az.set_xlabel('Parametro 2')
    ax_az.set_ylabel('Parametro 1')
    fig_az.tight_layout()
    # -----------------
    plt.show()
    return

def plot_option_two(filename=""):
    frequency_values = []
    elevation_values_raw = []
    azimut_values_raw = []

    if filename == "": 
        filename = 'logs/log_etapa2_informe.log'

    with open(filename, 'r') as f:
        aux_freq = 0
        current_elevation = 0.0
        current_azimut = 0.0
        
        for line in f:
            if 'Frecuencia' in line:
                aux_freq = line[38:]
                frequency_values.append(float(aux_freq))
                
            elif 'Elevacion' in line:
                current_elevation = line[50:].split()[0]
                elevation_values_raw.append(float(current_elevation))
                
            elif 'Azimut' in line:
                current_azimut = line[47:].split()[0]
                azimut_values_raw.append(float(current_azimut))
                
    
    plt.plot(frequency_values,elevation_values_raw, label='Ancho en Elevación')
    plt.plot(frequency_values, azimut_values_raw, label='Ancho en Azimuth')
    plt.xlabel('Frecuencia [Hz]')
    plt.ticklabel_format(axis='x', style='sci', scilimits=(6,6))
    plt.ylabel('Ancho del Haz Principal [°]')
    plt.legend()
    plt.grid(True)
    plt.show()

    return

def plot_by_option(option, filename=""):
    if option == 1: return plot_option_one(filename=filename)
    if option == 2: return plot_option_two(filename=filename)