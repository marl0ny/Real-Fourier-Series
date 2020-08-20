"""
Manager class for the sliders.
"""
from . import QtWidgets, QtCore, QtGui
from .slider import HorizontalSliderBox
from typing import List, Any


class VariableSlidersManager:
    """
    Manager for dynamic sliders that are created from
    the function text input.
    """
    def __init__(self,
                 parent: QtWidgets.QWidget = None) -> None:
        """
        Constructor.

        Parameters:
         parent: the parent widget.
        """
        self._parent = parent
        self._scroll_area = None
        self._sliders = []

    def set_sliders(self,
                    layouts: List[QtWidgets.QLayout],
                    sliders_info: dict, slider_min_val: float = -10.0,
                    slider_max_val: float = 10.0,
                    number_of_ticks: int = 2001) -> None:
        """
        Create and display the variable sliders. Requires
        a layout as input to put the sliders in.

        Parameters:
         layout: the layouts to place the sliders in.
         slider_info: a dict that dictates the properties for each
         of the sliders.
         slider_min_val: the minimum value of the sliders.
         slider_max_val: the maximum value of the sliders.
         number_of_ticks: the number of ticks for the sliders.
        """
        #BUG - removed (kind of)
        # Originally this function was intended to also accept an argument
        # that contained a list of observers for the slider.
        # This didn't work, because doing this caused all the sliders
        # to have the same appearance (the same name and value),
        # but otherwise each slider outputted their intended values
        # (no idea what caused this behaviour).
        # For now the only observers added is the _parent attribute.
        d = sliders_info
        if len(d) > 4:
            slider_container = QtWidgets.QVBoxLayout()
            widget_slider_container = QtWidgets.QWidget(parent=self._parent)
            widget_slider_container.setLayout(slider_container)
            for k in range(len(d)):
                symbol = d[k][0]
                value = d[k][1]
                slider_box = HorizontalSliderBox(self._parent, symbol)
                slider_container.addWidget(slider_box)
                slider_box.set_range(slider_min_val, slider_max_val)
                slider_box.set_number_of_ticks(number_of_ticks)
                slider_box.set_observers([self._parent])
                slider_box.set_value(value)
                self._sliders.append(slider_box)
            self._scroll_area = QtWidgets.QScrollArea()
            height = sum([self._sliders[i].height() for i in range(2)])
            width = self._sliders[k].width()
            self._scroll_area.setMinimumHeight(height)
            self._scroll_area.setMaximumHeight(height*2)
            self._scroll_area.setMinimumWidth(width)
            slider_container.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
            self._scroll_area.setWidget(widget_slider_container)
            for layout in layouts:
                layout.addWidget(self._scroll_area)
        else:
            for k in range(len(d)):
                symbol = d[k][0]
                value = d[k][1]
                slider_box = HorizontalSliderBox(None, symbol)
                for j in range(len(layouts)):
                    layouts[j].addWidget(slider_box)
                slider_box.set_range(slider_min_val, slider_max_val)
                slider_box.set_number_of_ticks(number_of_ticks)
                slider_box.set_observers([self._parent])
                slider_box.set_value(value)
                self._sliders.append(slider_box)

    def get_slider_parameters(self) -> List[Any]:
        """
        Get the parameters of the sliders.

        Returns:
         the parameters of the sliders.
        """
        params = []
        for slider in self._sliders:
            info = slider.get_slider_info()
            params.append(info['value'])
        return params

    def destroy_sliders(self, layouts: List[QtWidgets.QLayout]) -> None:
        """
        Destroy the sliders. Requires the layout object where the
        sliders originally appeared.

        Parameters:
         the layouts for which to remove the sliders from.
        """
        if self._scroll_area:
            while self._sliders:
                slider_box = self._sliders.pop()
                slider_box.destroy_slider()
                slider_box.close()
            for layout in layouts:
                layout.removeWidget(self._scroll_area)
            # TODO: Need to check that everything in the scroll
            # area is actually cleaned up and that nothing is leaked.
            self._scroll_area.close()
            self._scroll_area = None
        else:
            while self._sliders:
                slider_box = self._sliders.pop()
                for layout in layouts:
                    layout.removeWidget(slider_box)
                slider_box.destroy_slider()
                slider_box.close()
