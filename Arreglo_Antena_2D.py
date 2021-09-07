#==============================================================================
#Titulo:  Arreglo_Antena_2D
#Autor: Zenon Saavedra 
#==============================================================================

"""
    Realiza el BeamForming de un arreglo de antenas. 
        Geometria del arreglo: en 3 Dimensiones
        Fuentes/antenas: Radiadores Isotropicos
        Las distancias se encuentran en funcion de longitude de onda (lambda) de la señal
        -m pip install --upgrade pip' command.
Created on Fri Jun 11 14:51:10 2021
@author: Zenon
"""
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import math
import scipy.spatial.distance as distance
import scipy.integrate as integrate
from scipy.interpolate import interp1d
import logging
from enum import Enum

class Disposiciones(Enum):
    RECTANGULAR = 0
    CIRCULAR = 1

class ArregloGeneral(object):
    
    def __init__(self,posiciones,excitaciones,patron=None):
        """Arreglo tridimensional
        
           posiciones:  matriz real n*3 cuyos vectores fila son las posiciones x,y,z de las fuentes del arreglo
           excitaciones: vector complejo de n elementos representando la amplitud y fase de excitación de cada fuente del arreglo
           patron: patron en 3D de un elemento 
           """
        self.posiciones = posiciones
        self.excitaciones = excitaciones
        if patron is not None: 
            self.patron = patron
        else:
            self.patron = [lambda phi,theta:1]
    
    def apuntar(self,phi,theta):
        """Modifica las fases de las excitaciones manteniendo sus amplitudes para apuntar el haz principal en la dirección dada
        
        @param phi ángulo diedro del plano xz al plano xr donde r es la dirección de apuntamiento
        @param theta ángulo del eje z al vector de apuntamiento r
        """
        normal = np.array((np.cos(phi)*np.sin(theta),np.sin(phi)*np.sin(theta),np.cos(theta)))
        fases = -2*np.pi*self.posiciones@normal
        self.excitaciones = np.abs(self.excitaciones)*np.exp(1j*fases)

    def _campo_dirUnica(self,phi_i,theta_i):
        normal = np.array((np.cos(phi_i)*np.sin(theta_i),np.sin(phi_i)*np.sin(theta_i),np.cos(theta_i)))
        fases = 2*np.pi*self.posiciones@normal  

        patronAntena = self.patron[0](phi_i,theta_i)
        return patronAntena*sum(self.excitaciones*np.exp(1j*fases))


        #return Patron_antena*sum(self.excitaciones*np.exp(1j*fases))

    def _densidadPotencia(self,phi_i,theta_i):
        return (np.abs(self._campo_dirUnica(phi_i,theta_i))**2)/(2*120*np.pi)

    def _potencia_media(self):
        promedio = integrate.dblquad(lambda phi,theta: self._densidadPotencia(phi,theta)*np.sin(theta),0,np.pi,-np.pi,np.pi)[0]/(4*np.pi)
        return promedio
    
    def directividad(self,phi,theta):
        promedio = self._potencia_media()        
        def directividad_dirUnica(phi_i,theta_i):
            return self._densidadPotencia(phi_i,theta_i)/promedio
        
        directividad_vec = np.vectorize(directividad_dirUnica)
        return directividad_vec(phi,theta)
  
    def campo(self,phi,theta):
        campo_vec = np.vectorize(self._campo_dirUnica)
        return campo_vec(phi,theta)
#==============================================================================
def Beamwidth(phi_0, theta_0,N_phi,N_theta ,D):

    beamwidth_theta = np.arcsin(np.sin(theta_0) + (0.4429/(N_theta*D))) - np.arcsin(np.sin(theta_0) - (0.4429/(N_phi*D)))
    phi_aux = np.arcsin(np.sin(phi_0) + (0.4429/(N_phi*D))) - np.arcsin(np.sin(phi_0) - (0.4429/(N_phi*D)))
    #beamwidth_phi = 2* np.arcsin(np.sin(phi_0)*np.sin(phi_aux))


    return [math.degrees(beamwidth_theta), math.degrees(phi_aux)]
#==============================================================================        
class Arreglo_2D(object):
    """
        Genera el patron de radiacion (campo lejado) de un arreglo de antena en 2D, en funcion
        de la distribucion geometrica del arreglo y de las excitaciones de cada uno 
        de los elementos del arreglo
    
    """
    
    def __init__(self,posiciones,excitaciones):
        """
        Inicializador del la clase Arreglo _2D
        
            posiciones: Posiciones de los elementos
            excitacionesws: Excitaciones de cada uno de los elementos
        """
        self.posiciones = posiciones  
        self.excitaciones = excitaciones
    
    def apuntar(self,phi,theta):
        """
            Modifica las fases de las excitaciones manteniendo sus amplitudes para apuntar el haz principal en la dirección dada
        
            phi: ángulo diedro del plano xz al plano xr donde r es la dirección de apuntamiento
            theta: ángulo del eje z al vector de apuntamiento r
        """
        normal = np.array((np.cos(phi)*np.sin(theta),np.sin(phi)*np.sin(theta),np.cos(theta)))
        fases = -2*np.pi*self.posiciones@normal
        self.excitaciones = np.abs(self.excitaciones)*np.exp(1j*fases)
    
        
    def _campo_dirUnica(self,phi_i,theta_i):
        """
            Determina el campo (E) para una dada direccion phi y theta
        """
        V_Normal = np.array((np.cos(phi_i)*np.sin(theta_i),np.sin(phi_i)*np.sin(theta_i),np.cos(theta_i)))
            
        fases = 2*np.pi * self.posiciones@V_Normal # fases de cada elemento con respecto al plano que tiene un vector normal (V_Normal)
        return sum(self.excitaciones * np.exp(1j*fases)) # Campo = excitaciones * Factor de Arreglo
        
        
    def campo(self,phi, theta):    
        """
            Determina el patron de campo (E) del arreglo en todas las coordenadas esfericas (phi,theta)
        """
        campo_vec = np.vectorize(self._campo_dirUnica)
        return campo_vec(phi,theta)
#==============================================================================        
def amplitudCosElev(posiciones,escala=0.8):
    """
    Aplica un peso a los valores de las excitaciones, de cada fuente del arreglo.
    Los pesos seguiran la forma de un coseno alzado. Se alcanza el maximo valor de 
    los pesos en el medio del arreglo
    """

    centro = np.mean(posiciones,axis=0)
    desplazamientos = posiciones-centro
    radios = np.linalg.norm(desplazamientos,axis=1)
    rmax=np.max(radios)
    A = 1+np.cos(np.pi*escala*radios/rmax)
    return A/np.linalg.norm(A)*A.size**.5   
#==============================================================================        
def Graficar_2D(arreglo,phi,theta,nombre,posiciones,dx,dy,dz):
    """
    Realiza la representacion del patron de radiacion del arreglo
            y ubica las antenas en un espacio x,y,z
    """    
    a1 = arreglo
    #PHI,THETA = np.meshgrid(phi,theta)
    THETA, PHI = np.meshgrid(theta,phi)

    f = lambda x,y: np.abs(a1.campo(x,y))   #R = np.abs(a1.campo(PHI,THETA))
    #f = lambda x,y: np.abs(a1.directividad(x,y))   #R = np.abs(a1.campo(PHI,THETA))
    R = f(PHI,THETA)    

    X = R * np.cos(PHI) * np.sin(THETA)
    Y = R * np.sin(PHI) * np.sin(THETA)
    Z = R * np.cos(THETA)
    Rmax = np.max(R)

    fig = plt.figure()
    ax = fig.add_subplot(projection = '3d')
    ax.set_xlim(-Rmax,Rmax)
    ax.set_ylim(-Rmax,Rmax)
    ax.set_zlim(-Rmax,Rmax)

    ax.plot_surface(X,Y,Z,rcount=100,ccount=100,facecolors=cm.jet(R/Rmax),shade=False)
    #ax.plot_surface(X,Y,Z,rcount = 100,ccount = 100,color="lightblue",shade=True,lightsource=matplotlib.colors.LightSource(30,70))
    #ax.contour3D(X, Y, Z, 50) #ax.plot_surface(X, Y, Z, rstride=1, cstride=1,cmap='viridis', edgecolor='none')
    ax.set_title(" "+nombre + " ( Dmax or Emax : %2.2f" % Rmax + ")")

    #Rmax = grafica3d(ax,arreglo.directividad,phi,theta,corteLobuloPrincipal=.5)
    


    [xi, yi , zi] = 50*np.transpose(posiciones-np.array(((dx,dy,dz))))
    ax.scatter(xi,yi,zi, c = 'green',  marker='+' , linewidth = 2)
    # xi = [:,0] ; yi = [:,1], zi = [:,2]   # selecciona columnas, use la transpuesta de puntos
#==============================================================================
def Geom_Arreglo(D = 1, Nx = 1, Ny = 1, Nz = 1):
    """Posiciona en un plano x,y,z a cada una de las antenas del arreglo
            
        Array(n,2) plot Geom_Arreglo( int D, int Nx ,int Ny)
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
def Geom_Arreglo_circular(DR = 1,Nr = 1, N = 1,Dz =1, Nz = 1):
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
#==============================================================================
def Ancho_Haz(arreglo, phi, theta, corteLobuloPrincipal):
    print('Entro a ANCHO_HAZ')
    a1 = arreglo #Arreglo variable definida como un objeto de la clase Arreglo general
    THETA, PHI = np.meshgrid(theta,phi) #En THETA y PHI se guardan los valores de forma matricial de las coordenadas theta,phi
    f = lambda x,y: np.abs(a1.directividad(x,y))   #R = np.abs(a1.campo(PHI,THETA))
    R = f(PHI,THETA) #matriz de 50*50
    
    Rmax = np.max(R)
    i_phi,i_theta = np.where(R == Rmax)
    theta_apuntado = np.degrees(theta[int(i_theta)])
    phi_apuntado = np.degrees(phi[int(i_phi)])  
  
    fig = plt.figure()    

    ax1 = fig.add_subplot(2,1,1)
    y_campo_phi = np.abs(a1.directividad(math.radians(phi_apuntado),theta))
    x_theta = np.degrees(theta)
    ax1.plot(x_theta,y_campo_phi)
    ax1.set_title("Patron $\\theta$"), ax1.grid(True)
    
    
    x = [0]
    y = [0]
    Rmax= np.max(y_campo_phi)
    Rrange = Rmax*0.3
    for i in np.arange(np.size(y_campo_phi,0)):
        if (y_campo_phi[i] >= Rrange):
            x = np.append(x,np.array([y_campo_phi[i]]),axis=0)
            y = np.append(y,np.array([x_theta[i]]),axis=0)
    y = y[1:]
    x = x[1:]

    index_Rmax = np.where( x == Rmax )
    index = int(index_Rmax[0])

    R_left = x[0:index] 
    theta_left = y[0:index]
    R_right = x[index:-1] 
    theta_right = y[index:-1]

    theta_hp_min = np.interp(Rmax*(2**-0.5),R_left,theta_left)
    theta_hp_max = np.interp(-Rmax*(2**-0.5),-R_right,theta_right)
    #print(theta_hp_max,theta_hp_min)
    ax1.plot(theta_hp_min,Rmax*(2**-0.5),'or',theta_hp_max,Rmax*(2**-0.5),'or')
    Ancho_theta =  theta_hp_max - theta_hp_min
    

    ax1 = fig.add_subplot(2,1,2)
    x_phi = np.degrees(phi)
    y_campo_theta = np.abs(a1.directividad(phi,math.radians(theta_apuntado)))
    ax1.plot(x_phi,y_campo_theta)
    ax1.set_title("Patron $\\varphi$ "), ax1.grid(True)

    xx = [0]
    yy = [0]
    Rmax= np.max(y_campo_theta)
    Rrange = Rmax*0.3
    for i in np.arange(np.size(y_campo_theta,0)):
        if (y_campo_theta[i] >= Rrange):
            xx = np.append(xx,np.array([y_campo_theta[i]]),axis=0)
            yy = np.append(yy,np.array([x_phi[i]]),axis=0)
    yy = yy[1:]
    xx = xx[1:]

    index_Rmax = np.where( xx == Rmax )
    index = int(index_Rmax[0])
    R_left = xx[0:index] 
    phi_left = yy[0:index]
    R_right = xx[index:-1]
    phi_right = yy[index:-1]

    phi_hp_min = np.interp(Rmax*corteLobuloPrincipal,R_left,phi_left)
    phi_hp_max = np.interp(-Rmax*corteLobuloPrincipal,-R_right,phi_right)
    #print(phi_hp_max,phi_hp_min)
    ax1.plot(phi_hp_min,Rmax*corteLobuloPrincipal,'or',phi_hp_max,Rmax*(2**-0.5),'or')
    Ancho_phi = phi_hp_max - phi_hp_min
    
    return [Ancho_theta,Ancho_phi]
#==============================================================================
def patronMonopoloCuartoOnda():
    self = patronMonopoloCuartoOnda
    if ("patron" not in dir(self)):
        epsilon = 1e-6
        def f_denorm(theta):
            theta=np.array(theta)
            determinado = (theta > epsilon) & (theta <= np.pi/2)
            result = np.zeros(theta.shape)
            theta_determinado = theta[determinado]
            result[determinado] = np.cos(np.pi/2*np.cos(theta_determinado))/np.sin(theta_determinado) 
            return result
        #simetria axial, eje z
        potenciaMedia = integrate.quad(lambda th: f_denorm(th)**2*np.sin(th),0,np.pi)[0]/2
        escala = 1/potenciaMedia**.5 # para normalizar a potencia media 1
        def patron(phi,theta):
            return escala*f_denorm(theta)
        self.patron = patron
    return self.patron
#==============================================================================

def main(param1,param2,param3,param4,param5):
    logging.info('Empezando Log')

    disposicion_arreglo = Disposiciones.RECTANGULAR
    logging.info('Comenzando Geom_Arreglo')
    if disposicion_arreglo == Disposiciones.RECTANGULAR:
        D = 0.25 # separacion entre elementos
        Nx = 15 # cantidad de elementos en la direccion x
        Ny = 15 # cantidad de elementos en la direccion y
        Nz = 1 # cantidad de elementos en la direccion z
        
        [posiciones,excitaciones] = Geom_Arreglo(param1,param2,param3,param4)
    elif disposicion_arreglo == Disposiciones.CIRCULAR: #el arreglo es circular
        
        [posiciones,excitaciones] = Geom_Arreglo_circular(param1,param2,param3,param4,param5)
        #exi = amplitudCosElev(pos,0.7)
        #arreglo = Arreglo_2D(pos,exi)
    
    arreglo = ArregloGeneral(posiciones,excitaciones,[patronMonopoloCuartoOnda()])
    phi_apuntado = 50
    theta_apuntado = 30
    # logging.info('Apuntamiento deseado:')
    # logging.info(f' -Azimuth = {phi_apuntado}')
    # logging.info(f' -Elevac. = {theta_apuntado}')

    arreglo.apuntar(math.radians(phi_apuntado),math.radians(theta_apuntado))
    theta = np.linspace(0,np.pi,100)
    phi = np.linspace(-np.pi,np.pi,100)
    Graficar_2D(arreglo, phi, theta,"Arreglo en 2D",posiciones,0,0,0)
    
    #Directividad = arreglo2.directividad(math.radians(phi_apuntado),math.radians(theta_apuntado))
    #print("Directividad Max: %2.2f " % Directividad)   
    
    [Ancho_Haz_Elevacion, Ancho_Haz_Acimut] = Ancho_Haz(arreglo, phi, theta, 2**-0.5)
    logging.info('Resultados:')
    logging.info(f' -Ancho de Elevacion  = {Ancho_Haz_Elevacion}')
    logging.info(f' -Ancho de Azimuth = {Ancho_Haz_Acimut}')    
    
    #[a, b] = Beamwidth(math.radians(phi_apuntado),math.radians(theta_apuntado),Nx,Ny,D)
    #print(a)
    #print(b) 
    logging.info('mostrando...')
    plt.show()    

    # INICIO    
if __name__ == '__main__':
    logging.basicConfig(
        filename='antenas_log.log',
        level=logging.INFO,
        # handlers=logging.StreamHandler(),
        format='%(asctime)s - %(message)s',
    )

    DR = 0.25 #separacion radial entre elementos
    Nr = 10 # Num. de anillos   (Para un unico elemento Nr = 0)
    N = 10 # Num. de elementos por anillo
    Dz = 0.25 # separacion sobre el eje z
    Nz = 1 # Num de elementos sobre el eje z
    #Logueo los datos:
    logging.info(f'Datos CONSTANTES del arreglo CIRCULAR:')
    logging.info(f'  -DR = {DR}')
    logging.info(f'  -Dz = {Dz}')
    logging.info(f'  -Nz = {Nz}')

    main(DR,10,10,1,Nz)
    """"
    for aux in range(10,11):#20):
        logging.info(f'----------Cantidad de Anillos {aux}-------------')
        for aux2 in range(30,31):
            logging.info(f'Cantidad de Elementos: {aux2}')
            main(DR,aux,aux2,Dz,Nz)
        logging.info("-------------------------------------------")
    """    


"""
    # ------------
    DR = 0.25 #Distancias entre radios
    Nr = 15 # Num. de anillos   (Para un unico elemento Nr = 0)
    N = 15 # Num. de elementos por anillo
    Dz = 0.25 # separacion sobre el eje z
    Nz = 1 # Num de elementos sobre el eje z    

    [pos,exi] = Geom_Arreglo_circular(DR,Nr,N,Dz,Nz)
    #exi = amplitudCosElev(pos,0.7)
    #arreglo = Arreglo_2D(pos,exi)
    arreglo2 = ArregloGeneral(pos,exi,[patronMonopoloCuartoOnda()])
    phi_apuntado = 60
    theta_apuntado = 20
    #arreglo.apuntar(math.radians(phi_apuntado),math.radians(theta_apuntado))
    arreglo2.apuntar(math.radians(phi_apuntado),math.radians(theta_apuntado))
    theta = np.linspace(0,np.pi)
    phi = np.linspace(-np.pi,np.pi)
    Graficar_2D(arreglo2, phi, theta,"Arreglo en 2D Circular",pos,0,0,0)
    # ------------

    # ------------
    D=0.25
    Nx=8
    Ny=8
    N=Nx*Ny

    #arreglo sobre superficie esférica
    posiciones=D*np.array([(x,y,np.sqrt(2*1.5**2-(x-1.5)**2-(y-1.5)**2)) for x in range(Nx) for y in range(Ny)])


    fig = plt.figure()
    ax = fig.add_subplot(projection = '3d')
    [xi, yi, zi] = np.transpose(posiciones)
    ax.scatter(xi,yi,zi, c = 'red',  marker='o' , linewidth = 5)
    ax.set_xlim(-4,4)
    ax.set_ylim(-4,4)
    ax.set_zlim(-4,4)
    # ------------
"""