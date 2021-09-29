import numpy as np
import math
from enum import Enum


class Disposiciones(Enum):
    RECTANGULAR = 0
    STAR = 1
    CIRCULAR2 = 2

class GeometryArray():
    def __init__(self, distribution_type=Disposiciones.RECTANGULAR):
        self.distribution_name = distribution_type
        self.posiciones = []
        self.excitaciones = []

    def populate_array(self, separacion, param1, param2):
        if self.distribution_name == Disposiciones.RECTANGULAR.value:
            [self.posiciones, self.excitaciones] = generate_rectangular_geometry(D=separacion, Nx=param1, Ny=param2)
        
        elif self.distribution_name == Disposiciones.STAR.value:
            [self.posiciones, self.excitaciones] = generate_star_geometry(DR=separacion, Nr=param1, N=param2)

        elif self.distribution_name == Disposiciones.CIRCULAR2.value:
            [self.posiciones, self.excitaciones] = generate_circular2_geometry(Dr=separacion, Nr=param1, N=param2)

    def get_positions(self):
        return self.posiciones

    def get_excitations(self):
        return self.excitaciones

    def get_params_names(self):
        param1 = 'Param1'
        param2 = 'Param2'

        if self.distribution_name == Disposiciones.RECTANGULAR.value:
            param1 = 'Number of elements along X axis'
            param2 = 'Number of elements along Y axis'
        
        elif self.distribution_name == Disposiciones.STAR.value:
            param1 = 'Number of elements along Radial Axis (i.e. Rings)'
            param2 = 'Number of elements per Ring'

        elif self.distribution_name == Disposiciones.CIRCULAR2.value:
            param1 = 'Number of elements along Radial Axis (i.e. Rings)'
            param2 = 'Number of elements for the First Ring'
            
        return [param1, param2]


def generate_rectangular_geometry(D = 1, Nx = 1, Ny = 1, Nz = 1):
    """Posiciona en un plano x,y,z a cada una de las antenas del arreglo
            
    Array(n,2) plot Geom_Arreglo_Rectangular( int D, int Nx ,int Ny)
        Entrada:
            separacion: D: Distancia entre elementos en las direcciones x e y [en Nº long. de onda]
            param1: Nx: Num  de antenes en la direccion x
            param2: Ny: Num de antenas en la direccion y
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
        
            
def generate_star_geometry(DR=1, Nr=1, N=1, Dz=1, Nz=1):
    """Posiciona en un plano x,y,z a cada una de las antenas del arreglo

    Array(n,2)  Geom_Arreglo_Circular( int Dr, int Nr ,int N, int Dz, int Nz)
    Entrada:
        separacion: Dr: Distancia entre elementos en las direccion radial [en Nº long. de onda] 
        param1: Nr: Num de antenas en la direccion radial
        param2: N: Num de antenas en cada anillo (radio)
        Dz: Distancia entre elementos en las direccion z [en Nº long. de onda] 
        Nz: Num de antenas en la direccion z
    Salida: 
        posiciones: Posiciones Geo. de cada elemento en un plano x,y,z
        excitaciones: excitaciones de cada uno de los elemnentos (en este caso tipo isotropicos)
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


def generate_circular2_geometry(Dr=1, Nr=1, N=1, Dz=1, Nz=1):
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
    [xi, yi , zi] = 1*np.transpose(posiciones)
    
    exitaciones = np.array(np.size(posiciones,axis=0)*[1])
    return [posiciones, exitaciones]
    