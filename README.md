# Interactive Fourier Series in Matplotlib
Visualize the Fourier series for any real periodic function!
To obtain this program, first download or clone this repository, then ensure that you have the latest version of Python with [Tkinter](https://docs.python.org/3/library/tk.html), [Matplotlib](https://matplotlib.org), 
[Numpy](https://numpy.org), and [Sympy](https://www.sympy.org/en/index.html) installed. You may also optionally install [PySide2](https://wiki.qt.io/Qt_for_PythonPySide2) if you want to use it for the GUI instead of Tkinter. 
You can then launch this program by either running `app.py` if you're using Tkinter, or `qt_app.py` if you're using PySide2. You should see the Fourier series of the rectangle function expressed in terms of rotating complex exponentials.

<img src="https://raw.githubusercontent.com/marl0ny/Real-Fourier-Series/master/rect.gif" />

To visualize the Fourier series of a different function, choose one of the preset functions in the `Preset Waveform f(t)`drop down menu, or enter a new function in the `Enter waveform f(t)` entry box. 
Change the number of circles displayed by moving the `Maximum Frequency` slider around. To set the animation speed, shift the `Animation Speed` slider. To close the app, click `QUIT`. 

## References:
[Wikipedia - Fourier series](https://en.wikipedia.org/wiki/Fourier_series) <br>
[Chapter 7 of Mark Newman's Computational Physics](http://www-personal.umich.edu/~mejn/cp/)
