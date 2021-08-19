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

    beamwidth_theta = np.arcsin(np.sin(theta_0) + (0.4429/(N_theta*D))) - np.arcsin(np.sin(theta_0) - (0.4429/(N_theta*D)))
    phi_aux = np.arcsin(np.sin(phi_0) + (0.4429/(N_phi*D))) - np.arcsin(np.sin(phi_0) - (0.4429/(N_phi*D)))
    #beamwidth_phi = 2* np.arcsin(np.sin(phi_0)*np.sin(phi_aux))


    return [math.degrees(beamwidth_theta), math.degrees(phi_aux)]
#==============================================================================        
class Arreglo_2D(object):
    """
        Genera el patron de radiacion (campo lejado) de un arreglo de antena en 2D, en funcion
        de la distribucion geometrica del arreglo y de las exitaciones de cada uno 
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
    Aplica un peso a los valores de las exitaciones, de cada fuente del arreglo.
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
    ax.scatter(xi,yi,zi, c = 'blue',  marker='o' , linewidth = 2)
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
                exitaciones: Son las exitaciones de cada uno de los elemnentos (en este caso tipo isotropicos)
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
    exitaciones = np.array(Nx*Ny*Nz*[1])
    
    return [posiciones, exitaciones]
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
                exitaciones: Exitaciones de cada uno de los elemnentos (en este caso tipo isotropicos)
    ----------------------------------------------------------------------------------------------
    """
    paso_ang = 360/N
    pos_r = np.linspace(1,Nr,Nr)
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

    exitaciones = np.array(((Nz*Nr*N)+Nz)*[1])
    return [posiciones, exitaciones]
#==============================================================================
def Ancho_Haz(arreglo, phi, theta, corteLobuloPrincipal, phi_apuntado,theta_apuntado):
    
    a1 = arreglo #Arreglo variable definida como un objeto de la clase Arreglo general
    THETA, PHI = np.meshgrid(theta,phi) #En THETA y PHI se guardan los valores de forma matricial de las coordenadas theta,phi
    f = lambda x,y: np.abs(a1.directividad(x,y))   #R = np.abs(a1.campo(PHI,THETA))
    R = f(PHI,THETA) #matriz de 50*50
    
    Rmax = np.max(R)
    Rhp= Rmax*corteLobuloPrincipal #calculo del modulo del vector de media potencia
    
    """
    pos_phi = np.arange(np.size(phi,0))
    pos_theta = np.arange(np.size(theta,0))
    phi_hp= np.array([[0]])
    theta_hp= np.array([[0]])
    R_hp= np.array([[0]])

    for i in pos_phi:
        for j in pos_theta:
            if (R[i][j] >= (Rhp - (Rhp*0.02) ) and R[i][j] <= (Rhp + (Rhp*0.02) ) ):
                aux_phi= np.array([[phi[i]]])
                aux_theta= np.array([[theta[j]]])
                aux_R= np.array([[R[i][j]]])
                phi_hp= np.append(phi_hp,aux_phi,axis=0)
                theta_hp= np.append(theta_hp,aux_theta,axis=0)
                R_hp= np.append(R_hp,aux_R,axis=0)
    
    R_hp = R_hp[1:]
    theta_hp = theta_hp[1:]
    phi_hp = phi_hp[1:]
    

    print("Ancho phi : %2.2f" % (np.max(np.degrees(phi_hp))- np.min(np.degrees(phi_hp))))
    print("Ancho theta : %2.2f" % (np.max(np.degrees(theta_hp))- np.min(np.degrees(theta_hp))))
    

    fig = plt.figure() #fig variable definida como un objeto de la funcion figure de la libreria plt
    ax = fig.add_subplot(projection = '3d')    
   
    
    X = R_hp * np.cos(phi_hp) * np.sin(theta_hp)
    Y = R_hp * np.sin(phi_hp) * np.sin(theta_hp)
    Z = R_hp * np.cos(theta_hp)
    ax.scatter(X,Y,Z, c = 'blue',  marker='o' , linewidth = 2) #Grafica las posiciones de cada antena indicando su ubicacion con un marcador
    ax.set_title("Ancho del Haz (Lobulo Principal)")
    """


    fig = plt.figure()    

    ax1 = fig.add_subplot(2,1,1)
    y_campo_phi = np.abs(a1.directividad(math.radians(phi_apuntado),theta))
    x_theta = np.degrees(theta)
    ax1.plot(x_theta,y_campo_phi)
    ax1.set_title("Patron $\\theta$"), ax1.grid(True)
    aux = [0]
    aux1 = [0]

    for i in np.arange(np.size(y_campo_phi,0)):
        if (y_campo_phi[i] >= (Rhp - (Rhp*0.02)) ):
            aux = np.append(aux,np.array([x_theta[i]]),axis=0)
    aux = aux[1:]
    Ancho_theta =  np.max(aux)- np.min(aux)
    

    ax1 = fig.add_subplot(2,1,2)
    x_phi = np.degrees(phi)
    y_campo_theta = np.abs(a1.directividad(phi,math.radians(theta_apuntado)))
    ax1.plot(x_phi,y_campo_theta)
    ax1.set_title("Patron $\\varphi$ "), ax1.grid(True)

    for i in np.arange(np.size(y_campo_theta,0)):
        if (y_campo_theta[i] >= (Rhp - (Rhp*0.02))):
            aux1 = np.append(aux1,np.array([x_phi[i]]),axis=0)
    aux1 = aux1[1:]
    Ancho_phi = np.max(aux1)- np.min(aux1)

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




def main():

    D = 0.25 # separacion entre elementos
    Nx = 20 # cantidad de elementos en la direccion x
    Ny = 10 # cantidad de elementos en la direccion y
    Nz = 1 # cantidad de elementos en la direccion z
    
    [posiciones,exitaciones] = Geom_Arreglo(D, Nx, Ny, Nz)
    #arreglo = Arreglo_2D(posiciones,exitaciones)
    arreglo = ArregloGeneral(posiciones,exitaciones,[patronMonopoloCuartoOnda()])
    phi_apuntado = 50   
    theta_apuntado = 20
    arreglo.apuntar(math.radians(phi_apuntado),math.radians(theta_apuntado))
    theta = np.linspace(0,np.pi,500)
    phi = np.linspace(-np.pi,np.pi,500)
    Graficar_2D(arreglo, phi, theta,"Arreglo en 2D Rectangular",posiciones,(D*(Nx-1))/2,(D*(Ny-1))/2,(D*(Nz-1))/2)
    [Ancho_Haz_Elevacion, Ancho_Haz_Acimut] = Ancho_Haz(arreglo, phi, theta, 2**-0.5, phi_apuntado,theta_apuntado)
    print("\n")
    #print("Directividad Max: %2.2f " % Directividad)   
    print("Ancho del Haz (Acimut): %2.2f " % Ancho_Haz_Acimut)
    print("Ancho del Haz (Elevacion): %2.2f " % Ancho_Haz_Elevacion)  
        




    """
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

    """
    
    #[a, b] = Beamwidth(math.radians(phi_apuntado),math.radians(theta_apuntado),Nx,Ny,D)
    
    #print(a)
    #print(b)
    #Directividad = arreglo2.directividad(math.radians(phi_apuntado),math.radians(theta_apuntado))

    
    
    """    
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
    """    
    plt.show()
    

    # INICIO    
if __name__ == '__main__':
    main()


