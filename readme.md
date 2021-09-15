Instrucciones para instalar las librerias necesarias para correr este software:

1. Descargar el repositorio
2. Crear un ambiente virtual en la carpeta del repositorio
3. Activar el ambiente y ejecutar:
    pip install -r requirements.txt

Para correr graficar los datos simulados para este informe, correr:
    -Para graficar el heatmap correspondiente a la etapa 1: graficar_etapa1.py
    -Para graficar el plot X-Y correspondiente a la etapa 2: graficar_etapa2.py


El software presente en este repositorio está separado en 2 partes:
    A. Las que simulan, hacen cálculos y generan datos
        Archivos: Arreglo_Antena_2D.py
    B. Las que grafican los datos generados
        Archivos: graficar_etapa1.py, graficar_etapa2.py, heatmap.py

El archivo de Jupyter Notebook Patron_arreglo_v3 fue tomado de las clases
y representa el core del funcionamiento.

Para correr una simulación de prueba, ejecutar:
    Arreglo_Antena_2D.py
y seguir las instrucciones


