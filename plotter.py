from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, \
    NavigationToolbar2Tk
from matplotlib.pyplot import close


class ChartPlotter():
    def __init__(self, frame):
        self.frame = frame
        self.figure = None
        self.axes = None
        self.canvas = None
        self.toolbar = None

    def draw_chart(self):
        self.figure = Figure(figsize=(6, 5), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side='top', fill='both', expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.frame)
        self.toolbar.update()
        self.figure.tight_layout()

    def plot_pie_chart(self, labels, values, title):
        self.clear_chart()
        self.draw_chart()
        self.axes.pie(values, labels=labels, autopct='%1.2f%%', startangle=90,
                      pctdistance=0.85)
        self.axes.set_title(title)
        self.axes.axis('equal')
        self.canvas.draw()

    def plot_bar_chart(self, labels, values, title):
        self.clear_chart()
        self.draw_chart()
        if not values:
            self.show_message("Nenhum dado válido para o gráfico de barras.")
            return
        self.axes.bar(labels, values, color='skyblue')
        self.axes.set_ylabel('Valor')
        self.axes.set_title(title)
        self.figure.autofmt_xdate()
        self.canvas.draw()

    def plot_line_chart(self, labels, values, title, **kwargs):
        x_label = kwargs.get('x_label', None)
        y_label = kwargs.get('y_label', None)
        self.clear_chart()
        self.draw_chart()
        if not values or not labels:
            self.show_message("Nenhum dado válido para o gráfico de linhas.")
            return
        self.axes.plot(labels, values, marker='o', linestyle='-', color='blue')
        self.axes.set_xlabel(x_label)
        self.axes.set_ylabel(y_label)
        self.axes.set_title(title)
        self.figure.autofmt_xdate()
        self.axes.autoscale_view(True, True, True)
        self.figure.tight_layout()
        self.canvas.draw()

    def clear_chart(self):
        if self.toolbar:
            self.toolbar.destroy()
            self.toolbar = None
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        if self.figure:
            close(self.figure)
            self.figure = None
            self.axes = None

    def show_message(self, message):
        self.clear_chart()
        self.figure = Figure(figsize=(6, 5), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side='top', fill='both', expand=True)
        self.axes.text(0.5, 0.5, message, horizontalalignment='center',
                       verticalalignment='center', fontsize=12, color='gray',
                       transform=self.axes.transAxes)
        self.axes.axis('off')
        self.canvas.draw()
        self.frame.update_idletasks()
