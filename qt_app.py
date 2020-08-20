import sys
from qt_widgets import QtWidgets, QtCore, QtGui
from qt_widgets import HorizontalSliderBox, HorizontalEntryBox
from qt_widgets import VariableSlidersManager
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from animation import FourierAnimation
from typing import Union


class Canvas(FigureCanvasQTAgg):
    """
    The canvas.
    """

    def __init__(self,
                 parent: QtWidgets.QMainWindow,
                 rect: QtCore.QRect) -> None:
        """
        The constructor.

        Parameters:
         parent: The parent widget that this
         canvas is being created from
         rect: used to get information
         about the screen width and screen height.
        """
        width = rect.width()
        dpi = int(150*width//1920)
        self._parent = parent
        self._ani = FourierAnimation("3*rect(t)/2", dpi)
        self._ani.set_speed(1)
        FigureCanvasQTAgg.__init__(self, self._ani.figure)
        self.setMinimumHeight(400)
        self.setMinimumWidth(int(width*0.75))
        self._mouse_usage = 0
        self._prev_mouse_position = []

    def get_animation(self):
        """
        Getter for the animation object.

        Returns:
         The animation object.
        """
        return self._ani

    def animation_loop(self) -> None:
        """
        Do the main animation loop.
        """
        self._ani.animation_loop()


class App(QtWidgets.QMainWindow):
    """
    Main qt5 app.
    """

    def __init__(self) -> None:
        """
        Initializer.
        """
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle("A simple GUI")
        self.menu_bar = self.menuBar()
        file_menu = self.menu_bar.addMenu('&file')
        file_menu.addAction("Save figure",
                            lambda: self.canvas.get_animation(
                            ).figure.savefig("figure.png"))
        file_menu.addAction("Quit",
                            lambda: QtWidgets.QApplication.exit())
        self.help = self.menu_bar.addMenu('&help')
        dialogue = QtWidgets.QMessageBox(self)
        # dialogue.aboutQt(self, "Title")
        self.message_box = dialogue
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.help.addAction("instructions", self.show_instructions)
        self.help.addAction("about the GUI", self.show_about_gui)
        # self._scroll_area = None
        # self.sliders = []
        self._setting_sliders = False
        self.variable_sliders = VariableSlidersManager(parent=self)
        self.window = QtWidgets.QWidget(self)
        self.layout = QtWidgets.QHBoxLayout(self.window)
        rect = QtWidgets.QApplication.desktop().screenGeometry()
        self.canvas = Canvas(self, rect)
        color_name = self.window.palette().color(
                QtGui.QPalette.Background).name()
        self.canvas.get_animation().figure.patch.set_facecolor(color_name)
        # self.layout.addWidget(self.menu_bar)
        self.layout.addWidget(self.canvas)
        self.control_widgets = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.control_widgets)
        self._build_control_widgets()
        self.setCentralWidget(self.window)
        self.canvas.animation_loop()

    def _build_control_widgets(self):
        """
        Build the control widgets.
        """
        self.entry = HorizontalEntryBox(
            "Enter waveform f(t)")
        self.dropdown_dict = {
            "sine": "sin(t)",
            "cosine": "cos(t)",
            "gaussian": "3*exp(-t**2/(2*sigma**2 ))/2 - 1/2",
            "sinc": "3*sinc(k*(6.5)*t)/2 - 1/2",
            "rectangle": "3*rect(t)/2",
            "sawtooth": "t/pi",
            "triangle": "abs(t)",
            # "function 1": "a*exp(-rect(k*t)**2)",
            # "wave packet": "sin(4*k*t)*exp(-(t - x)**2/(2*sigma**2))",
            # "sum of cosines": "0" +
            # "".join([" + a_%d*cos(%d*t)" % (i, i) for i in range(1, 8)])
            }
        dropdown_list = ["Preset Waveform f(t)"]
        dropdown_list.extend([key for key in self.dropdown_dict])
        self.dropdown = QtWidgets.QComboBox(self)
        self.dropdown.addItems(dropdown_list)
        if hasattr(self.dropdown, "textActivated"):
            self.dropdown.textActivated.connect(self.on_dropdown_changed)
        else:
            self.dropdown.activated.connect(self.on_dropdown_changed)
        self.entry.set_observers([self])
        self.circles_slider = HorizontalSliderBox(self, "Maximum Frequency")
        self.slider_speed = HorizontalSliderBox(self, "Speed")
        self.circles_slider.set_observers([self])
        self.circles_slider.set_range(1, 80)
        self.circles_slider.set_value_string_format("%d")
        self.circles_slider.set_number_of_ticks(80)
        self.circles_slider.set_value(80)
        self.circles_slider.toggle_range_controls()
        self.slider_speed.set_observers([self])
        self.slider_speed.set_range(-5, 5)
        self.slider_speed.set_value_string_format("%d")
        self.slider_speed.set_number_of_ticks(11)
        self.slider_speed.set_value(1)
        self.slider_speed.toggle_range_controls()
        # self.control_widgets.addWidget(self.mouse_dropdown)
        self.control_widgets.addWidget(self.dropdown)
        self.control_widgets.addWidget(self.entry)
        self.control_widgets.addWidget(self.circles_slider)
        self.control_widgets.addWidget(self.slider_speed)

    def show_instructions(self) -> None:
        """
        Show instructions.
        """
        message = (
            "This app displays the (discrete) Fourier series of "
            "real, periodic, and well-behaved functions "
            "using rotating circles to represent each term. "
            "To visualize the Fourier Series for a different function, "
            "choose one of the preset functions in the "
            "Preset Waveform f(t) dropown menu, "
            "or enter a new function in the Enter waveform f(t) entry box. "
            "The function that you entered must be a function of t. "
            "This function can depend on other variables, where "
            "these variables are changed through sliders. "
            "Change the number of circles displayed by changing the value "
            "of the Maximum Frequency slider. "
            "To change the animation rate, use the Speed slider. "
            "Take a screenshot of the graph by selecting the "
            "file sidebar and clicking Save figure. "
            "To close the app, go to the file sidebar and select Quit."
        )
        self.message_box.about(self, "Instructions", message)

    def show_about_gui(self) -> None:
        """
        Show the about dialog.
        """
        message = (r"The GUI is built using "
                   r"<a href=https://wiki.qt.io/Qt_for_PythonPySide2>"
                   r"PySide2</a>,"
                   r" which is published under the"
                   r" <a href=https://www.gnu.org/licenses/"
                   r"lgpl-3.0.en.html>LGPL</a>."
                   )
        self.message_box.about(self, "About", message)

    def on_dropdown_changed(self, text: Union[int, str]) -> None:
        """
        Perform an action when the dropdown is changed.

        Parameters:
         text: either the index of the dropdown or text
         at the given index of the dropdown.
        """
        if isinstance(text, str):
            if not text == "Preset Waveform f(t)":
                self.set_function_from_text(self.dropdown_dict[text])
        elif isinstance(text, int):
            n = text
            text = self.dropdown.itemText(n)
            if not text == "Preset Waveform f(t)":
                self.set_function_from_text(self.dropdown_dict[text])
        ani = self.canvas.get_animation()
        if text == "gaussian":
            ani.function_display.set_text(r"$f(t; \sigma) = "
                                          r"exp(-t^2/2 \sigma^2)$"
                                          r" ,   $ t = s (mod(2 \pi)) - \pi $"
                                          )
        elif text == "sinc":
            ani.function_display.set_text(r"$f(t; k) = "
                                          r"sinc(kt)$"
                                          r" ,   $ t = s (mod(2 \pi)) - \pi $"
                                          )
        else:
            ani.function_display.set_text(r"$f(t)$"
                                          r" ,   $ t = s (mod(2 \pi)) - \pi $"
                                          )

    def set_function_from_text(self, text: str) -> None:
        """
        Set the function from text.

        Parameters:
         text: function expressed as a string.
        """
        if text.strip() != "":
            function_name = text
            try:
                ani = self.canvas.get_animation()
                ani.set_function(function_name)
            except Exception as e:
                print(e)
                return
            self.destroy_sliders()
            self._setting_sliders = True
            d = ani.function.get_enumerated_default_values()
            self.variable_sliders.set_sliders(
                [self.control_widgets], d)
            self.control_widgets.addWidget(self.circles_slider)
            self.control_widgets.addWidget(self.slider_speed)
            self._setting_sliders = False
            self.on_slider_changed({})

    def on_slider_changed(self, slider_input: dict) -> None:
        """
        When the slider is changed perform some action.

        Parameters:
         slider_input: a dictionary containing information
         about the slider.
        """
        if 'id' in slider_input and isinstance(slider_input['id'], str):
            ani = self.canvas.get_animation()
            if slider_input['id'] == "Speed":
                ani.set_speed(slider_input['value'])
            elif slider_input['id'] == "Maximum Frequency":
                ani.set_number_of_circles(int(slider_input['value'])+1)
        else:
            if not self._setting_sliders:
                params = self.variable_sliders.get_slider_parameters()
                ani = self.canvas.get_animation()
                ani.set_params(*params)

    def destroy_sliders(self) -> None:
        """
        Destroy the sliders.
        """
        self.variable_sliders.destroy_sliders(
            [self.control_widgets, self.layout])
        self.control_widgets.removeWidget(self.circles_slider)
        self.control_widgets.removeWidget(self.slider_speed)

    def on_entry_returned(self, text: str) -> None:
        """
        Perform an action when the enter function is pressed.

        Parameters:
         text: a string from an entry box.
        """
        self.set_function_from_text(text)


if __name__ == "__main__":
    # import matplotlib.pyplot as plt
    qt_app = QtWidgets.QApplication(sys.argv)
    app = App()
    app.show()
    sys.exit(qt_app.exec_())
