"""
User defined widget classes wrapped over the widgets defined
in PySide2.
"""
# import sys
from PySide2 import QtWidgets, QtCore, QtGui
from typing import Any


class Slider(QtWidgets.QSlider):
    """
    Slider class
    """

    def __init__(self, slider_id: Any,
                 orientation: QtCore.Qt.Orientation,
                 context: Any) -> None:
        """
        Constructor.

        Parameters:
         slider_id: slider identification.
         orientation: slider orientation.
         context: the object that is using this slider.
        """
        QtWidgets.QSlider.__init__(self, orientation, context)
        self._slider_id = slider_id
        self._observers = []
        self._lim = [self.minimum(), self.maximum()]
        self.setRange(0, 200)
        self.valueChanged.connect(self.notify_change)

    def set_observers(self, slider_observers: list) -> None:
        """
        Set slider observers.

        Parameters:
         slider_observers: the objects that will observe this slider.
        """
        self._observers = slider_observers

    def set_number_of_ticks(self, number_of_ticks: int) -> None:
        """
        Set the total number of intervals in the slider.

        Parameters:
         number_of_ticks: total number of intervals.
        """
        self.setRange(1, number_of_ticks)

    def set_range(self, min_val: float, max_val: float) -> None:
        """
        Set the range of the slider.

        Parameters:
         min_val: The lowest possible value that the slider can take.
         max_val: The largest possible value that the slider can take.
        """
        self._lim = [min_val, max_val]

    def _transform(self, slider_val: int) -> float:
        """
        Transform rules for the slider.
        """
        lim = self._lim
        slider_val = slider_val - self.minimum()
        m = (lim[1] - lim[0])/(self.maximum() - self.minimum())
        return m*slider_val + lim[0]

    def set_slider(self, value: float) -> None:
        """
        Set a value for the slider.

        Parameters:
         value: the value to set the slider to.
        """
        lim = self._lim
        value = value - lim[0]
        m = (self.maximum() - self.minimum())/(lim[1] - lim[0])
        self.setSliderPosition(int(m*value + self.minimum()))

    def notify_change(self, val: int) -> None:
        """
        Notify to observers that the slider has changed.

        Parameters:
         val: the value that the slider changed to.
        """
        val = self._transform(val)
        for observer in self._observers:
            observer.on_slider_changed({'value': val,
                                       'id': self._slider_id})

    def get_slider_info(self) -> dict:
        """
        Get information about the slider.

        Returns:
         A dictionary containing information about the slider.
        """
        val = self.value()
        val = self._transform(val)
        return {'value': val, 'id': self._slider_id}


class HorizontalSliderBox(QtWidgets.QGroupBox):
    """
    GUI Box containing a slider as well as some other widgets.
    """
    def __init__(self, context: Any,
                 slider_id: Any) -> None:
        """
        Constructor.

        Parameters:
         context: the object that is using the widget.
         slider_id: the id of the slider.
        """
        QtWidgets.QGroupBox.__init__(self)
        self.setMinimumWidth(250)
        self.setMaximumWidth(300)
        self.setMaximumHeight(100)
        self._string_format = "%s = %.2f"
        self._layout = QtWidgets.QVBoxLayout()
        self._label = QtWidgets.QLabel("Set " + str(slider_id))
        self._slider = Slider(slider_id,
                              QtCore.Qt.Horizontal,
                              context)
        self._layout.addWidget(self._label)
        self._layout.addWidget(self._slider)
        self.setLayout(self._layout)

    def set_range(self, min_val: float, max_val: float) -> None:
        """
        Set the range of the slider.

        Parameters:
         min_val: The lowest possible value that the slider can take.
         max_val: The largest possible value that the slider can take.
        """
        self._slider.set_range(min_val, max_val)

    def set_number_of_ticks(self, number_of_ticks: int) -> None:
        """
        Set the total number of intervals in the slider.

        Parameters:
         number_of_ticks: total number of intervals.
         """
        self._slider.setRange(0, number_of_ticks - 1)

    def set_slider(self, value: float) -> None:
        """
        Set a value for the slider.

        Parameters:
         value: the value to set the slider to.
        """
        self._slider.set_slider(value)

    def set_observers(self,
                      slider_observers: list) -> None:
        """
        Set slider observers.

        Parameters:
         slider_observers: the objects that will observe the slider.
        """
        slider_observers.append(self)
        self._slider.set_observers(slider_observers)

    def set_value_string_format(self, string_format: str) -> None:
        """
        Set the value string format.

        Parameters:
         string format: the string format to display the value
         of the slider.
        """
        self._string_format = "%s = " + string_format

    def on_slider_changed(self, slider_input: dict) -> None:
        """
        Respond to changes in the slider.

        Parameters:
         slider_input: the changes from the slider.
        """
        val = slider_input['value']
        slider_id = slider_input['id']
        self._label.setText(self._string_format % (slider_id, val))

    def destroy_slider(self) -> None:
        """
        Destroy the slider.
        """
        self._layout.removeWidget(self._slider)
        self._slider.destroy()
        self._slider.close()
        self.close()

    def get_slider_info(self) -> dict:
        """
        Get information about the slider.

        Returns:
         A dictionary containing information about the slider.
        """
        return self._slider.get_slider_info()


class HorizontalEntryBox(QtWidgets.QGroupBox):
    """
    GUI Box that contains an label and text input widget.
    """

    def __init__(self, label_name: str) -> None:
        """
        Constructor.

        Parameters:
         label_name: the label for the entry widget.
        """
        QtWidgets.QGroupBox.__init__(self)
        self.setMinimumWidth(250)
        self.setMaximumWidth(300)
        self.setMaximumHeight(125)
        self._observers = []
        self._label = QtWidgets.QLabel(label_name)
        self._layout = QtWidgets.QVBoxLayout()
        self._input = QtWidgets.QLineEdit()
        self._input.returnPressed.connect(self.notify_change)
        self._button = QtWidgets.QPushButton("OK")
        self._button.clicked.connect(self.notify_change)
        self._layout.addWidget(self._label)
        self._layout.addWidget(self._input)
        self._layout.addWidget(self._button)
        self.setLayout(self._layout)

    def set_observers(self, observers: list) -> None:
        """
        Set the observers for the line edit widget.

        Parameters:
         observers: The observers of the widget.
        """
        self._observers = observers

    def notify_change(self) -> None:
        """
        Notify to the observers that the line edit has changed
        """
        for observer in self._observers:
            observer.on_entry_returned(
                self._input.text())
