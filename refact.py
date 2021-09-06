#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import makedirs, path
from io import BytesIO
from shutil import rmtree
import matplotlib.pyplot as plt

from PIL import Image, ImageTk
import numpy as np
from scipy import signal
from matplotlib import mlab
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import pandas as pd

from matplotlib import use
use('TkAgg')

# number of sensor
# e.g. 3 for "accelerometer, magnetmeter and gyroscope", 2 for "left arm and right arm"
SENSORS = 3

# this directory stores figure png files
DATA_DIR = path.join(path.dirname(path.abspath(__file__)), ".data")

# regenerate data directory when program launched
try:
    rmtree(DATA_DIR)
except FileNotFoundError:
    pass
makedirs(DATA_DIR)

# figure size settings
dpi = 97
figsize_big = (12, 3)
figsize_small = (4, 3)
figsize_pixel_big = (figsize_big[0] * dpi, figsize_big[1] * dpi)
figsize_pixel_small = (figsize_small[0] * dpi, figsize_small[1] * dpi)

# generate blank figure for initialize
plt.figure(dpi=dpi, figsize=figsize_big)
plt.savefig(DATA_DIR + "/init.png")
plt.close()
plt.figure(dpi=dpi, figsize=figsize_small)
plt.savefig(DATA_DIR + "/init_s.png")
plt.close()

def remove_ext(filename):
    return path.splitext(path.basename(filename))[0]


def get_img_data(f, maxsize=(1200, 850)):
    """
    Generate image data using PIL
    """
    img = Image.open(f)
    img.thumbnail(maxsize)
    bio = BytesIO()
    img.save(bio, format="PNG")
    del img
    return bio.getvalue()

def detect_data_warning(data):
    """
    detect max or min adjoining
    """
    max_idx = np.where(data == data.max())[0]
    min_idx = np.where(data == data.min())[0]

    return any([max_idx[i] + 1 == max_idx[i + 1] for i in range(len(max_idx) - 1)]) or any([min_idx[i] + 1 == min_idx[i + 1] for i in range(len(min_idx) - 1)])

def update_status(sg_window, event, values, data_structure):
    """
    gui update
    """
    pass

class DataStructure():
    def __init__(self):
        self.sampling_rate = 200
        self.segment_duration_sec = 5
        self.frame_range = [0, -1]

        self.filenames = ["", ""]
        self.data = [None, None]
        self.current_data = 0 # showing data index (0 or 1)

        self.modes = ["Spectral Amplitude", "Spectrogram"] # あとで修正(wavelet)
        self.current_mode = 0
        self.sensors = ["sensor"+str(i + 1) for i in range(SENSORS)] # "sensor1", "sensor2", ...
        
        self.results = {
            0: { # file 1
                "sa_peak_amplitude" : [[None] * 4] * SENSORS , # on "spectral amplitude" mode
                "sa_peak_frequency" : [[None] * 4] * SENSORS ,
                "sa_fwhm"           : [[None] * 4] * SENSORS ,
                "sa_hwp"            : [[None] * 4] * SENSORS ,
                "sa_tsi"            : [[None] * 4] * SENSORS ,

                "sp_peak_amplitude" : [[None] * 4] * SENSORS , # on "Spectrogram" mode
                "sp_peak_frequency" : [[None] * 4] * SENSORS ,
                "sp_peak_time"      : [[None] * 4] * SENSORS
            },
            1: { # file 2
                "sa_peak_amplitude" : [[None] * 4] * SENSORS , # on "spectral amplitude" mode
                "sa_peak_frequency" : [[None] * 4] * SENSORS ,
                "sa_fwhm"           : [[None] * 4] * SENSORS ,
                "sa_hwp"            : [[None] * 4] * SENSORS ,
                "sa_tsi"            : [[None] * 4] * SENSORS ,

                "sp_peak_amplitude" : [[None] * 4] * SENSORS , # on "Spectrogram" mode
                "sp_peak_frequency" : [[None] * 4] * SENSORS ,
                "sp_peak_time"      : [[None] * 4] * SENSORS
            },
            -1: { # relational values between file1 and file 2
                "coherence"         : [[None] * 4] * SENSORS ,
            }
        }





data_structure = DataStructure()

# GUI setup

small_size = (10, 1)
medium_size = (20, 1)
data_input_frame = sg.Frame(
    layout=[
        [sg.Text("data1: "), sg.InputText(key="input1", size=medium_size, enable_events=True, readonly=True, visible=False), sg.FileBrowse(key="file1", target="input1", file_types=(('EXCELファイル/CSVファイル', '*.xlsx'), ('EXCELファイル/CSVファイル', '*.xlsm'), ('EXCELファイル/CSVファイル', '*.csv')), enable_events=True), sg.Button("clear data", key="clear_data")],
        [sg.Text("data2: "), sg.InputText(key="input2", size=medium_size, enable_events=True, readonly=True, visible=False), sg.FileBrowse(key="file2", target="input2", file_types=(('EXCELファイル/CSVファイル', '*.xlsx'), ('EXCELファイル/CSVファイル', '*.xlsm'), ('EXCELファイル/CSVファイル', '*.csv')), enable_events=True), sg.Text("progress: "), sg.Text("--%", key="progress")]
    ], title="")

preview_frame = sg.Frame(
    layout=[
        [
            sg.Image(data=get_img_data(DATA_DIR + "/init.png"), key="data_preview")
        ],
        [sg.Button("popup...", key="popup_preview")]
    ], title="data preview")

settings_frame = sg.Frame(
    layout=[
        [
            sg.Column([
                [sg.Text("now showing: ")],
                [sg.Text("data window: ")],
                [sg.Text("Analysis: ")],
                [sg.Text("Sensor: ")],
            ]),
            sg.Column([
                [sg.Combo(["data_list"], key="data_select", size=medium_size, enable_events=True, readonly=True)],
                [sg.Combo(["mode_lst"], key="mode_select", size=medium_size, enable_events=True, readonly=True)],
                [sg.Combo(["sensor_lst"], key="sensor_select", size=medium_size, enable_events=True, readonly=True)],
                
        ])]
    ], title=""
    )

results1 = sg.Frame(
    layout=[
        [
            sg.Column([
                [sg.Text("Spectrogram Peak Amplitude: ")],
                [sg.Text("Spectrogram Peak Frequency(Hz): ")],
                [sg.Text("Spectrogram Peak Time(s): ")],
                [sg.Text("Whole Peak Amplitude: ")],
                [sg.Text("Whole Peak Frequency(Hz): ")],
                [sg.Text("Full-width Half Maximum(Hz): ")],
                [sg.Text("Half-width Power: ")],
                [sg.Text("Tremor Stability Index: ")]
            ]),
            sg.Column([
                [sg.InputText("None", key="sp_peak_amp1", readonly=True, size=small_size)],
                [sg.InputText("None", key="sp_peak_freq1", readonly=True, size=small_size)],
                [sg.InputText("None", key="sp_peak_time1", readonly=True, size=small_size)],
                [sg.InputText("None", key="wh_peak_amp1", readonly=True, size=small_size)],
                [sg.InputText("None", key="wh_peak_freq1", readonly=True, size=small_size)],
                [sg.InputText("None", key="fwhm1", readonly=True, size=small_size)],
                [sg.InputText("None", key="hwp1", readonly=True, size=small_size)],
                [sg.InputText("None", key="tsi1", readonly=True, size=small_size)]
            ])
        ]
    ], title="data1")

results2 = sg.Frame(
    layout=[
        [
            sg.Column([
                [sg.Text("Spectrogram Peak Amplitude: ")],
                [sg.Text("Spectrogram Peak Frequency(Hz): ")],
                [sg.Text("Spectrogram Peak Time(s): ")],
                [sg.Text("Whole Peak Amplitude: ")],
                [sg.Text("Whole Peak Frequency(Hz): ")],
                [sg.Text("Full-width Half Maximum(Hz): ")],
                [sg.Text("Half-width Power: ")],
                [sg.Text("Tremor Stability Index: ")]
            ]),
            sg.Column([
                [sg.InputText("None", key="sp_peak_amp2", readonly=True, size=small_size)],
                [sg.InputText("None", key="sp_peak_freq2", readonly=True, size=small_size)],
                [sg.InputText("None", key="sp_peak_time2", readonly=True, size=small_size)],
                [sg.InputText("None", key="wh_peak_amp2", readonly=True, size=small_size)],
                [sg.InputText("None", key="wh_peak_freq2", readonly=True, size=small_size)],
                [sg.InputText("None", key="fwhm2", readonly=True, size=small_size)],
                [sg.InputText("None", key="hwp2", readonly=True, size=small_size)],
                [sg.InputText("None", key="tsi2", readonly=True, size=small_size)]
            ])
        ]
    ], title="data2")

results3 = sg.Frame(
    layout=[
        [
            sg.Column([
                [sg.Text("coherence(x   ): ")],
                [sg.Text("coherence(y   ): ")],
                [sg.Text("coherence(z   ): ")],
                [sg.Text("coherence(norm): ")]
            ]),
            sg.Column([
                [sg.InputText("None", key="coh_x", readonly=True, size=small_size)],
                [sg.InputText("None", key="coh_y", readonly=True, size=small_size)],
                [sg.InputText("None", key="coh_z", readonly=True, size=small_size)],
                [sg.InputText("None", key="coh_norm", readonly=True, size=small_size)]
            ])
        ]
    ], title="")

results_wrapper = sg.Frame(
    layout=[
        [sg.Column([
            [sg.Button("copy to clipboard", key="copy_to_clipboard")],
            [results1],
            [results2],
            [results3],
            [sg.Text(size=(100, 5), key='-MULTILINE-', visible=False)],
        ], scrollable=True, vertical_scroll_only=True, size=(500, 500))]
    ], title="results"
)

graph_wrapper = sg.Frame(
    layout=[
        [sg.Image(data=get_img_data(DATA_DIR + "/init.png"), key="fig_norm")],
        [
            sg.Image(data=get_img_data(DATA_DIR + "/init_s.png"), key="fig_x"),
            sg.Image(data=get_img_data(DATA_DIR + "/init_s.png"), key="fig_y"), 
            sg.Image(data=get_img_data(DATA_DIR + "/init_s.png"), key="fig_z")
        ]
    ], title="graph"
)

settings_frame2 = sg.Frame(
    layout=[
        [sg.Text("Segment duration(s): "), sg.InputText(default_text="segment_duration_sec", key="segment_duration_sec", size=small_size, enable_events=False)],
        [sg.Text("Sampling rate(Hz): "), sg.InputText(default_text="sampling_rate", key="sampling_rate", size=small_size, enable_events=False)],
        [sg.Text("Frame range: "), sg.InputText(default_text=0, key="range_start", size=small_size, enable_events=False), sg.Text(" to "), sg.InputText(default_text=-1, key="range_end", size=small_size, enable_events=False)],
        [sg.Button("Apply", key="settings_updated", enable_events=True)]
    ]
    , title="settings"
)

layout=[
    [sg.Column([[data_input_frame], [settings_frame], [settings_frame2], [results_wrapper]]), sg.Column([[preview_frame], [graph_wrapper]])],
]
sg_window = sg.Window("tremor analysis", layout, resizable=True)
while True:
    event, values = sg_window.read()
    if (event == sg.WIN_CLOSED):
        break
    else:
        update_status(sg_window, event, values, data_structure)
sg_window.close()