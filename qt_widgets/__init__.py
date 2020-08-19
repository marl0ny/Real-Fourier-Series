"""
User defined widget classes wrapped over the widgets defined
in PySide2.
"""
from PySide2 import QtWidgets, QtCore, QtGui
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


class LineEdit(QtWidgets.QLineEdit):
    """
    Line Edit class.
    """
    def __init__(self, parent: QtWidgets.QWidget = None) -> None:
        """
        Constructor.

        Parameters:
         parent: the parent of this widget.
        """
        self._parent = parent
        QtWidgets.QLineEdit.__init__(self, parent=parent)

    def focusOutEvent(self, q_event: QtGui.QFocusEvent) -> None:
        """
        Focus out event handler.

        Parameters:
         q_event: the focus event.
        """
        self._parent.line_edit_focus_out(q_event)


class LabelWithLineEdit(QtWidgets.QWidget):
    """
    Label with line edit next to it.
    """
    def __init__(self, label: str = "", 
                 parent: "Union[EditableLabel, "
                 "SliderRangeControls]" = None) -> None:
        """
        Constructor

        Parameters:
         label: set the label for this widget
         parent: the parent of this widget
        """
        QtWidgets.QWidget.__init__(self)
        self._parent = parent
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        self._label = QtWidgets.QLabel(label)
        self._line_edit = LineEdit(parent=self)
        self._line_edit.setFocusPolicy(QtCore.Qt.ClickFocus)
        self._line_edit.returnPressed.connect(self._parent.line_edit_returned)
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

    def get_line_edit(self) -> QtWidgets.QLineEdit:
        """
        Getter for the line edit.

        Returns:
         the line edit
        """
        return self._line_edit

    def text(self) -> str:
        """
        Getter for the text label.
        
        Returns:
         text label.
        """
        return self._line_edit.text()

    def line_edit_focus_out(self,
                            qt_event: QtGui.QFocusEvent) -> None:
        """
        Perform an action when the line edit is
        focused out.

        Parameters:
         qt_event: the focus event.
        """
        if self._parent is not None:
            self._parent.line_edit_returned()


class EditableLabel(QtWidgets.QStackedWidget):
    """
    An editable label. This is a stacked widget where
    by default only the label widget is visible. 
    When the user clicks on the label the LabelWithLineEdit 
    widget is shown instead, which consists of a
    label and line edit.
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
        self._line_edit = LabelWithLineEdit("", self)
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
        try:
            value = float(self._line_edit.text())
            if value != self._parent.get_value():
                self._parent.set_slider(value)
        except ValueError as e:
            print(e)

    def mouseDoubleClickEvent(self, 
                              qt_event: QtGui.QMouseEvent) -> None:
        """
        Perform an action on a click event.

        Parameters:
         qt_event: the mouse event.
        """
        self.setCurrentIndex(not self.currentIndex())
        if self._parent:
            if self.currentIndex() == 0:
                value = float(self._line_edit.text())
                if value != self._parent.get_value():
                    self._parent.set_slider(value)
            else:
                self._line_edit.get_line_edit().setFocus(
                    QtCore.Qt.MouseFocusReason)


class SliderRangeControls(QtWidgets.QFrame):
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
        min_label_line_edit.setFocusPolicy(QtCore.Qt.NoFocus)
        min_label_line_edit.set_line_edit(str(slider_lim[0]))
        max_label_line_edit = LabelWithLineEdit(max_label, self)
        max_label_line_edit.setFocusPolicy(QtCore.Qt.NoFocus)
        max_label_line_edit.set_line_edit(str(slider_lim[1]))
        tick_label_line_edit = LabelWithLineEdit(ticks_label, self)
        tick_label_line_edit.setFocusPolicy(QtCore.Qt.NoFocus)
        tick_label_line_edit.set_line_edit(str(number_of_ticks))
        layout.addWidget(min_label_line_edit)
        layout.addWidget(max_label_line_edit)
        layout.addWidget(tick_label_line_edit)
        button = QtWidgets.QPushButton("Close")
        if parent is not None:
            button.clicked.connect(parent.close_range_controls)
        layout.addWidget(button)

    def line_edit_returned(self, *args: Any) -> None:
        """
        Perform an action when the line edit is returned.
        """
        # TODO Need to improve this.
        min_val = float(self._layout.itemAt(0).widget().text())
        max_val = float(self._layout.itemAt(1).widget().text())
        tick_val = int(self._layout.itemAt(2).widget().text())
        if min_val >= max_val or tick_val <= 1:
            return
        if self._parent is not None:
            value = self._parent.get_value()
            self._parent.set_number_of_ticks(tick_val)
            self._parent.set_range(min_val, max_val)
            slider_info = self._parent.get_slider_info()
            if value > max_val:
                value = max_val
            if value < min_val:
                value = min_val
            else:
                intval = (max_val - min_val)/(tick_val - 1)
                rem = (value - min_val) % intval
                if rem >= intval/2.0:
                    value += intval - rem
                # else:
                #     value -= rem
            print(value - min_val, rem, intval, (value - min_val)/intval)
            slider_info['value'] = value
            self._parent.set_slider(float(slider_info['value']))
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

    def set_slider(self, value: float) -> None:
        """
        Set a value for the slider.

        Parameters:
         value: the value to set the slider to.
        """
        self._slider.set_slider(value)

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
            # self._show_range_controls = True
            # q = QtWidgets.QMenu("menu", self)
            # q.addAction("Set range", self.build_range_controls)
            # q.exec_(QtCore.QPoint(QtGui.QCursor.pos()))

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
            SliderRangeControls(slider_lim, n_ticks, self)
        self._layout.addWidget(self._range_controls)

    def close_range_controls(self) -> None:
        """
        Close the range control widgets.
        """
        self.setMaximumHeight(100)
        self._range_controls.line_edit_returned()
        self._range_controls.close()
        self._range_controls = None


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
                slider_box.set_slider(value)
                self._sliders.append(slider_box)
            self._scroll_area = QtWidgets.QScrollArea()
            height = sum([self._sliders[i].height() for i in range(2)])
            width = self._sliders[k].width()
            self._scroll_area.setMinimumHeight(height)
            self._scroll_area.setMinimumWidth(width)
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
                slider_box.set_slider(value)
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
        # self.setFrameShape(QtWidgets.QFrame.StyledPanel)
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
