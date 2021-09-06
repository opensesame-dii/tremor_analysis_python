import tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np


root = tkinter.Tk()
root.title("matplotlib 埋め込み")

#グラフデータ
x = np.linspace(0, 2*np.pi, 400)
y = np.sin(x)

#グラフ用オブジェクト生成
fig = Figure(figsize=(12, 3), dpi=97)   #Figure
ax = fig.add_subplot(1, 1, 1)           #Axes
#line, = ax.plot(x, y)                   #2DLine

#Figureを埋め込み
canvas = FigureCanvasTkAgg(fig, root)
canvas.get_tk_widget().pack()

#ツールバーを表示
toolbar=NavigationToolbar2Tk(canvas, root)

root.mainloop()