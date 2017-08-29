from pprint import pprint
import os
from stan.parser import sar
from stan.plotter import PlotlyGraph


'''
Можно использовать сглаживание на больших данных     gr.append_data(' ', x=x, y=у, sma=True, sma_interval=10)


'''

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_XML = FILE_DIR + '/files/sar_DTDv2.19.xml'
GRAPH_DIR = 'graph/'

# настройки графиков
X_SIGN = 'Длительность теста, c'


def cpu(stan_data, hostname):
    plot_file_name = GRAPH_DIR + 'cpu_' + hostname + '.html'
    gr = PlotlyGraph('cpu ' + hostname)
    x = [x for x in range(len(stan_data['index']))]
    gr.append_data('Утилизация CPU ', x=x, y=stan_data['cpu_all_util'])
    gr.append_data('Утилизация CPU пользователем', x=x, y=stan_data['cpu_all_usr'])
    gr.append_data('Утилизация CPU системой', x=x, y=stan_data['cpu_all_sys'])
    gr.sign_axes(x_sign=X_SIGN, y_sign='Утилизация CPU, %')
    gr.plot(plot_file_name)


def mem(stan_data, hostname):
    plot_file_name = GRAPH_DIR + 'mem_' + hostname + '.html'
    gr = PlotlyGraph('mem ' + hostname)
    y = [y / 1024 for y in stan_data['mem_active']]
    x = [x for x in range(len(stan_data['index']))]
    gr.append_data('mem mem_memfree', x=x, y=stan_data['mem_memfree'])
    gr.append_data('mem mem_memused', x=x, y=stan_data['mem_memused'])
    gr.append_data('mem mem_swpfree', x=x, y=stan_data['mem_swpfree'])
    gr.append_data('mem mem_swpused', x=x, y=stan_data['mem_swpused'])
    gr.sign_axes(x_sign=X_SIGN, y_sign='Утилизация памяти, kbmem')
    gr.plot(plot_file_name)


def io(stan_data, hostname):
    plot_file_name = GRAPH_DIR + 'io_' + hostname + '.html'
    gr = PlotlyGraph('io ' + hostname)
    x = [x for x in range(len(stan_data['index']))]
    gr.append_data('Read transactions per second', x=x, y=stan_data['io_rtps'])
    gr.append_data('Transactions per second (this includes both read and write)', x=x, y=stan_data['io_tps'])
    gr.append_data('Write transactions per second', x=x, y=stan_data['io_wtps'])
    gr.sign_axes(x_sign=X_SIGN, y_sign='rtps, шт')
    gr.plot(plot_file_name)


def io_bytes(stan_data, hostname):
    plot_file_name = GRAPH_DIR + 'io_bytes_' + hostname + '.html'
    gr = PlotlyGraph('io bytes' + hostname)
    x = [x for x in range(len(stan_data['index']))]
    gr.append_data('Bytes read per second', x=x, y=stan_data['io_bwrtn'])
    gr.append_data('Bytes written per second', x=x, y=stan_data['io_bread'])
    gr.sign_axes(x_sign=X_SIGN, y_sign='rtps, Bytes in second')
    gr.plot(plot_file_name)


def ldfvg(stan_data, hostname):
    # TODO: 'ldavg-1'
    # 'ldavg-5'
    # 'ldavg-15'
    pass


def net(stan_data, hostname):
    # TODO: 'rxkB/s'
    # 'txkB/s'
    pass


def runq_sz(stan_data, hostname):
    # TODO: ['runq-sz']['runq-sz']
    pass

if __name__ == '__main__':
    stat = sar.SarXmlParser()
    stat.parse(TEST_XML)
    stan_data = stat.get_stat()
    pprint(stan_data.metrics)
    cpu(stan_data=stan_data.flat(), hostname=stat.hostname)
    mem(stan_data=stan_data.flat(), hostname=stat.hostname)
    io(stan_data=stan_data.flat(), hostname=stat.hostname)
    io_bytes(stan_data=stan_data.flat(), hostname=stat.hostname)