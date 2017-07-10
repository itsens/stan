#!/usr/bin/env python3

from stan.stan.plotter import PlotlyGraph
import random
import os
import time

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PLOT_FILE_NAME = FILE_DIR + '/files/plotly_graph_example.html'


if __name__ == '__main__':
    test_time = 3600  # one week = 604800 seconds

    start_gen_data = int(time.time()*1000)
    data_1 = [[x for x in range(test_time)], [random.choice(range(60, 80)) for x in range(test_time)]]
    data_2 = [[x for x in range(test_time)], [random.choice(range(20, 25)) for x in range(test_time)]]
    data_3 = [[x for x in range(test_time)], [random.choice(range(30, 55)) for x in range(test_time)]]
    end_of_gen_data = int(time.time()*1000)
    print('Data generated in {} ms'.format(end_of_gen_data-start_gen_data))

    start_plotting = int(time.time()*1000)
    gr = PlotlyGraph('Test graph')
    gr.append_data('DATA_1', data_1[0], data_1[1])
    gr.append_data('DATA_2', data_2[0], data_2[1], y2=True)
    gr.append_data('DATA_3', data_3[0], data_3[1], sma=True, sma_interval=10)
    gr.sign_axes(x_sign='Time, s', y_sign='new title for y', y2_sign='new title for y2')
    gr.plot(PLOT_FILE_NAME)
    end_plotting = int(time.time()*1000)
    print('Data plotted in {} ms'.format(end_plotting-start_plotting))
