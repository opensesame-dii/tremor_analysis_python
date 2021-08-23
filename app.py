# coding:utf-8

import os, shutil
from io import BytesIO
from PIL import Image, ImageTk
import numpy as np
#from numpy.core.fromnumeric import _shape_dispatcher
from scipy import signal
import matplotlib.pyplot as plt
import matplotlib as m
from matplotlib import mlab
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import matplotlib
import pandas as pd
matplotlib.use('TkAgg')

FREQ_LOW = 2
FREQ_HIGH = 12

data_dir = ".gui_data"
dpi = 97
wide_figsize = (12, 3)
wide_figsize_dots = (wide_figsize[0] * dpi, wide_figsize[1] * dpi)
narrow_figsize = (4, 3)
narrow_figsize_dots = (narrow_figsize[0] * dpi, narrow_figsize[1] * dpi)
#データ置き場を作成
try:
    shutil.rmtree(data_dir)
except:
    pass
os.makedirs(data_dir)
plt.figure(dpi=dpi, figsize=wide_figsize)
plt.savefig(data_dir + "/init.png")
plt.close()
plt.figure(dpi=dpi, figsize=narrow_figsize)
plt.savefig(data_dir + "/init_s.png")
plt.close()

#filename = "sample-data"
#filename = "ActiGraphdata_csv.csv"
#filename = "sample-data/Tsuboi Tremor Sample.csv"
#filename = "sample-data/csv2.csv"
#filename = "trial/f4a6.csv"
#data = np.loadtxt(filename, delimiter=",", dtype=np.float64, skiprows=1)

fs = 128
segment_duration = 5

def remove_ext(filename):
    return os.path.splitext(os.path.basename(filename))[0]


def stft(x, fs, nperseg, noverlap=None):
    """
    Params:
    data: array
        signal input
    fs: integer/float
        sampling rate
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
    # tukey window を使用
    window = signal.tukey(nperseg)
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
    print("spectrogram shape: {}".format(result.shape))

    # 20Hzまでを出力
    max_f = 20
    print(len(data) / fs - segment_duration / 2)
    if (x_length - len(data)) < 0:
        t = np.linspace(segment_duration / 2, len(data) / fs - segment_duration / 2, result.shape[0] + (len(data) - x_length))[0:x_length - len(data)]
    else:
        t = np.linspace(segment_duration / 2, len(data) / fs - segment_duration / 2, result.shape[0] + (len(data) - x_length))
    return result.T[0:int(nPad / fs * max_f), :] * 2 / sum_window, np.linspace(0, max_f, int(nPad / fs * max_f)), t


def spectrogram_analize(data_i, fs, nperseg, filename, sensor, start=0, end=-1):
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
        sg.Popup("invalid range setting")
        return None, None, None

    data = data_i[:, start: end + 1]

    print("nperseg: {}".format(nperseg))


    specs = []
    for i in range(3):
        spec, f, t = np.abs(stft(signal.detrend(data[i]), fs, int(nperseg)))
        specs.append(spec)
    # convert to 3-dimensional ndarray
    specs = np.array(specs) #specs.shape: (3, 640, 527)
    vmin = np.min(specs)
    vmax = np.max(specs)
    # add norm
    specs = np.append(specs, [np.linalg.norm(specs, axis=0)], axis=0)

    for ax in range(3):
        plt.figure(dpi=dpi, figsize=narrow_figsize)
        plt.pcolormesh(t, f, specs[ax], cmap="jet", vmin=vmin, vmax=vmax)
        plt.ylabel("Frequency [Hz]")
        plt.xlabel("Time [sec]")
        cbar = plt.colorbar()
        cbar.ax.set_ylabel("Intensity [dB]")
        #cbar.set_clim(0, 1.1) #plt3.2まで
        #cbar.mappable.set_clim(0, 1.1) #plt3.3以降
        #plt.show()
        plt.savefig(data_dir + "/" + remove_ext(filename) + str(ax) + sensor + "sp.png")
        plt.close()
        #print("saved: ", data_dir + "/" + remove_ext(filename) + str(ax) + sensor + "sp.png")

    plt.figure(dpi=dpi, figsize=wide_figsize)
    plt.pcolormesh(t, f, specs[3], cmap="jet")
    plt.ylabel("Frequency [Hz]")
    plt.xlabel("Time [sec]")
    cbar = plt.colorbar()
    cbar.ax.set_ylabel("Intensity [dB]")
    #cbar.set_clim(0, 1.1) #plt3.2まで
    #cbar.mappable.set_clim(0, 1.1) #plt3.3以降
    #plt.show()
    plt.savefig(data_dir + "/" + remove_ext(filename) + "norm" + sensor + "sp.png")
    plt.close()

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

def power_density_analize(data_i, fs, nperseg, filename, sensor, start=0, end=-1):
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
        sg.Popup("invalid range setting")
        return None, None, None

    data = data_i[:, start: end + 1]
    print("nperseg: {}".format(nperseg))


    specs = []
    for i in range(3):
        #################################################################################
        # matlab の detrend の結果と, scipyのdetrend の結果を比較→一致すれば, stftを使いまわして2乗して時間での平均を出せば多分いける
        # scipy の scipy.signal.detrend() が使えるらしい(絶対誤差0.0001以下)
        spec, f, t = stft(signal.detrend(data[i]), fs, int(nperseg), int(nperseg * 0.75))
        specs.append(np.sum(np.power(np.abs(spec), 1), axis=1) / (len(t)))
        
    # convert to 3-dimensional ndarray
    specs = np.array(specs) #specs.shape: (3, 640)
    #specs /= np.sum(np.power(signal.tukey(int(nperseg)), 2)) / np.power(np.sum(signal.tukey(int(nperseg))), 2)
    vmin = np.min(specs)
    vmax = np.max(specs)
    
    # add norm
    specs = np.append(specs, [np.linalg.norm(specs, axis=0)], axis=0)

    for i in range(3):
        plt.figure(dpi=dpi, figsize=narrow_figsize)
        plt.ylim(0, vmax * 1.2)
        plt.plot(f, specs[i])
        #plt.show()
        plt.savefig(data_dir + "/" + remove_ext(filename) + str(i) + sensor + "am.png")
        plt.close()
    plt.figure(dpi=dpi, figsize=wide_figsize)
    plt.ylim(0, np.max(specs[3]) * 1.05)
    plt.plot(f, specs[3])
    l, u, lv, uv, hwp = FullWidthHalfMaximum(f, specs[3])
    fwhm = uv - lv
    print(l, u, lv, uv)
    print(specs[3, int(l)])
    plt.fill_between(f[l:u], specs[3, l:u], color="r", alpha=0.5)
    #plt.show()
    plt.savefig(data_dir + "/" + remove_ext(filename) + "norm" + sensor + "am.png")
    plt.close()

    recording = len(data[0]) / fs
    f_offset = int(specs.shape[1] * 2 / 20)
    
    peak_amp = np.max(specs[3, f_offset:])
    peak_idx = np.where(specs[3] == peak_amp)
    peak_freq = f[peak_idx[0][0]]
    tsi = TremorStabilityIndex(data[0], fs)

    print("=" * 20)

    print("recording(s): {}".format(recording))
    print("peak amplitude: {}  {}".format(peak_amp, peak_idx))
    print("peak frequency(Hz): {}".format(peak_freq))
    print("Full-width Half Maximum(Hz): {}".format(fwhm))
    print("Half-width power: {}".format(hwp))
    print("Tremor Stability Index: {}".format(tsi))

    print("=" * 20)

    return peak_amp, peak_freq, fwhm, hwp, tsi
    

def FullWidthHalfMaximum(x, y):
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
    
def TremorStabilityIndex(x, fs):
    """
    Tremor Stability Index

    Params
    x: array-like
        data
    fs: int/float
        sampling rate
    """
    x_detrend = signal.detrend(x)
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

def coherence(data1, data2, fs, start=0, end=-1):
    """
    now developing
    """
    if (len(data1) != len(data2)):
        sg.Popup("data1 and data2 have different lengths")
        return None

    if (end == -1):
        end = len(data1) - 1
    elif (start > end):
        sg.Popup("invalid range setting")
        return None

    x1 = data1[start: end + 1]
    x2 = data2[start: end + 1]

    nfft = 2 ** 10
    noverlap = 2 ** 9
    Cyx, f = mlab.cohere(x2, x1, NFFT=nfft, Fs=fs,
                window=mlab.window_hanning, noverlap=noverlap)
    
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


"""
file_num = "4"
print("sample" + file_num)
df1 = pd.read_csv("sample-data/sample" + file_num + "a.csv", header=None, skiprows=10, index_col=0, encoding="shift jis")
npdata1=np.array(df1.values.flatten())
nparray1=np.reshape(npdata1,(df1.shape[0],df1.shape[1]))

df2 = pd.read_csv("sample-data/sample" + file_num + "b.csv", header=None, skiprows=10, index_col=0, encoding="shift jis")
npdata2=np.array(df2.values.flatten())
nparray2=np.reshape(npdata2,(df2.shape[0],df2.shape[1]))

coherence(nparray1[:,0], nparray2[:,0], 200)

plt.plot(nparray1[:,0])
plt.plot(nparray2[:,0])
plt.show()
"""

"""
data_preview_fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
# https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Matplotlib.py
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg
"""

def get_img_data(f, maxsize=(1200, 850)):
    """Generate image data using PIL
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

def update_status(sg_window, event, values, shared_data):
    sg_window["progress"].update("00%")
    print(event)
    file1_name = values["input1"]
    file2_name = values["input2"]
    # zoom_rate = values["preview_zoom"]

    need_update_preview = False
    need_update_calculation = False
    need_update_outputs = False
    data1_updated = False
    data2_updated = False

    #sg_window["text1"].update(file1_name)
    #t = np.arange(0, 3, .01)
    #data_preview_fig.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))
    #fig_canvas_agg = draw_figure(sg_window['-CANVAS-'].TKCanvas, data_preview_fig)
    
    # sg_window["data_preview"].update(data=get_img_data(file1_name))
    
    # when file1 updated
    if (event == "input1" and file1_name != "" and file1_name != shared_data.data1_file_name):
        try:
            df1 = pd.read_csv(file1_name, header=None, skiprows=10, index_col=0, encoding="shift jis")
            npdata1=np.array(df1.values.flatten())
            shared_data.data1 = np.reshape(npdata1,(df1.shape[0],df1.shape[1]))
            shared_data.data1_file_name = file1_name
            print(file1_name)
            need_update_preview = True
            need_update_calculation = True
            need_update_outputs = True
            data1_updated = True

            for i in range(9):
                if (detect_data_warning(shared_data.data1[:,i])):
                    sg.Popup("Warning: data at column {} may go off the scale".format(i+1))
                
        except FileNotFoundError:
            sg.Popup("Error: file not found")
            
    # when file2 updated
    if (event == "input2" and file2_name != "" and file2_name != shared_data.data2_file_name):
        try:
            df2 = pd.read_csv(file2_name, header=None, skiprows=10, index_col=0, encoding="shift jis")
            npdata2=np.array(df2.values.flatten())
            shared_data.data2 = np.reshape(npdata2,(df2.shape[0],df2.shape[1]))
            shared_data.data2_file_name = file2_name
            print(file2_name)
            need_update_preview = True
            need_update_calculation = True
            need_update_outputs = True
            data2_updated = True

        except FileNotFoundError:
            sg.Popup("Error: file not found")

    if (event == "sensor_select"):
        shared_data.sensor = values["sensor_select"]
        need_update_preview = True
        need_update_outputs = True

    elif (event == "data_select"):
        shared_data.data_using = values["data_select"]
        need_update_preview = True
        need_update_outputs = True
    
    elif (event == "window_selection"):
        shared_data.window = values["window_selection"]
        need_update_calculation = True
        need_update_outputs = True
        print("window")
    elif (event == "mode_select"):
        shared_data.mode = values["mode_select"]
        need_update_outputs = True

    elif (event == "clear_data"):
        shared_data.__init__()
        need_update_outputs = True
        need_update_calculation = True
        need_update_preview = True
        sg_window["sp_peak_amp1"].update("None")
        sg_window["sp_peak_freq1"].update("None")
        sg_window["sp_peak_time1"].update("None")
        sg_window["wh_peak_amp1"].update("None")
        sg_window["wh_peak_freq1"].update("None")
        sg_window["fwhm1"].update("None")
        sg_window["hwp1"].update("None")
        sg_window["tsi1"].update("None")

        sg_window["sp_peak_amp2"].update("None")
        sg_window["sp_peak_freq2"].update("None")
        sg_window["sp_peak_time2"].update("None")
        sg_window["wh_peak_amp2"].update("None")
        sg_window["wh_peak_freq2"].update("None")
        sg_window["fwhm2"].update("None")
        sg_window["hwp2"].update("None")
        sg_window["tsi2"].update("None")

        sg_window["coh_x"].update("None")
        sg_window["coh_y"].update("None")
        sg_window["coh_z"].update("None")
        sg_window["coh_norm"].update("None")

        sg_window["fig_norm"].update(data=get_img_data(data_dir + "/init.png"))
        sg_window["fig_x"].update(data=get_img_data(data_dir + "/init_s.png"))
        sg_window["fig_y"].update(data=get_img_data(data_dir + "/init_s.png"))
        sg_window["fig_z"].update(data=get_img_data(data_dir + "/init_s.png"))

    elif(event == "popup_preview"):
        if (eval("shared_data." + shared_data.data_using) is not None):
            for i in shared_data.sensor_dic[shared_data.sensor]:
                plt.plot(eval("shared_data." + shared_data.data_using)[:,i])
            plt.legend(labels=["x", "y", "z"])
            plt.show()
            plt.close()
        else:
            sg.popup(shared_data.data_using + " is not loaded")

    elif(event == "copy_to_clipboard"):
        sensor_idx = str(shared_data.sensor_lst.index(shared_data.sensor))
        
        sg_window.FindElement('-MULTILINE-').Update(
            str(eval("shared_data.data1_" + sensor_idx + "_peak_amp")) + "\n" + \
            str(eval("shared_data.data1_" + sensor_idx + "_peak_freq")) + "\n" + \
            str(eval("shared_data.data1_" + sensor_idx + "_peak_time")) + "\n" + \
            str(eval("shared_data.data1_" + sensor_idx + "_wh_peak_amp")) + "\n" + \
            str(eval("shared_data.data1_" + sensor_idx + "_wh_peak_freq")) + "\n" + \
            str(eval("shared_data.data1_" + sensor_idx + "_fwhm")) + "\n" + \
            str(eval("shared_data.data1_" + sensor_idx + "_hwp")) + "\n" + \
            str(eval("shared_data.data1_" + sensor_idx + "_tsi")) + "\n" + \
            str(eval("shared_data.data2_" + sensor_idx + "_peak_amp")) + "\n" + \
            str(eval("shared_data.data2_" + sensor_idx + "_peak_freq")) + "\n" + \
            str(eval("shared_data.data2_" + sensor_idx + "_peak_time")) + "\n" + \
            str(eval("shared_data.data2_" + sensor_idx + "_wh_peak_amp")) + "\n" + \
            str(eval("shared_data.data2_" + sensor_idx + "_wh_peak_freq")) + "\n" + \
            str(eval("shared_data.data2_" + sensor_idx + "_fwhm")) + "\n" + \
            str(eval("shared_data.data2_" + sensor_idx + "_hwp")) + "\n" + \
            str(eval("shared_data.data2_" + sensor_idx + "_tsi")) + "\n" + \
            str(eval("shared_data.coh" + sensor_idx)) + "\n" + \
            str(eval("shared_data.coh" + sensor_idx + "_0")) + "\n" + \
            str(eval("shared_data.coh" + sensor_idx + "_1")) + "\n" + \
            str(eval("shared_data.coh" + sensor_idx + "_2"))
        )
        sg_window.FindElement('-MULTILINE-').Widget.clipboard_clear()
        sg_window.FindElement('-MULTILINE-').Widget.clipboard_append( sg_window.FindElement('-MULTILINE-').Get())

    elif (event == "settings_updated"):
        if (shared_data.segment_duration_sec != int(values["segment_duration_sec"])):
            shared_data.segment_duration_sec = int(values["segment_duration_sec"])
            need_update_calculation = True
            need_update_outputs = True
        if (shared_data.sampling_rate != int(values["sampling_rate"])):
            shared_data.sampling_rate = int(values["sampling_rate"])
            need_update_calculation = True
            need_update_outputs = True
        print(int(values["range_start"]))
        print(shared_data.range_start)
        if (shared_data.range_start != int(values["range_start"])):
            shared_data.range_start = int(values["range_start"])
            need_update_calculation = True
            need_update_outputs = True
        if (shared_data.range_end != int(values["range_end"])):
            shared_data.range_end = int(values["range_end"])
            need_update_calculation = True
            need_update_outputs = True

    if (need_update_preview):
        if (eval("shared_data." + shared_data.data_using) is not None):
            plt.figure(dpi=97, figsize=wide_figsize)
            #plt.figure(dpi=97, figsize=shared_data.zoom_dic[shared_data.zoom_rate])

            for j in shared_data.sensor_dic[shared_data.sensor]:
                    plt.plot(eval("shared_data." + shared_data.data_using)[:,j])
            plt.legend(labels=["x", "y", "z"])
            plt.savefig(data_dir + "/" + "preview.png")
            plt.close()
            sg_window["data_preview"].update(data=get_img_data(data_dir + "/preview.png"))
            #sg_window["data_preview"].update(data=get_img_data(data_dir + "/preview.png"), size=(shared_data.zoom_dic[shared_data.zoom_rate][0] * dpi, shared_data.zoom_dic[shared_data.zoom_rate][1] * dpi))
        else:
            sg_window["data_preview"].update(data=get_img_data(data_dir + "/init.png"))

    if (need_update_calculation):

            
        if (data1_updated):
            i = 1
            if(eval("shared_data.data" + str(i)) is not None and eval("shared_data.data" + str(i) + "_file_name") is not None):
                for j in range(3):
                    sg_window["progress"].update(str((j + 1) * 30) + "%")
                    a, f, t = spectrogram_analize(eval("shared_data.data" + str(i))[:, j*3: j*3 + 3].T, shared_data.sampling_rate, shared_data.sampling_rate * shared_data.segment_duration_sec, eval("shared_data.data" + str(i) + "_file_name"), shared_data.sensor_lst[j], start=shared_data.range_start, end=shared_data.range_end)
                    exec("shared_data.data" + str(i) + "_" + str(j) + "_peak_amp = a")
                    exec("shared_data.data" + str(i) + "_" + str(j) + "_peak_freq = f")
                    exec("shared_data.data" + str(i) + "_" + str(j) + "_peak_time = t")
                    a, f, fwhm, hwp, tsi = power_density_analize(eval("shared_data.data" + str(i))[:, j*3: j*3 + 3].T, shared_data.sampling_rate, shared_data.sampling_rate * shared_data.segment_duration_sec, eval("shared_data.data" + str(i) + "_file_name"), shared_data.sensor_lst[j], start=shared_data.range_start, end=shared_data.range_end)
                    exec("shared_data.data" + str(i) + "_" + str(j) + "_wh_peak_amp = a")
                    exec("shared_data.data" + str(i) + "_" + str(j) + "_wh_peak_freq = f")
                    exec("shared_data.data" + str(i) + "_" + str(j) + "_fwhm = fwhm")
                    exec("shared_data.data" + str(i) + "_" + str(j) + "_hwp = hwp")
                    exec("shared_data.data" + str(i) + "_" + str(j) + "_tsi = tsi")

        if(data2_updated):
            i = 2
            if(eval("shared_data.data" + str(i)) is not None and eval("shared_data.data" + str(i) + "_file_name") is not None):
                for j in range(3):
                    sg_window["progress"].update(str((j + 1) * 30) + "%")
                    a, f, t = spectrogram_analize(eval("shared_data.data" + str(i))[:, j*3: j*3 + 3].T, shared_data.sampling_rate, shared_data.sampling_rate * shared_data.segment_duration_sec, eval("shared_data.data" + str(i) + "_file_name"), shared_data.sensor_lst[j], start=shared_data.range_start, end=shared_data.range_end)
                    exec("shared_data.data" + str(i) + "_" + str(j) + "_peak_amp = a")
                    exec("shared_data.data" + str(i) + "_" + str(j) + "_peak_freq = f")
                    exec("shared_data.data" + str(i) + "_" + str(j) + "_peak_time = t")
                    a, f, fwhm, hwp, tsi = power_density_analize(eval("shared_data.data" + str(i))[:, j*3: j*3 + 3].T, shared_data.sampling_rate, shared_data.sampling_rate * shared_data.segment_duration_sec, eval("shared_data.data" + str(i) + "_file_name"), shared_data.sensor_lst[j], start=shared_data.range_start, end=shared_data.range_end)
                    exec("shared_data.data" + str(i) + "_" + str(j) + "_wh_peak_amp = a")
                    exec("shared_data.data" + str(i) + "_" + str(j) + "_wh_peak_freq = f")
                    exec("shared_data.data" + str(i) + "_" + str(j) + "_fwhm = fwhm")
                    exec("shared_data.data" + str(i) + "_" + str(j) + "_hwp = hwp")
                    exec("shared_data.data" + str(i) + "_" + str(j) + "_tsi = tsi")
        if(not data1_updated and not data2_updated):
            for i in range(1, 3):
                if(eval("shared_data.data" + str(i)) is not None and eval("shared_data.data" + str(i) + "_file_name") is not None):
                    for j in range(3):
                        sg_window["progress"].update(str((j + 1) * i * 15) + "%")
                        a, f, t = spectrogram_analize(eval("shared_data.data" + str(i))[:, j*3: j*3 + 3].T, shared_data.sampling_rate, shared_data.sampling_rate * shared_data.segment_duration_sec, eval("shared_data.data" + str(i) + "_file_name"), shared_data.sensor_lst[j], start=shared_data.range_start, end=shared_data.range_end)
                        exec("shared_data.data" + str(i) + "_" + str(j) + "_peak_amp = a")
                        exec("shared_data.data" + str(i) + "_" + str(j) + "_peak_freq = f")
                        exec("shared_data.data" + str(i) + "_" + str(j) + "_peak_time = t")
                        a, f, fwhm, hwp, tsi = power_density_analize(eval("shared_data.data" + str(i))[:, j*3: j*3 + 3].T, shared_data.sampling_rate, shared_data.sampling_rate * shared_data.segment_duration_sec, eval("shared_data.data" + str(i) + "_file_name"), shared_data.sensor_lst[j], start=shared_data.range_start, end=shared_data.range_end)
                        exec("shared_data.data" + str(i) + "_" + str(j) + "_wh_peak_amp = a")
                        exec("shared_data.data" + str(i) + "_" + str(j) + "_wh_peak_freq = f")
                        exec("shared_data.data" + str(i) + "_" + str(j) + "_fwhm = fwhm")
                        exec("shared_data.data" + str(i) + "_" + str(j) + "_hwp = hwp")
                        exec("shared_data.data" + str(i) + "_" + str(j) + "_tsi = tsi")

        if (shared_data.data1 is not None and shared_data.data2 is not None):
            # coherence update
            for i in range(3):
                for j in range(3):
                    exec("shared_data.coh" + str(i) + "_" + str(j) + " = coherence(shared_data.data1[:, 3 * i + j], shared_data.data2[:, 3 * i + j], shared_data.sampling_rate)")
                exec("shared_data.coh" + str(i) + " = coherence(np.linalg.norm(shared_data.data1[:, 3 * i: 3 * i + 3], axis=1), np.linalg.norm(shared_data.data2[:, 3 * i: 3 * i + 3], axis=1), shared_data.sampling_rate)")


    if (need_update_outputs):
        if (eval("shared_data." + shared_data.data_using) is not None):
            
            # mode
            if (shared_data.mode == "Spectral Amplitude"):
                sg_window["fig_norm"].update(data=get_img_data(data_dir + "/" + remove_ext(eval("shared_data." + shared_data.data_using + "_file_name")) + "norm" + shared_data.sensor + "am.png"))
                sg_window["fig_x"].update(data=get_img_data(data_dir + "/" + remove_ext(eval("shared_data." + shared_data.data_using + "_file_name")) + "0" + shared_data.sensor + "am.png"))
                sg_window["fig_y"].update(data=get_img_data(data_dir + "/" + remove_ext(eval("shared_data." + shared_data.data_using + "_file_name")) + "1" + shared_data.sensor + "am.png"))
                sg_window["fig_z"].update(data=get_img_data(data_dir + "/" + remove_ext(eval("shared_data." + shared_data.data_using + "_file_name")) + "2" + shared_data.sensor + "am.png"))
            elif(shared_data.mode == "Spectrogram"):
                sg_window["fig_norm"].update(data=get_img_data(data_dir + "/" + remove_ext(eval("shared_data." + shared_data.data_using + "_file_name")) + "norm" + shared_data.sensor + "sp.png"))
                sg_window["fig_x"].update(data=get_img_data(data_dir + "/" + remove_ext(eval("shared_data." + shared_data.data_using + "_file_name")) + "0" + shared_data.sensor + "sp.png"))
                sg_window["fig_y"].update(data=get_img_data(data_dir + "/" + remove_ext(eval("shared_data." + shared_data.data_using + "_file_name")) + "1" + shared_data.sensor + "sp.png"))
                sg_window["fig_z"].update(data=get_img_data(data_dir + "/" + remove_ext(eval("shared_data." + shared_data.data_using + "_file_name")) + "2" + shared_data.sensor + "sp.png"))
        else:
            sg_window["fig_norm"].update(data=get_img_data(data_dir + "/init.png"))
            sg_window["fig_x"].update(data=get_img_data(data_dir + "/init_s.png"))
            sg_window["fig_y"].update(data=get_img_data(data_dir + "/init_s.png"))
            sg_window["fig_z"].update(data=get_img_data(data_dir + "/init_s.png"))

        if (shared_data.sensor == "Accelerometer"):
            sg_window["sp_peak_amp1"].update(shared_data.data1_0_peak_amp)
            sg_window["sp_peak_freq1"].update(shared_data.data1_0_peak_freq)
            sg_window["sp_peak_time1"].update(shared_data.data1_0_peak_time)
            sg_window["wh_peak_amp1"].update(shared_data.data1_0_wh_peak_amp)
            sg_window["wh_peak_freq1"].update(shared_data.data1_0_wh_peak_freq)
            sg_window["fwhm1"].update(shared_data.data1_0_fwhm)
            sg_window["hwp1"].update(shared_data.data1_0_hwp)
            sg_window["tsi1"].update(shared_data.data1_0_tsi)

            sg_window["sp_peak_amp2"].update(shared_data.data2_0_peak_amp)
            sg_window["sp_peak_freq2"].update(shared_data.data2_0_peak_freq)
            sg_window["sp_peak_time2"].update(shared_data.data2_0_peak_time)
            sg_window["wh_peak_amp2"].update(shared_data.data2_0_wh_peak_amp)
            sg_window["wh_peak_freq2"].update(shared_data.data2_0_wh_peak_freq)
            sg_window["fwhm2"].update(shared_data.data2_0_fwhm)
            sg_window["hwp2"].update(shared_data.data2_0_hwp)
            sg_window["tsi2"].update(shared_data.data2_0_tsi)

            if (shared_data.data1 is not None and shared_data.data2 is not None):
                # coherence show
                sg_window["coh_x"].update(shared_data.coh0_0)
                sg_window["coh_y"].update(shared_data.coh0_1)
                sg_window["coh_z"].update(shared_data.coh0_2)
                sg_window["coh_norm"].update(shared_data.coh0)
            else:
                sg_window["coh_x"].update("None")
                sg_window["coh_y"].update("None")
                sg_window["coh_z"].update("None")
                sg_window["coh_norm"].update("None")

        elif (shared_data.sensor == "magnetmeter"):
            sg_window["sp_peak_amp1"].update(shared_data.data1_1_peak_amp)
            sg_window["sp_peak_freq1"].update(shared_data.data1_1_peak_freq)
            sg_window["sp_peak_time1"].update(shared_data.data1_1_peak_time)
            sg_window["wh_peak_amp1"].update(shared_data.data1_1_wh_peak_amp)
            sg_window["wh_peak_freq1"].update(shared_data.data1_1_wh_peak_freq)
            sg_window["fwhm1"].update(shared_data.data1_1_fwhm)
            sg_window["hwp1"].update(shared_data.data1_1_hwp)
            sg_window["tsi1"].update(shared_data.data1_1_tsi)
            
            sg_window["sp_peak_amp2"].update(shared_data.data2_1_peak_amp)
            sg_window["sp_peak_freq2"].update(shared_data.data2_1_peak_freq)
            sg_window["sp_peak_time2"].update(shared_data.data2_1_peak_time)
            sg_window["wh_peak_amp2"].update(shared_data.data2_1_wh_peak_amp)
            sg_window["wh_peak_freq2"].update(shared_data.data2_1_wh_peak_freq)
            sg_window["fwhm2"].update(shared_data.data2_1_fwhm)
            sg_window["hwp2"].update(shared_data.data2_1_hwp)
            sg_window["tsi2"].update(shared_data.data2_1_tsi)

            if (shared_data.data1 is not None and shared_data.data2 is not None):
                # coherence show
                sg_window["coh_x"].update(shared_data.coh1_0)
                sg_window["coh_y"].update(shared_data.coh1_1)
                sg_window["coh_z"].update(shared_data.coh1_2)
                sg_window["coh_norm"].update(shared_data.coh1)
            else:
                sg_window["coh_x"].update("None")
                sg_window["coh_y"].update("None")
                sg_window["coh_z"].update("None")
                sg_window["coh_norm"].update("None")

        elif (shared_data.sensor == "Gyroscope"):
            sg_window["sp_peak_amp1"].update(shared_data.data1_2_peak_amp)
            sg_window["sp_peak_freq1"].update(shared_data.data1_2_peak_freq)
            sg_window["sp_peak_time1"].update(shared_data.data1_2_peak_time)
            sg_window["wh_peak_amp1"].update(shared_data.data1_2_wh_peak_amp)
            sg_window["wh_peak_freq1"].update(shared_data.data1_2_wh_peak_freq)
            sg_window["fwhm1"].update(shared_data.data1_2_fwhm)
            sg_window["hwp1"].update(shared_data.data1_2_hwp)
            sg_window["tsi1"].update(shared_data.data1_2_tsi)
            
            sg_window["sp_peak_amp2"].update(shared_data.data2_2_peak_amp)
            sg_window["sp_peak_freq2"].update(shared_data.data2_2_peak_freq)
            sg_window["sp_peak_time2"].update(shared_data.data2_2_peak_time)
            sg_window["wh_peak_amp2"].update(shared_data.data2_2_wh_peak_amp)
            sg_window["wh_peak_freq2"].update(shared_data.data2_2_wh_peak_freq)
            sg_window["fwhm2"].update(shared_data.data2_2_fwhm)
            sg_window["hwp2"].update(shared_data.data2_2_hwp)
            sg_window["tsi2"].update(shared_data.data2_2_tsi)

            if (shared_data.data1 is not None and shared_data.data2 is not None):
                # coherence show
                sg_window["coh_x"].update(shared_data.coh2_0)
                sg_window["coh_y"].update(shared_data.coh2_1)
                sg_window["coh_z"].update(shared_data.coh2_2)
                sg_window["coh_norm"].update(shared_data.coh2)
            else:
                sg_window["coh_x"].update("None")
                sg_window["coh_y"].update("None")
                sg_window["coh_z"].update("None")
                sg_window["coh_norm"].update("None")

    sg_window["progress"].update("--%")
#spectrogram_analize(data[:, 0:3].T, fs, segment_duration * fs)

#power_density_analize(data[:, 0:3].T, fs, segment_duration * fs)

class SharedData:
    def __init__(self):
        # self.zoom_lst = [1, 2, 5 ,10, 20]
        # self.zoom_dic = {}
        # for rate in self.zoom_lst:
        #     self.zoom_dic["x" + str(rate)] = (4 * rate, 3)
        self.data_lst = ["data1", "data2"]
        self.mode_lst = ["Spectral Amplitude", "Spectrogram"]
        self.sensor_lst = ["Accelerometer","magnetmeter", "Gyroscope"]
        self.sensor_dic = {}
        for i in range(len(self.sensor_lst)):
            self.sensor_dic[self.sensor_lst[i]] = (0 + i * 3, 1 + i * 3, 2 + i * 3)
        self.window_lst = [
            "barthann","bartlett","blackman","blackmanharris","bohman","boxcar","chebwin","cosine","flattop","gaussian","general_gaussian","hamming","hann","kaiser","nuttall","parzen","slepian","triang"
            ]

        self.range_start = 0
        self.range_end = -1

        self.data1 = None
        self.data2 = None
        self.data_using = self.data_lst[0]
        self.data1_file_name = None
        self.data2_file_name = None
        # self.zoom_rate = "x1"
        self.window = self.window_lst[0]
        self.mode = self.mode_lst[0]
        self.sensor = self.sensor_lst[0]
        self.segment_duration_sec = 5
        self.sampling_rate = 200

        self.data1_0_peak_amp = None
        self.data1_0_peak_freq = None
        self.data1_0_peak_time = None
        self.data1_0_wh_peak_amp = None
        self.data1_0_wh_peak_freq = None
        self.data1_0_fwhm = None
        self.data1_0_hwp = None
        self.data1_0_tsi = None
        
        self.data2_0_peak_amp = None
        self.data2_0_peak_freq = None
        self.data2_0_peak_time = None
        self.data2_0_wh_peak_amp = None
        self.data2_0_wh_peak_freq = None
        self.data2_0_fwhm = None
        self.data2_0_hwp = None
        self.data2_0_tsi = None

        self.data1_1_peak_amp = None
        self.data1_1_peak_freq = None
        self.data1_1_peak_time = None
        self.data1_1_wh_peak_amp = None
        self.data1_1_wh_peak_freq = None
        self.data1_1_fwhm = None
        self.data1_1_hwp = None
        self.data1_1_tsi = None
        
        self.data2_1_peak_amp = None
        self.data2_1_peak_freq = None
        self.data2_1_peak_time = None
        self.data2_1_wh_peak_amp = None
        self.data2_1_wh_peak_freq = None
        self.data2_1_fwhm = None
        self.data2_1_hwp = None
        self.data2_1_tsi = None

        self.data1_2_peak_amp = None
        self.data1_2_peak_freq = None
        self.data1_2_peak_time = None
        self.data1_2_wh_peak_amp = None
        self.data1_2_wh_peak_freq = None
        self.data1_2_fwhm = None
        self.data1_2_hwp = None
        self.data1_2_tsi = None
        
        self.data2_2_peak_amp = None
        self.data2_2_peak_freq = None
        self.data2_2_peak_time = None
        self.data2_2_wh_peak_amp = None
        self.data2_2_wh_peak_freq = None
        self.data2_2_fwhm = None
        self.data2_2_hwp = None
        self.data2_2_tsi = None

        self.coh0 = None # sensor1 norm
        self.coh0_0 = None # sensor1 x
        self.coh0_1 = None # sensor1 y
        self.coh0_2 = None # sensor1 z
        self.coh1 = None # sensor2 norm
        self.coh1_0 = None # sensor2 x
        self.coh1_1 = None # sensor2 y
        self.coh1_2 = None # sensor2 z
        self.coh2 = None # sensor3 norm
        self.coh2_0 = None # sensor3 x
        self.coh2_1 = None
        self.coh2_2 = None


shared_data = SharedData()

### GUI ###

small_size = (10, 1)
medium_size = (20, 1)
data_input_frame = sg.Frame(
    layout=[
        [sg.Text("data1: "), sg.InputText(key="input1", size=medium_size, enable_events=True, readonly=True, visible=False), sg.FileBrowse(key="file1", target="input1", file_types=(('EXCELファイル/CSVファイル', '*.xlsx'), ('EXCELファイル/CSVファイル', '*.xlsm'), ('EXCELファイル/CSVファイル', '*.csv')), enable_events=True), sg.Button("clear data", key="clear_data")],
        [sg.Text("data2: "), sg.InputText(key="input2", size=medium_size, enable_events=True, readonly=True, visible=False), sg.FileBrowse(key="file2", target="input2", file_types=(('EXCELファイル/CSVファイル', '*.xlsx'), ('EXCELファイル/CSVファイル', '*.xlsm'), ('EXCELファイル/CSVファイル', '*.csv')), enable_events=True), sg.Text("progress: "), sg.Text("--%", key="progress")]
    ], title="")

preview_frame = sg.Frame(
    layout=[
        [#sg.Combo(["x" + str(rate) for rate in shared_data.zoom_lst], key="preview_zoom", size=small_size, default_value="x1", readonly=True, enable_events=True),
        
        #sg.Column([[sg.Image(data=get_img_data(data_dir + "/init.png"), key="data_preview")]], size=(800, 300), scrollable=True)
        sg.Image(data=get_img_data(data_dir + "/init.png"), key="data_preview", size=wide_figsize_dots)
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
                [sg.Combo(shared_data.data_lst, key="data_select", size=medium_size, default_value=shared_data.data_using, enable_events=True, readonly=True)],
                [sg.Combo(
                    shared_data.window_lst, 
                    key="window_selection", size=medium_size, default_value="barthann", enable_events=True, readonly=True)
                    ],
                [sg.Combo(shared_data.mode_lst, key="mode_select", size=medium_size, default_value=shared_data.mode_lst[0], enable_events=True, readonly=True)],
                [sg.Combo(shared_data.sensor_lst, key="sensor_select", size=medium_size, default_value=shared_data.sensor_lst[0], enable_events=True, readonly=True)],
                
        ])]
    ], title=""
    )

"""
results1 = sg.Frame(layout=[
            [sg.Column([
                [sg.Text("Peak Amplitude: ")],
                [sg.Text("Peak Frequency(Hz): ")],
                [sg.Text("Peak Time(s): ")],
                [sg.Text("Full-width Half Maximum(Hz): ")],
                [sg.Text("Half-width Power: ")],
                [sg.Text("Tremor Stability Index: ")]
            ],
            sg.Column([
                [sg.InputText("--", key="peak_amp1")],
                [sg.InputText("--", key="peak_freq1")],
                [sg.InputText("--", key="peak_time1")],
                [sg.InputText("--", key="fwhm1")],
                [sg.InputText("--", key="hwp1")],
                [sg.InputText("--", key="tsi1")]
            ]))]
], title="data1")
"""
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
"""
results2 = sg.Frame(layout=[
            [sg.Column([
                [sg.Text("Peak Amplitude: ")],
                [sg.Text("Peak Frequency(Hz): ")],
                [sg.Text("Peak Time(s): ")],
                [sg.Text("Full-width Half Maximum(Hz): ")],
                [sg.Text("Half-width Power: ")],
                [sg.Text("Tremor Stability Index: ")]
            ],
            sg.Column([
                [sg.InputText("--", key="peak_amp2")],
                [sg.InputText("--", key="peak_freq2")],
                [sg.InputText("--", key="peak_time2")],
                [sg.InputText("--", key="fwhm2")],
                [sg.InputText("--", key="hwp2")],
                [sg.InputText("--", key="tsi2")]
            ]))]
], title="data2")
"""
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
"""
results3 = sg.Frame(layout=[
    [sg.Column([
        [sg.Text("coherence: ")],
        ],
    sg.Column([
        [sg.InputText("--", key="coh")],
    ]))] 
], title="common")
"""
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
        [sg.Image(data=get_img_data(data_dir + "/init.png"), key="fig_norm", size=wide_figsize_dots)],
        [
            sg.Image(data=get_img_data(data_dir + "/init_s.png"), key="fig_x", size=narrow_figsize_dots),
            sg.Image(data=get_img_data(data_dir + "/init_s.png"), key="fig_y", size=narrow_figsize_dots), 
            sg.Image(data=get_img_data(data_dir + "/init_s.png"), key="fig_z", size=narrow_figsize_dots)
        ]
    ], title="graph"
)

settings_frame2 = sg.Frame(
    layout=[
        [sg.Text("Segment duration(s): "), sg.InputText(default_text=shared_data.segment_duration_sec, key="segment_duration_sec", size=small_size, enable_events=False)],
        [sg.Text("Sampling rate(Hz): "), sg.InputText(default_text=shared_data.sampling_rate, key="sampling_rate", size=small_size, enable_events=False)],
        [sg.Text("Frame range: "), sg.InputText(default_text=0, key="range_start", size=small_size, enable_events=False), sg.Text(" to "), sg.InputText(default_text=-1, key="range_end", size=small_size, enable_events=False)],
        [sg.Button("Apply", key="settings_updated", enable_events=True)]
    ]
    , title="settings"
)
"""
settings_frame = sg.Frame(
    layout=[
        [
            sg.Column([
                [sg.Text("now showing: ")],
                [sg.Text("data window: ")],
                [sg.Text("Analysis: ")],
                [sg.Text("Sensor: ")],
                [sg.Text("Segment duration(s): ")],
                [sg.Text("Sampling rate(Hz): ")],
            ]),
            sg.Column([
                [sg.Combo(shared_data.data_lst, key="data_select", size=medium_size, default_value=shared_data.data_using, enable_events=True, readonly=True)],
                [sg.Combo(
                    shared_data.window_lst, 
                    key="window_selection", size=medium_size, default_value="barthann", enable_events=True, readonly=True)
                    ],
                [sg.Combo(shared_data.mode_lst, key="mode_select", size=medium_size, default_value=shared_data.mode_lst[0], enable_events=True, readonly=True)],
                [sg.Combo(shared_data.sensor_lst, key="sensor_select", size=medium_size, default_value=shared_data.sensor_lst[0], enable_events=True, readonly=True)],
                [sg.InputText(default_text=shared_data.segment_duration_sec, key="segment_duration_sec", size=small_size, enable_events=True)],
                [sg.InputText(default_text=shared_data.sampling_rate, key="sampling_rate", size=small_size, enable_events=True)]
        ])]
    ], title=""
    )
"""
"""
layout=[
    [sg.Column([[data_input_frame], [settings_frame]]), preview_frame],
    [results_wrapper, graph_wrapper]
]
"""
layout=[
    [sg.Column([[data_input_frame], [settings_frame], [settings_frame2], [results_wrapper]], scrollable=True), sg.Column([[preview_frame], [graph_wrapper]], scrollable=True)],
]
sg_window = sg.Window("tremor analysis", layout, resizable=True)
while True:
    event, values = sg_window.read()
    if (event == sg.WIN_CLOSED):
        break
    else:
        update_status(sg_window, event, values, shared_data)
sg_window.close()




"""
spec, f, t = np.abs(stft(data[:,0], fs, segment_duration * fs))

# peak time とか出す & x, y, z の計算→ノルム出す→誤差を確認
peak_amp = np.max(spec)
peak_idx = np.where(spec == peak_amp)


plt.pcolormesh(t, f, spec, cmap="jet")


plt.ylabel("Frequency [Hz]")
plt.xlabel("Time [sec]")
cbar = plt.colorbar()
#cbar.ax.set_ylabel("Intensity [dB]")

#cbar.set_clim(0, 1.1) #plt3.2まで
#cbar.mappable.set_clim(0, 1.1) #plt3.3以降

cbar.ax.set_ylabel("Intensity")
#plt.savefig("nfft4096-npersegL.png")
#plt.savefig("0612-p.png")
plt.show()
"""