# Import modules
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends import backend_tkagg
import matplotlib.animation as animation
from sympy import symbols, lambdify, abc, latex, diff, integrate
from sympy.parsing.sympy_parser import parse_expr
from keyword import kwlist

np.seterr(all = 'raise')

def convert_to_function(string):
    """Using the sympy module, parse string input into a mathematical expression.
    Returns the original string, the latexified string,
    the mathematical expression in terms of sympy symbols,
    and a lambdified function
    """
    symbolic_function=parse_expr(string)
    latexstring=latex(symbolic_function)
    lambda_function=lambdify(abc.t,symbolic_function)
    string=string.replace('*','')
    latexstring="$"+latexstring+"$"
    return string, latexstring, symbolic_function, lambda_function

def normalize(y,dx):
    """Normalize a given function over a domain"""
    temp= np.trapz(y*y,dx=dx)
    temp= np.sqrt(temp)
    return y/temp

def fit_ybounds(y,y0,yf):
    """Make a function conform to certain boundaries"""
    ymin=np.amin(y)
    ymax=np.amax(y)
    yext=ymax-ymin
    y=(yf-y0)*((y-ymin)/yext)+y0
    return y


class Fourier_Series_Animation_Real:

    def __init__(self,function_name,N=256,tau=6.283185307179586,dpi=150):
        """The number of points and length of period are defined,
        then further functions are called.
        """

        self.N   = N #Total number of points
        self.M   = N #Total number of exponential phasors.
        # This is equal to the number of points when appplying the fft,
        # but for rfft it is roughly half.

        self.tau = tau # Period
        itvl=tau/N
        self.t   = np.linspace(-tau/2,tau/2-itvl,N) #Time Array
        # itvl ensures that t[-1] does not equal t[0] for a waveform
        # that is periodic along t.

        # Show only positive frequencies
        self.only_positive_freqs=True

        # Colour of the plot
        self.plot_color="red"

        # Resolution of the plot
        self.dpi=dpi

        # Fourier Circles
        # Fourier circles are the circles traced by each phasor
        self.show_circles = True #Whether to show circles
        self.T=50 #Number of points to draw for each circle

        #Animation speed or frames per each animation number i
        self.fpi = 1

        #Total number of animation frames. The initial number is -2.
        self._i = -2

        self.update_waveform_by_entry(function_name)
        self.init_animation()

    def update_waveform_by_entry(self,function_name):
        """From string input, initialize the waveform and then perform a
        Fast Fourier Transform on it to decompose it to its Fourier Amplitudes.
        Called each time the waveform is changed.
        """

        assert not (any([(keyword + " ") in function_name for keyword in kwlist]))
        string, latexstring, symbolic_function, lambda_function=\
        convert_to_function(function_name)

        #Test out the function first to see if it is valid
        tmp = np.complex(np.sqrt(lambda_function(0)))

        #self.title=latexstring+",   "+"$0 \leq t < 2 \pi $"
        self.title=latexstring+",   "+"$ t = s (mod(2 \pi)) - \pi $"

        if len(self.title) > 100: #If the title is too long, shorten it
            #self.title="f(t)"+",   "+"$0 \leq t < 2 \pi $"
            self.title="f(t)"+",   "+"$ t = s (mod(2 \pi)) - \pi $"

        #Depending on the version of sympy,
        #the lambda function may not support numpy arrays
        try:
            self.x =lambda_function(self.t) #This is the function
        except:
            self.x=\
            np.array([lambda_function(self.t[i]) for i in range (len(self.t))])

        #Ensure that the plot remains inside the viewable boundaries
        if (np.amax(np.abs(self.x))>1.05):
            dt=self.tau/self.N
            self.x=fit_ybounds(self.x,-1.,1.)
            #self.x=normalize(self.x,dt)
            #self.title=r"$ \alpha_{norm} ( $"+self.title+r"$)$"

        self.z =self.x*(1.0+0.0j)
        self.z_abs=np.abs(self.z)

        #If only positive frequencies are used
        #In this case an rfft is performed.
        if (self.only_positive_freqs):

            self.M=self.N//2+1 #number of points returned by rfft
            self.F_raw=2*np.fft.rfft(self.x)/self.N #rfft of the function
            self.frequencies_raw=np.fft.rfftfreq(self.N) # get the fequency bins

            ind=np.argsort(self.frequencies_raw)
            #sort frequencies from lowest to highest
            self.frequencies=np.sort(self.frequencies_raw)
            self.F=np.array([self.F_raw[ind[i]] for i in range (self.M)])
            self.F[0]*=0.5

        #If both positive and negative frequencies are used
        else:

            self.F_raw=np.fft.fft(self.z)/self.N #fft of the function
            self.frequencies_raw=np.fft.fftfreq(self.N) # get the fequency bins

            ind=np.argsort(self.frequencies_raw)
            #sort frequencies from lowest to highest
            self.frequencies=np.sort(self.frequencies_raw)
            self.F=np.array([self.F_raw[ind[i]] for i in range (self.N)])

    def init_animation(self):
        """Initialize all matplotlib objects
        and construct the first frame animation.
        Only called once.
        """

        self.figure=plt.figure(figsize=(10,3),dpi=self.dpi)

        self.ax = self.figure.add_subplot(1, 1, 1, aspect=1)
        self.ax.grid(linestyle="--")

        #Viewable range
        maxval=np.amax(self.x)
        view=2*maxval
        self.ax.set_xlim(-2.*maxval-0.1*view,2)
        self.ax.set_ylim(-maxval-0.1*view,maxval+0.1*view)

        #Initialize title and set its location
        #self.plot_title=self.ax.text(-1,1,self.title)
        self.plot_title=self.ax.text(-2.05,1,self.title)

        #Setup plot of original function
        self.t_=np.linspace(2.,6.,self.N)
        self.x=np.roll(self.x,(-2*self.fpi))

        self.ax.set_xticks([2.,3.,4.,5.,6.])
        self.ax.set_yticks([])
        #self.ax.set_xticklabels(\
        #                    ["0",r"$ \pi/2$",r"$ \pi$",r"3$ \pi/2$",r"$2 \pi$"])
        self.ax.set_xticklabels(\
                            [r"$s - \pi$",r"$s - \pi/2$",r"s",
                            r"$s + \pi/2$",r"$s + \pi$"])

        self.update_phasor_plots(init_call=True)

        self.original,=self.ax.plot(self.t_,self.x,
                                    color=self.plot_color,animated=True)

    def update_phasor_plots(self,init_call=False):
        """Initialize phasor plots. Called each time the waveform is changed.
        """
        if (self.show_circles):

            T=self.T
            self.F_curve=np.zeros([(T+1)*self.M],np.complex)

            #Make the first phasor
            self.F_curve[0]=\
            self.F[0]*np.exp(-2*np.pi*self._i*1.0j*self.frequencies[0])

            #Make the first circle
            for m in range(T):
                    self.F_curve[m+1]\
                            =self.F[0]*np.exp(0*1.0j*np.pi*((m+1)/T))

            for j in range(1,self.M):
                k=j*(T+1)
                temp=self.F[j]
                #if np.abs(self.F[j]) >= (max_z/(self.M/2)):

                #Make the jth phasor
                phase=np.exp(-2*np.pi*self._i*1.0j*self.frequencies[j])
                temp*=phase
                temp2=self.F_curve[k-1]
                self.F_curve[k]=temp2+temp

                """
                # No circle for the 0 frequency
                if (self.frequencies[j]==0):
                    for l in range(T):
                        self.F_curve[l+k+1]=self.F_curve[k]
                else:

                    #Make the jth circle
                    for l in range(T):
                        #if i==2:
                        #    print(str(l+k))
                        self.F_curve[l+k+1]\
                                =temp2+temp*np.exp(2*1.0j*np.pi*((l+1)/T))
                """
                #Make the jth circle
                for l in range(T):
                    #if i==2:
                    #    print(str(l+k))
                    self.F_curve[l+k+1]\
                            =temp2+temp*np.exp(2*1.0j*np.pi*((l+1)/T))

        else:

            #Array containing each phasor amplitude
            self.F_curve=np.zeros([self.M],np.complex)

            self.F_curve[0]=self.F[0]
            for i in range (1,self.M):
                self.F_curve[i]=self.F_curve[i-1]+self.F[i]

        #the horizontal dashed line
        #that marks the value fo the waveform at a given t
        horizontal=np.linspace(np.imag(self.F_curve[-1]),2.,2)
        vertical=np.real(self.F_curve[-1])
        vertical=np.array([vertical,vertical])

        #If this is the first time that the function is called,
        #initialize the plot
        if (init_call):
            self.plot,=\
            self.ax.plot(np.imag(self.F_curve),np.real(self.F_curve),\
                         color="black",linewidth=1.,animated=True)
            self.line,=self.ax.plot(horizontal,vertical,
                                    "--",color=self.plot_color)

        #Otherwise update the plot
        else:
            self.plot.set_xdata(np.imag(self.F_curve))
            self.plot.set_ydata(np.real(self.F_curve))

            self.line.set_xdata(horizontal)
            self.line.set_ydata(vertical)

        #self.ax.plot(self.F_curve[-1])

    def update(self,function_name):
        """If a new function is inputed, update the plots
        """
        try:
            self.update_waveform_by_entry(function_name)
            self.x=np.roll(self.x,(self._i))
            self.plot_title.set_text(self.title)
            self.update_phasor_plots()
        except Exception as E:
            print("Unable to recognize input due to the following error:")
            print(E)
            print("Input must:")
            print("-only be a function of t")
            print("-be real")
            print("-contain recognizable functions")
            print("-use ** for powers instead of ^\n")

    def animate(self,i):
        """Animation function for all later frames
        """
        fpi=self.fpi
        self._i+=fpi
        self.x=np.roll(self.x,fpi)
        end_point=0.
        max_z=np.amax(self.z_abs)

        if (self.show_circles):

            T=self.T

            #Make the first phasor
            self.F_curve[0]=\
            self.F[0]*np.exp(-2*np.pi*self._i*1.0j*self.frequencies[0])

            #Make the first circle
            for m in range(T):
                    self.F_curve[m]\
                            =self.F[0]*np.exp(0*1.0j*np.pi*((m+1)/T))

            for j in range(1,self.M):
                k=j*(T+1)
                temp=self.F[j]
                #if np.abs(self.F[j]) >= (max_z/(self.M/2)):

                #Make the jth phasor
                phase=np.exp(-2*np.pi*self._i*1.0j*self.frequencies[j])
                temp*=phase
                temp2=self.F_curve[k-1]
                self.F_curve[k]=temp2+temp

                """
                # No circle for the 0 frequency
                if (self.frequencies[j]==0):
                    for l in range(T):
                        self.F_curve[l+k+1]=self.F_curve[k]
                else:

                    #Make the jth circle
                    for l in range(T):
                        #if i==2:
                        #    print(str(l+k))
                        self.F_curve[l+k+1]\
                                =temp2+temp*np.exp(2*1.0j*np.pi*((l+1)/T))
                """
                #Make the jth circle
                for l in range(T):
                    #if i==2:
                    #    print(str(l+k))
                    self.F_curve[l+k+1]\
                            =temp2+temp*np.exp(2*1.0j*np.pi*((l+1)/T))

        else:

            self.F_curve[0]=\
                    self.F[0]*np.exp(-2*np.pi*self._i*1.0j*self.frequencies[0])
            for j in range(1,self.M):
                temp=self.F[j]
                #if np.abs(self.F[j]) >= (max_z/(self.M/2)):
                phase=np.exp(-2*np.pi*self._i*1.0j*self.frequencies[j])
                temp*=phase
                self.F_curve[j]=self.F_curve[j-1]+temp

        self.original.set_ydata(self.x)

        horizontal=np.linspace(np.imag(self.F_curve[-1]),2.,2)
        vertical=np.real(self.F_curve[-1])
        vertical=np.array([vertical,vertical])

        #Update the plots

        self.line.set_xdata(horizontal)
        self.line.set_ydata(vertical)

        self.plot.set_xdata(np.imag(self.F_curve))
        self.plot.set_ydata(np.real(self.F_curve))

        return (self.line,)+(self.original,)+(self.plot,)+(self.plot_title,)


    def animation_loop(self,makemovie=False):
        """Function for main animation loop
        """
        interval= 10 if self.show_circles else 20
        #interval= 16 if self.show_circles else 32

        #Only know how to do this in jupyter notebook
        if (makemovie):
            self.main_animation=animation.FuncAnimation\
                (self.figure, self.animate,blit=True,
                 frames=2*self.N, interval=interval/2)
            try:
                from IPython.display import HTML
                HTML(self.main_animation.to_jshtml())
                self.main_animation.save("movie.mp4")
            except:
                pass
        self.main_animation=animation.FuncAnimation\
                (self.figure, self.animate,blit=True, interval=interval)

if __name__ == "__main__":

    Ani=Fourier_Series_Animation_Real("sin(t)")

    string =r"(5/2)*("
    for i in range(1,40,2):
        string+="+sin(t*"+str(i)+")/(pi*"+str(i)+")"
    string+=")"

    Ani.update(string)
    #Ani.update("11*sinc(t**2)/8-1/2")
    #Ani.update("sin(t)")
    Ani.animation_loop()
    plt.show()
