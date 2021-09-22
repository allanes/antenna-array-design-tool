from matplotlib import pyplot as plt


def main(archivo=""):
    valores_eje_frecuencia = []
    valores_elevacion_raw = []
    valores_azimuth_raw = []

    if archivo == "": 
        archivo = 'logs/log_etapa2_informe.log'

    with open(archivo, 'r') as f:
        aux_frec = 0
        aux_elevacion_actual = 0.0
        aux_azimuth_actual = 0.0
        
        for line in f:
            if 'Frecuencia' in line:
                aux_frec = line[38:]
                valores_eje_frecuencia.append(float(aux_frec))
                
            elif 'Elevacion' in line:
                aux_elevacion_actual = line[50:].split()[0]
                valores_elevacion_raw.append(float(aux_elevacion_actual))
                
            elif 'Azimut' in line:
                aux_azimuth_actual = line[47:].split()[0]
                valores_azimuth_raw.append(float(aux_azimuth_actual))
                
    
    plt.plot(valores_eje_frecuencia,valores_elevacion_raw, label='Ancho en Elevación')
    plt.plot(valores_eje_frecuencia, valores_azimuth_raw, label='Ancho en Azimuth')
    plt.xlabel('Frecuencia [Hz]')
    plt.ticklabel_format(axis='x', style='sci', scilimits=(6,6))
    plt.ylabel('Ancho del Haz Principal [°]')
    plt.legend()
    plt.grid(True)
    plt.show()

    return

if __name__ == '__main__':
    main()
    


    