"""
Line edit with label.
"""
from . import QtWidgets, QtCore, QtGui


class LineEdit(QtWidgets.QLineEdit):
    """
    Line Edit that is used by the LabelWithLineEdit class.
    """
    def __init__(self, parent: "LabelWithLineEdit" = None) -> None:
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
                 "SliderBoxRangeControls]" = None) -> None:
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
