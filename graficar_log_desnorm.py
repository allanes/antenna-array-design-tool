from matplotlib import pyplot as plt


def main():
    valores_eje_frecuencia = []
    valores_elevacion_raw = []
    valores_azimuth_raw = []

    with open('antenas_log.log', 'r') as f:
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
        
    plt.plot(
        valores_eje_frecuencia,valores_elevacion_raw, 
        valores_eje_frecuencia, valores_azimuth_raw
        )
    plt.show()

    return

if __name__ == '__main__':
    main()
    


    