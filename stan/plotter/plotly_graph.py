from itertools import chain
import plotly
from plotly.graph_objs import Scatter, Layout, Line
import numpy
from random import randint
import os


class PlotlyGraph:
    def __init__(self, graph_title, random_colors: bool = False):
        self.random_colors = random_colors
        self.default_colors = chain(['rgb(47, 117, 181)',
                                     'rgb(84, 130, 53)',
                                     'rgb(198, 89, 17)',
                                     'rgb(51, 63, 79)',
                                     'rgb(110, 65, 143)',
                                     'rgb(165, 27, 27)'])

        self.data = []
        self.layout = Layout(title=graph_title, separators=', ')
        # self.layout = Layout(title=graph_title, separators=', ', width=1000, height=900) # TODO: resolution for PNG
        # self.layout.update(titlefont=dict(size=36))
        # self.layout.update(width=900, height=500)
        # self.layout.update(font=dict(family='Courier New, monospace', size=25, color='#7f7f7f'))
        # self.layout()

        self.layout.update(xaxis=dict(title='x_axis', showline=True, showticklabels=True, ticks='outside',
                                      separatethousands=True))
        self.layout.update(yaxis=dict(title='y_axis', showline=True,
                                      anchor='x', side='left',
                                      showticklabels=True, ticks='outside', separatethousands=True,
                                      exponentformat='none'))
        self.layout.update(legend=dict(orientation='h', xanchor='middle', y=-0.3))

        self.shapes = []

        self.max_x = 0
        self.max_y = 0
        self.max_y2 = 0

    @staticmethod
    def _moving_average(interval, window_size):
        window = numpy.ones(int(window_size)) / float(window_size)
        return numpy.convolve(interval, window, 'same')

    @staticmethod
    def _random_color():
        return 'rgb({r}, {g}, {b})'.format(r=randint(0, 255),
                                           g=randint(0, 255),
                                           b=randint(0, 255))

    def append_data(self, name: str, x: list, y: list, y2: bool = False, sma: bool = False, sma_interval: int = 5):
        if len(x) is 0 or len(y) is 0:
            raise ValueError('"x" or "y" must not be empty')
        if len(x) != len(y):
            raise ValueError('"x" and "y" must be the same length')

        if self.random_colors:
            line_color = self._random_color()
        else:
            line_color = next(self.default_colors)

        self.max_x = max([self.max_x, max(x)])

        if y2:
            self.max_y2 = max([self.max_y2, max(n for n in y if n is not None)])
            self.layout.update(yaxis2=dict(title='y2_axis', showline=True, anchor='x', overlaying='y',
                                           side='right', showticklabels=True, ticks='outside', showgrid=False,
                                           separatethousands=True, range=[0, self.max_y2]))
        else:
            self.max_y = max([self.max_y, max(n for n in y if n is not None)])
            self.layout.update(yaxis=dict(range=[0, self.max_y]))

        scatter_params = dict()
        scatter_params['x'] = x
        scatter_params['y'] = y
        if sma:
            scatter_params['opacity'] = '0.5'
        scatter_params['line'] = Line(width=2, color=line_color)
        scatter_params['name'] = name
        if y2:
            scatter_params['yaxis'] = 'y2'
        self.data.append(Scatter(**scatter_params))

        if sma:

            # filtering None values
            sma_x = [x[offset] for offset, value in enumerate(y) if value is not None]
            sma_y = [value for value in y if value is not None]

            ma = self._moving_average(sma_y, sma_interval)
            ma_scatter_params = dict()
            ma_scatter_params['x'] = sma_x[sma_interval:1 - sma_interval]
            ma_scatter_params['y'] = ma[sma_interval:1 - sma_interval]
            ma_scatter_params['line'] = Line(width=2, color=line_color)
            ma_scatter_params['name'] = name + ' (sma)'
            if y2:
                ma_scatter_params['yaxis'] = 'y2'
            self.data.append(Scatter(**ma_scatter_params))

    def config_axes(self, x_sign: str = False, y_sign: str = False, y2_sign: str = False,
                    x_max=False, y_max=False, y2_max=False):
        self.sign_axes(x_sign=x_sign, y_sign=y_sign, y2_sign=y2_sign)
        if x_max:
            self.layout.update(xaxis=dict(range=[0, x_max]))
        if y_max:
            self.layout.update(yaxis=dict(range=[0, y_max]))
        if y2_max:
            self.layout.update(yaxis2=dict(range=[0, y2_max]))

    def sign_axes(self, x_sign: str = False, y_sign: str = False, y2_sign: str = False):
        if x_sign:
            self.layout.update(xaxis=dict(title=x_sign))
        if y_sign:
            self.layout.update(yaxis=dict(title=y_sign))
        if y2_sign:
            self.layout.update(yaxis2=dict(title=y2_sign))

    def add_vertical_line(self, x, color='rgb(55, 128, 191)', width=3):
        self.shapes.append(dict(type='line',
                                x0=x,
                                y0=0,
                                x1=x,
                                y1=None,
                                line=dict(color=color,
                                          width=width)))

    def add_horizontal_line(self, y, color='rgb(55, 128, 191)', width=3):
        self.shapes.append(dict(type='line',
                                x0=0,
                                y0=y,
                                x1=None,
                                y1=y,
                                line=dict(color=color,
                                          width=width)))

    def add_redline(self, x):
        self.add_vertical_line(x=x, color='red', width=3)

    def plot(self, file_name):
        if len(self.data) == 0:
            print('No data to plot')
            return 1

        if len(self.shapes) > 0:
            for shape in self.shapes:
                if shape['x1'] is None:
                    shape['x1'] = self.max_x
                elif shape['y1'] is None:
                    shape['y1'] = self.max_y
            self.layout.update(shapes=self.shapes)

        plotly.offline.plot(dict(layout=self.layout, data=self.data),
                            filename=file_name, auto_open=False,
                            # image='png', image_filename='io',
                            image_width=700, image_height=450,
                            show_link=False)


class SarGraph:
    def __init__(self, hostname):
        self.stan_data = None
        self.graph_dir = None
        self.hostname = hostname

        self.x_sing = 'Длительность теста, c'

    def __cpu(self):
        plot_file_name = self.graph_dir + 'cpu_' + self.hostname + '.html'
        gr = PlotlyGraph('Утилизация ЦП')
        x = [x for x in range(len(self.stan_data['index']))]
        gr.append_data('Утилизация CPU ', x=x, y=self.stan_data['cpu_all_util'])
        gr.append_data('Процент времени в ожидании завершения ввода\вывода', x=x, y=self.stan_data['cpu_all_iowait'])
        gr.sign_axes(x_sign=self.x_sing, y_sign='%')
        gr.plot(plot_file_name)

    def __cpu_cores_util(self):
        plot_file_name = self.graph_dir + 'cpu_single_util_' + self.hostname + '.html'
        gr = PlotlyGraph('Утилизация ЦП', random_colors=True)
        x = [x for x in range(len(self.stan_data['index']))]

        cpu_dict = self.__get_cpu_core_dict()

        for _ in cpu_dict:
            gr.append_data('Утилизация ' + _, x=x, y=self.stan_data[_])

        gr.sign_axes(x_sign=self.x_sing, y_sign='%')
        gr.plot(plot_file_name)

    def __get_cpu_core_dict(self):
        cpu_dict = set()
        for _ in self.stan_data.keys():
            if 'cpu' in _:
                if 'util' in _:
                    cpu_dict.add(_)
        return cpu_dict

    def __mem(self, units: str = 'GB'):
        plot_file_name = self.graph_dir + 'mem_' + self.hostname + '.html'
        gr = PlotlyGraph('Утилизация оперативной памяти')

        if units == 'KB':
            y = self.stan_data['mem_memused']
            y2 = self.stan_data['mem_swpused']
        elif units == 'MB':
            y = list(map(lambda a: a / 1024, self.stan_data['mem_memused']))
            y2 = list(map(lambda a: a / 1024, self.stan_data['mem_swpused']))
        elif units == 'GB':
            y = list(map(lambda a: a / 1024 / 1024, self.stan_data['mem_memused']))
            y2 = list(map(lambda a: a / 1024 / 1024, self.stan_data['mem_swpused']))

        gr.append_data('Оперативная память', x=self.stan_data['index'], y=y)
        gr.append_data('Файл подкачки', x=self.stan_data['index'], y=y2)
        gr.sign_axes(x_sign=self.x_sing, y_sign='Гб')
        gr.plot(plot_file_name)

    def __io(self):
        plot_file_name = self.graph_dir + 'io_' + self.hostname + '.html'
        gr = PlotlyGraph('Утилизация диска (в операциях/c)')
        x = [x for x in range(len(self.stan_data['index']))]
        gr.append_data('Чтение', x=x, y=self.stan_data['io_rtps'])
        gr.append_data('Запись', x=x, y=self.stan_data['io_wtps'])
        gr.append_data('Чтение/запись)', x=x, y=self.stan_data['io_tps'])
        gr.sign_axes(x_sign=self.x_sing, y_sign='операций/с')
        gr.plot(plot_file_name)

    def __io_bytes(self):
        plot_file_name = self.graph_dir + 'io_bytes_' + self.hostname + '.html'
        gr = PlotlyGraph('Утилизация диска (в Байт/с)')
        x = [x for x in range(len(self.stan_data['index']))]
        gr.append_data('Чтение', x=x, y=self.stan_data['io_bwrtn'])
        gr.append_data('Запись', x=x, y=self.stan_data['io_bread'])
        gr.sign_axes(x_sign=self.x_sing, y_sign='Байт/c')
        gr.plot(plot_file_name)

    def __dev_util(self):
        plot_file_name = self.graph_dir + 'dev_util_' + self.hostname + '.html'
        gr = PlotlyGraph('Утилизация диска (в %)', random_colors=True)
        x = [x for x in range(len(self.stan_data['index']))]

        io_dict = self.__get_dev_dict()

        for _ in io_dict:
            gr.append_data('' + _, x=x, y=self.stan_data[_])

        gr.sign_axes(x_sign=self.x_sing, y_sign='%')
        gr.plot(plot_file_name)

    def __get_dev_dict(self):
        io_dict = set()
        for _ in self.stan_data.keys():
            if 'disk_' in _:
                if 'util-percent' in _:
                    io_dict.add(_)
        return io_dict

    def __queue(self):
        plot_file_name = self.graph_dir + 'queue_' + self.hostname + '.html'
        gr = PlotlyGraph('Средняя загрузка')
        x = [x for x in range(len(self.stan_data['index']))]
        gr.append_data('За 1 минуту', x=x, y=self.stan_data['queue_ldavg-1'])
        gr.append_data('За 5 минут', x=x, y=self.stan_data['queue_ldavg-5'])
        gr.append_data('За 15 минут', x=x, y=self.stan_data['queue_ldavg-15'])
        gr.sign_axes(x_sign=self.x_sing, y_sign='операций/мин')
        gr.plot(plot_file_name)

    def __net(self):
        pass

    def sar_graph(self, sets: set = {'cpu', 'cpu_single', 'mem', 'io', 'io_bytes', 'dev_util', 'queue'},
                  graph_dir=os.path.dirname(os.path.abspath(__file__)),
                  stan_data=''):

        if not sets.issubset({'cpu', 'cpu_single', 'mem', 'io', 'io_bytes', 'dev_util', 'queue'}):
            raise ValueError

        self.graph_dir = graph_dir
        self.stan_data = stan_data

        graphs = {'cpu': self.__cpu,
                  'cpu_single': self.__cpu_cores_util,
                  'mem': self.__mem,
                  'io': self.__io,
                  'io_bytes': self.__io_bytes,
                  'dev_util': self.__dev_util,
                  'queue': self.__queue}

        for graph in sets:
            graphs[graph]()
