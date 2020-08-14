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

    def add_observers(self, slider_observer: QtWidgets.QWidget) -> None:
        """
        Add a slider observer.

        Parameters:
         slider_observer: an observer.
        """
        self._observers.append(slider_observer)

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


class LabelWithLineEdit(QtWidgets.QWidget):
    """
    Label with line edit next to it.
    """
    def __init__(self, label: str = "", 
                 parent: QtWidgets.QWidget = None) -> None:
        """
        Constructor

        Parameters:
         label: set the label for this widget
         parent: the parent of this widget
        """
        QtWidgets.QWidget.__init__(self)
        if not parent:
            parent = self
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setMargin(0)
        self._label = QtWidgets.QLabel(label)
        self._line_edit = QtWidgets.QLineEdit()
        self._line_edit.returnPressed.connect(parent.line_edit_returned)
        self.layout.addWidget(self._label)
        self.layout.addWidget(self._line_edit)

    def set_line_edit_label(self, text: str) -> None:
        """
        When the text on this widget is being edited,
        set the label for the line edit.

        Parameters:
         text: the text to set the line edit label.
        """
        self._label.setText(text)

    def set_line_edit(self, text: str) -> None:
        """
        Set the text shown on the line edit.

        Parameters:
         text: the text for the line edit itself.
        """
        self._line_edit.setText(text)

    def text(self) -> str:
        """
        Getter for the text label.
        
        Returns:
         text label.
        """
        return self._line_edit.text()


class EditableLabel(QtWidgets.QStackedWidget):
    """
    An editable label.
    """
    def __init__(self, label: str = "", 
                 parent: QtWidgets.QWidget = None) -> None:
        """
        Constructor

        Parameters:
         label: set the label for this widget
         parent: the parent of this widget
        """
        QtWidgets.QStackedWidget.__init__(self)
        self._parent = parent
        self._label = QtWidgets.QLabel(label)
        self._line_edit = LabelWithLineEdit(parent=self)
        self.addWidget(self._label)
        self.addWidget(self._line_edit)

    def setText(self, text: str) -> None:
        """
        Set the text of the label when the widget
        is not being edited.

        Parameters:
         text: the text on the label.
        """
        self._label.setText(text)

    def set_line_edit_label(self, text: str) -> None:
        """
        When the text on this widget is being edited,
        set the label for the line edit.

        Parameters:
         text: the text to set the line edit label.
        """
        self._line_edit.set_line_edit_label(text)

    def set_line_edit(self, text: str) -> None:
        """
        Set the text shown on the line edit.

        Parameters:
         text: the text for the line edit itself.
        """
        self._line_edit.set_line_edit(text)

    def line_edit_returned(self) -> None:
        """
        When the return key is pressed on the line edit
        enter the value to the slider and only display the label.
        """
        # if self.currentIndex() == 1 and self._parent:
        self.setCurrentIndex(not self.currentIndex())
        self._parent.set_slider(float(self._line_edit.text()))

    def mouseDoubleClickEvent(self, 
                              qt_event: QtGui.QMouseEvent) -> None:
        self.setCurrentIndex(not self.currentIndex())
        if self.currentIndex() == 0 and self._parent:
            self._parent.set_slider(float(self._line_edit.text()))


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
        self._varname_equals_string = "%s ="
        self._string_format = self._varname_equals_string + " %.2f"
        self._number_format = "%.2f"
        self._layout = QtWidgets.QVBoxLayout()
        self._label = EditableLabel("Set " + str(slider_id), parent=self)
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
        self._number_format = string_format
        self._string_format = self._varname_equals_string + \
                              ' ' + string_format

    def on_slider_changed(self, slider_input: dict) -> None:
        """
        Respond to changes in the slider.

        Parameters:
         slider_input: the changes from the slider.
        """
        val = slider_input['value']
        slider_id = slider_input['id']
        self._label.set_line_edit_label(self._varname_equals_string
                                        % slider_id)
        self._label.setCurrentIndex(0)
        self._label.set_line_edit(self._number_format % val)
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
