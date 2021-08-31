


def main():
    valores_eje_cantidad_anillos = []
    valores_eje_cantidad_elementos = []
    valores_elevacion = []
    valores_azimuth = []

    with open('antenas_log_bak.log', 'r') as f:
        anillo_actual = 0
        for line in f:
            # print(line[15:])
            if line[26:].startswith('-TT'):
                valores_eje_cantidad_anillos.append(line[58:].split()[0])
                continue
            if line[26:].startswith('Cantidad'): #'Cantidad de Elementos'
                valores_eje_cantidad_elementos.append(line[49:].split()[0])
                continue
            if line[26:].startswith(' -Ancho de E'):
                valores_elevacion.append(line[50:].split()[0])
                continue
            if line[26:].startswith(' -Ancho de A'):
                valores_azimuth.append(line[47:].split()[0])
                continue

    return [
        valores_eje_cantidad_anillos,
        valores_eje_cantidad_elementos,
        valores_azimuth,
        valores_elevacion
    ]

if __name__ == '__main__':
    [x,y,z1,z2] = main()
    print(f'largo de x: {len(x)}')
    print(f'largo de y: {len(y)}')
    print(f'largo de z1: {len(z1)}')
    print(f'largo de z2: {len(z2)}')
    print(x)
    print(y)