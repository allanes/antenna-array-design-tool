"""Here are defined some essential classes and methods for Antenna Arrays 
analysis. An 'ArregloGeneral' object represents a 3-dimensional Atenna 
Array and may be used to evaluate Beamforming performance.

"""
import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import math
from numpy.lib.function_base import average
import scipy.integrate as integrate

class AntennaArray(object):
    """Core object for evaluating antenna arrays.

    This is used to represent an arbitrary array of atennas and perform analysis
    of antennas systems for applications in HF radar systems.
    

    """
    def __init__(self,positions,excitations,pattern=None):
        """Initializer.

        Parameters
        ----------
        positions : array_like
            Array of [x,y,z] tupples mapping all elements of any antenna array
        excitations : array_like
            Array of excitation complex values for all elements of the given
            antenna array
        pattern : array_like, optional
            Radiation pattern of an isolated radiator from the antenna array.
            Defaults to an isotropic radiator.      
        """
        self.positions = positions
        self.excitations = excitations
        if pattern is not None: 
            self.pattern = pattern
        else:
            self.pattern = [lambda phi,theta:1]
    
    def aiming(self,phi,theta):
        """Aims the main beam towards a desired directon.

        Use this to modify the `excitation`s phases so that main lobe points
        toward the given direction.
        
        Parameters
        ----------
        phi : array_like
            ángulo diedro del plano xz al plano xr donde r es la dirección de apuntamiento
        theta : array_like
            ángulo del eje z al vector de apuntamiento r

        Notes
        -----
        Only the phase is modified, not the amplitud.
        
        """
        normal = np.array((np.cos(phi)*np.sin(theta),np.sin(phi)*np.sin(theta),np.cos(theta)))
        phases = -2*np.pi*self.positions@normal
        self.excitations = np.abs(self.excitations)*np.exp(1j*phases)

    def _unique_direction_field(self,phi_i,theta_i):
        normal = np.array((np.cos(phi_i)*np.sin(theta_i),np.sin(phi_i)*np.sin(theta_i),np.cos(theta_i)))
        phases = 2*np.pi*self.positions@normal  

        antenna_pattern = self.pattern[0](phi_i,theta_i)
        return antenna_pattern*sum(self.excitations*np.exp(1j*phases))

    def _power_density(self,phi_i,theta_i):
        return (np.abs(self._unique_direction_field(phi_i,theta_i))**2)/(2*120*np.pi)

    def _half_power(self):
        average = integrate.dblquad(lambda phi,theta: self._power_density(phi,theta)*np.sin(theta),0,np.pi,-np.pi,np.pi,epsabs=1.49e-03, epsrel=50*1.49e-03)[0]/(4*np.pi)
        return average
    
    def directivity(self,phi,theta):
        average = self._half_power()        
        def directividad_dirUnica(phi_i,theta_i):
            return self._power_density(phi_i,theta_i)/average
        
        directividad_vec = np.vectorize(directividad_dirUnica)
        return directividad_vec(phi,theta)
  
    def vectorial_field(self,phi,theta):
        campo_vec = np.vectorize(self._unique_direction_field)
        return campo_vec(phi,theta)

    def get_beam_width(self, plot=False):
        theta = np.linspace(0,np.pi,100)
        phi = np.linspace(-np.pi,np.pi,100)
        THETA, PHI = np.meshgrid(theta,phi) #En THETA y PHI se guardan los valores de forma matricial de las coordenadas theta,phi
        f = lambda x,y: np.abs(self.directivity(x,y))   #R = np.abs(arreglo.campo(PHI,THETA))
        _R = f(PHI,THETA)
        
        _Rmax = np.max(_R)
        i_phi,i_theta = np.where(_R == _Rmax)
        theta_apuntado = np.degrees(theta[int(i_theta)])
        phi_apuntado = np.degrees(phi[int(i_phi)])  

        y_campo_phi = np.abs(self.directivity(math.radians(phi_apuntado),theta))
        x_theta = np.degrees(theta)

        if plot: 
            fig = plt.figure()    
            ax1 = fig.add_subplot(2,1,1)
            ax1.plot(x_theta,y_campo_phi)
            ax1.set_title("Patron $\\theta$"), ax1.grid(True)
        
        x = [0]
        y = [0]
        
        _Rmax= np.max(y_campo_phi)
        _Rrange = _Rmax*0.3
        for i in np.arange(np.size(y_campo_phi,0)):
            if (y_campo_phi[i] >= _Rrange):
                x = np.append(x,np.array([y_campo_phi[i]]),axis=0)
                y = np.append(y,np.array([x_theta[i]]),axis=0)
        y = y[1:]
        x = x[1:]

        index_Rmax = np.where( x == _Rmax )
        index = int(index_Rmax[0])

        R_left = x[0:index] 
        theta_left = y[0:index]
        R_right = x[index:-1] 
        theta_right = y[index:-1]

        theta_hp_min = np.interp(_Rmax*(2**-0.5),R_left,theta_left)
        if len(R_right) == 0:
            theta_hp_max = 90
        else:
            theta_hp_max = np.interp(-_Rmax*(2**-0.5),-R_right,theta_right)
        
        if plot: ax1.plot(theta_hp_min,_Rmax*(2**-0.5),'or',theta_hp_max,_Rmax*(2**-0.5),'or')
        
        elev_width = theta_hp_max - theta_hp_min        
        x_phi = np.degrees(phi)
        y_campo_theta = np.abs(self.directivity(phi,math.radians(theta_apuntado)))

        if plot: 
            ax1 = fig.add_subplot(2,1,2)
            ax1.plot(x_phi,y_campo_theta)
            ax1.set_title("Patron $\\varphi$ "), ax1.grid(True)

        xx = [0]
        yy = [0]
        _Rmax= np.max(y_campo_theta)
        _Rrange = _Rmax*0.3
        for i in np.arange(np.size(y_campo_theta,0)):
            if (y_campo_theta[i] >= _Rrange):
                xx = np.append(xx,np.array([y_campo_theta[i]]),axis=0)
                yy = np.append(yy,np.array([x_phi[i]]),axis=0)
        yy = yy[1:]
        xx = xx[1:]

        index_Rmax = np.where( xx == _Rmax )
        index = int(index_Rmax[0])
        R_left = xx[0:index] 
        phi_left = yy[0:index]
        R_right = xx[index:-1]
        phi_right = yy[index:-1]

        intensidad_media_potencia = _Rmax * (2**-0.5)
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
        azim_width = phi_hp_max - phi_hp_min
        directivity = _Rmax

        return [elev_width, azim_width, directivity]

    def plot_3D(self):
        """Realiza la representacion del patron de radiacion del arreglo
        y ubica las antenas en un espacio x,y,z
        
        """    
        theta = np.linspace(0,np.pi,100)
        phi = np.linspace(-np.pi,np.pi,100)
        THETA, PHI = np.meshgrid(theta,phi)
        f = lambda x,y: np.abs(self.vectorial_field(x,y))        
        _R = f(PHI,THETA)    

        _X = _R * np.cos(PHI) * np.sin(THETA)
        _Y = _R * np.sin(PHI) * np.sin(THETA)
        _Z = _R * np.cos(THETA)
        Rmax = np.max(_R)

        fig = plt.figure()
        ax = fig.add_subplot(projection = '3d')
        ax.set_xlim(-Rmax,Rmax)
        ax.set_ylim(-Rmax,Rmax)
        ax.set_zlim(-Rmax,Rmax)

        ax.plot_surface(_X,_Y,_Z,rcount=100,ccount=100,facecolors=cm.jet(_R/Rmax),shade=False)
        ax.set_title("3D Array")
        [dx,dy,dz] = [0,0,0]
        [xi, yi , zi] = 50*np.transpose(self.positions-np.array(((dx,dy,dz))))
        ax.scatter(xi,yi,zi, c = 'green',  marker='+' , linewidth = 2)

        plt.show()


def amplitud_coseno_elevado(posiciones,escala=0.8):
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


def quarter_wave_monopole_pattern():
    self = quarter_wave_monopole_pattern
    if ("pattern" not in dir(self)):
        epsilon = 1e-6
        def f_denorm(theta):
            theta=np.array(theta)
            determinado = (theta > epsilon) & (theta <= np.pi/2)
            result = np.zeros(theta.shape)
            theta_determinado = theta[determinado]
            result[determinado] = np.cos(np.pi/2*np.cos(theta_determinado))/np.sin(theta_determinado) 
            return result
        # Simetria axial, eje z
        potenciaMedia = integrate.quad(lambda th: f_denorm(th)**2*np.sin(th),0,np.pi)[0]/2
        escala = 1/potenciaMedia**.5 # para normalizar a potencia media 1
        def pattern(phi,theta):
            return escala*f_denorm(theta)
        self.pattern = pattern
    return self.pattern


def denormalise_frequencies(frequencies_list,distance_reference):
    C = 3e8 # Speed Light
    n = np.size(frequencies_list)
    _lambda = C/frequencies_list
    d_real = distance_reference*_lambda[0]
    denormalised_distance = d_real/_lambda

    return denormalised_distance

def denormalise_distance(frequencies_list,distance_reference):
    C = 3e8 # Speed Light
    _lambda = C/frequencies_list
    d_real = distance_reference*_lambda[0]
    denormalised_distance = d_real/_lambda
    ret = denormalised_distance*_lambda
    return ret[0]


if __name__ == '__main__':
    print('\n**Este modulo debe ser incluido en la sección "imports" para ser usado**')
    print('Intentar corriendo funciones_disenio.py')
