__author__ = 'borodenkov.e.a@gmail.com'

from pprint import pprint
from stan.parser import JmeterCsvParser
from stan.plotter import PlotlyGraph
import os

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_XML = FILE_DIR + '/files/jm_results.xml'
TEST_CSV = 'C:\\tmp\\jm_results.csv'
GRAPH_FILE = FILE_DIR + '/files/{}.html'
# TEST_XML = FILE_DIR + '/files/jmeter.b2b.xml'


def samples_per_time(GRAPH_FILE, flat_stat):
    graph = PlotlyGraph('Интенсивность запросов')
    graph.append_data(name='Успешные', x=flat_stat['index'], y=flat_stat['SampleCount'], sma=True, sma_interval=60)
    graph.append_data(name='Неуспешные', x=flat_stat['index'], y=flat_stat['ErrorCount'])

    graph.config_axes(x_sign='Длительность теста, s',
                      y_sign='запрос/с')
    graph.plot(GRAPH_FILE)
    print('graph complite:  {}'.format(GRAPH_FILE))


def mean_per_time_all(GRAPH_FILE, flat_stat):
    graph = PlotlyGraph('Арифмитеское среднее по всем запросам')
    graph.append_data(name='Длительность отклика', x=flat_stat['index'], y=flat_stat['elapsed_mean_all'],
                      sma=True, sma_interval=60)
    graph.append_data(name='Запросы в секунду', x=flat_stat['index'], y=flat_stat['SampleCount'],
                      y2=True, sma=True, sma_interval=60)
    graph.config_axes(y_max=5000,
                      x_sign='time, s',
                      y_sign='mc',
                      y2_sign='запрос/c')
    graph.plot(GRAPH_FILE)
    print('graph complite:  {}'.format(GRAPH_FILE))

def label(GRAPH_FILE, flat_stat):
    gr = PlotlyGraph('Длительность отлика')
    gr.append_data(name='Авторизация', x=flat_stat['index'], y=flat_stat['httpr: auth'])
    gr.append_data(name='Выписка ЕГРИП', x=flat_stat['index'], y=flat_stat['httpr: get fns_egrip_full_smev3'])
    gr.append_data(name='Выписка ЕГРЮЛ', x=flat_stat['index'], y=flat_stat['httpr: get fns_egrul_full_smev3'])
    gr.append_data(name='asdf', x=flat_stat['index'], y=flat_stat['SampleCount'], y2=True)
    gr.sign_axes(x_sign='asdf', y_sign='мс', y2_sign=flat_stat)
    gr.plot(GRAPH_FILE)
    print('graph complite:  {}'.format(GRAPH_FILE))


if __name__ == '__main__':
    print(TEST_CSV)
    jm_parser = JmeterCsvParser()
    jm_parser.parse(TEST_CSV)
    jm_stat = jm_parser.get_stat()

    print('\nmetrics:\n')
    for _ in jm_stat.metrics:
        print(_)
    # pprint("jm stat metrics:    {}".format(jm_stat.metrics))
    flat_stat = jm_stat.flat()

    jm_parser_rps = JmeterCsvParser()
    jm_parser_rps.parser_rps(TEST_CSV)
    rps_stat = jm_parser_rps.get_rps_stat()
    print('\n rps data metrics:\n')
    for _ in rps_stat.metrics:
        print(_)
    flat_stat2 = rps_stat.flat()
    print(flat_stat2)




    # pprint('keys statistics jmeter logs: {}'.format(flat_stat.keys()))

    # samples_per_time(GRAPH_FILE.format('sample_count'), flat_stat=flat_stat)
    # mean_per_time_all(GRAPH_FILE.format('quantile_95'), flat_stat=flat_stat)
    # label(GRAPH_FILE.format('label'), flat_stat=flat_stat)
