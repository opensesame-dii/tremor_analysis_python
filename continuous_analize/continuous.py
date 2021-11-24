#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from logging import root, warning
from os import makedirs, path, name
from io import BytesIO
# from shutil import rmtree
import matplotlib.pyplot as plt
from copy import deepcopy
from sys import exit

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# from PIL import Image, ImageTk
import numpy as np
from scipy.signal import hamming, detrend, morlet2, cwt, spectrogram, get_window
from matplotlib.mlab import cohere, window_hanning
from matplotlib.pyplot import specgram as pltspectrogram
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import backend_tools as cbook
# import PySimpleGUI as sg
import pandas as pd

from matplotlib import use
use('TkAgg')
plt.rcParams['figure.subplot.bottom'] = 0.18
# number of sensor
# e.g. 3 for "accelerometer, magnetmeter and gyroscope", 2 for "left arm and right arm"
SENSORS = 3

# frequency for analysis target
MAX_F = 20
MIN_F = 2


# figure size settings #白い画像を生成
dpi = 97
figsize_big = (12, 3)
figsize_small = (4, 3)
figsize_pixel_big = (figsize_big[0] * dpi, figsize_big[1] * dpi)
figsize_pixel_small = (figsize_small[0] * dpi, figsize_small[1] * dpi)



if __name__ == "__main__":
    app = MainApp()
    app.mainloop()