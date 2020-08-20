"""
Slider widgets.
"""
from . import QtWidgets, QtCore, QtGui
from .labelled_line_edit import LabelWithLineEdit
from .editable_label import EditableLabel
from typing import Any, List


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

    def get_range(self) -> List[float]:
        """
        Get the range of the slider.

        Returns:
         A list containing the
         minimum and maximum value of the slider.
        """
        return self._lim

    def _transform(self, slider_val: int) -> float:
        """
        Transform rules for the slider.
        """
        lim = self._lim
        slider_val = slider_val - self.minimum()
        m = (lim[1] - lim[0])/(self.maximum() - self.minimum())
        return m*slider_val + lim[0]

    def set_value(self, value: float) -> None:
        """
        Set a value for the slider.

        Parameters:
         value: the value to set the slider to.
        """
        lim = self._lim
        value = value - lim[0]
        m = (self.maximum() - self.minimum())/(lim[1] - lim[0])
        slider_float_value = m*value + self.minimum()
        slider_value = int(slider_float_value)
        if slider_float_value - slider_value > 0.5:
            slider_value += 1
        self.setSliderPosition(slider_value)

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

    def get_value(self) -> float:
        """
        Get the value of the slider.

        Returns:
         the value of the slider.
        """
        return self._transform(self.value())

    def get_slider_info(self) -> dict:
        """
        Get information about the slider.

        Returns:
         A dictionary containing information about the slider.
        """
        val = self._transform(self.value())
        return {'value': val, 'id': self._slider_id}


class SliderBoxRangeControls(QtWidgets.QFrame):
    """
    A range control widget for the
    HorizontalSliderBox class.
    """

    def __init__(self, slider_lim: List[int],
                 number_of_ticks: int,
                 parent: "HorizontalSliderBox" = None) -> None:
        """
        Constructor.

        Parameters:
         slider_lim: list containing the
         initial minimum and maximum values of the slider
         number_of_ticks: number of ticks of the slider.
         parent: the parent HorizontalSliderBox widget.
        """
        QtWidgets.QFrame.__init__(self, parent)
        self._parent = parent
        layout = QtWidgets.QVBoxLayout(self)
        self._layout = layout
        self.setLayout(layout)
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        min_label = "min: "
        max_label = "max: "
        ticks_label = "number of ticks: "
        min_label_line_edit = LabelWithLineEdit(min_label, self)
        # min_label_line_edit.setFocusPolicy(QtCore.Qt.NoFocus)
        min_label_line_edit.set_line_edit(str(slider_lim[0]))
        max_label_line_edit = LabelWithLineEdit(max_label, self)
        # max_label_line_edit.setFocusPolicy(QtCore.Qt.NoFocus)
        max_label_line_edit.set_line_edit(str(slider_lim[1]))
        tick_label_line_edit = LabelWithLineEdit(ticks_label, self)
        # tick_label_line_edit.setFocusPolicy(QtCore.Qt.NoFocus)
        tick_label_line_edit.set_line_edit(str(number_of_ticks))
        layout.addWidget(min_label_line_edit)
        layout.addWidget(max_label_line_edit)
        layout.addWidget(tick_label_line_edit)
        button = QtWidgets.QPushButton("Close")
        if parent is not None:
            button.clicked.connect(parent.close_range_controls)
        layout.addWidget(button)
        # self.setMinimumHeight(parent.height() if parent 
        #                       is not None else 100)
        if parent is not None:
            parent.setMinimumHeight(2*parent.height() + self.height())

    def line_edit_returned(self, *args: Any) -> None:
        """
        Perform an action when the line edit is returned.
        """
        # TODO Need to improve this.
        min_val = float(self._layout.itemAt(0).widget().text())
        max_val = float(self._layout.itemAt(1).widget().text())
        tick_val = int(self._layout.itemAt(2).widget().text())
        if min_val >= max_val or tick_val <= 1 or tick_val > 65535:
            return
        if self._parent is not None:
            value = self._parent.get_value()
            self._parent.set_number_of_ticks(tick_val)
            self._parent.set_range(min_val, max_val)
            if value > max_val:
                value = max_val
            if value < min_val:
                value = min_val
            m = (tick_val - 1)/(max_val - min_val)
            slider = self._parent.get_slider()
            slider_info = self._parent.get_slider_info()
            tick_float_value = m*(value - min_val)
            if (tick_float_value % 1.0) >= 0.5:
                tick_float_value += (1.0 - 
                                     tick_float_value % 1.0)
            tick_value = int(tick_float_value + slider.minimum())
            value = (tick_value - slider.minimum())/m + min_val 
            slider.setValue(tick_value)
            slider_info['value'] = value
            self._parent.on_slider_changed(slider_info)


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
        # QtWidgets.QFrame.__init__(self)
        # self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setMinimumWidth(250)
        self.setMaximumWidth(300)
        self.setMaximumHeight(100)
        self._enable_range_controls = True
        self._range_controls = None
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

    def get_slider(self) -> Slider:
        """
        Getter for the slider.

        Returns:
         the slider.
        """
        return self._slider

    def set_value(self, value: float) -> None:
        """
        Set a value for the slider.

        Parameters:
         value: the value to set the slider to.
        """
        self._slider.set_value(value)

    def get_value(self) -> float:
        """
        Get the slider value.

        Returns:
         the slider value.
        """
        return self._slider.get_value()

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
        self._string_format = self._varname_equals_string + ' ' + string_format

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

    def mousePressEvent(self, qt_event: QtGui.QMouseEvent) -> None:
        """
        Respond to a mouse press event.

        Parameters:
         qt_event: the mouse event.
        """
        if (self._enable_range_controls and
            qt_event.buttons() == QtCore.Qt.RightButton
                and not self._range_controls):
            pass
            self._show_range_controls = True
            q = QtWidgets.QMenu("menu", self)
            q.addAction("Set range", self.build_range_controls)
            q.exec_(QtCore.QPoint(QtGui.QCursor.pos()))

    def toggle_range_controls(self) -> None:
        """
        Toggle the range controls.
        """
        self._enable_range_controls = \
            not self._enable_range_controls

    def build_range_controls(self, *arg: Any) -> None:
        """
        Build the range control widgets.
        """
        self.setMaximumHeight(220)
        slider_lim = self._slider.get_range()
        n_ticks = self._slider.maximum() \
            - self._slider.minimum() + 1
        self._range_controls = \
            SliderBoxRangeControls(slider_lim, n_ticks, self)
        self._layout.addWidget(self._range_controls)

    def close_range_controls(self) -> None:
        """
        Close the range control widgets.
        """
        self.setMinimumHeight(0)
        self.setMaximumHeight(100)
        self._range_controls.line_edit_returned()
        self._range_controls.close()
        self._range_controls = None
