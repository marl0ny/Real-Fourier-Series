"""
Entry box that contains a QtLabel and a QtLineEdit
"""
from . import QtWidgets


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
