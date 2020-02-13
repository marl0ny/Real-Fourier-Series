"""
The main application
"""
from animation import FourierAnimation, VariableNotFoundError
from matplotlib.backends import backend_tkagg
import tkinter as tk


class App(FourierAnimation):
    """
    App class
    """
    def __init__(self) -> None:
        """
        The constructor.
        """
        self.window = tk.Tk()
        self.window.title("Visualization of Fourier Series")
        width = self.window.winfo_screenwidth()
        dpi = int(150*width//1920)
        FourierAnimation.__init__(self, "3*rect(t)/2", dpi)

        # Thanks to StackOverflow user rudivonstaden for
        # giving a way to get the colour of the tkinter widgets:
        # https://stackoverflow.com/questions/11340765/
        # default-window-colour-tkinter-and-hex-colour-codes
        #
        #     https://stackoverflow.com/q/11340765
        #     [Question by user user2063:
        #      https://stackoverflow.com/users/982297/user2063]
        #
        #     https://stackoverflow.com/a/11342481
        #     [Answer by user rudivonstaden:
        #      https://stackoverflow.com/users/1453643/rudivonstaden]
        #
        colour = self.window.cget('bg')
        if colour == 'SystemButtonFace':
            colour = "#F0F0F0"
        # Thanks to StackOverflow user user1764386 for
        # giving a way to change the background colour of a plot.
        #
        #    https://stackoverflow.com/q/14088687
        #    [Question by user user1764386:
        #     https://stackoverflow.com/users/1764386/user1764386]
        #
        self.figure.patch.set_facecolor(colour)

        self.canvas = backend_tkagg.FigureCanvasTkAgg(
            self.figure,
            master=self.window
            )
        self.canvas.get_tk_widget().grid(
                row=1, column=0, rowspan=8, columnspan=3)
        self.function_dropdown_dict = {
            "sine": "sin(t)",
            "cosine": "cos(t)",
            "gaussian": "3*exp(-t**2/(2*sigma**2 ))/2 - 1/2",
            "sinc": "3*sinc(k*(6.5)*t)/2 - 1/2",
            "rectangle": "3*rect(t)/2",
            "sawtooth": "t/pi",
            "triangle": "abs(t)"
            }
        self.function_dropdown_string = tk.StringVar(self.window)
        self.function_dropdown_string.set("Preset Waveform f(t)")
        self.function_dropdown = tk.OptionMenu(
            self.window,
            self.function_dropdown_string,
            *tuple(key for key in self.function_dropdown_dict),
            command=self.set_function_dropdown
            )
        self.function_dropdown.grid(
                row=2, column=3, padx=(10, 10), pady=(0, 0))

        self.enter_function_label = tk.Label(
                self.window,
                text="Enter waveform f(t)",
                )
        self.enter_function_label.grid(row=3, column=3,
                                       sticky=tk.S + tk.E + tk.W,
                                       padx=(10, 10),
                                       pady=(0, 0))
        self.enter_function = tk.Entry(self.window)
        self.enter_function.grid(row=4, column=3,
                                 sticky=tk.N + tk.E + tk.W + tk.S,
                                 padx=(10, 10))
        self.enter_function.bind("<Return>", self.set_function_entry)
        self.update_button = tk.Button(self.window, text='OK',
                                       command=self.set_function_entry)
        self.update_button.grid(row=5, column=3,
                                sticky=tk.N + tk.E + tk.W,
                                padx=(10, 10),
                                pady=(0, 0)
                                )
        self.sliderslist = []
        self.circles_slider = None
        self.slider_speed = None
        self._speed = 1
        self.quit_button = None
        self._number_of_circles = 128
        self._set_widgets_after_param_sliders()

    def _set_widgets_after_param_sliders(self, k: int = 5) -> None:
        """
        Set widgets after parameter sliders
        """
        self.circles_slider = tk.Scale(self.window, from_=1, to=128,
                                       label="Maximum Frequency: ",
                                       orient=tk.HORIZONTAL,
                                       # length=128,
                                       command=self.set_number_of_circles)
        self.circles_slider.grid(row=k+1, column=3,
                                 sticky=tk.N + tk.E + tk.W,
                                 padx=(10, 10))
        self.circles_slider.set(self._number_of_circles)
        self.slider_speed = tk.Scale(self.window, from_=-9, to=8,
                                     label="Animation Speed: ",
                                     orient=tk.HORIZONTAL,
                                     length=200,
                                     command=self.set_animation_speed)
        self.slider_speed.grid(row=k+2, column=3,
                               sticky=tk.N + tk.E + tk.W,
                               padx=(10, 10))
        self.slider_speed.set(self._speed)
        self.quit_button = tk.Button(
                self.window, text='QUIT',
                command=lambda *args: [
                        self.window.quit(), self.window.destroy()]
                    )
        self.quit_button.grid(row=k+3, column=3, pady=(0, 0))

    def set_animation_speed(self, *arg: tk.Event):
        """
        Set the speed of the animation.
        """
        j = self.slider_speed.get()
        self._speed = j
        self.set_speed(j)

    def set_function_entry(self, *event: tk.Event):
        """
        Update the function using the text entry.
        """
        try:
            self.set_function(self.enter_function.get())
            self.set_widgets()
        except VariableNotFoundError:
            print("Input not recognized.\nInput function must:\n"
                  "- depend on at least t\n"
                  "- be a recognized function\n"
                  "- use '**' instead of '^' for powers\n")

    def set_function_dropdown(self, *event: tk.Event) -> None:
        """
        Update the function by the dropdown menu.
        """
        event = event[0]
        self.set_function(self.function_dropdown_dict[event])
        if event == "gaussian":
            self.function_display.set_text(r"$f(t; \sigma) = "
                                           r"exp(-t^2/2 \sigma^2)$"
                                           r" ,   $ t = s (mod(2 \pi)) - \pi $"
                                           )
        elif event == "sinc":
            self.function_display.set_text(r"$f(t; k) = "
                                           r"sinc(kt)$"
                                           r" ,   $ t = s (mod(2 \pi)) - \pi $"
                                           )
        else:
            self.function_display.set_text(r"$f(t)$"
                                           r" ,   $ t = s (mod(2 \pi)) - \pi $"
                                           )
        self.set_widgets()

    def set_number_of_circles(self, *event: tk.Event) -> None:
        """
        Set the number of circles.
        """
        resolution = self.circles_slider.get()
        self._number_of_circles = resolution
        FourierAnimation.set_number_of_circles(self, resolution+1)

    def slider_update(self, *event: tk.Event) -> None:
        """
        Update the parameters using the sliders.
        """
        params = []
        for i in range(len(self.sliderslist)):
            params.append(self.sliderslist[i].get())
        self.set_params(*params)

    def set_widgets(self) -> None:
        """
        Set the widgets
        """
        rnge = 10.0
        for slider in self.sliderslist:
            slider.destroy()
        self.sliderslist = []
        self.circles_slider.destroy()
        self.slider_speed.destroy()
        self.quit_button.destroy()
        default_vals = self.function.get_default_values()
        k = 0
        for i, symbol in enumerate(self.function.parameters):
            self.sliderslist.append(tk.Scale(self.window,
                                             label="change "
                                             + str(symbol) + ":",
                                             from_=-rnge, to=rnge,
                                             resolution=0.01,
                                             orient=tk.HORIZONTAL,
                                             length=200,
                                             command=self.slider_update))
            self.sliderslist[i].grid(row=i + 6, column=3,
                                     sticky=tk.N + tk.E + tk.W,
                                     padx=(10, 10), pady=(0, 0))
            self.sliderslist[i].set(default_vals[symbol])
            k += 1
        self._set_widgets_after_param_sliders(k+5)


if __name__ == "__main__":
    app = App()
    app.animation_loop()
    tk.mainloop()
