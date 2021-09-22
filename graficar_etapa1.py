import numpy as np
from matplotlib import pyplot as plt
import heatmap


def main(archivo=""):
    valores_eje_parametro1 = []
    valores_eje_parametro2 = []
    valores_elevacion_raw = []
    valores_azimuth_raw = []
    
    if archivo == "": 
        archivo = 'logs/log_etapa1_20210922_132302.log'

    with open(archivo, 'r') as f:
        aux_parametro1_actual = 0
        aux_parametro2_actual = 0
        aux_elevacion_actual = 0.0
        aux_azimuth_actual = 0.0
        paso_por_aca_flag = 0

        for line in f:
            if 'Parametro 1' in line:
                aux_parametro1_actual = line[64:].split()[0]
                valores_eje_parametro1.append(int(aux_parametro1_actual))
                paso_por_aca_flag += 1
            
            elif 'Parametro 2' in line:
                if (paso_por_aca_flag > 1): 
                    continue
                aux_parametro2_actual = line[74:].split()[0]
                if not aux_parametro1_actual in valores_eje_parametro2:
                    valores_eje_parametro2.append(int(aux_parametro2_actual))
            
            elif ' Elevacion' in line:
                aux_elevacion_actual = line[50:].split()[0]
                valores_elevacion_raw.append(float(aux_elevacion_actual))
            
            elif ' Azimut' in line:
                aux_azimuth_actual = line[47:].split()[0]
                valores_azimuth_raw.append(float(aux_azimuth_actual))
        
    # Reacomodo un poco los datos
    indice_truncar_arreglo = len(valores_eje_parametro1)*len(valores_eje_parametro2)
    valores_elevacion_raw = valores_elevacion_raw[:indice_truncar_arreglo]
    valores_azimuth_raw = valores_azimuth_raw[:indice_truncar_arreglo]

    valores_elevacion = np.reshape(
            np.array(valores_elevacion_raw), 
            (len(valores_eje_parametro1), len(valores_eje_parametro2))
        )

    valores_azimuth = np.reshape(
            np.array(valores_azimuth_raw), 
            (len(valores_eje_parametro1), len(valores_eje_parametro2))
        )

    fig, ax = plt.subplots()
    im = ax.imshow(valores_elevacion)
    
    im, cbar = heatmap.heatmap(
        data=valores_elevacion,
        row_labels=valores_eje_parametro1,
        col_labels=valores_eje_parametro2,
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
    im_az = ax_az.imshow(valores_azimuth)
    
    im_az, cbar = heatmap.heatmap(
        data=valores_azimuth,
        row_labels=valores_eje_parametro1,
        col_labels=valores_eje_parametro2,
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

if __name__ == '__main__':
    main()
    