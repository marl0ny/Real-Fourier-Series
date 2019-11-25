"""
Main file.
"""
from matplotlib.backends import backend_tkagg
from animate import FourierSeriesAnimation
import tkinter as tk


class App:
    """
    App class.
    """

    def __init__(self) -> None:
        """
        Initializer.
        """

        self.window = tk.Tk()
        self.window.title("Visualization of Fourier Series")
        self.window.configure(background='white')

        # Set plot resolution
        width = self.window.winfo_screenwidth()
        dpi = int(150*width//1920)

        self.painting = FourierSeriesAnimation("sin(t)", dpi=dpi)

        string = r"(5/2)*("
        for i in range(1, 40, 2):
            string += "+sin(t*"+str(i)+")/(pi*" + str(i) + ")"
        string += ")"
        self.painting.update(string)

        self.canvas = backend_tkagg.FigureCanvasTkAgg(
                self.painting.figure, master=self.window)

        self.canvas.get_tk_widget().grid(
                row=1, column=0, rowspan=8, columnspan=3)

        self.function_dropdown_dict = {
            "sine": "sin(t)",
            "cosine": "cos(t)",
            "gaussian": "3*exp(-t**2)/2-1/2",
            "sinc": "3*sinc((6.5)*t)/2",
            "rectangle": string,
            "sawtooth": "t",
            "triangle": "abs(t)"
            }
        self.function_dropdown_string = tk.StringVar(self.window)
        self.function_dropdown_string.set("Preset Waveform f(t)")
        self.function_dropdown = tk.OptionMenu(
            self.window,
            self.function_dropdown_string,
            *tuple(key for key in self.function_dropdown_dict),
            command=self.update_by_dropdown
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
        self.enter_function.bind("<Return>", self.update)
        self.update_button = tk.Button(self.window, text='OK',
                                       command=self.update)
        self.update_button.grid(row=5, column=3,
                                sticky=tk.N + tk.E + tk.W,
                                padx=(10, 10),
                                pady=(0, 0)
                                )

        self.slider_speed_label = tk.Label(self.window, text="Animation Speed")
        self.slider_speed_label.grid(row=6, column=3,
                                     sticky=tk.S + tk.E + tk.W,
                                     padx=(10, 10))

        self.slider_speed = tk.Scale(self.window, from_=-9, to=8,
                                     orient=tk.HORIZONTAL,
                                     length=200,
                                     command=self.change_animation_speed)
        self.slider_speed.grid(row=7, column=3,
                               sticky=tk.N + tk.E + tk.W,
                               padx=(10, 10))

        self.slider_speed.set(1)

        self.quit_button = tk.Button(
                self.window, text='QUIT',
                command=lambda *args: [
                        self.window.quit(), self.window.destroy()]
                    )

        self.quit_button.grid(row=8, column=3, pady=(0, 0))

        self.painting.animation_loop()

    def update(self, *args: tk.Event) -> None:
        """
        Update the function by entry input.
        """
        self.painting.update(self.enter_function.get())
        self.function_dropdown_string.set("Preset Waveform f(t)")

    def update_by_dropdown(self, event: tk.Event) -> None:
        """
        Update the function by the dropdown menu.
        """
        self.painting.update(self.function_dropdown_dict[event])
        if not(("sin" in self.painting.title and not (
                "sinc" in self.painting.title))
               or "cos" in self.painting.title):
            self.painting.plot_title.set_text("f(t)"+",   "
                                              + "$ t = s (mod(2 \pi)) - \pi $")

    def change_animation_speed(self, event: tk.Event) -> None:
        """
        Change the animation speed.
        """
        j = self.slider_speed.get()
        self.painting.fpi = j
        # self.painting.update(self.enter_function.get())


if __name__ == "__main__":

    run = App()

    tk.mainloop()
