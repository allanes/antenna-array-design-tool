import numpy as np
import math
from enum import Enum


class Disposiciones(Enum):
    RECTANGULAR = 0
    CIRCULAR = 1
    CIRCULAR2 = 2


def Geom_Arreglo_Rectangular(D = 1, Nx = 1, Ny = 1, Nz = 1):
    """Posiciona en un plano x,y,z a cada una de las antenas del arreglo
            
        Array(n,2) plot Geom_Arreglo_Rectangular( int D, int Nx ,int Ny)
            Entrada:
                D: Distancia entre elementos en las direcciones x e y [en Nº long. de onda]
                Nx: Num  de antenes en la direccion x
                Ny: Num de antenas en la direccion y
            Salida: 
                posiciones: Posiciones Geo. de cada elemento en un plano x,y,z
                excitaciones: Son las excitaciones de cada uno de los elemnentos (en este caso tipo isotropicos)
    """
    
    pos_x = np.arange(Nx)
    pos_y = np.arange(Ny)
    pos_z = np.arange(Nz)
    B = np.array([[0,0,0]])
    for i in pos_x:
        for j in pos_y:
            for k in pos_z:
                Aux = np.array([[i*D, j*D, k*D]]) 
                B = np.append(B,Aux,axis=0)
    
    posiciones = B[1:]   
    excitaciones = np.array(Nx*Ny*Nz*[1])
    
    return [posiciones, excitaciones]
#==============================================================================        
def Geom_Arreglo_Circular(DR = 1,Nr = 1, N = 1,Dz =1, Nz = 1):
    """
        Posiciona en un plano x,y,z a cada una de las antenas del arreglo
    ----------------------------------------------------------------------------------------------        
        Array(n,2)  Geom_Arreglo_Circular( int Dr, int Nr ,int N, int Dz, int Nz)
            Entrada:
                Dr: Distancia entre elementos en las direccion radial [en Nº long. de onda] 
                Nr: Num de antenas en la direccion radial
                N: Num de antenas en cada anillo (radio)
                Dz: Distancia entre elementos en las direccion z [en Nº long. de onda] 
                Nz: Num de antenas en la direccion z
            Salida: 
                posiciones: Posiciones Geo. de cada elemento en un plano x,y,z
                excitaciones: excitaciones de cada uno de los elemnentos (en este caso tipo isotropicos)
    ----------------------------------------------------------------------------------------------
    """
    paso_ang = 360/N
    pos_r = np.linspace(1,Nr,num=Nr)
    pos_z = np.arange(Nz)
    angulo = np.arange(N)
    B = np.array([[0,0,0]])

    for i in angulo:
        for j in pos_r:
            for k in pos_z:   
                x = (DR*j) * np.cos(math.radians(paso_ang*i))
                y = (DR*j) * np.sin(math.radians(paso_ang*i))
                Aux = np.array([[x, y, k*Dz]]) 
                B = np.append(B,Aux,axis=0)
    posiciones = B[1:]
    
    for k in pos_z:
        Aux2 = np.array([[0, 0, k*Dz]]) 
        posiciones = np.append(posiciones,Aux2,axis=0)

    excitaciones = np.array(((Nz*Nr*N)+Nz)*[1])
    return [posiciones, excitaciones]


def Geom_Arreglo_Circular_2(Dr=1,Nr=1,N=1, Dz=1, Nz=1):
    """
        Posiciona en un plano x,y,z a cada una de las antenas del arreglo
    ----------------------------------------------------------------------------------------------        
        Array(n,2)  Geom_Arreglo_Circular( int Nr, int n ,int Dr, int Dz, int Nz)
            Entrada:
                Nr: Num de anillos 
                n: numero de elementos en el primer anillo 
                Dr: radio del primer anillo 
                Dz: Distancia entre elementos en las direccion z [en Nº long. de onda] 
                Nz: Num de antenas en la direccion z
            Salida: 
                posiciones: Posiciones Geo. de cada elemento en un plano x,y,z
                exitaciones: Exitaciones de cada uno de los elemnentos (en este caso tipo isotropicos)
    ----------------------------------------------------------------------------------------------
    """
    pos_r = np.arange(Nr)
    pos_z = np.arange(Nz)
    B = np.array([[0,0,0]])

    for k in pos_z:
        for i in pos_r:
            elementos_en_anillo_actual = i*N
            theta = np.linspace(0,2*np.pi,elementos_en_anillo_actual+1)
            #print(np.degrees(theta))
            for j in np.arange(np.size(theta)-1):
                x = i*Dr*np.cos(theta[j])
                y = round(i*Dr*np.sin(theta[j]),5)
                Aux = np.array([[x, y, k*Dz]]) 
                B = np.append(B,Aux,axis=0)
        Aux2 = np.array([[0, 0, k*Dz]]) 
        B = np.append(B,Aux2,axis=0)
 

    posiciones = B[1:]
    #print(np.size(posiciones,axis=0))
    #print(posiciones)
    
    #fig = plt.figure()
    #ax = fig.add_subplot(projection = '3d')
    
    [xi, yi , zi] = 1*np.transpose(posiciones)
    #ax.scatter(xi,yi,zi, c = 'blue',  marker='o' , linewidth = 2)
    exitaciones = np.array(np.size(posiciones,axis=0)*[1])
    return [posiciones, exitaciones]


def generate_distribution(disposicion, separacion, param1, param2):
    if disposicion == Disposiciones.RECTANGULAR.value:
        [posiciones,excitaciones] = Geom_Arreglo_Rectangular(separacion, Nx=param1, Ny=param2)
    elif disposicion == Disposiciones.CIRCULAR.value:
        [posiciones,excitaciones] = Geom_Arreglo_Circular(separacion,Nr=param1,N=param2)
    elif disposicion == Disposiciones.CIRCULAR2.value:
        [posiciones,excitaciones] = Geom_Arreglo_Circular_2(separacion,Nr=param1,N=param2)
    else:
        [posiciones,excitaciones] = [0, 0]

    return [posiciones, excitaciones]