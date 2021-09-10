#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, shutil
from io import BytesIO
from shutil import rmtree
import tkinter
from PySimpleGUI.PySimpleGUI import B, Column
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from PIL import Image, ImageTk
import numpy as np
from scipy import signal
import matplotlib as m
from matplotlib import mlab
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import PySimpleGUI as sg
import matplotlib
import pandas as pd
matplotlib.use('TkAgg')



import tkinter as tk
from tkinter import ttk

class Application(tk.Frame):
    def __init__(self,master):
        super().__init__(master)
        self.pack()

        #self.master.geometry("300x300")
        #self.master.title("Tkinter with Class")

        self.create_widgets()


    # Create Widgets function
    def create_widgets(self):
        #情報フレームとグラフフレームの作成
        self.info_frame = tkinter.Frame(self, bg="#778899")
        self.img_frame = tkinter.Frame(self, bg="#778899")

        #データを選択するフレーム
        self.data_input_frame = ttk.Frame(self.info_frame,relief="groove",borderwidth=5)
        self.data_label1 = ttk.Label(
            self.data_input_frame,
            text="data1:"
            )
        self.data_label1.grid(row=0, column=0) 

        self.brows_button1 = ttk.Button(self.data_input_frame,text="Brows")
        self.brows_button1.bind("<ButtonPress>")
        self.brows_button1.grid(row=0, column=1)  

        self.clear_button = ttk.Button(self.data_input_frame,text="clear")
        self.clear_button.grid(row=0, column=2)

        self.data_label2 = ttk.Label(
            self.data_input_frame,
            text = "data2:"
        )
        self.data_label2.grid(row=1, column=0)

        self.brows_button2 = ttk.Button(self.data_input_frame,text="Brows")
        self.brows_button2.bind("<ButtonPress>")
        self.brows_button2.grid(row=1, column=1)

        self.progress = ttk.Label(
            self.data_input_frame,
            text= "progress:"
        )
        self.progress.grid(row=1, column=2)
        self.progress_bar = ttk.Label(
            self.data_input_frame,
            text= "--%"
        )
        self.progress_bar.grid(row=1, column=3)

        

        #Entry
        self.name = tk.StringVar()
        self.entry_name = ttk.Entry(self)
        self.entry_name.configure(textvariable = self.name)
        self.entry_name.pack()

        #Label2
        self.label_name=ttk.Label(self)
        self.label_name.configure(text = 'Please input something in Entry')
        self.label_name.pack()

    # Event Callback Function
    def say_Hello(self):
        print("Hello, World")  # on python console
        self.label_hello.configure(text="I Have benn Clicked!")
        print(self.name.get())
        self.label_name.configure(text=self.name.get())



#def main():
  #  root = tk.Tk()
   # app = Application(master=root)#Inheritクラスの継承！
   # app.mainloop()

#if __name__ == "__main__":
 #   main()

Application().mainloop



#GUI
"""
#メインウィンドウの設定
root = Tk()
root.title("tremor")
root.state("zoomed")
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
clip.grid(row=0, column=0,sticky=W)
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
data_input_frame.grid(row = 0, column=0, padx=10, pady=20,sticky=W)
settings_frame.grid(row=2, column=0, padx=10, pady=5,sticky=W)
settings_frame2.grid(row=3, column=0, padx=10, pady=5,sticky=W)
result_frame.grid(row=4, column=0,sticky=W, padx=10)
data1_frame.grid(row=1, column=0,sticky=W,pady=10)
data2_frame.grid(row=2, column=0,sticky=W, pady=10)
coherence_frame.grid(row=3,column=0, sticky=W,pady=10)
can.grid(row=0, column=0)
can2.grid(row=1, column=0)
can3.grid(row=2, column=0)
can_x.grid(row=0, column=0)
can_y.grid(row=0, column=1)
can_z.grid(row=0, column=2)

root.mainloop()


"""     

