__author__ = 'borodenkov.e.a@gmail.com'

from pprint import pprint
from stan.parser import JmeterCsvParser
from stan.plotter import PlotlyGraph
import os

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_XML = FILE_DIR + '/files/jm_results.xml'
TEST_CSV = FILE_DIR + '/files/jm_results.csv'
GRAPH_FILE = FILE_DIR + '/files/{}.html'
# TEST_XML = FILE_DIR + '/files/jmeter.b2b.xml'


def sample_count(GRAPH_FILE, flat_stat):
    graph = PlotlyGraph('Интенсивность запросов')
    graph.append_data(name='SuccessSamples', x=flat_stat['index'], y=flat_stat['SampleCount'])
    graph.append_data(name='ErrorSamples', x=flat_stat['index'], y=flat_stat['ErrorCount'])

    graph.config_axes(x_sign='time, s',
                      y_sign='Samples per second')
    graph.plot(GRAPH_FILE)


def label_quantile(GRAPH_FILE, flat_stat):
    graph = PlotlyGraph('95 перцентиль длительности отлика')
    graph.append_data(name='Quantile 95', x=flat_stat['index'], y=flat_stat['quantile_95'],
                      sma=True, sma_interval=60)
    graph.append_data(name='SuccessSamples', x=flat_stat['index'], y=flat_stat['SampleCount'],
                      y2=True, sma=True, sma_interval=60)
    graph.config_axes(y_max=1000,
                      x_sign='time, s',
                      y_sign='mc',
                      y2_sign='запрос/c')
    graph.plot(GRAPH_FILE)

def quantile_threads(GRAPH_FILE, flat_stat):
    graph = PlotlyGraph('95 перцентиль длительности отлика')
    graph.append_data(name='Quantile 95', x=flat_stat['index'], y=flat_stat['quantile_95'])
    graph.append_data(name='SuccessSamples', x=flat_stat['index'], y=flat_stat['allThreads'], y2=True)
    graph.config_axes(x_sign='time, s',
                      y_sign='mc',
                      y2_sign='Динамика подачи нагрузки/c')
    graph.plot(GRAPH_FILE)




if __name__ == '__main__':
    jm_parser = JmeterCsvParser()
    jm_parser.parse(TEST_CSV)
    jm_stat = jm_parser.get_stat()
    flat_stat = jm_stat.flat()

    sample_count(GRAPH_FILE.format('sample_count'), flat_stat=flat_stat)
    label_quantile(GRAPH_FILE.format('quantile_95'), flat_stat=flat_stat)
    quantile_threads(GRAPH_FILE.format('allThreads'), flat_stat=flat_stat)

    print(jm_stat.metrics)
    for key in list(jm_stat.keys())[0:1]:
        pprint(jm_stat[key])
    pprint(jm_stat)

    graph = PlotlyGraph('95 перцентиль длительности отлика')
    graph.append_data(name='Quantile 95', x=flat_stat['index'], y=flat_stat['quantile_95'])#, y=flat_stat['quantile_95'])
    graph.append_data(name='SuccessSamples', x=flat_stat['index'], y=flat_stat['SampleCount'], y2=True)

    graph.sign_axes(x_sign='time, s', y_sign='Samples per second', y2_sign='Интенсивность запросов, с')
    # graph.plot(GRAPH_FILE.format('quantile_95'))


    # ff = JmeterGraph()
    # ff.sample_count_long()
    # ff.label_quantile_long
