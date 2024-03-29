#!/usr/bin/env python3

from stan.plotter import PlotlyGraph, SarGraph
from stan.parser import sar
import random
import os
import time

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PLOT_FILE_NAME = FILE_DIR + '/files/plotly_graph_example.html'


def generate_graph():
    test_time = 360  # one week = 604800 seconds

    start_gen_data = int(time.time() * 1000)
    data_1 = [[x for x in range(test_time)], [random.choice(range(60, 80)) for x in range(test_time)]]
    data_2 = [[x for x in range(test_time)], [random.choice(range(20, 25)) for x in range(test_time)]]
    data_3 = [[x for x in range(test_time)], [random.choice([31, 32, 33, 34, 35, None]) for x in range(test_time)]]
    end_of_gen_data = int(time.time() * 1000)
    print('Data generated in {} ms'.format(end_of_gen_data - start_gen_data))

    start_plotting = int(time.time() * 1000)
    gr = PlotlyGraph('Test graph')
    gr.append_data('DATA_1', data_1[0], data_1[1])
    gr.append_data('DATA_2', data_2[0], data_2[1], y2=True)
    gr.append_data('DATA_3', data_3[0], data_3[1], sma=True, sma_interval=10)
    gr.sign_axes(x_sign='Time, s', y_sign='new title for y', y2_sign='new title for y2')
    gr.add_vertical_line(100)
    gr.add_horizontal_line(40)
    gr.add_redline(200)
    gr.plot(PLOT_FILE_NAME)
    end_plotting = int(time.time() * 1000)
    print('Data plottled in {} ms'.format(end_plotting - start_plotting))


def sar_statdart_graph(TEST_XML, FILE_DIR):
    stat = sar.SarXmlParser()
    stat.parse(TEST_XML)
    stan_data = stat.get_stat()
    ss = stan_data.flat()

    qq = SarGraph(stat.hostname)

    qq.sar_graph(graph_dir=FILE_DIR + '/files/sar/', stan_data=ss)


if __name__ == '__main__':
    generate_graph()
    ### строим стандартные графики sar CPU MEM

    # sar_statdart_graph(TEST_XML=FILE_DIR+'/files/sar_DTDv2.19.xml', FILE_DIR=FILE_DIR)



