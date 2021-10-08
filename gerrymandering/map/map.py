import tkinter

class Map:
    def __init__(self, data, width=1200, height=700, title='Map', padding=50):
        self.root = tkinter.Tk()
        self.root.geometry(f'{str(width)}x{str(height)}')
        self.root.title(title)

        self.canvas = tkinter.Canvas(self.root, width=width, height=height)
        self.canvas.pack()

        self.precincts = {}
        self.polygons = []
        shapes = []
        i = 0

        for feature in data:
            shapes += feature.tkinter()
            self.precincts[feature.name] = [j for j in range(i, len(shapes))]
            i = len(shapes)

        max_height = max([max(shape[1:][::2]) for shape in shapes])
        min_height = min([min(shape[1:][::2]) for shape in shapes])
        dh = (height - padding*2) / (max_height - min_height)

        max_width = max([max(shape[::2]) for shape in shapes])
        min_width = min([min(shape[::2]) for shape in shapes])
        dw = (width - padding*2) / (max_width - min_width)

        scale = min([dw, dh])

        shapes = [[i for j in zip([(x-min_width)*scale+padding for x in shape[::2]], [height-(y-min_height)*scale-padding for y in shape[1:][::2]]) for i in j] for shape in shapes]

        for shape in shapes:
            self.polygons.append(self.canvas.create_polygon(*shape, fill='white', outline='black'))

    def set_precinct(self, precinct, color):
        for i in self.precincts[precinct]:
            self.canvas.itemconfigure(self.polygons[i], fill=color)#, outline=color)

    def mainloop(self):
        return self.root.mainloop()

    def after(self, dt, function, *args, **kwargs):
        return self.root.after(dt, function, *args, **kwargs)



