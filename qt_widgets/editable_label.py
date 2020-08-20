"""
Editable labels.
"""
from . import QtWidgets, QtCore, QtGui
from .labelled_line_edit import LabelWithLineEdit


class EditableLabel(QtWidgets.QStackedWidget):
    """
    An editable label. This is a stacked widget where
    by default only the label widget is visible.
    When the user clicks on the label the LabelWithLineEdit
    widget is shown instead, which consists of a
    label and line edit.
    """
    def __init__(self, label: str = "",
                 parent: "HorizontalSliderBox" = None) -> None:
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
                self._parent.set_value(value)
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
                    self._parent.set_value(value)
            else:
                self._line_edit.get_line_edit().setFocus(
                    QtCore.Qt.MouseFocusReason)
