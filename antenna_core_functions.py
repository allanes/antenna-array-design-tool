"""Here are defined some essential classes and methods for Antenna Arrays 
analysis. An 'ArregloGeneral' object represents a 3-dimensional Atenna 
Array and may be used to evaluate Beamforming performance.

"""
import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import math
import scipy.integrate as integrate

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
        promedio = integrate.dblquad(lambda phi,theta: self._densidadPotencia(phi,theta)*np.sin(theta),0,np.pi,-np.pi,np.pi,epsabs=1.49e-03, epsrel=50*1.49e-03)[0]/(4*np.pi)
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

    def get_beam_width(self, plot=False):
        theta = np.linspace(0,np.pi,100)
        phi = np.linspace(-np.pi,np.pi,100)
        THETA, PHI = np.meshgrid(theta,phi) #En THETA y PHI se guardan los valores de forma matricial de las coordenadas theta,phi
        f = lambda x,y: np.abs(self.directividad(x,y))   #R = np.abs(arreglo.campo(PHI,THETA))
        R = f(PHI,THETA) #matriz de 50*50
        
        Rmax = np.max(R)
        i_phi,i_theta = np.where(R == Rmax)
        theta_apuntado = np.degrees(theta[int(i_theta)])
        phi_apuntado = np.degrees(phi[int(i_phi)])  

        if plot: fig = plt.figure()    

        if plot: ax1 = fig.add_subplot(2,1,1)
        y_campo_phi = np.abs(self.directividad(math.radians(phi_apuntado),theta))
        x_theta = np.degrees(theta)
        if plot: 
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
        if len(R_right) == 0:
            theta_hp_max = 90
        else:
            theta_hp_max = np.interp(-Rmax*(2**-0.5),-R_right,theta_right)
        
        if plot: ax1.plot(theta_hp_min,Rmax*(2**-0.5),'or',theta_hp_max,Rmax*(2**-0.5),'or')
        Ancho_theta =  theta_hp_max - theta_hp_min
        

        if plot: ax1 = fig.add_subplot(2,1,2)
        x_phi = np.degrees(phi)
        y_campo_theta = np.abs(self.directividad(phi,math.radians(theta_apuntado)))
        if plot:
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

        intensidad_media_potencia = Rmax * (2**-0.5)
        phi_hp_min = np.interp(intensidad_media_potencia,R_left,phi_left)
        phi_hp_max = np.interp(-intensidad_media_potencia,-R_right,phi_right)
        
        if plot: ax1.plot(
            phi_hp_min,
            intensidad_media_potencia,
            'or',
            phi_hp_max,
            intensidad_media_potencia,
            'or'
            ) 
        Ancho_phi = phi_hp_max - phi_hp_min
        Directividad = Rmax
        return [Ancho_theta,Ancho_phi,Directividad]

    def plot_3D(self):
        """Realiza la representacion del patron de radiacion del arreglo
        y ubica las antenas en un espacio x,y,z
        
        """    
        theta = np.linspace(0,np.pi,100)
        phi = np.linspace(-np.pi,np.pi,100)
        THETA, PHI = np.meshgrid(theta,phi)

        f = lambda x,y: np.abs(self.campo(x,y))   #R = np.abs(self.campo(PHI,THETA))
        #f = lambda x,y: np.abs(self.directividad(x,y))   #R = np.abs(self.campo(PHI,THETA))
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
        # ax.set_title(" "+nombre + " ( Dmax or Emax : %2.2f" % Rmax + ")")
        ax.set_title("3D Array")

        #Rmax = grafica3d(ax,self.directividad,phi,theta,corteLobuloPrincipal=.5)
        
        [dx,dy,dz] = [0,0,0]

        [xi, yi , zi] = 50*np.transpose(self.posiciones-np.array(((dx,dy,dz))))
        ax.scatter(xi,yi,zi, c = 'green',  marker='+' , linewidth = 2)
        # xi = [:,0] ; yi = [:,1], zi = [:,2]   # selecciona columnas, use la transpuesta de puntos

        plt.show()
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
def Unnormalisation_Freq(Freq,D):
    C = 3e8 # Speed Light
    n = np.size(Freq)
    Dn = np.zeros(n)
    Lambda = C/Freq
    d_real = D*Lambda[0]
    D_unnorm = d_real/Lambda

    return [D_unnorm,D_unnorm*Lambda]
#==============================================================================

if __name__ == '__main__':
    print('\n**Este modulo debe ser incluido en la sección "imports" para ser usado**')
    print('Intentar corriendo funciones_disenio.py')
