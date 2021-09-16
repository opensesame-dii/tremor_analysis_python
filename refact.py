#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import makedirs, path, name
from io import BytesIO
# from shutil import rmtree
import matplotlib.pyplot as plt
from copy import deepcopy

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# from PIL import Image, ImageTk
import numpy as np
from scipy.signal import hamming, detrend
from matplotlib.mlab import cohere, window_hanning
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

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        #メインウィンドウの設定
        # root = tkinter.Tk()
        # root.title("tremor")
        self.title("tremor")

        if name == "nt":
            self.state("zoomed")
        elif name == "posix":
            self.attributes("-zoomed", "1")
        self.configure(bg="#778899")

     

        #情報フレームとグラフフレームの作成
        info_frame = tk.Frame(self, bg="#778899")
        img_frame = tk.Frame(self, bg="#778899")

        #データを選択するフレーム
        data_input_frame = ttk.Frame(info_frame,relief="groove",borderwidth=5)
        data_label1 = ttk.Label(
            data_input_frame,
            text="data1:"
            )
        data_label1.grid(row=0, column=0) 

        self.brows_button1 = ttk.Button(data_input_frame,text="Brows")
        self.brows_button1.bind("<ButtonPress>", self.file_dialog)
        self.brows_button1.grid(row=0, column=1)  

        self.clear_button = ttk.Button(data_input_frame,text="clear")
        self.clear_button.grid(row=0, column=2)

        data_label2 = ttk.Label(data_input_frame,text = "data2:")
        data_label2.grid(row=1, column=0)

        self.brows_button2 = ttk.Button(data_input_frame,text="Brows")
        self.brows_button2.bind("<ButtonPress>",self.file_dialog)
        self.brows_button2.grid(row=1, column=1)

        progress = ttk.Label(data_input_frame,text= "progress:")
        progress.grid(row=1, column=2)
        self.progress_bar = ttk.Label(data_input_frame,text= "--")
        self.progress_bar.grid(row=1, column=3)
        per = ttk.Label(data_input_frame,text = "%")
        per.grid(row=1, column=4)

        #モード選択
        settings_frame = ttk.Frame(info_frame,relief="groove")
        now_showing = ttk.Label(settings_frame,text="now showing:")
        now_showing.grid(row=0, column=0)
        analysis = ttk.Label(settings_frame, text="Analysis:")
        analysis.grid(row=1, column=0)
        sensor = ttk.Label(settings_frame, text="Sensor")
        sensor.grid(row=2, column=0)

        #この書き方（moduleを使う）は良くない気がする、、、
        module = ("data_list","mode_list","analysis","sensor_list")
        self.now_showing_box = ttk.Combobox(settings_frame, values=module[0], state="readonly")
        self.now_showing_box.grid(row=0, column=1)
        self.analysis_box = ttk.Combobox(settings_frame, values=module[2], state="readonly")
        self.analysis_box.grid(row=1, column=1)
        self.sensor_box = ttk.Combobox(settings_frame, values=module[3], state="readonly")
        self.sensor_box.grid(row=2, column=1)

        #settings
        settings_frame2 = ttk.Frame(info_frame,relief="groove")
        seg = ttk.Label(settings_frame2, text="Segment duration(s):")
        seg.grid(row=0, column=0)
        samp = ttk.Label(settings_frame2, text="Sampling rate(Hz):")
        samp.grid(row=1, column=0)
        frame_range = ttk.Label(settings_frame2, text="Frame range:")
        frame_range.grid(row=2, column=0)

        self.seg_txt = tk.Entry(settings_frame2,width=20,)
        self.seg_txt.grid(row=0, column=1)
        self.samp_txt = tk.Entry(settings_frame2, width=20)
        self.samp_txt.grid(row=1, column=1)
        self.range_txt1 = tk.Entry(settings_frame2, width=20)
        self.range_txt1.grid(row=2, column=1)
        self.range_txt2 = tk.Entry(settings_frame2,width=20)
        self.range_txt2.grid(row=2, column=3)
        self.range_to = ttk.Label(settings_frame2, text="to")
        self.range_to.grid(row=2, column=2)
        self.apply_button = ttk.Button(settings_frame2, text="Apply")
        self.apply_button.grid(row=3, column=0)

        #result
        result_frame = ttk.Frame(info_frame, relief="groove")

        self.clip = ttk.Button(result_frame, text="copy to clipboard")
        self.clip.grid(row=0, column=0,sticky=tk.W)

        #data出力のフレーム
        data1_frame = ttk.Frame(result_frame, relief="groove")
        data2_frame = ttk.Frame(result_frame, relief="groove")

        self.data_frames = [data1_frame,data2_frame]

        for data_ in self.data_frames:        
            spa = ttk.Label(data_, text="Spectrogram Peak Amplitude:")
            spa.grid(row=0, column=0)
            spf = ttk.Label(data_, text="Spectrogram Peak Frequency(Hz): ")
            spf.grid(row=1, column=0)
            spt = ttk.Label(data_, text = "Spectrogram Peak Time(s): ")
            spt.grid(row=2, column=0)
            wpa = ttk.Label(data_, text = "Whole Peak Amplitude: ")
            wpa.grid(row=3, column=0)
            wpf = ttk.Label(data_, text = "Whole Peak Frequency(Hz): ")
            wpf.grid(row=4, column=0)
            fhm = ttk.Label(data_, text = "Full-width Half Maximum(Hz): ")
            fhm.grid(row=5, column=0)
            hp = ttk.Label(data_, text = "Half-width Power: ")
            hp.grid(row=6, column=0)
            tsi = ttk.Label(data_, text = "Tremor Stability Index: ")
            tsi.grid(row=7, column=0)

            self.spa_txt = tk.Entry(data_,width=20)
            self.spa_txt.insert(tk.END,"None")
            self.spa_txt.grid(row=0, column=1)
            self.spf_txt = tk.Entry(data_, width=20)
            self.spf_txt.insert(tk.END,"None")
            self.spf_txt.grid(row=1, column=1)
            self.spt_txt = tk.Entry(data_,width=20)
            self.spt_txt.insert(tk.END,"None")
            self.spt_txt.grid(row=2, column=1)
            self.wpa_txt = tk.Entry(data_, width=20)
            self.wpa_txt.insert(tk.END,"None")
            self.wpa_txt.grid(row=3, column=1)
            self.wpf_txt = tk.Entry(data_, width=20)
            self.wpf_txt.insert(tk.END,"None")
            self.wpf_txt.grid(row=4, column=1)
            self.fhm_txt = tk.Entry(data_, width=20)
            self.fhm_txt.insert(tk.END,"None")
            self.fhm_txt.grid(row=5, column=1)
            self.hp_txt = tk.Entry(data_, width=20)
            self.hp_txt.insert(tk.END,"None")
            self.hp_txt.grid(row=6, column=1)
            self.tsi_txt = tk.Entry(data_, width=20)
            self.tsi_txt.insert(tk.END,"None")
            self.tsi_txt.grid(row=7, column=1)


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

        self.x_txt = tk.Entry(coherence_frame, width=20)
        self.x_txt.insert(tk.END,"None")
        self.x_txt.grid(row=0, column=1)
        self.y_txt = tk.Entry(coherence_frame, width=20)
        self.y_txt.insert(tk.END,"None")
        self.y_txt.grid(row=1, column=1)
        self.z_txt = tk.Entry(coherence_frame, width=20)
        self.z_txt.insert(tk.END,"None")
        self.z_txt.grid(row=2, column=1)
        self.norm_txt = tk.Entry(coherence_frame, width=20)
        self.norm_txt.insert(tk.END,"None")
        self.norm_txt.grid(row=3, column=1)


        #data previewのグラフ


        can = ttk.Frame(img_frame)
        fig = Figure(figsize = (10,3),dpi = 100)
        ax = fig.add_subplot(1,1,1)
        #line, =  ax.plot(x,y)
        self.canvas = FigureCanvasTkAgg(fig,can)
        self.canvas.draw()
        #canvas.get_tk_widget().grid(row=0, rowspan=4,column=1+1,sticky=tkinter.E)
        self.canvas.get_tk_widget().pack()
        toolbar1 = NavigationToolbar2Tk(self.canvas, can)

        can2 = ttk.Frame(img_frame)
        self.canvas2 = FigureCanvasTkAgg(fig, can2)
        self.canvas2.draw()
        self.canvas2.get_tk_widget().pack()
        toolbar2 = NavigationToolbar2Tk(self.canvas2, can2)
        #canvas2.get_tk_widget().grid(row=4, column=1)

        can3 = ttk.Frame(img_frame)

        can_x = ttk.Frame(can3)
        can_y = ttk.Frame(can3)
        can_z = ttk.Frame(can3)

        can_list = [can_x,can_y,can_z]
        for can_ in can_list:
            fig3 = Figure(figsize = (2.5,2.5),dpi = 100)
            ax = fig3.add_subplot(1,1,1)
            self.canvas_ = FigureCanvasTkAgg(fig3, can_)
            self.canvas_.draw()
            self.canvas_.get_tk_widget().pack()
            self.toolbar3 = NavigationToolbar2Tk(self.canvas_, can_)


        #フレームの配置
        info_frame.grid(row=0, column=0)
        img_frame.grid(row=0, column=1)
        data_input_frame.grid(row = 0, column=0, padx=10, pady=20,sticky=tk.W)
        settings_frame.grid(row=2, column=0, padx=10, pady=5,sticky=tk.W)
        settings_frame2.grid(row=3, column=0, padx=10, pady=5,sticky=tk.W)
        result_frame.grid(row=4, column=0,sticky=tk.W, padx=10)
        data1_frame.grid(row=1, column=0,sticky=tk.W,pady=10)
        data2_frame.grid(row=2, column=0,sticky=tk.W, pady=10)
        coherence_frame.grid(row=3,column=0, sticky=tk.W,pady=10)
        can.grid(row=0, column=0)
        can2.grid(row=1, column=0)
        can3.grid(row=2, column=0)
        can_x.grid(row=0, column=0)
        can_y.grid(row=0, column=1)
        can_z.grid(row=0, column=2)

        # root.mainloop()


        # number of sensor
        # e.g. 3 for "accelerometer, magnetmeter and gyroscope", 2 for "left arm and right arm"
        self.SENSORS_NUM = 3

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
        self.sensors = ["sensor" + str(i + 1) for i in range(self.SENSORS_NUM)] # "sensor1", "sensor2", ...
        
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

    #ファイルを選ぶ関数
    def file_dialog(self, event):
        ftypes =[('EXCELファイル/CSVファイル', '*.xlsx'),
            ('EXCELファイル/CSVファイル', '*.xlsm'),
            ('EXCELファイル/CSVファイル', '*.csv')]
        fname = filedialog.askopenfilename(filetypes=ftypes)
        print(fname)

    def stft(self, x, fs, nperseg, segment_duration, noverlap=None):
        """
        Params:
        data: array
            signal input
        fs: integer/float
            sampling rate
        segment_duration: integer/float
            stft segment duration(sec)
        nperseg: integer
            sample number per segment
        ---
        return: 
        s: ndarray
            stft result
        f: ndarray
            cyclical frequencies
        t: ndarray
            time instants
        """

        x_length = len(x)
        print("data length: {}".format(x_length))

        L = np.min((x_length, nperseg))
        nTimesSpectrogram = 500; 
        if (noverlap is None):
            noverlap = np.ceil(L - (x_length - L) / (nTimesSpectrogram - 1))
            noverlap = int(np.max((1,noverlap)))
        #nFFTMinimam = 2 ** 12
        nPad = np.max([2 ** int(np.ceil(np.log2(L))), 2 ** 12])
        print("nPad: {}".format(nPad))
        #print("noverlap: ", noverlap)
        # hamming window を使用
        window = hamming(nperseg)
        sum_window = np.sum(window)

        # セグメントがいくつあるか
        seg = int(np.ceil((x_length - noverlap) / (nperseg - noverlap)))
        #print(seg)
        # データを nperseg, noverlap に合う長さになるようゼロ埋め
        data = np.append(x, np.zeros(int(nperseg * seg - noverlap * (seg - 1) - x_length)))
        print("padded data length: {}".format(len(data)))  
        
        result = np.empty((0, nPad))
        for iter in range(seg):
            #seg_data = data[(nperseg - noverlap) * iter : (nperseg - noverlap) * iter + nperseg]
            seg_data = data[(nperseg - noverlap) * iter : (nperseg - noverlap) * iter + nperseg] * window
            
            # ゼロ埋めの方法3パターン→結果は変わらない?
            # どまんなかにデータ
            seg_data = np.append(np.zeros((nPad - nperseg) // 2), seg_data)
            seg_data = np.append(seg_data, np.zeros(nPad - len(seg_data)))
            

            """
            # ケツだけにゼロ
            seg_data = np.append(seg_data, np.zeros(nPad - nperseg))
            """

            """
            # アタマをゼロ
            seg_data = np.append(np.zeros(nPad - nperseg), seg_data)
            """
            # result = np.append(result, [np.fft.fft(seg_data)] * window, axis=0)
            result = np.append(result, [np.fft.fft(seg_data)], axis=0)
        # print("spectrogram shape: {}".format(result.shape))

        # 20Hzまでを出力
        max_f = 20
        # print(len(data) / fs - segment_duration / 2)
        if (x_length - len(data)) < 0:
            t = np.linspace(segment_duration / 2, len(data) / fs - segment_duration / 2, result.shape[0] + (len(data) - x_length))[0:x_length - len(data)]
        else:
            t = np.linspace(segment_duration / 2, len(data) / fs - segment_duration / 2, result.shape[0] + (len(data) - x_length))
        return result.T[0:int(nPad / fs * max_f), :] * 2 / sum_window, np.linspace(0, max_f, int(nPad / fs * max_f)), t


    def spectrogram_analize(self, data_i, fs, nperseg, filename, sensor, start=0, end=-1):
        """
        Params
        data: array(3, n)
            x, y, z data
        fs: int/float
            sampling rate
        nperseg: int
            sample number per stft segment
        filename: str
            filename
        sensor: str
            sensor name
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

        print("nperseg: {}".format(nperseg))


        specs = []
        for i in range(3):
            # start = time.time()
            spec, f, t = np.abs(self.stft(detrend(data[i]), fs, self.segment_duration_sec, int(nperseg)))
            specs.append(spec)
            # elapsed_time = time.time() - start
            # print ("elapsed_time:\n{0}".format(elapsed_time))
        # convert to 3-dimensional ndarray
        specs = np.array(specs) #specs.shape: (3, 640, 527)
        vmin = np.min(specs)
        vmax = np.max(specs)
        # add norm
        specs = np.append(specs, [np.linalg.norm(specs, axis=0)], axis=0)

        for ax in range(3):
            """
            plt.figure(dpi=dpi, figsize=narrow_figsize)
            plt.pcolormesh(t, f, specs[ax], cmap="jet", vmin=vmin, vmax=vmax)
            plt.ylabel("Frequency [Hz]")
            plt.xlabel("Time [sec]")
            cbar = plt.colorbar()
            cbar.ax.set_ylabel("Intensity [dB]")
            #cbar.set_clim(0, 1.1) #plt3.2まで
            #cbar.mappable.set_clim(0, 1.1) #plt3.3以降
            #plt.show()
            #### plt.savefig(data_dir + "/" + remove_ext(filename) + str(ax) + sensor + "sp.png")
            plt.close()
            #print("saved: ", data_dir + "/" + remove_ext(filename) + str(ax) + sensor + "sp.png")
            """
        """
        plt.figure(dpi=dpi, figsize=wide_figsize)
        plt.pcolormesh(t, f, specs[3], cmap="jet")
        plt.ylabel("Frequency [Hz]")
        plt.xlabel("Time [sec]")
        cbar = plt.colorbar()
        cbar.ax.set_ylabel("Intensity [dB]")
        #cbar.set_clim(0, 1.1) #plt3.2まで
        #cbar.mappable.set_clim(0, 1.1) #plt3.3以降
        #plt.show()
        #### plt.savefig(data_dir + "/" + remove_ext(filename) + "norm" + sensor + "sp.png")
        plt.close()
        """
        recording = len(data[0]) / fs
        f_offset = int(specs.shape[2] * 2 / 20)
        # print("s t {} {}".format(t[0], t[-1]))
        peak_amp = np.max(specs[3, f_offset:, :])
        peak_idx = np.where(specs[3] == peak_amp)
        peak_freq = f[peak_idx[0][0]]
        peak_time = t[peak_idx[1][0]]

        print("=" * 20)

        print("recording(s): {}".format(recording))
        print("peak amplitude: {}  {}".format(peak_amp, peak_idx))
        print("peak frequency(Hz): {}".format(peak_freq))
        print("peaktime(s): {}".format(peak_time))

        print("=" * 20)

        return peak_amp, peak_freq, peak_time

    def power_density_analize(self, data_i, fs, nperseg, filename, sensor, start=0, end=-1):
        """
        Params
        data: array(3, n)
            x, y, z data
        fs: int/float
            sampling rate
        nperseg: int
            sample number per stft segment
        filename: str
            filename
        sensor: str
            sensor name
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
        print("nperseg: {}".format(nperseg))


        specs = []
        for i in range(3):
            #################################################################################
            # matlab の detrend の結果と, scipyのdetrend の結果を比較→一致すれば, stftを使いまわして2乗して時間での平均を出せば多分いける
            # scipy の scipy.signal.detrend() が使えるらしい(絶対誤差0.0001以下)
            spec, f, t = self.stft(detrend(data[i]), fs, self.segment_duration_sec, int(nperseg), int(nperseg * 0.75))
            specs.append(np.sum(np.power(np.abs(spec), 1), axis=1) / (len(t)))
            
        # convert to 3-dimensional ndarray
        specs = np.array(specs) #specs.shape: (3, 640)
        #specs /= np.sum(np.power(signal.tukey(int(nperseg)), 2)) / np.power(np.sum(signal.tukey(int(nperseg))), 2)
        vmin = np.min(specs)
        vmax = np.max(specs)
        
        # add norm
        specs = np.append(specs, [np.linalg.norm(specs, axis=0)], axis=0)

        for i in range(3):
            """
            plt.figure(dpi=dpi, figsize=narrow_figsize)
            plt.ylim(0, vmax * 1.2)
            plt.plot(f, specs[i])
            #plt.show()
            #### plt.savefig(data_dir + "/" + remove_ext(filename) + str(i) + sensor + "am.png")
            plt.close()
            """
        """
        plt.figure(dpi=dpi, figsize=wide_figsize)
        plt.ylim(0, np.max(specs[3]) * 1.05)
        plt.plot(f, specs[3])
        """
        l, u, lv, uv, hwp = self.full_width_half_maximum(f, specs[3])
        fwhm = uv - lv
        print(l, u, lv, uv)
        print(specs[3, int(l)])
        plt.fill_between(f[l:u], specs[3, l:u], color="r", alpha=0.5)
        #plt.show()
        #### plt.savefig(data_dir + "/" + remove_ext(filename) + "norm" + sensor + "am.png")
        plt.close()
        recording = len(data[0]) / fs
        f_offset = int(specs.shape[1] * 2 / 20)
        
        peak_amp = np.max(specs[3, f_offset:])
        peak_idx = np.where(specs[3] == peak_amp)
        peak_freq = f[peak_idx[0][0]]
        tsi = self.tremor_stability_index(data[0], fs)

        print("=" * 20)

        print("recording(s): {}".format(recording))
        print("peak amplitude: {}  {}".format(peak_amp, peak_idx))
        print("peak frequency(Hz): {}".format(peak_freq))
        print("Full-width Half Maximum(Hz): {}".format(fwhm))
        print("Half-width power: {}".format(hwp))
        print("Tremor Stability Index: {}".format(tsi))

        print("=" * 20)

        return peak_amp, peak_freq, fwhm, hwp, tsi

    def wavelet_analize(self):
        pass

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
        print(peak_idx)
        lower = peak_idx
        upper = peak_idx

        ###########################
        # spline 補間 を使いたいか?

        while (y_ndarray[lower] > peak_val_half and lower >= 0):
            lower -= 1
        if (y_ndarray[lower] != peak_val_half):
            lower_v = (x[lower] + x[lower + 1]) / 2 # ピークの半分を跨いだ場合は中央値を取る
        else:
            lower_v = x[lower]

        while (y_ndarray[upper] > peak_val_half and upper <= length):
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

        plt.boxplot(delta_freq, showmeans=True, vert=False
        #, whis="range"
        )
        plt.xlabel("delta-f")
        plt.close()
        #plt.show()

        # 四分位範囲
        q75, q25 = np.percentile(delta_freq, [75 ,25])
        return q75 - q25

    def coherence(self, data1, data2, fs, start=0, end=-1):
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
        plt.ylim(0, 1)
        plt.xlim(xlim_l, xlim_r)
        plt.xlabel("Frequency[Hz]")
        plt.plot(f, Cyx)
        #plt.show()
        plt.close()

        l = (len(x1) - noverlap) // (nfft - noverlap)
        z = 1 - np.power(0.05, 1 / (l - 1))
        print("z: ", z)
        print("significant points rate: ", len(Cyx[Cyx >= z]) / len(Cyx)) # 有意な値の割合
        Cyx = Cyx[Cyx >= z]
        # print(Cyx)
        coh = np.sum(Cyx) * df
        print("coherence: ", coh)
        return coh

    def update(self):
        pass



if __name__ == "__main__":
    app = MainApp()
    app.mainloop()

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
"""