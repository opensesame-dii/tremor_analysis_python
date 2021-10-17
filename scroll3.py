# https://water2litter.net/rum/post/python_tkinter_resizeable_canvas/
import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image, ImageTk

# ここにクラスのコードを書き込む
class ScrollableFrame(tk.Frame):
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
            yscrollcommand=self.vscrollbar.set, xscrollcommand=self.hscrollbar.set)
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
        self.interior = tk.Frame(self.canvas)
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
class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title('scrollbar trial')
        self.pack(fill=tk.BOTH, expand=True)
        self.create_widgets()

    def create_widgets(self):
        self.canvas_frame = ScrollableFrame(self, minimal_canvas_size)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # self.control_frame = tk.Frame(self)
        # self.control_frame.pack(side=tk.TOP, fill=tk.Y, expand=False)

        # self.label_title1 = ttk.Label(self.control_frame, text='Window coordinate')
        # self.label_title1.pack()
        # self.point_x = tk.StringVar()
        # self.point_y = tk.StringVar()
        # self.label_x = ttk.Label(self.control_frame, textvariable=self.point_x)
        # self.label_x.pack()
        # self.label_y = ttk.Label(self.control_frame, textvariable=self.point_y)
        # self.label_y.pack()
        # self.label_title2 = ttk.Label(self.control_frame, text='Canvas coordinate')
        # self.label_title2.pack()
        # self.point_xc = tk.StringVar()
        # self.point_yc = tk.StringVar()
        # self.label_xc = ttk.Label(self.control_frame, textvariable=self.point_xc)
        # self.label_xc.pack()
        # self.label_yc = ttk.Label(self.control_frame, textvariable=self.point_yc)
        # self.label_yc.pack()
        # self.canvas_frame.canvas.bind('<ButtonPress-1>', self.pickup_point)

        # canvasに画像をセットする
        im = ImageTk.PhotoImage(image=read_image)
        self.canvas_frame.canvas.config(width=read_image.width, height=read_image.height)
        self.canvas_frame.canvas.photo = im
        self.canvas_frame.canvas.create_image(0, 0, anchor='nw', image=im)

        frame = tk.Frame(self.canvas_frame.interior, bg="#583493", )
        frame.pack()
        text = tk.Label(frame, text="asdf")
        # text.pack()
        text.grid(row=0, column=0)

    # ポインタの座標を取得する
    def pickup_point(self, event):
        self.point_x.set('x : ' + str(event.x))
        self.point_y.set('y : ' + str(event.y))
        self.point_xc.set('x : ' + str(self.canvas_frame.canvas.canvasx(event.x)))
        self.point_yc.set('y : ' + str(self.canvas_frame.canvas.canvasy(event.y)))
        print(event.x, event.y, self.canvas_frame.canvas.canvasx(event.x), self.canvas_frame.canvas.canvasy(event.y))

read_image = Image.open('test_figure.png')
canvas_width, canvas_height = read_image.size
minimal_canvas_size = read_image.size

# アプリケーション起動
root = tk.Tk()
app = Application(master=root)
app.mainloop()