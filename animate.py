"""
Animation.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from sympy import lambdify, abc, latex, Function, FunctionClass
from sympy.parsing.sympy_parser import parse_expr
from keyword import kwlist
from typing import Tuple, List
np.seterr(all='raise')


def convert_to_function(string: str) -> Tuple[
        str, str, Function, FunctionClass]:
    """
    Using the sympy module,
    parse string input into a mathematical expression.
    Returns the original string, the latexified string,
    the mathematical expression in terms of sympy symbols,
    and a lambdified function
    """
    symbolic_function = parse_expr(string)
    latexstring = latex(symbolic_function)
    lambda_function = lambdify(abc.t, symbolic_function)
    string = string.replace('*', '')
    latexstring = "$" + latexstring + "$"
    return string, latexstring, symbolic_function, lambda_function


def normalize(y: np.ndarray, dx: float) -> np.ndarray:
    """
    Normalize a given function over a domain
    """
    temp = np.trapz(y*y, dx=dx)
    temp = np.sqrt(temp)
    return y/temp


def fit_ybounds(y: np.ndarray, y0: float, yf: float) -> np.ndarray:
    """
    Make a function conform to certain boundaries
    """
    ymin = np.amin(y)
    ymax = np.amax(y)
    yext = ymax-ymin
    y = (yf - y0)*((y - ymin)/yext) + y0
    return y


class FourierSeriesAnimation:
    """
    Fourier Series Animation class.
    """

    def __init__(self,
                 function_name: str,
                 n: int = 256, tau: float = 6.283185307179586,
                 dpi: int = 150) -> None:
        """
        The number of points and length of period are defined,
        then further functions are called.

        Input:
        function_name: Name of the function
        n: the number of points
        tau: the total period of the function. Don't confuse tau with
             the mathematical constant, 2pi just happens to be convenient.
        dpi: density per square inch, which dictates the resolution
             of the plot
        """

        self.n = n  # Total number of points
        self.m = n  # Total number of exponential phasors.
        # This is equal to the number of points when appplying the fft,
        # but for rfft it is roughly half.

        self.tau = tau  # Period
        itvl = tau/n
        self.t = np.linspace(-tau/2, tau/2 - itvl, n)  # Time Array
        # itvl ensures that t[-1] does not equal t[0] for a waveform
        # that is periodic along t.

        # Show only positive frequencies
        self.only_positive_freqs = True

        # Colour of the plot
        self.plot_color = "red"

        # Resolution of the plot
        self.dpi = dpi

        # Fourier Circles
        # Fourier circles are the circles traced by each phasor
        self.show_circles = True  # Whether to show circles
        self.pts_per_circle = 50  # Number of points to draw for each circle

        # Animation speed or frames per each animation number i
        self.fpi = 1

        # Total number of animation frames. The initial number is -2.
        self._i = -2

        self.update_waveform_by_entry(function_name)
        self.init_animation()

    def update_waveform_by_entry(self, function_name: str) -> None:
        """From string input, initialize the waveform and then perform a
        Fast Fourier Transform on it to decompose it to its Fourier amplitudes.
        Called each time the waveform is changed.
        """

        assert not (
                any([(keyword + " ") in function_name for keyword in kwlist]))
        (string, latexstring,
         symbolic_function,
         lambda_function) = convert_to_function(function_name)

        # Test out the function first to see if it is valid
        # tmp = np.complex(np.sqrt(lambda_function(0)))

        # self.title=latexstring+",   "+"$0 \leq t < 2 \pi $"
        self.title = latexstring + ",   " + "$ t = s (mod(2 \pi)) - \pi $"

        if len(self.title) > 100:  # If the title is too long, shorten it
            # self.title="f(t)"+",   "+"$0 \leq t < 2 \pi $"
            self.title = "f(t)" + ",   " + "$ t = s (mod(2 \pi)) - \pi $"

        # Depending on the version of sympy,
        # the lambda function may not support numpy arrays
        try:
            self.x = lambda_function(self.t)  # This is the function
        except Exception as e:
            print(e)
            self.x = np.array(
                    [lambda_function(self.t[i]) for i in range(len(self.t))])

        # Ensure that the plot remains inside the viewable boundaries
        if (np.amax(np.abs(self.x)) > 1.05):
            # dt = self.tau/self.n
            self.x = fit_ybounds(self.x, -1.0, 1.0)
            # self.x=normalize(self.x, dt)
            # self.title=r"$ \alpha_{norm} ( $"+self.title+r"$)$"

        self.z = self.x*(1.0 + 0.0j)
        self.z_abs = np.abs(self.z)

        # If only positive frequencies are used
        # In this case an rfft is performed.
        if (self.only_positive_freqs):

            self.m = self.n//2 + 1   # number of points returned by rfft
            self.f_raw = 2*np.fft.rfft(self.x)/self.n  # rfft of the function
            self.frequencies_raw = np.fft.rfftfreq(self.n)
            # get the fequency bins

            ind = np.argsort(self.frequencies_raw)
            # sort frequencies from lowest to highest
            self.frequencies = np.sort(self.frequencies_raw)
            self.f = np.array([self.f_raw[ind[i]] for i in range(self.m)])
            self.f[0] *= 0.5

        # If both positive and negative frequencies are used
        else:

            self.f_raw = np.fft.fft(self.z)/self.n  # fft of the function
            self.frequencies_raw = np.fft.fftfreq(self.n)
            # get the fequency bins

            ind = np.argsort(self.frequencies_raw)
            # sort frequencies from lowest to highest
            self.frequencies = np.sort(self.frequencies_raw)
            self.f = np.array([self.f_raw[ind[i]] for i in range(self.n)])

    def init_animation(self) -> None:
        """Initialize all matplotlib objects
        and construct the first frame animation.
        Only called once at the very beggining of this program.
        """

        self.figure = plt.figure(figsize=(10, 3), dpi=self.dpi)

        self.ax = self.figure.add_subplot(1, 1, 1, aspect=1)
        self.ax.grid(linestyle="--")

        # Viewable range
        maxval = np.amax(self.x)
        view = 2*maxval
        self.ax.set_xlim(-2.*maxval-0.1*view, 2)
        self.ax.set_ylim(-maxval-0.1*view, maxval+0.1*view)

        # Initialize title and set its location
        # self.plot_title=self.ax.text(-1,1,self.title)
        self.plot_title = self.ax.text(-2.05, 1, self.title)

        # Setup plot of original function
        self.t_ = np.linspace(2.0, 6.0, self.n)
        self.x = np.roll(self.x, (-2*self.fpi))

        self.ax.set_xticks([2.0, 3.0, 4.0, 5.0, 6.0])
        self.ax.set_yticks([])
        # self.ax.set_xticklabels(\
        #                     [
        # "0",r"$ \pi/2$",r"$ \pi$",r"3$ \pi/2$",r"$2 \pi$"])
        self.ax.set_xticklabels([r"$s - \pi$", r"$s - \pi/2$", r"s",
                                 r"$s + \pi/2$", r"$s + \pi$"])

        self.update_phasor_plots(init_call=True)

        self.original, = self.ax.plot(self.t_, self.x,
                                      color=self.plot_color, animated=True)

    def update_phasor_plots(self, init_call: bool = False) -> None:
        """Initialize phasor plots. Called each time the waveform is changed.
        """
        if (self.show_circles):

            ptspercircle = self.pts_per_circle
            self.f_curve = np.zeros([(ptspercircle + 1)*self.m], np.complex)

            # Make the first phasor
            self.f_curve[0] = self.f[0]*np.exp(
                    -2*np.pi*self._i*1.0j*self.frequencies[0])

            # Make the first circle
            for m in range(ptspercircle):
                self.f_curve[m + 1] = self.f[0]*np.exp(
                        0*1.0j*np.pi*((m + 1)/ptspercircle))

            for j in range(1, self.m):
                k = j*(ptspercircle + 1)
                temp = self.f[j]
                # if np.abs(self.f[j]) >= (max_z/(self.m/2)):

                # Make the jth phasor
                phase = np.exp(-2*np.pi*self._i*1.0j*self.frequencies[j])
                temp *= phase
                temp2 = self.f_curve[k - 1]
                self.f_curve[k] = temp2 + temp

                """
                # No circle for the 0 frequency
                if (self.frequencies[j] == 0):
                    for l in range(ptspercircle):
                        self.f_curve[l+k+1] = self.f_curve[k]
                else:

                    #Make the jth circle
                    for l in range(ptspercircle):
                        #if i == 2:
                        #    print(str(l + k))
                        self.f_curve[l + k + 1]\
                                =temp2 + temp*np.exp(2*1.0j*np.pi*((l + 1)/T))
                """
                # Make the jth circle
                for l in range(ptspercircle):
                    # if i==2:
                    #     print(str(l+k))
                    self.f_curve[l+k+1] = temp2 + temp*np.exp(
                            2*1.0j*np.pi*((l+1)/ptspercircle))

        else:

            # Array containing each phasor amplitude
            self.f_curve = np.zeros([self.m], np.complex)

            self.f_curve[0] = self.f[0]
            for i in range(1, self.m):
                self.f_curve[i] = self.f_curve[i-1] + self.f[i]

        # the horizontal dashed line
        # that marks the value fo the waveform at a given t
        horizontal = np.linspace(np.imag(self.f_curve[-1]), 2.0, 2)
        vertical = np.real(self.f_curve[-1])
        vertical = np.array([vertical, vertical])

        # If this is the first time that the function is called,
        # initialize the plot
        if (init_call):
            self.plot, = self.ax.plot(
                    np.imag(self.f_curve), np.real(self.f_curve),
                    color="black", linewidth=1., animated=True)
            self.line, = self.ax.plot(horizontal,
                                      vertical, "--", color=self.plot_color)

        # Otherwise update the plot
        else:
            self.plot.set_xdata(np.imag(self.f_curve))
            self.plot.set_ydata(np.real(self.f_curve))

            self.line.set_xdata(horizontal)
            self.line.set_ydata(vertical)

        # self.ax.plot(self.f_curve[-1])

    def update(self, function_name: str) -> None:
        """If a new function is inputed, update the plots
        """
        try:
            self.update_waveform_by_entry(function_name)
            self.x = np.roll(self.x, (self._i))
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

    def animate(self, i: int) -> List[plt.Artist]:
        """Animation function for all later frames
        """
        fpi = self.fpi
        self._i += fpi
        self.x = np.roll(self.x, fpi)
        # end_point = 0.
        # max_z = np.amax(self.z_abs)

        if (self.show_circles):

            ptspercircle = self.pts_per_circle

            # Make the first phasor
            self.f_curve[0] = self.f[0]*np.exp(
                    -2*np.pi*self._i*1.0j*self.frequencies[0])

            # Make the first circle
            for m in range(ptspercircle):
                self.f_curve[m] = self.f[0]*np.exp(
                            0*1.0j*np.pi*((m + 1)/ptspercircle))

            for j in range(1, self.m):
                k = j*(ptspercircle + 1)
                temp = self.f[j]
                # if np.abs(self.f[j]) >= (max_z/(self.m/2)):

                # Make the jth phasor
                phase = np.exp(-2*np.pi*self._i*1.0j*self.frequencies[j])
                temp *= phase
                temp2 = self.f_curve[k-1]
                self.f_curve[k] = temp2 + temp

                """
                # No circle for the 0 frequency
                if (self.frequencies[j] == 0):
                    for l in range(ptspercircle):
                        self.f_curve[l + k + 1] = self.f_curve[k]
                else:

                    #Make the jth circle
                    for l in range(ptspercircle):
                        #if i==2:
                        #    print(str(l + k))
                        self.f_curve[l + k + 1]\
                                =temp2 +
                                temp*np.exp(2*1.0j*np.pi*(
                                (l + 1)/ptspercircle))
                """
                # Make the jth circle
                for l in range(ptspercircle):
                    # if i==2:
                    #     print(str(l+k))
                    self.f_curve[l + k + 1] = temp2 + temp*np.exp(
                            2*1.0j*np.pi*((l+1)/ptspercircle))

        else:

            self.f_curve[0] = self.f[0]*np.exp(
                    -2*np.pi*self._i*1.0j*self.frequencies[0])
            for j in range(1, self.m):
                temp = self.f[j]
                # if np.abs(self.f[j]) >= (max_z/(self.m/2)):
                phase = np.exp(-2*np.pi*self._i*1.0j*self.frequencies[j])
                temp *= phase
                self.f_curve[j] = self.f_curve[j-1] + temp

        self.original.set_ydata(self.x)

        horizontal = np.linspace(np.imag(self.f_curve[-1]), 2.0, 2)
        vertical = np.real(self.f_curve[-1])
        vertical = np.array([vertical, vertical])

        # Update the plots
        self.line.set_xdata(horizontal)
        self.line.set_ydata(vertical)
        self.plot.set_xdata(np.imag(self.f_curve))
        self.plot.set_ydata(np.real(self.f_curve))

        return (self.line, self.original, self.plot, self.plot_title)

    def animation_loop(self, makemovie: bool = False) -> None:
        """Function for main animation loop
        """
        interval = 10 if self.show_circles else 20
        # interval= 16 if self.show_circles else 32

        # Only know how to do this in jupyter notebook
        if (makemovie):
            self.main_animation = animation.FuncAnimation(
                    self.figure, self.animate, blit=True,
                    frames=2*self.n, interval=interval/2
                    )
            try:
                from IPython.display import HTML
                HTML(self.main_animation.to_jshtml())
                self.main_animation.save("movie.mp4")
            except Exception as e:
                print(e)
        self.main_animation = animation.FuncAnimation(
                self.figure, self.animate, blit=True, interval=interval)


if __name__ == "__main__":

    ani = FourierSeriesAnimation("sin(t)")

    string = r"(5/2)*("
    for i in range(1, 40, 2):
        string += "+sin(t*" + str(i) + ")/(pi*" + str(i) + ")"
    string += ")"

    ani.update(string)
    # Ani.update("11*sinc(t**2)/8-1/2")
    # Ani.update("sin(t)")
    ani.animation_loop()
    # plt.show()
