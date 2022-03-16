## Introducción

Este software es una herramienta para asistir en el diseño de Arreglos de Antenas. 
Está orientado a exponer lo aprendido y a respaldar el informe final entregado en el curso de posgrado: "*Diseño Avanzado de Arreglos de Antenas*", impartido por el Dr. Ing. Fernando Alberto Miranda Bonomi, en la Universidad Nacional de Tucumán, según *res. HCD 0165/2021*. 

El informe presentado se encuentra en la carpeta `/Informe`

Además, partes de esta herramienta serán reutilizadas para la construcción de un simulador de Radares OTH, enmarcado en el proyecto PIDDEF 03/2020.

## Instalación

Para instalar las librerias necesarias para correr este software:

1. Descargar el repositorio
2. Crear un ambiente virtual con Python 3.6 o superior en la carpeta del repositorio
3. Activar el ambiente y ejecutar:
    pip install -r requirements.txt

Para iniciar la aplicacion, ejecutar:

`python utilities.py`

## Instrucciones de uso
El software presente en este repositorio está separado en 3 partes:

***Plot3d***: Pestaña que permite configurar un arreglo de prueba y muestra su:
-   Distribución espacial,
-   Patrón de radiación,
-   Ancho de haz de azimuth y
-   Ancho de haz de elevación

***Etapa 1***: Evalúa el ancho de haz de azimuth y elevación para un conjunto arbitrario de arreglos de antenas. Los datos se loguean en la carpeta `/logs/`.Esto permite analizar el comportamiento de un arreglo en función de los parámetros que se pueden variar:
-   Distribución,
-   Serparación,
-   Apuntamiento (elevación, azimuth),
-   Número de elementos en un eje
-   Número de elementos en el otro eje

***Etapa 2***: Permite ingresar los datos del arreglo seleccionado en la etapa anterior, luego de analizar los resultados. Acá se debe elegir la frecuencia de diseño, con la cual desnormalizarlo. La salida es su respuesta en frecuencia y también queda logueada en la carpeta `/logs`.

## Overview
El archivo de Jupyter Notebook Patron_arreglo_v3 fue tomado de las clases y representa el core del funcionamiento.

Para la simulación completa, se requieren 2 etapas:

-   Etapa 1: Calcula el ancho del haz principal en elevación y azimuth. El ancho se evalúa para un conjunto de arreglos con un apuntamiento dado, variando la cantidad de elementos
en 2 ejes. Para arreglos rectangulares, los ejes corresponden con los ejes cartesianos.
Para otros arreglos, la forma esta dada por la función que genera la distribucion. Está pensada para ser usada con la frecuencia normalizada. La visualización de estos datos es de utilidad para elegir arreglo a desnormalizar en la Etapa 2.

-   Etapa 2. Calcula el ancho del haz en función de la frecuencia. Trabaja sobre el arreglo elegido en la Etapa 1 y lo desnormaliza en frecuencia, de forma que esta etapa evalúa la respuesta en frecuencia de un arreglo completamente parametrizado.


