from itertools import chain
import plotly
from plotly.graph_objs import Scatter, Layout, Line
import numpy
from random import randint


class PlotlyGraph:
    def __init__(self, graph_title, random_colors: bool=False):
        self.random_colors = random_colors
        self.default_colors = chain(['rgb(47, 117, 181)',
                                     'rgb(84, 130, 53)',
                                     'rgb(198, 89, 17)',
                                     'rgb(51, 63, 79)',
                                     'rgb(110, 65, 143)',
                                     'rgb(165, 27, 27)'])

        self.data = []
        self.layout = Layout(title=graph_title, separators=', ')
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

    def append_data(self, name: str, x: list, y: list, y2: bool=False, sma: bool=False, sma_interval: int=5):
        if len(x) is 0 or len(y) is 0:
            raise ValueError('"x" or "y" must not be empty')
        if len(x) != len(y):
            raise ValueError('"x" and "y" must be the same length')

        if self.random_colors:
            line_color = self._random_color()
        else:
            line_color = next(self.default_colors)
        if y2:
            self.max_y2 = max([self.max_y2, max(n for n in y if n is not None)])
            self.layout.update(yaxis2=dict(title='y2_axis', showline=True, anchor='x', overlaying='y',
                                           side='right', showticklabels=True, ticks='outside', showgrid=False,
                                           range=[0, self.max_y2]))
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
            ma_scatter_params['x'] = sma_x[sma_interval:1-sma_interval]
            ma_scatter_params['y'] = ma[sma_interval:1-sma_interval]
            ma_scatter_params['line'] = Line(width=2, color=line_color)
            ma_scatter_params['name'] = name + ' (sma)'
            if y2:
                ma_scatter_params['yaxis'] = 'y2'
            self.data.append(Scatter(**ma_scatter_params))

    def sign_axes(self, x_sign: str=False, y_sign: str=False, y2_sign: str=False):
        if x_sign:
            self.layout.update(xaxis=dict(title=x_sign))
        if y_sign:
            self.layout.update(yaxis=dict(title=y_sign))
        if y2_sign:
            self.layout.update(yaxis2=dict(title=y2_sign))

    def plot(self, file_name):
        if len(self.data) == 0:
            print('No data to plot')
            return 1

        plotly.offline.plot(dict(layout=self.layout, data=self.data),
                            filename=file_name, auto_open=False,
                            # image='png', image_filename='io',
                            image_width=700, image_height=450,
                            show_link=False)
