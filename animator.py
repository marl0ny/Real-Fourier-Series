"""
Abstract animation class and constants.
"""
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.text import Text
from matplotlib.collections import Collection, PathCollection
from matplotlib.quiver import QuiverKey, Quiver
import matplotlib.animation as animation
from typing import List, Tuple
from time import perf_counter

artists = [Line2D, Collection, Text, QuiverKey, Quiver, PathCollection]


class Animator:
    """
    Abstract animation class that adds a small layer of abstraction
    over the matplotlib animation functions and interfaces.

    To use this class:
        -Inherit this in a derived class.
        -The Figure object is already instantiated in this class as the
         attribute self.figure. Create instances of
         plotting objects from this, such as Line2D.
        -Update the plots inside the update method, which must be
         overriden.
        -Call the animation_loop method to show the animation.

    Attributes:
    figure [Figure]: Use this to obtain plot elements.
    """

    def __init__(self, dpi: int,
                 figsize: Tuple[int], animation_interval: int) -> None:
        """
        Initializer
        """
        self.dots_per_inches = dpi
        self.animation_interval = animation_interval

        self.figure = plt.figure(
                figsize=figsize,
                dpi=self.dots_per_inches
        )
        self.main_animation = None

        # All private attributes.
        self._plots = []
        self._delta_t = 1.0/60.0
        self._t = perf_counter()

    def add_plot(self, plot: plt.Artist) -> None:
        """
        Add a list of plot objects so that they can be animated.
        """
        self._plots.append(plot)

    def add_plots(self, plot_objects: List[plt.Artist]) -> None:
        """
        Add multiple plots to be animated.
        """
        self._plots.extend(plot_objects)

    def update(self, delta_t: float) -> None:
        """
        Update how each plots will change between each animation frame.
        This must be implemented in any derived classes.
        """
        raise NotImplementedError

    def _make_frame(self, i: int) -> list:
        """
        Generate a single animation frame.
        """
        self.update(self._delta_t)
        t = perf_counter()
        self._delta_t = t - self._t
        self._t = t
        # print(self._plots)
        return self._plots

    def _add_plots(self) -> None:
        """
        Add plots before doing the main animation loop.
        """
        text_objects = []  # Ensure that text boxes are rendered last
        self_dict = self.__dict__
        for key in self_dict:
            if any([isinstance(self_dict[key], artist) for
                    artist in artists]):
                if self_dict[key] not in self._plots:
                    # Ensure that text boxes are rendered last
                    if isinstance(self_dict[key], Text):
                        text_objects.append(self_dict[key])
                    else:
                        self._plots.append(self_dict[key])
        self._plots.extend(text_objects)

    def animation_loop(self) -> None:
        """This method plays the animation. This must be called in order
        for an animation to be shown.
        """
        self._add_plots()
        self.main_animation = animation.FuncAnimation(
                self.figure,
                self._make_frame,
                blit=True,
                interval=self.animation_interval
        )
