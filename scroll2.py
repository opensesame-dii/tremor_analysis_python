import tkinter as tk
root = tk.Tk()
root.geometry("400x200")

# Canvas Widget を生成
canvas = tk.Canvas(root)
canvas.pack(side=tk.LEFT, fill=tk.BOTH)

# Scrollbar を生成して配置
bar = tk.Scrollbar(root, orient=tk.VERTICAL)
bar.pack(side=tk.RIGHT, fill=tk.Y)

# Scrollbarを制御をCanvasに通知する処理を追加
bar.config(command=canvas.yview)

# Canvasのスクロール範囲を設定
canvas.config(scrollregion=(0,0,400,400))

# Canvasの可動域をScreoobarに通知する処理を追加
canvas.config(yscrollcommand=bar.set)

# Frame Widgetを 生成
frame = tk.Frame(canvas)

# Frame Widgetを Canvas Widget上に配置
canvas.create_window((0,0), window=frame, anchor=tk.NW, width=canvas.cget('width'))

# Frame上に適当なコンテンツを配置
tk.Label(frame, text="Hello World!!", font=("",24)).pack()

root.mainloop()