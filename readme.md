Instrucciones para instalar las librerias necesarias para correr este software:

1. Descargar el repositorio
2. Crear un ambiente virtual en la carpeta del repositorio
3. Activar el ambiente y ejecutar:
    pip install -r requirements.txt

Para iniciar la aplicacion, ejecutar:
    `utilities.py`



Overview:

Para correr graficar los datos simulados para este informe, correr:
    -Para graficar el heatmap correspondiente a la etapa 1: graficar_etapa1.py
    -Para graficar el plot X-Y correspondiente a la etapa 2: graficar_etapa2.py


El software presente en este repositorio está separado en 2 partes:
    A. Las que simulan, hacen cálculos y generan datos
        Archivos: Arreglo_Antena_2D.py (backend de simulacion)
                  funciones_disenio.py (programa principal)
    
    B. Las que grafican los datos generados
        Archivos: graficar_etapa1.py
                  graficar_etapa2.py, heatmap.py

El archivo de Jupyter Notebook Patron_arreglo_v3 fue tomado de las clases
y representa el core del funcionamiento.

Para la simulación 1 arreglo de prueba, ejecutar:
    funciones_disenio.py,
y elegir la opción 3

Para la simulación completa, se requieren 2 etapas:

-Etapa 1: Calcula el ancho del haz principal en elevación y azimuth. El ancho se evalúa para un conjunto de arreglos con un apuntamiento dado, variando la cantidad de elementos
en 2 ejes. Para arreglos rectangulares, los ejes corresponden con los ejes cartesianos. 
Para otros arreglos, la forma esta dada por la función que genera la distribucion. Está 
pensada para ser usada con la frecuencia normalizada. La visualización de estos datos es de utilidad para elegir arreglo a desnormalizar en la Etapa 2.

-Etapa 2. Calcula el ancho del haz en función de la frecuencia. Trabaja sobre el arreglo elegido en la Etapa 1 y lo desnormaliza en frecuencia, de forma que esta etapa evalúa la respuesta en frecuencia de un arreglo completamente parametrizado.


