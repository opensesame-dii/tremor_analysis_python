#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import makedirs, path, name
from io import BytesIO
# from shutil import rmtree
import matplotlib.pyplot as plt
from copy import deepcopy

import tkinter
from tkinter import ttk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# from PIL import Image, ImageTk
import numpy as np
# from scipy import signal
# from matplotlib import mlab
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# import PySimpleGUI as sg
import pandas as pd

from matplotlib import use
use('TkAgg')

# number of sensor
# e.g. 3 for "accelerometer, magnetmeter and gyroscope", 2 for "left arm and right arm"
SENSORS = 3

""" # Tkinter に移行したため不要
# this directory stores figure png files
DATA_DIR = path.join(path.dirname(path.abspath(__file__)), ".data") #ファイルの場所

# regenerate data directory when program launched
try:
    rmtree(DATA_DIR)
except FileNotFoundError:
    pass
makedirs(DATA_DIR)
"""
# figure size settings #白い画像を生成
dpi = 97
figsize_big = (12, 3)
figsize_small = (4, 3)
figsize_pixel_big = (figsize_big[0] * dpi, figsize_big[1] * dpi)
figsize_pixel_small = (figsize_small[0] * dpi, figsize_small[1] * dpi)

""" # Tkinter に移行したため不要
# generate blank figure for initialize #画像を保存
plt.figure(dpi=dpi, figsize=figsize_big)
plt.savefig(DATA_DIR + "/init.png")
plt.close()
plt.figure(dpi=dpi, figsize=figsize_small)
plt.savefig(DATA_DIR + "/init_s.png")
plt.close()  #ここまで初期化
"""


def remove_ext(filename):
    return path.splitext(path.basename(filename))[0]  #拡張子を消す

# Tkinter に移行したため不要
# def get_img_data(f, maxsize=(1200, 850)):
#     """
#     Generate image data using PIL
#     """
#     img = Image.open(f)
#     img.thumbnail(maxsize)
#     bio = BytesIO()
#     img.save(bio, format="PNG")
#     del img
#     return bio.getvalue()  #

def detect_data_warning(data):
    """
    detect max or min adjoining      #変なデータをはじく警告
    """
    max_idx = np.where(data == data.max())[0]
    min_idx = np.where(data == data.min())[0]

    return any([max_idx[i] + 1 == max_idx[i + 1] for i in range(len(max_idx) - 1)]) or any([min_idx[i] + 1 == min_idx[i + 1] for i in range(len(min_idx) - 1)])

def update_status(sg_window, event, values, data_structure):
    """
    gui update　　#まだできてない
    """
    pass

class AppData():
    def __init__(self):
        # number of sensor
        # e.g. 3 for "accelerometer, magnetmeter and gyroscope", 2 for "left arm and right arm"
        self.SENSORS = 3

        """
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
        """



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
""" # PySimpleGUI から Tkinter に移行
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
"""


#メインウィンドウの設定
root = tkinter.Tk()
root.title("tremor")
if name == "nt":
    root.state("zoomed")
elif name == "posix":
    root.attributes("-zoomed", "1")
root.configure(bg="#778899")

#ファイルを選ぶ関数
def file_dialog(event):
    ftypes =[('EXCELファイル/CSVファイル', '*.xlsx'),
        ('EXCELファイル/CSVファイル', '*.xlsm'),
        ('EXCELファイル/CSVファイル', '*.csv')]
    fname = filedialog.askopenfilename(filetypes=ftypes)

#フレームの色を変える
#s = ttk.Style()
#s.configure("color", background = "#778899")

#情報フレームとグラフフレームの作成
info_frame = tkinter.Frame(root, bg="#778899")
img_frame = tkinter.Frame(root, bg="#778899")

#データを選択するフレーム
data_input_frame = ttk.Frame(info_frame,relief="groove",borderwidth=5)
data_label1 = ttk.Label(
    data_input_frame,
    text="data1:"
    )
data_label1.grid(row=0, column=0) 

brows_button1 = ttk.Button(data_input_frame,text="Brows")
brows_button1.bind("<ButtonPress>", file_dialog)
brows_button1.grid(row=0, column=1)  

clear_button = ttk.Button(data_input_frame,text="clear")
clear_button.grid(row=0, column=2)

data_label2 = ttk.Label(
    data_input_frame,
    text = "data2:"
)
data_label2.grid(row=1, column=0)

brows_button2 = ttk.Button(data_input_frame,text="Brows")
brows_button2.bind("<ButtonPress>",file_dialog)
brows_button2.grid(row=1, column=1)

progress = ttk.Label(
    data_input_frame,
    text= "progress:"
)
progress.grid(row=1, column=2)
progress_bar = ttk.Label(
    data_input_frame,
    text= "--%"
)
progress_bar.grid(row=1, column=3)

#モード選択
settings_frame = ttk.Frame(info_frame,relief="groove")
now_showing = ttk.Label(settings_frame,text="now showing:")
now_showing.grid(row=0, column=0)
analysis = ttk.Label(settings_frame, text="Analysis:")
analysis.grid(row=1, column=0)
sensor = ttk.Label(settings_frame, text="Sensor")
sensor.grid(row=2, column=0)

module = ("data_list","mode_list","analysis","sensor_list")
now_showing_box = ttk.Combobox(settings_frame, values=module[0], state="readonly")
now_showing_box.grid(row=0, column=1)
analysis_box = ttk.Combobox(settings_frame, values=module[2], state="readonly")
analysis_box.grid(row=1, column=1)
sensor_box = ttk.Combobox(settings_frame, values=module[3], state="readonly")
sensor_box.grid(row=2, column=1)

#settings
settings_frame2 = ttk.Frame(info_frame,relief="groove")
seg = ttk.Label(settings_frame2, text="Segment duration(s):")
seg.grid(row=0, column=0)
samp = ttk.Label(settings_frame2, text="Sampling rate(Hz):")
samp.grid(row=1, column=0)
range = ttk.Label(settings_frame2, text="Frame range:")
range.grid(row=2, column=0)

seg_txt = tkinter.Entry(settings_frame2,width=20,)
seg_txt.grid(row=0, column=1)
samp_txt = tkinter.Entry(settings_frame2, width=20)
samp_txt.grid(row=1, column=1)
range_txt1 = tkinter.Entry(settings_frame2, width=20)
range_txt1.grid(row=2, column=1)
range_txt2 = tkinter.Entry(settings_frame2,width=20)
range_txt2.grid(row=2, column=3)
range_to = ttk.Label(settings_frame2, text="to")
range_to.grid(row=2, column=2)
apply_button = ttk.Button(settings_frame2, text="Apply")
apply_button.grid(row=3, column=0)

#result
result_frame = ttk.Frame(info_frame, relief="groove")

clip = ttk.Button(result_frame, text="copy to clipboard")
clip.grid(row=0, column=0,sticky=tkinter.W)
#data1用
data1_frame = ttk.Frame(result_frame, relief="groove")
spa = ttk.Label(data1_frame, text="Spectrogram Peak Amplitude:")
spa.grid(row=0, column=0)
spf = ttk.Label(data1_frame, text="Spectrogram Peak Frequency(Hz): ")
spf.grid(row=1, column=0)
spt = ttk.Label(data1_frame, text = "Spectrogram Peak Time(s): ")
spt.grid(row=2, column=0)
wpa = ttk.Label(data1_frame, text = "Whole Peak Amplitude: ")
wpa.grid(row=3, column=0)
wpf = ttk.Label(data1_frame, text = "Whole Peak Frequency(Hz): ")
wpf.grid(row=4, column=0)
fhm = ttk.Label(data1_frame, text = "Full-width Half Maximum(Hz): ")
fhm.grid(row=5, column=0)
hp = ttk.Label(data1_frame, text = "Half-width Power: ")
hp.grid(row=6, column=0)
tsi = ttk.Label(data1_frame, text = "Tremor Stability Index: ")
tsi.grid(row=7, column=0)

spa_txt = tkinter.Entry(data1_frame,width=20)
spa_txt.insert(tkinter.END,"None")
spa_txt.grid(row=0, column=1)
spf_txt = tkinter.Entry(data1_frame, width=20)
spf_txt.insert(tkinter.END,"None")
spf_txt.grid(row=1, column=1)
spt_txt = tkinter.Entry(data1_frame,width=20)
spt_txt.insert(tkinter.END,"None")
spt_txt.grid(row=2, column=1)
wpa_txt = tkinter.Entry(data1_frame, width=20)
wpa_txt.insert(tkinter.END,"None")
wpa_txt.grid(row=3, column=1)
wpf_txt = tkinter.Entry(data1_frame, width=20)
wpf_txt.insert(tkinter.END,"None")
wpf_txt.grid(row=4, column=1)
fhm_txt = tkinter.Entry(data1_frame, width=20)
fhm_txt.insert(tkinter.END,"None")
fhm_txt.grid(row=5, column=1)
hp_txt = tkinter.Entry(data1_frame, width=20)
hp_txt.insert(tkinter.END,"None")
hp_txt.grid(row=6, column=1)
tsi_txt = tkinter.Entry(data1_frame, width=20)
tsi_txt.insert(tkinter.END,"None")
tsi_txt.grid(row=7, column=1)

#data2
data2_frame = ttk.Frame(result_frame, relief="groove")
spa2 = ttk.Label(data2_frame, text="Spectrogram Peak Amplitude:")
spa2.grid(row=0, column=0)
spf2 = ttk.Label(data2_frame, text="Spectrogram Peak Frequency(Hz): ")
spf2.grid(row=1, column=0)
spt2 = ttk.Label(data2_frame, text = "Spectrogram Peak Time(s): ")
spt2.grid(row=2, column=0)
wpa2 = ttk.Label(data2_frame, text = "Whole Peak Amplitude: ")
wpa2.grid(row=3, column=0)
wpf2 = ttk.Label(data2_frame, text = "Whole Peak Frequency(Hz): ")
wpf2.grid(row=4, column=0)
fhm2 = ttk.Label(data2_frame, text = "Full-width Half Maximum(Hz): ")
fhm2.grid(row=5, column=0)
hp2 = ttk.Label(data2_frame, text = "Half-width Power: ")
hp2.grid(row=6, column=0)
tsi2 = ttk.Label(data2_frame, text = "Tremor Stability Index: ")
tsi2.grid(row=7, column=0)

spa2_txt = tkinter.Entry(data2_frame,width=20)
spa2_txt.insert(tkinter.END,"None")
spa2_txt.grid(row=0, column=1)
spf2_txt = tkinter.Entry(data2_frame, width=20)
spf2_txt.insert(tkinter.END,"None")
spf2_txt.grid(row=1, column=1)
spt2_txt = tkinter.Entry(data2_frame,width=20)
spt2_txt.insert(tkinter.END,"None")
spt2_txt.grid(row=2, column=1)
wpa2_txt = tkinter.Entry(data2_frame, width=20)
wpa2_txt.insert(tkinter.END,"None")
wpa2_txt.grid(row=3, column=1)
wpf2_txt = tkinter.Entry(data2_frame, width=20)
wpf2_txt.insert(tkinter.END,"None")
wpf2_txt.grid(row=4, column=1)
fhm2_txt = tkinter.Entry(data2_frame, width=20)
fhm2_txt.insert(tkinter.END,"None")
fhm2_txt.grid(row=5, column=1)
hp2_txt = tkinter.Entry(data2_frame, width=20)
hp2_txt.insert(tkinter.END,"None")
hp2_txt.grid(row=6, column=1)
tsi2_txt = tkinter.Entry(data2_frame, width=20)
tsi2_txt.insert(tkinter.END,"None")
tsi2_txt.grid(row=7, column=1)

#coherence
coherence_frame = ttk.Frame(result_frame, relief="groove")
coh_x = ttk.Label(coherence_frame, text="coherence(x ):")
coh_x.grid(row=0, column=0)
coh_y = ttk.Label(coherence_frame, text="coherence(y ):")
coh_y.grid(row=1, column=0)
coh_z = ttk.Label(coherence_frame, text="coherence(z ):")
coh_z.grid(row=2, column=0)
coh_norm = ttk.Label(coherence_frame, text="coherence(norm): ")
coh_norm.grid(row=3, column=0)

x_txt = tkinter.Entry(coherence_frame, width=20)
x_txt.insert(tkinter.END,"None")
x_txt.grid(row=0, column=1)
y_txt = tkinter.Entry(coherence_frame, width=20)
y_txt.insert(tkinter.END,"None")
y_txt.grid(row=1, column=1)
z_txt = tkinter.Entry(coherence_frame, width=20)
z_txt.insert(tkinter.END,"None")
z_txt.grid(row=2, column=1)
norm_txt = tkinter.Entry(coherence_frame, width=20)
norm_txt.insert(tkinter.END,"None")
norm_txt.grid(row=3, column=1)
#data previewのグラフ


can = ttk.Frame(img_frame)
fig = Figure(figsize = (10,3),dpi = 100)
ax = fig.add_subplot(1,1,1)
#line, =  ax.plot(x,y)
canvas = FigureCanvasTkAgg(fig,can)
canvas.draw()
#canvas.get_tk_widget().grid(row=0, rowspan=4,column=1+1,sticky=tkinter.E)
canvas.get_tk_widget().pack()
toolbar1 = NavigationToolbar2Tk(canvas, can)

can2 = ttk.Frame(img_frame)
canvas2 = FigureCanvasTkAgg(fig, can2)
canvas2.draw()
canvas2.get_tk_widget().pack()
toolbar2 = NavigationToolbar2Tk(canvas2, can2)
#canvas2.get_tk_widget().grid(row=4, column=1)

can3 = ttk.Frame(img_frame)
can_x = ttk.Frame(can3)
fig3 = Figure(figsize = (2.5,2.5),dpi = 100)
ax = fig3.add_subplot(1,1,1)
canvas_x = FigureCanvasTkAgg(fig3, can_x)
canvas_x.draw()
canvas_x.get_tk_widget().pack()
toolbar3 = NavigationToolbar2Tk(canvas_x, can_x)

can_y = ttk.Frame(can3)
canvas_y = FigureCanvasTkAgg(fig3, can_y)
canvas_y.draw()
canvas_y.get_tk_widget().pack()
toolbar4 = NavigationToolbar2Tk(canvas_y, can_y)

can_z = ttk.Frame(can3)
canvas_z = FigureCanvasTkAgg(fig3, can_z)
canvas_z.draw()
canvas_z.get_tk_widget().pack()
toolbar5 = NavigationToolbar2Tk(canvas_z, can_z)


#フレームの配置
info_frame.grid(row=0, column=0)
img_frame.grid(row=0, column=1)
data_input_frame.grid(row = 0, column=0, padx=10, pady=20,sticky=tkinter.W)
settings_frame.grid(row=2, column=0, padx=10, pady=5,sticky=tkinter.W)
settings_frame2.grid(row=3, column=0, padx=10, pady=5,sticky=tkinter.W)
result_frame.grid(row=4, column=0,sticky=tkinter.W, padx=10)
data1_frame.grid(row=1, column=0,sticky=tkinter.W,pady=10)
data2_frame.grid(row=2, column=0,sticky=tkinter.W, pady=10)
coherence_frame.grid(row=3,column=0, sticky=tkinter.W,pady=10)
can.grid(row=0, column=0)
can2.grid(row=1, column=0)
can3.grid(row=2, column=0)
can_x.grid(row=0, column=0)
can_y.grid(row=0, column=1)
can_z.grid(row=0, column=2)

root.mainloop()