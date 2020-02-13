from .functions import FunctionRtoR
import numpy as np
from sympy import abc
from typing import List


class Circles:
    """
    Graph of the rotating complex exponentials.
    """
    def __init__(self, ax) -> None:
        """
        The initializer.
        """
        self._pts_per_circle = 50
        self._data = FourierData()
        # self._data.set_y_range(ax.get_ylim())
        self.resolution = self._data.n//2 + 1
        self._circles = np.zeros(
            [(self._pts_per_circle + 1)*self.resolution], np.complex)
        self._gen_circle = np.array([np.exp(
            2*1.0j*np.pi*((m + 1)/self._pts_per_circle))
                                     for m in range(self._pts_per_circle)],
                                    np.complex)
        plot, = ax.plot(np.imag(self._circles), np.real(self._circles),
                        linewidth=1.0, color="black", animated=True)
        self._EPSILON = (
                np.max(plot.get_ydata()) - np.min(plot.get_ydata()))/10
        self._plot = plot
        self.update_plots(0)

    def get_plot(self):
        """
        Get the matplotlib object that represents the
        graph of the rotating complex exponentials.
        """
        return self._plot

    def set_number_of_circles(self, resolution: int) -> None:
        """
        Set the number of circles.
        """
        if (self._data.n//2+1) >= resolution > 0:
            self.resolution = resolution

    def get_amplitudes(self) -> np.ndarray:
        """
        Get a copy of the Fourier amplitudes.
        """
        amps = self._data.get_unscaled_amplitudes()
        amps = np.copy(amps)
        for i in range(self.resolution, self._data.n//2 + 1):
            amps[i] = 0.0
        return amps

    def get_end_point(self) -> np.complex:
        """
        Get the end point of the rotating complex exponentials.
        """
        return self._circles[-1]

    def update_plots(self, i: int) -> None:
        """
        Update the graph of the circles.
        """
        a = self._data.get_amplitudes()
        f = self._data.get_frequencies()
        circles = self._circles
        # Draw all phasors and circles.
        for j in range(self.resolution):
            if j == 0:
                circles[0] = a[0]*np.exp(-2*np.pi*i*1.0j*f[0])
                for m in range(self._pts_per_circle):
                    circles[m + 1] = a[0]*np.exp(0*1.0j*np.pi*(
                            (m + 1)/self._pts_per_circle))
            else:
                k = j*(self._pts_per_circle + 1)
                amplitude = np.exp(-2*np.pi*i*1.0j*f[j])*a[j]
                circles[k] = amplitude + self._circles[k - 1]
                self._draw_circle(circles[k - 1], amplitude, k)
        stop_index = self.resolution*(self._pts_per_circle + 1) - 1
        for j in range(stop_index, len(circles)):
            circles[j] = circles[stop_index]
        self._plot.set_xdata(np.imag(circles))
        self._plot.set_ydata(np.real(circles))

    def _draw_circle(self, centre: float, amp: float, k: int) -> None:
        """
        Draw a single circle. Helper method for update_plots.
        """
        if np.real(amp*np.conj(amp)) < self._EPSILON:
            point = centre + amp
            print("This statement is reached.")
            for m in range(self._pts_per_circle):
                self._circles[k + m + 1] = point
        else:
            for m in range(self._pts_per_circle):
                self._circles[k + m + 1] = centre + amp*self._gen_circle[m]
                # self._circles[k + m + 1] = centre + amp*np.exp(
                #    2*1.0j*np.pi*((m + 1)/self._pts_per_circle))

    def set_period(self, start: float, period: float) -> None:
        """
        Set the period.
        """
        self._data.set_period(start, period)

    def set_number_of_points(self, n: int) -> None:
        """
        Set the number of points.
        """
        self._data.set_number_of_points(n)

    def get_number_of_points(self) -> int:
        """
        Get the number of points.
        """
        return self._data.n

    def set_params(self, *args) -> None:
        """
        Set parameters.
        """
        self._data.set_params(*args)

    def set_function(self, function: FunctionRtoR) -> None:
        """
        Set the function.
        """
        self._data.set_function(function)


class FourierData:
    """
    Class that stores data about the fourier amplitudes.
    """

    def __init__(self) -> None:
        """
        The constructor
        """
        period = 2*np.pi
        self.period = period
        self.function = FunctionRtoR("a*sin(10*k*(t - phi))", abc.t)
        self.n = 256
        self.y_limits = [-1, 1]
        self.t = np.linspace(-period/2,
                             period*(1.0/2.0 - 1.0/256.0),
                             256)
        kwargs = self.function.get_default_values()
        args = (kwargs[s] for s in kwargs)
        self.f = np.fft.rfftfreq(self.n)
        self._sort_arr = np.argsort(self.f)
        self.f = np.array([
                self.f[self._sort_arr[i]]
                for i in range(len(self.f))])
        self.x = np.array([], np.float)
        self.a = np.array([], np.float)
        self._rescale = VerticalRescaler()
        self._update_data(self.t, *args)

    def get_unscaled_amplitudes(self) -> np.ndarray:
        """
        Get the Fourier amplitudes
        before any scaling is applied
        """
        return self._original_amplitudes

    def get_amplitudes(self) -> np.ndarray:
        """
        Get the Fourier amplitudes.
        """
        return self.a

    def get_frequencies(self) -> np.ndarray:
        """
        Get the Fourier frequencies.
        """
        return self.f

    def _update_data(self, t: np.array, *args) -> None:
        """
        Update the data.
        """
        self.x = self.function(t, *args)
        self._rescale.set_scale_values(self.x, self.y_limits)
        if not self._rescale.in_bounds():
            self.x = self._rescale(self.x)
            print("Rescaled Amplitudes")
        self._original_amplitudes = np.fft.rfft(self.x)
        self.a = 2*self._original_amplitudes/self.n
        self.a = np.array([
                self.a[self._sort_arr[i]]
                for i in range(len(self.a))])
        self.a[0] *= 0.5  # Scale the 0th frequency amplitude by one half.

    def set_params(self, *args) -> None:
        """
        Set the parameters of the function
        """
        self._update_data(self.t, *args)

    def set_number_of_points(self, n: int) -> None:
        """
        Set the number of points to sample.
        """
        self.n = n
        start = self.t[0]
        period = self.period
        self.t = np.linspace(start,
                             start + period*(1.0 - 1.0/self.n),
                             self.n)
        self._update_data(self.t,
                          *self.function.get_default_values())

    def set_period(self, start: float, period: float) -> None:
        """
        Set the period.
        """
        self.period = period
        self.t = np.linspace(start,
                             start + period*(1.0 - 1.0/self.n),
                             self.n)
        self._update_data(self.t,
                          *self.function.get_default_values())

    def set_function(self, function: FunctionRtoR) -> None:
        """
        Take the discrete Fourier transform of a new function.
        """
        self.function = function
        kwargs = self.function.get_default_values()
        args = (kwargs[s] for s in kwargs)
        self._update_data(self.t, *args)

    def set_y_range(self, y_limits) -> None:
        """
        Set the limits on the y-axis.
        """
        self.y_limits = y_limits


class VerticalRescaler:
    """
    Rescale vertically.
    """

    def __init__(self) -> None:
        """
        The constructor.
        """
        self._y_min = -1
        self._y_max = 1
        self._y_diff = self._y_max - self._y_min
        self._plot_range = [-1, 1]
        self._plot_range_diff = self._plot_range[1] - self._plot_range[0]

    def set_scale_values(
            self, y_arr: np.ndarray, plot_range: List[int]) -> None:
        """
        Set new values.
        """
        self._y_min = np.amin(y_arr)
        self._y_max = np.amax(y_arr)
        self._y_diff = self._y_max - self._y_min
        self._plot_range = plot_range
        self._plot_range_diff = plot_range[1] - plot_range[0]

    def in_bounds(self) -> bool:
        """
        Determine if a function is already within the y-boundaries.
        """
        plot_range = self._plot_range
        return ((plot_range[0] <= self._y_min <= plot_range[1]) and
                (plot_range[0] <= self._y_max <= plot_range[1]))

    def __call__(self, y_arr) -> np.ndarray:
        """
        Rescale the function by a certain amount.
        """
        y_arr = ((
            self._plot_range_diff)*(
                (y_arr - self._y_min)/self._y_diff)
                 + self._plot_range[0])
        return y_arr
