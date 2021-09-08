#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import makedirs, path
from io import BytesIO
from shutil import rmtree
import matplotlib.pyplot as plt
from copy import deepcopy

from PIL import Image, ImageTk
import numpy as np
from scipy import signal
from matplotlib import mlab
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import pandas as pd

from matplotlib import use
use('TkAgg')

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

class AppData():
    def __init__(self):
        # number of sensor
        # e.g. 3 for "accelerometer, magnetmeter and gyroscope", 2 for "left arm and right arm"
        self.SENSORS = 3

        # this directory stores figure png files
        self.DATA_DIR = path.join(path.dirname(path.abspath(__file__)), ".data")

        # regenerate data directory when program launched
        try:
            rmtree(self.DATA_DIR)
        except FileNotFoundError:
            pass
        makedirs(self.DATA_DIR)

        # figure size settings
        self.dpi = 97
        self.figsize_big = (12, 3)
        self.figsize_small = (4, 3)
        self.figsize_pixel_big = (self.figsize_big[0] * self.dpi, self.figsize_big[1] * self.dpi)
        self.figsize_pixel_small = (self.figsize_small[0] * self.dpi, self.figsize_small[1] * self.dpi)

        # generate blank figure for initialize
        # いらないかも
        plt.figure(dpi=self.dpi, figsize=self.figsize_big)
        plt.savefig(self.DATA_DIR + "/init.png")
        plt.close()
        plt.figure(dpi=self.dpi, figsize=self.figsize_small)
        plt.savefig(self.DATA_DIR + "/init_s.png")
        plt.close()



        self.sampling_rate = 200
        self.segment_duration_sec = 5
        self.frame_range = [0, -1]

        self.filenames = ["", ""]
        self.data = [None, None]
        self.current_data = 0 # showing data index (0 or 1)

        self.modes = ["Spectral Amplitude", "Spectrogram"] # あとで修正(wavelet)
        self.current_mode = 0
        self.sensors = ["sensor"+str(i + 1) for i in range(self.SENSORS)] # "sensor1", "sensor2", ...
        
        empty = [[None, None, None, None], [None, None, None, None], [None, None, None, None]]

        self.results = {
            0: { # file 1
                "sa_peak_amplitude" : deepcopy(empty) , # on "spectral amplitude" mode
                "sa_peak_frequency" : deepcopy(empty) ,
                "sa_fwhm"           : deepcopy(empty) ,
                "sa_hwp"            : deepcopy(empty) ,
                "sa_tsi"            : deepcopy(empty) ,

                "sp_peak_amplitude" : deepcopy(empty) , # on "Spectrogram" mode
                "sp_peak_frequency" : deepcopy(empty) ,
                "sp_peak_time"      : deepcopy(empty)
            },
            1: { # file 2
                "sa_peak_amplitude" : deepcopy(empty) , # on "spectral amplitude" mode
                "sa_peak_frequency" : deepcopy(empty) ,
                "sa_fwhm"           : deepcopy(empty) ,
                "sa_hwp"            : deepcopy(empty) ,
                "sa_tsi"            : deepcopy(empty) ,

                "sp_peak_amplitude" : deepcopy(empty) , # on "Spectrogram" mode
                "sp_peak_frequency" : deepcopy(empty) ,
                "sp_peak_time"      : deepcopy(empty)
            },
            -1: { # relational values between file1 and file 2
                "coherence"         : deepcopy(empty) ,
            }
        }

    def stft(self):
        pass

    def spectrogram_analize(self):
        pass

    def power_density_analize(self):
        pass

    def wavelet_analize(self):
        pass

    def full_width_half_maximum(self):
        pass

    def tremor_stability_index(self):
        pass

    def coference(self):
        pass

    def update(self):
        pass





app_data = AppData()

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
            sg.Image(data=get_img_data(app_data.DATA_DIR + "/init.png"), key="data_preview")
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
        [sg.Image(data=get_img_data(app_data.DATA_DIR + "/init.png"), key="fig_norm")],
        [
            sg.Image(data=get_img_data(app_data.DATA_DIR + "/init_s.png"), key="fig_x"),
            sg.Image(data=get_img_data(app_data.DATA_DIR + "/init_s.png"), key="fig_y"), 
            sg.Image(data=get_img_data(app_data.DATA_DIR + "/init_s.png"), key="fig_z")
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
        update_status(sg_window, event, values, app_data)
sg_window.close()