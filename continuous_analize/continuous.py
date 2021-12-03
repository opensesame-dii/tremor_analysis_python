#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from logging import root, warning
import os
from io import BytesIO
# from shutil import rmtree
import matplotlib.pyplot as plt
from copy import deepcopy
from sys import exit

import datetime

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


class ScrollableFrame(tk.Frame):
# https://water2litter.net/rum/post/python_tkinter_resizeable_canvas/

    def __init__(self, parent, minimal_canvas_size):
        tk.Frame.__init__(self, parent)

        self.minimal_canvas_size = minimal_canvas_size

        # 縦スクロールバー
        self.vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=False)

        # 横スクロールバー
        self.hscrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.hscrollbar.pack(fill=tk.X, side=tk.BOTTOM, expand=False)

        # Canvas
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0,
            yscrollcommand=self.vscrollbar.set, xscrollcommand=self.hscrollbar.set,  bg="#778899")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # スクロールバーをCanvasに関連付け
        self.vscrollbar.config(command=self.canvas.yview)
        self.hscrollbar.config(command=self.canvas.xview)

        self.canvas.configure(yscrollcommand=self.vscrollbar.set)
        self.canvas.configure(xscrollcommand=self.hscrollbar.set)
        

        # Canvasの位置の初期化
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # スクロール範囲の設定
        self.canvas.config(scrollregion=(0, 0, self.minimal_canvas_size[0], self.minimal_canvas_size[1]))

        # Canvas内にフレーム作成
        self.interior = tk.Frame(self.canvas, bg="#778899")
        self.canvas.create_window(0, 0, window=self.interior, anchor='nw')

        # Canvasの大きさを変える関数
        def _configure_interior(event):
            size = (max(self.interior.winfo_reqwidth(), self.minimal_canvas_size[0]),
                max(self.interior.winfo_reqheight(), self.minimal_canvas_size[1]))
            self.canvas.config(scrollregion=(0, 0, size[0], size[1]))
            if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
                self.canvas.config(width = self.interior.winfo_reqwidth())
            if self.interior.winfo_reqheight() != self.canvas.winfo_height():
                self.canvas.config(height = self.interior.winfo_reqheight())

        # 内部フレームの大きさが変わったらCanvasの大きさを変える関数を呼び出す
        self.interior.bind('<Configure>', _configure_interior)
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # assign YYYYMMDDhhmm when app launched to analize target directory name
        self.launched_str = datetime.datetime.now().strftime("%Y%m%d%H%M")
        self.python_dir = os.path.dirname(os.path.abspath(__file__))
        # data directory name
        # self.target_dir = os.path.join(self.python_dir, "data-" + self.launched_str)
        self.target_dir = os.path.join(self.python_dir, "data-dev") #開発用 
        if not os.path.isdir(self.target_dir):
            os.mkdir(self.target_dir)

        print(self.target_dir)
        # number of sensor
        # e.g. 3 for "accelerometer, magnetmeter and gyroscope", 2 for "left arm and right arm"
        self.SENSORS_NUM = 3

        self.sampling_rate = 200
        self.segment_duration_sec = 5
        self.frame_range = [0, -1]

        

        self.result_value_keys = [
            "sp_peak_amplitude",
            "sp_peak_frequency",
            "sp_peak_time",
            "sa_peak_amplitude",
            "sa_peak_frequency",
            "sa_fwhm",
            "sa_hwp",
            "sa_tsi",
            "wt_peak_amplitude",
            "wt_peak_frequency",
            "wt_peak_time",
        ]
        self.result_graph_keys = [
            "sa_graph",
            "sp_graph",
            "wavelet",
        ]


        # exit event
        self.protocol("WM_DELETE_WINDOW", self.app_exit)

        #メインウィンドウの設定
        # root = tkinter.Tk()
        # root.title("tremor")
        self.title("tremor continuous analizer")

        #if os.name == "nt":
         #   self.state("zoomed")
        #elif os.name == "posix":
         #   self.attributes("-zoomed", "1")
        #self.configure(bg="#778899")

        self.create_window()

    def scan(self):
        pass

    def run(self):
        pass

    def create_window(self):
        self.buttonframe = ttk.Frame(self)
        self.filelistframe = ttk.Frame(self)

        self.scan_button = ttk.Button(self.buttonframe,text="scan",command=lambda: self.scan()) 
        self.run_button = ttk.Button(self.buttonframe,text="run",command=lambda: self.run())
        self.filelist_box = tk.Text(self.filelistframe)
        self.progress_bar_text = tk.StringVar(self.buttonframe)
        self.progress_bar_text.set("--")
        self.progress_bar = ttk.Label(self.buttonframe)
        self.per = ttk.Label(self.buttonframe,text = "%")
        self.directoryname = ttk.Label(self.filelistframe,text="解析対象のディレクトリ: " + "data " +self.launched_str)

        self.buttonframe.grid(row=0,column=0)
        self.filelistframe.grid(row=0,column=1)
        self.scan_button.grid(row=0,column=0)
        self.run_button.grid(row=1,column=0) 
        self.filelist_box.grid(row=1,column=0) 
        self.directoryname.grid(row=0,column=0) 
        self.progress_bar.grid(row=2,column=0)
        self.per.grid(row=2,column=1)

    def app_exit(self):
        plt.close('all')
        #self.destroy()
        exit()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()