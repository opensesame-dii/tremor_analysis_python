import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

class ClassFrame(tk.Frame):
    def __init__(self, master, bg=None, width=None, height=None):
        super().__init__(master, bg=bg, width=width, height=height)


class ClassLabelFrameTop(tk.LabelFrame):
    def __init__(self, master, text=None, pad_x=None, pad_y=None, bg=None):
        super().__init__(master, text=text, padx=pad_x, pady=pad_y, bg=bg)
        button1 = tk.Button(self, text="タブ1", bg=bg)
        button1.pack(side="left", padx=(10, 0))
        button2 = tk.Button(self, text="タブ2", bg=bg)
        button2.pack(side="left", padx=(10, 0))
        button3 = tk.Button(self, text="タブ3", bg=bg)
        button3.pack(side="left", padx=(10, 0))


class ClassLabelFrameLeft(tk.LabelFrame):
    def __init__(self, master, text=None, pad_x=None, pad_y=None, bg=None):
        super().__init__(master, text=text, padx=pad_x, pady=pad_y, bg=bg)
        left_button1 = tk.Button(self, text="アクション1", bg=bg)
        left_button1.pack(anchor=tk.NW, fill=tk.X, padx=(10, 10), pady=(0, 10))
        left_button2 = tk.Button(self, text="アクション2", width="50", bg=bg)
        left_button2.pack(anchor=tk.NW, fill=tk.X, padx=(10, 10), pady=(0, 10))
        left_button3 = tk.Button(self, text="アクション3", bg=bg)
        left_button3.pack(anchor=tk.NW, fill=tk.X, padx=(10, 10), pady=(0, 10))


class ClassCanvas(tk.Canvas):
    def __init__(self, master, scroll_width, scroll_height, bg):
        super().__init__(master, bg=bg)
        # Scrollbarを生成してCanvasに配置処理
        bar_y = tk.Scrollbar(self, orient=tk.VERTICAL)
        bar_x = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        bar_y.pack(side=tk.RIGHT, fill=tk.Y)
        bar_x.pack(side=tk.BOTTOM, fill=tk.X)
        bar_y.config(command=self.yview)
        bar_x.config(command=self.xview)
        self.config(yscrollcommand=bar_y.set, xscrollcommand=bar_x.set)
        # Canvasのスクロール範囲を設定
        self.config(scrollregion=(0, 0, scroll_width, scroll_height))


def main():
    root = tk.Tk()
    root.geometry("500x300")  # 横400x縦300
    bg_color = "snow"

    # 最上位のフレーム
    frame_big_left = ClassFrame(root, bg="white", width=180)
    frame_big_right = ClassFrame(root, bg="red")
    frame_big_left.pack(side=tk.LEFT, expand=0, fill=tk.Y)
    frame_big_right.pack(side=tk.LEFT, expand=1, fill=tk.BOTH)

    # 左側の大フレームの中に設置するラベル付き縦フレームのテスト
    label_frame_left_menu = ClassLabelFrameLeft(frame_big_left, text="左縦メニュー", pad_y=7, bg=bg_color)
    label_frame_left_menu.place(x=8, y=4, width=165)

    # Canvasを生成
    scroll_max = {"width": 600, "height": 700}
    canvas = ClassCanvas(frame_big_right, scroll_width=scroll_max["width"],
                         scroll_height=scroll_max["height"], bg="white")
    canvas.place(x=0, y=0, relheight=1, relwidth=1)
    # 確認用の矩形表示
    canvas.create_rectangle(50, 50, scroll_max["width"] - 100, scroll_max["height"] - 100,
                            fill="green", outline="blue", width=3)

    # 右側の大フレームの中に設置するlabelFrame
    label_frame_top = ClassLabelFrameTop(frame_big_right, text="メニュー", pad_x=0, pad_y=5, bg=bg_color)
    label_frame_top.place(x=8, y=4, width=200, height=50)
    label_frame_top.lift(canvas)

    # 右側のFrameの中に設置するFrame
    frame_test = ClassFrame(frame_big_right, bg="grey", width=200, height=50)
    frame_test.pack(side=tk.RIGHT, anchor=tk.SW, expand=0, padx=(10, 17), pady=(0, 25))

    root.mainloop()


if __name__ == "__main__":
    main()