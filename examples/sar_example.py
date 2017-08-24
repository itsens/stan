#!/usr/bin/env python3

from stan.parser import SarXmlParser
import os
from pprint import pprint
from stan.plotter import PlotlyGraph

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_XML = FILE_DIR + '/files/sar_DTDv2.19.xml'

def cpu(sar_stat, sar_parse):
    plot_file_name = 'cpu_' + sar_parse.hostname + '.html'
    gr = PlotlyGraph('jm_cpu' + sar_parse.hostname)
    gr.append_data('sar', x=sar_stat.keys(), y=sar_stat['cpu_all_util'])  # , y='cpu_all_usr')
    gr.sign_axes(x_sign='Длительность теста, c', y_sign='Load time, мс')
    gr.plot(plot_file_name)


if __name__ == '__main__':
    sar_parser = SarXmlParser()
    sar_parser.parse(TEST_XML)
    stat = sar_parser.get_stat()
    print(sar_parser.hostname)
    # pprint(stat)
    pprint(stat.keys())


    cpu(sar_stat=stat,
        sar_parse=sar_parser)
