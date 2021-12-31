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

        self.figsize_small = (3.3, 2.5)
        self.figsize_large = (9.9, 3)

        self.dir_list = [] # list of data directories
        self.file_extensions = [".xlsx", ".xlsm", ".csv"]

        self.result_value_keys = [
            "sp_peak_amplitude",
            "sp_peak_frequency",
            "sp_peak_time",
            "sa_peak_amplitude",
            "sa_peak_frequency",
            "sa_fwhm",
            "sa_hwp",
            "sa_tsi",
            # "wt_peak_amplitude",
            # "wt_peak_frequency",
            # "wt_peak_time",
        ]
        self.result_graph_keys = [
            "sa_graph",
            "sp_graph",
            # "wavelet",
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
        self.update_directoryname()
        self.dir_list = [] # list of data directories
        for d in os.listdir(self.target_dir):
            self.dir_list.append(os.path.join(self.target_dir, d))

            if (len(os.listdir(self.dir_list[-1])) != 2 and len(os.listdir(self.dir_list[-1])) != 1):
                err_msg = f"{len(os.listdir(self.dir_list[-1]))} files in {self.dir_list[-1]}, but must be 1 or 2"
                print(f"ERROR: {err_msg}")
                tk.messagebox.showerror("ERROR", err_msg)
                return False
            for filename in os.listdir(self.dir_list[-1]):
                if (not os.path.splitext(filename)[1] in self.file_extensions):
                    err_msg = f"invalid file extension {filename} in {d}"
                    print(f"ERROR: {err_msg}")
                    tk.messagebox.showerror("ERROR", err_msg)
                    return False
        self.update_directoryname(self.dir_list)
        return True

    def detect_data_warning(self, data):
        """
        detect going off the scale      #変なデータをはじく警告
        """
        max_idx = np.where(data == data.max())[0]
        min_idx = np.where(data == data.min())[0]

        return any([max_idx[i] + 1 == max_idx[i + 1] for i in range(len(max_idx) - 1)]) or any([min_idx[i] + 1 == min_idx[i + 1] for i in range(len(min_idx) - 1)])

    def run(self):
        # check file error
        if (not self.scan()):
            return
        
        for dir_idx in range(len(self.dir_list)):
            self.progress_bar_text.set(f"{dir_idx}/{len(self.dir_list)}")
            # filenames in the directory
            filenames = os.listdir(os.path.join(self.target_dir, self.dir_list[dir_idx]))

            res_lst = []
            data = []
            coh_results = None
            for file_idx in range(len(filenames)):
                df = pd.read_csv(os.path.join(self.target_dir, self.dir_list[dir_idx], filenames[file_idx]), 
                    header=None, skiprows=10, index_col=0, encoding="shift jis")
                npdata = np.array(df.values.flatten())
                data.append(np.reshape(npdata,(df.shape[0],df.shape[1])))
                
                # warning to go off the scale
                off_scale=[]
                for i in range(data[file_idx].shape[1]):
                    if (self.detect_data_warning(data[file_idx][:,i])):
                        print(f"WARNING: column {i} may go off the scale")
                        off_scale.append(i)

                if len(off_scale) != 0:   
                    self.infolist_box.insert("end", f"off-scale may occur in {self.dir_list[dir_idx]}/{filenames[file_idx]}: ")

                    for i in off_scale:
                        self.infolist_box.insert("end",str(i)+",")
                    self.infolist_box.insert("end","\n")

                for sensor_idx in range(self.SENSORS_NUM):
                    # analize
                    sp_graphs, sp_peak_time, sp_peak_freq, sp_peak_time = self.spectrogram_analize(data[file_idx][:, sensor_idx*self.SENSORS_NUM: sensor_idx*self.SENSORS_NUM + self.SENSORS_NUM].T, self.sampling_rate, self.sampling_rate * self.segment_duration_sec)
                    res_lst.append({})
                    
                    res_lst[-1]["sp_graphs"] = sp_graphs
                    res_lst[-1]["sp_peak_time"] = sp_peak_time
                    res_lst[-1]["sp_peak_freq"] = sp_peak_freq
                    res_lst[-1]["sp_peak_time"] = sp_peak_time

                    sa_graphs, sa_peak_amp, sa_peak_freq, sa_fwhm, sa_hwp, sa_tsi = self.power_density_analize(data[file_idx][:, sensor_idx*self.SENSORS_NUM: sensor_idx*self.SENSORS_NUM + self.SENSORS_NUM].T, self.sampling_rate, self.sampling_rate * self.segment_duration_sec)

                    res_lst[-1]["sa_graphs"] = sa_graphs
                    res_lst[-1]["sa_peak_amp"] = sa_peak_amp
                    res_lst[-1]["sa_peak_freq"] = sa_peak_freq
                    res_lst[-1]["sa_fwhm"] = sa_fwhm
                    res_lst[-1]["sa_hwp"] = sa_hwp
                    res_lst[-1]["sa_tsi"] = sa_tsi
                
            if (len(filenames) == 2):
                coh_results = []
                # coherence
                for sensor_idx in range(self.SENSORS_NUM):
                    coh_results.append([])
                    for axis_idx in range(3):
                        coh_results[-1].append(
                            self.ft_coherence(
                                data[0][:, 3 * sensor_idx + axis_idx], 
                                data[1][:, 3 * sensor_idx + axis_idx], 
                                self.sampling_rate))
                    # norm
                    coh_results[-1].append(
                        self.ft_coherence(
                            np.linalg.norm(data[0][:, 3 * sensor_idx: 3 * sensor_idx + axis_idx], axis=1), 
                            np.linalg.norm(data[1][:, 3 * sensor_idx:3 * sensor_idx + axis_idx], axis=1), 
                            self.sampling_rate))

            # ここで画像を書き出したい
            # 計算結果のデータは, res_lst に dictionary の list で格納
            # res_lst は, 各センサー毎に結果を入れてある
            # ファイルが2つあれば, 連続して格納される( len(res_lst) は3または6になる )
            
            # dictionary のキーとその型は次の通り
            # "sp_graphs"     : list of <class 'matplotlib.figure.Figure'> (x, y, z, norm の順)
            # "sp_peak_time"  : float
            # "sp_peak_freq"  : float
            # "sp_peak_time"  : float
            # "sa_graphs"     : list of <class 'matplotlib.figure.Figure'> (x, y, z, norm の順)
            # "sa_peak_amp"   : float
            # "sa_peak_freq"  : float
            # "sa_fwhm"       : float
            # "sa_hwp"        : float
            # "sa_tsi"        : float

            # 例えば1つ目のファイルのセンサー2の sa_peak_amp は 
            # res_lst[2]["sa_peak_amp"]
            # 2つ目のファイルのセンサー1の sa_peak_amp は 
            # res_lst[4]["sa_peak_amp"]

            # ファイルが2つ(左右の手のデータ)あれば, coh_resultsに coherence を list of list で格納 
            # センサーの順に,  x, y, z, norm の順 つまり coh_results[i][j]は, i番目のセンサーの j個目(x, y, z, norm)のデータを表す

            




            for i in res_lst:
                print(i)
            for i in coh_results:
                print(i)
        
        self.progress_bar_text.set("--/--")

        tk.messagebox.showinfo("Info", "analize finished")
        

    def update_directoryname(self, filename:list=None):
        if filename is None:
            pass

        


    def create_window(self):
        self.buttonframe = ttk.Frame(self)
        self.filelistframe = ttk.Frame(self)
        self.progress_frame = ttk.Frame(self.buttonframe)

        self.scan_button = ttk.Button(self.buttonframe,text="scan",command=lambda: self.scan()) 
        self.run_button = ttk.Button(self.buttonframe,text="run",command=lambda: self.run())
        self.infolist_box = tk.Text(self.filelistframe)
        self.progress_bar_text = tk.StringVar(self.buttonframe)
        self.progress_bar_text.set("--/--")
        self.progress_bar = ttk.Label(self.progress_frame, textvariable=self.progress_bar_text)
        self.per = ttk.Label(self.progress_frame,text = "progress: ")
        self.directoryname = ttk.Label(self.filelistframe,text="解析対象のディレクトリ: " + "data " +self.launched_str)

        self.buttonframe.grid(row=0,column=0)
        self.filelistframe.grid(row=0,column=1)
        self.scan_button.grid(row=0,column=0)
        self.run_button.grid(row=1,column=0) 
        self.infolist_box.grid(row=1,column=0) 
        self.directoryname.grid(row=0,column=0) 
        self.progress_frame.grid(row=2,column=0)
        self.progress_bar.grid(row=2,column=1)
        self.per.grid(row=2,column=0)

    def app_exit(self):
        plt.close('all')
        #self.destroy()
        exit()

    
    def spectrogram_analize(self, data_i, fs, nperseg, start=0, end=-1):
        """
        Params
        data: array(3, n)
            x, y, z data
        fs: int/float
            sampling rate
        nperseg: int
            sample number per stft segment
        start: integer
            analysis start frame
        end: integer
            analysis end frame
            -1 means end of input data
        """
        if (not len(data_i[0]) == len(data_i[1]) == len(data_i[2])):
            print("invalid input data")
            return None, None, None
        if (end == -1):
            end = len(data_i[0]) - 1
        elif (start > end):
            print("invalid range setting")
            # sg.Popup("invalid range setting")
            return None, None, None

        data = data_i[:, start: end + 1]

        # print("nperseg: {}".format(nperseg))


        specs = []
        x_length = len(data[0])
        nTimesSpectrogram = 500; 
        L = np.min((x_length, nperseg))
        noverlap = np.ceil(L - (x_length - L) / (nTimesSpectrogram - 1))
        noverlap = int(np.max((1,noverlap)))

        for i in range(3):
            # start = time.time()

            # scipy 
            f, t, spec = spectrogram(detrend(data[i]), fs, window=get_window("hamming", int(nperseg)), nperseg=int(nperseg), noverlap=noverlap, nfft=2**12, mode="magnitude", )
            
            
            # plt
            # spec, f, t, _ = pltspectrogram(detrend(data[i]), Fs=fs, pad_to=int(nperseg), noverlap=noverlap, NFFT=2**12, mode="default", scale="linear") 
            # spec = np.sqrt(np.array(spec))
            
            # self-created
            # spec, f, t = np.abs(self.stft(detrend(data[i]), fs, int(nperseg), self.segment_duration_sec))
            # elapsed_time = time.time() - start
            # print ("elapsed_time:\n{0}".format(elapsed_time))
            
            specs.append(np.abs(spec))
        # convert to 3-dimensional ndarray
        specs = np.array(specs) #specs.shape: (3, 640, 527)

        # trim into frequency range
        f_range = np.array([MIN_F, MAX_F]) * len(f) * 2 // self.sampling_rate
        specs = specs[:, f_range[0]: f_range[1] , :]
        f = f[f_range[0]: f_range[1]]

        vmin = np.min(specs)
        vmax = np.max(specs)
        # add norm
        specs = np.append(specs, [np.linalg.norm(specs, axis=0)], axis=0)

        graphs = [None, None, None, None]
        
        titles = ["x","y","z"]
        for i in range(3):
            graphs[i], ax = plt.subplots(figsize=self.figsize_small, dpi=100)
            graphs[i].subplots_adjust(left=0.2)
            im = ax.pcolormesh(t, f, specs[i], cmap="jet", vmin=vmin, vmax=vmax)
            ax.set_xlabel("Time [sec]")
            ax.set_ylabel("Frequency [Hz]")
            ax.set_title(titles[i])
            # axpos = axes.get_position()
            # cbar_ax = fig.add_axes([0.87, axpos.y0, 0.02, axpos.height])
            #cbar = self.results[data_idx]["sp_graph"][sensor_idx][i].colorbar(im,ax=ax)
            #cbar.set_label("Amplitude")
            # plt.show()
            # input("aa")

        graphs[3], ax = plt.subplots(figsize=self.figsize_large, dpi=100)
        im = ax.pcolormesh(t, f, specs[3], cmap="jet", vmin=vmin, vmax=vmax)
        ax.set_title("Norm")
        ax.set_xlabel("Time [sec]")
        ax.set_ylabel("Frequency [Hz]")

        # axpos = axes.get_position()
        # cbar_ax = fig.add_axes([0.87, axpos.y0, 0.02, axpos.height])
        cbar = graphs[3].colorbar(im,ax=ax)
        cbar.set_label("Amplitude")

        recording = len(data[0]) / fs
        #f_offset = int(specs.shape[2] * 2 / 20)
        # print("s t {} {}".format(t[0], t[-1]))


        peak_amp = np.max(specs[3, :, :])
        peak_idx = np.where(specs[3] == peak_amp)
        peak_freq = f[peak_idx[0][0]]
        peak_time = t[peak_idx[1][0]]

        # print("recording(s): {}".format(recording))
        # print("peak amplitude: {}  {}".format(peak_amp, peak_idx))
        # print("peak frequency(Hz): {}".format(peak_freq))
        # print("peaktime(s): {}".format(peak_time))

        plt.close("all")
        return graphs, peak_time, peak_freq, peak_time

    def power_density_analize(self, data_i, fs, nperseg, start=0, end=-1):
        """
        Params
        data: array(3, n)
            x, y, z data
        fs: int/float
            sampling rate
        nperseg: int
            sample number per stft segment
        start: integer
            analysis start frame
        end: integer
            analysis end frame
            -1 means end of input data
        """
        
        if (not len(data_i[0]) == len(data_i[1]) == len(data_i[2])):
            print("invalid input data")
            return None, None, None
        if (end == -1):
            end = len(data_i[0]) - 1
        elif (start > end):
            # sg.Popup("invalid range setting")
            print("invalid range setting")
            return None, None, None

        data = data_i[:, start: end + 1]
        # print("nperseg: {}".format(nperseg))
        # print(data.shape)

        specs = []
        for i in range(3):
            #################################################################################
            # matlab の detrend の結果と, scipyのdetrend の結果を比較→一致すれば, stftを使いまわして2乗して時間での平均を出せば多分いける
            # scipy の scipy.signal.detrend() が使えるらしい(絶対誤差0.0001以下)
            #spec, f, t = self.stft(detrend(data[i]), fs, int(nperseg), self.segment_duration_sec, int(nperseg * 0.75))
            f, t, spec = spectrogram(detrend(data[i]), fs, window=get_window("hamming", int(nperseg)), nperseg=int(nperseg), noverlap=int(nperseg * 0.75), nfft=2**12, mode="complex", ) # scipy
            # spec, f, t, _ = pltspectrogram(detrend(data[i]), Fs=fs, pad_to=int(nperseg), noverlap=int(nperseg * 0.75), NFFT=2**12, mode="magnitude", scale="linear") #plt
            specs.append(np.sum(np.power(np.abs(spec), 1), axis=1) / (len(t)))
            
        # convert to 3-dimensional ndarray
        specs = np.array(specs) #specs.shape: (3, 640)

        # trim into frequency range
        f_range = np.array([MIN_F, MAX_F]) * len(f) * 2 // self.sampling_rate
        specs = specs[:, f_range[0]: f_range[1]]
        f = f[f_range[0]: f_range[1]]

        #specs /= np.sum(np.power(signal.tukey(int(nperseg)), 2)) / np.power(np.sum(signal.tukey(int(nperseg))), 2)
        vmin = np.min(specs)
        vmax = np.max(specs)
        
        # add norm
        specs = np.append(specs, [np.linalg.norm(specs, axis=0)], axis=0)

        graphs = [None, None, None, None]
        for i in range(3):
            graphs[i], ax = plt.subplots(figsize=self.figsize_small, dpi=100)
            graphs[i].subplots_adjust(left=0.3)
            ax.set_ylim(0, vmax * 1.2)
            ax.plot(f, specs[i])
            ax.set_xlabel("Frequency [Hz]")
            ax.set_ylabel("Amplitude")
            titles = ["x","y","z"]
            ax.set_title(titles[i])

        vmax = np.max(specs[-1])
        graphs[3], ax = plt.subplots(figsize=self.figsize_large, dpi=100)
        ax.set_ylim(0, vmax * 1.2)
        ax.plot(f, specs[3])
        ax.set_title("Norm")
        ax.set_xlabel("Frequency [Hz]")
        ax.set_ylabel("Amplitude")

        l, u, lv, uv, hwp = self.full_width_half_maximum(f, specs[3])
        fwhm = uv - lv
        # print(l, u, lv, uv)
        # print(specs[3, int(l)])
        ax.fill_between(f[l:u], specs[3, l:u], color="r", alpha=0.5)
        #plt.show()
        #### plt.savefig(data_dir + "/" + remove_ext(filename) + "norm" + sensor + "am.png")
        recording = len(data[0]) / fs
        f_offset = int(specs.shape[1] * 2 / 20)
        
        peak_amp = np.max(specs[3, f_offset:])
        peak_idx = np.where(specs[3] == peak_amp)
        peak_freq = f[peak_idx[0][0]]
        tsi = self.tremor_stability_index(data[0], fs)



        # print("recording(s): {}".format(recording))
        # print("peak amplitude: {}  {}".format(peak_amp, peak_idx))
        # print("peak frequency(Hz): {}".format(peak_freq))
        # print("Full-width Half Maximum(Hz): {}".format(fwhm))
        # print("Half-width power: {}".format(hwp))
        # print("Tremor Stability Index: {}".format(tsi))

        plt.close("all")
        return graphs, peak_amp, peak_freq, fwhm, hwp, tsi

    def full_width_half_maximum(self, x, y):
        """
        calcurate Full-width Half Maximum and Half-witdh power
        
        Params
        x: array-like
        y: array-like

        Retuerns
        lower: int
            lower limit index
        upper: int
            upper limit index
        lower_v: int/float
            lower limit value (approximate)
        upper_v: int/float
            upper limit value (approximate)
        hwp: int/float
            Half-width power
        """
        y_ndarray = np.array(y)
        length = len(y_ndarray)
        peak_val_half = np.max(y_ndarray) / 2
        peak_idx = y_ndarray.argmax()
        # print(peak_idx)
        lower = peak_idx
        upper = peak_idx

        ###########################
        # spline 補間 を使いたいか?

        while (lower >= 0 and y_ndarray[lower] > peak_val_half):
            lower -= 1
        if (y_ndarray[lower] != peak_val_half):
            lower_v = (x[lower] + x[lower + 1]) / 2 # ピークの半分を跨いだ場合は中央値を取る
        else:
            lower_v = x[lower]
    
        while (upper < length - 1 and y_ndarray[upper] > peak_val_half):
            upper += 1    
        if (y_ndarray[upper] != peak_val_half):
            upper_v = (x[upper] + x[upper - 1]) / 2
        else:
            upper_v = x[upper]
        # hwp
        d = x[1] - x[0]
        hwp = np.sum(y_ndarray[lower: upper]) * d

        return (lower, upper, lower_v, upper_v, hwp)

    def tremor_stability_index(self, x, fs):
        """
        Tremor Stability Index

        Params
        x: array-like
            data
        fs: int/float
            sampling rate
        """
        x_detrend = detrend(x)
        length = len(x)

        # plt.plot(x_detrend)
        # plt.show()

        start = x_detrend[0]
        idx = 1
        # array of zero-crossing points index
        zero_crossing = np.empty(0)
        while (idx < length):
            while (idx < length and start * x_detrend[idx] > 0):
                idx += 1
            while (idx < length and start * x_detrend[idx] < 0):
                idx += 1
            zero_crossing = np.append(zero_crossing, idx)
        interval = np.diff(zero_crossing)
        tremor_freq = fs / interval # convert to frequency
        delta_freq = np.diff(tremor_freq)

        # 四分位範囲
        q75, q25 = np.percentile(delta_freq, [75 ,25])
        return q75 - q25

    def ft_coherence(self, data1, data2, fs, start=0, end=-1):
        """
        now developing
        """
        if (len(data1) != len(data2)):
            # sg.Popup("data1 and data2 have different lengths")
            print("data1 and data2 have different lengths")
            return None

        if (end == -1):
            end = len(data1) - 1
        elif (start > end):
            # sg.Popup("invalid range setting")
            print("invalid range setting")
            return None

        x1 = data1[start: end + 1]
        x2 = data2[start: end + 1]

        nfft = 2 ** 10
        noverlap = 2 ** 9
        Cyx, f = cohere(x2, x1, NFFT=nfft, Fs=fs,
                    window=window_hanning, noverlap=noverlap)
        FREQ_LOW = 2
        FREQ_HIGH = 12
        xlim_l = FREQ_LOW
        xlim_r = FREQ_HIGH
        idx = [int(len(f) / f[-1] * xlim_l), int(len(f) / f[-1] * xlim_r)]
        f = f[idx[0] : idx[1]]
        df = f[1] - f[0]
        Cyx = Cyx[idx[0] : idx[1]]

        l = (len(x1) - noverlap) // (nfft - noverlap)
        z = 1 - np.power(0.05, 1 / (l - 1))
        # print("z: ", z)
        # print("significant points rate: ", len(Cyx[Cyx >= z]) / len(Cyx)) # 有意な値の割合
        Cyx = Cyx[Cyx >= z]
        # print(Cyx)
        coh = np.sum(Cyx) * df
        # print("coherence: ", coh)

        return coh


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()