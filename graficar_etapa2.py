from matplotlib import pyplot as plt


def main():
    valores_eje_frecuencia = []
    valores_elevacion_raw = []
    valores_azimuth_raw = []

    with open('logs\log_etapa2_20210914_195724_informe_invalido.log', 'r') as f:
        aux_frec = 0
        aux_elevacion_actual = 0.0
        aux_azimuth_actual = 0.0
        
        for line in f:
            if line[26:].startswith('Frec'):
                aux_frec = line[38:]
                valores_eje_frecuencia.append(float(aux_frec))
                continue
            if line[26:].startswith(' -Ancho de E'):
                aux_elevacion_actual = line[50:].split()[0]
                valores_elevacion_raw.append(float(aux_elevacion_actual))
                continue
            if line[26:].startswith(' -Ancho de A'):
                aux_azimuth_actual = line[47:].split()[0]
                valores_azimuth_raw.append(float(aux_azimuth_actual))
                continue
    
    plt.plot(valores_eje_frecuencia,valores_elevacion_raw, label='Ancho en Elevación')
    plt.plot(valores_eje_frecuencia, valores_azimuth_raw, label='Ancho en Azimuth')
    plt.xlabel('Frecuencia [MHz]')
    plt.ticklabel_format(axis='x', style='sci', scilimits=(6,6))
    plt.ylabel('Ancho del Haz Principal [°]')
    plt.legend()
    plt.show()

    return

if __name__ == '__main__':
    main()
    


    