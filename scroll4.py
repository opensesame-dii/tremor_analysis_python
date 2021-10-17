# https://qiita.com/hatorijobs/items/afa037278ef442cddbc5#%E7%B6%99%E6%89%BF%E3%82%92%E5%88%A9%E7%94%A8%E3%81%97%E3%81%9F%E5%A0%B4%E5%90%88%E3%81%AE%E3%82%B3%E3%83%BC%E3%83%89%E4%B8%8A%E3%82%88%E3%82%8A%E8%89%AF%E3%81%84%E3%81%A8%E6%80%9D%E3%81%86

import tkinter as tk
import tkinter.ttk as ttk

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, bar_x = True, bar_y = True):
        super().__init__(container)
        self.canvas = tk.Canvas(self)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        if bar_y:
            self.scrollbar_y = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
            self.scrollbar_y.pack(side=tk.RIGHT, fill="y")
            self.canvas.configure(yscrollcommand=self.scrollbar_y.set)
        if bar_x:
            self.scrollbar_x = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
            self.scrollbar_x.pack(side=tk.BOTTOM, fill="x")
            self.canvas.configure(xscrollcommand=self.scrollbar_x.set)
        self.canvas.pack(side=tk.LEFT, fill="both", expand=True)


root = tk.Tk()

frame = ScrollableFrame(root)

for i in range(50):
    for j in range(50):
        ttk.Entry(frame.scrollable_frame, width=5).grid(row=i, column=j)

frame.pack()
root.mainloop()