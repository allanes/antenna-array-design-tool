import numpy as np
import math
from enum import Enum


class Distributions(Enum):
    RECTANGULAR = 0
    STAR = 1
    CIRCULAR2 = 2

class GeometryArray():
    def __init__(self, distribution_type=Distributions.RECTANGULAR):
        self.distribution_name = distribution_type
        self.positions = []
        self.excitations = []

    def populate_array(self, separation, param1, param2):
        if self.distribution_name == Distributions.RECTANGULAR.value:
            [self.positions, self.excitations] = generate_geometry_rectangular(D=separation, Nx=param1, Ny=param2)
        
        elif self.distribution_name == Distributions.STAR.value:
            [self.positions, self.excitations] = generate_geometry_star(radial_distance=separation, elements_radial_dir=param1, elements_per_ring=param2)

        elif self.distribution_name == Distributions.CIRCULAR2.value:
            [self.positions, self.excitations] = generate_geometry_circular2(first_ring_radius=separation, rings=param1, first_ring_elements=param2)

        return self.excitations


def get_params_names(distribution_type):
    param1 = 'Param1'
    param2 = 'Param2'

    if distribution_type == Distributions.RECTANGULAR.value:
        param1 = 'Elements in X axis'
        param2 = 'Elements in Y axis'
    
    elif distribution_type == Distributions.STAR.value:
        param1 = 'Rings'
        param2 = 'Elements per Ring'

    elif distribution_type == Distributions.CIRCULAR2.value:
        param1 = 'Rings'
        param2 = 'Elements in First Ring'
        
    return [param1, param2]


def generate_geometry_rectangular(D = 1, Nx = 1, Ny = 1, Nz = 1):
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
    _B = np.array([[0,0,0]])
    for i in pos_x:
        for j in pos_y:
            for k in pos_z:
                aux = np.array([[i*D, j*D, k*D]]) 
                _B = np.append(_B,aux,axis=0)
    
    positions = _B[1:]
    excitations = np.array(Nx*Ny*Nz*[1])    
    return [positions, excitations]
        
            
def generate_geometry_star(radial_distance=1, elements_radial_dir=1, elements_per_ring=1, vertical_distance=1, elements_vertical_dir=1):
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
    angular_step = 360/elements_per_ring
    pos_r = np.linspace(1,elements_radial_dir,num=elements_radial_dir)
    pos_z = np.arange(elements_vertical_dir)
    angle = np.arange(elements_per_ring)
    B = np.array([[0,0,0]])

    for i in angle:
        for j in pos_r:
            for k in pos_z:   
                x = (radial_distance*j) * np.cos(math.radians(angular_step*i))
                y = (radial_distance*j) * np.sin(math.radians(angular_step*i))
                aux = np.array([[x, y, k*vertical_distance]]) 
                B = np.append(B,aux,axis=0)
    positions = B[1:]
    
    for k in pos_z:
        aux2 = np.array([[0, 0, k*vertical_distance]]) 
        positions = np.append(positions,aux2,axis=0)

    excitations = np.array(((elements_vertical_dir*elements_radial_dir*elements_per_ring)+elements_vertical_dir)*[1])
    return [positions, excitations]


def generate_geometry_circular2(first_ring_radius=1, rings=1, first_ring_elements=1, Dz=1, Nz=1):
    """Posiciona en un plano x,y,z a cada una de las antenas del arreglo
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
    """
    pos_r = np.arange(rings)
    pos_z = np.arange(Nz)
    B = np.array([[0,0,0]])

    for k in pos_z:
        for i in pos_r:
            current_ring_elements = i*first_ring_elements
            theta = np.linspace(0,2*np.pi,current_ring_elements+1)
            #print(np.degrees(theta))
            for j in np.arange(np.size(theta)-1):
                x = i*first_ring_radius*np.cos(theta[j])
                y = round(i*first_ring_radius*np.sin(theta[j]),5)
                aux = np.array([[x, y, k*Dz]]) 
                B = np.append(B,aux,axis=0)
        aux2 = np.array([[0, 0, k*Dz]]) 
        B = np.append(B,aux2,axis=0)

    positions = B[1:]
    [xi, yi , zi] = 1*np.transpose(positions)
    
    excitations = np.array(np.size(positions,axis=0)*[1])
    return [positions, excitations]
    