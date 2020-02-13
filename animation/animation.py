import numpy as np
import matplotlib.pyplot as plt
from .animator import Animator
from .circles import Circles, VerticalRescaler
from sympy import abc
from .functions import FunctionRtoR
# from time import perf_counter


class FourierAnimation(Animator):

    def __init__(self, function_name: str, dpi: int = 120) -> None:
        """
        The constructor
        """
        figsize = (10, 3)
        Animator.__init__(self, dpi, figsize, 15)
        self.counts = -2
        self.increment = 4
        ax = self.figure.add_subplot(
            1, 1, 1, aspect="equal")
        maxval = 1.0
        view = 2*maxval
        ax.set_xlim(-2.0*maxval - 0.1*view, 2)
        ax.set_ylim(-maxval-0.1*view, maxval+0.1*view)
        ax.set_xticks([2.0, 3.0, 4.0, 5.0, 6.0])
        ax.set_yticks([])
        ax.set_xticklabels([r"$s - \pi$", r"$s - \pi/2$", r"s",
                            r"$s + \pi/2$", r"$s + \pi$"])
        ax.grid(linestyle="--")
        self.circles = Circles(ax)
        function = FunctionRtoR(function_name, abc.t)
        self.function = function
        # self.function_display = ax.text(-2.05, 1,
        #                                 r"$f(t) = %s$"
        #                                r" ,   $ t = s (mod(2 \pi)) - \pi $" %
        #                                 function.latex_repr)
        self.function_display = ax.text(-2.05, 1,
                                        r"$f(t)$"
                                        r" ,   $ t = s (mod(2 \pi)) - \pi $")
        self.circles.set_function(function)
        self.add_plots([self.circles.get_plot()])

        v_line, = ax.plot([0.0, 2.0], [0.0, 0.0],
                          linewidth=1.0, linestyle="--", color="red")
        self.v_line = v_line

        self.t = np.linspace(-np.pi, np.pi - 2*np.pi/256.0, 256)
        self.x = function(self.t)
        self.x = np.roll(self.x, self.counts)
        function_plot, = ax.plot(np.linspace(2.0, 6.0, 256),
                                 self.x, linewidth=1.0,
                                 # color="black"
                                 color="gray"
                                 )
        amps = self.circles.get_amplitudes()
        self.x2 = np.fft.irfft(amps)
        self.x2 = np.roll(self.x2, self.counts)
        circle_function_plot, = ax.plot(np.linspace(2.0, 6.0, 256),
                                        self.x, linewidth=1.0,
                                        color="red")
        self.function_plot = function_plot
        self.circle_function_plot = circle_function_plot
        # TODO: Have the vertical rescaler class defined in this file instead
        # and pass it to Circles. Try to only use one instance of this class.
        self._rescale = VerticalRescaler()
        self.y_limits = [-1.0, 1.0]

    def update(self, delta_t: float) -> None:
        """
        Overridden update method from the Animator class
        """
        # print("fps: %.0f" % (1/delta_t))
        self.counts += self.increment
        # t1 = perf_counter()
        self.circles.update_plots(self.counts)
        # t2 = perf_counter()
        end_point = self.circles.get_end_point()
        # print("%f" % ((t2 - t1) / delta_t))
        x1 = np.imag(end_point)
        y = np.real(end_point)
        self.v_line.set_xdata([x1, 2.0])
        self.v_line.set_ydata([y, y])
        self.x = np.roll(self.x, self.increment)
        self.x2 = np.roll(self.x2, self.increment)
        self.function_plot.set_ydata(self.x)
        self.circle_function_plot.set_ydata(self.x2)

    def set_speed(self, speed: int) -> None:
        """
        Set the speed of the animation.
        """
        speed = int(speed)  # Fix a bug
        self.increment = speed

    def get_speed(self) -> int:
        """
        get the speed of the animation
        """
        return self.increment

    def set_function(self, function_name: str) -> None:
        """
        Set function.
        """
        self.function = FunctionRtoR(function_name, abc.t)
        self.function_display.set_text(r"$f(t) = %s$"
                                       r" ,   $ t = s (mod(2 \pi)) - \pi $" %
                                       self.function.latex_repr)
        self.circles.set_function(self.function)
        self._set_x()

    def set_number_of_circles(self, resolution: int) -> None:
        """
        Set the number of circles.
        """
        self.circles.set_number_of_circles(resolution)
        self._set_x2()

    def _set_x(self, *params) -> None:
        """
        Set x data.
        """
        if params == ():
            self.x = self.function(self.t)
        else:
            self.x = self.function(self.t, *params)
        self._rescale.set_scale_values(self.x, self.y_limits)
        if not self._rescale.in_bounds():
            self.x = self._rescale(self.x)
        self.x = np.roll(self.x, self.counts)
        self._set_x2()

    def _set_x2(self) -> None:
        """
        Set the x2 data.
        """
        amps = self.circles.get_amplitudes()
        self.x2 = np.fft.irfft(amps)
        self.x2 = np.roll(self.x2, self.counts)

    def set_params(self, *args: float) -> None:
        """
        Set the parameters of the function.
        """
        self.circles.set_params(*args)
        self._set_x(*args)


if __name__ == "__main__":
    # from matplotlib import interactive
    # interactive(True)
    # a = FourierAnimation("exp(-t**2/0.16**2)- 0.5")
    a = FourierAnimation("exp(-t**2/0.16**2)")
    a.animation_interval = 30
    a.animation_loop()
    plt.show()
