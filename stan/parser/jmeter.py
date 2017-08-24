from pprint import pprint

__author__ = 'borodenkov.e.a@gmail.com'

from .parser import Parser, ParserError
from xml.etree.ElementTree import iterparse
from tqdm import tqdm
from stan import StanData, StanDict
import datetime

TIMESTAMP = 0  # сюда ложим первую временную метку


class JmeterXmlParser(Parser):
    """
    XML parser for stat files from jmeter util.

    example string:
    <httpSample t="3802" it="0" lt="3794" ct="4" ts="1499763762509"
                s="true" lb="HTTPR: documents" rm="OK" tn="TG: get page 75 documents  1-1"
                dt="text" de="" by="238961" sby="547" sc="1" ec="0" ng="1" na="1" hn="MSK-W0680">
    </httpSample>

    """

    def __init__(self):

        self.sampling_interval = 's'  # интервал для агригации данных по временной меткке

        self.file_path = None
        self.stat_length = None

        self.iterparse_context = None

        self.__current_timestamp = None

        self.data = dict()

        self.metrics = {'load_time': 't',
                        'latency': 'lt',
                        'connect_time': 'ct',
                        'timestamp': 'ts',
                        'label': 'lb',
                        'tread_group': 'tn',
                        'size_in_bytes': 'by',
                        'sent_bytes': 'sby',
                        'error_count': 'ec'
                        }

        self.stat = dict(loadtime=[],
                         latency=[],
                         connect_time=[],
                         timestamp=[],
                         label=[],
                         tread_group=[],
                         size_in_bytes=[],
                         sent_bytes=[],
                         error_count=[])

        self.load_time = list()  # Load time: 115
        self.it = list()
        self.latency = list()  # Latency: 89
        self.connect_time = list()  # Connect Time: 51
        self.timestamp = list()
        self.timestamp2 = list()
        self.s = list()  # "true"
        self.label = list()  # "HTTPR: login"
        self.rm = list()  # "OK"
        self.tread_group = list()  # "TG: get page 75 documents  1-1"
        self.dt = list()  # "text"
        self.de = list()  # "UTF-8"
        self.size_in_byte = list()  # "21978" Size in bytes: 21978
        self.sent_bytes = list()  # "1479" Sent bytes:1479
        self.sc = list()  # "1"
        self.error_count = list()  # Error Count: 0
        self.ng = list()  # "1"
        self.na = list()  # "1"
        self.hn = list()  # "MSK-W0680" >

        self.rps = list()

        self._connections_start_times = dict()
        self._success_tcp_connections = set()
        self._success_ssl_connections = set()
        self._failed_req_rsp_connections = set()

    # todo: для чего нужен этот перевод?
    def _get_time_interval(self, timestamp: int) -> int:
        """
        "Round" the timestamp to the specified interval

        :param timestamp:
        :return: time interval timestamp (Unix time)
        """
        # TODO: Expand the supported averaging intervals
        if self.sampling_interval == 's':
            return timestamp / 1000

    def _process_operation(self, operation: list):
        operation_timestamp = int(operation[TIMESTAMP])
        operation_time_interval = self._get_time_interval(operation_timestamp)

    def parse(self, file_path: str):
        if self.file_path is not None:
            self.__init__()

        self.file_path = file_path

        self.iterparse_context = iter(iterparse(self.file_path, events=('start', 'end')))
        next(self.iterparse_context)

        for event, element in self.iterparse_context:
            if event == 'end' and element.tag == 'httpSample':
                attributes = element.attrib
                for attribute in attributes:
                    if attribute == self.metrics['load_time']:
                        self.load_time.append(int(attributes[attribute]))
                    elif attribute == 'it':
                        self.it.append(int(attributes[attribute]))
                    elif attribute == self.metrics['latency']:
                        self.latency.append(int(attributes[attribute]))
                    elif attribute == self.metrics['timestamp']:
                        self.timestamp.append(int(attributes[attribute]))  # fixme преобразование  в UNIX формат
                    elif attribute == self.metrics['connect_time']:
                        self.connect_time.append(int(attributes[attribute]))
                    elif attribute == self.metrics['label']:
                        self.label.append(attributes[attribute])
                    elif attribute == self.metrics['size_in_bytes']:
                        self.size_in_byte.append(int(attributes[attribute]))
                    elif attribute == self.metrics['sent_bytes']:
                        self.sent_bytes.append(int(attributes[attribute]))
                    elif attribute == self.metrics['error_count']:
                        self.error_count.append(int(attributes[attribute]))

        # убираем микросекунды
        self.timestamp2 = [int(number / 1000) for number in self.timestamp]  # fixme вынести в функци

    def get_stat(self, data_format='flat', time_zone_correction=0):
        """
        return stat data with specified format.

        'flat' format:
        dict{timestamp=dict(),
            section_key_1=dict(),
            section_key_2=dict()
            ...}
        :param data_format: return data format
        :param time_zone_correction:
        :return: list() of data with specified format
        """
        if data_format not in {'flat', 'joined'}:
            raise ParserError('Incorrect data format: {}'.format(data_format))

        if data_format == 'flat':
            return dict(t=self.load_time,
                        it=self.it,
                        lt=self.latency,
                        ct=self.connect_time,
                        lb=self.label,
                        by=self.size_in_byte,
                        sby=self.sent_bytes,
                        ec=self.error_count,
                        ts=self.timestamp2)
        elif data_format == 'joined':
            # TODO: реализовать
            return self.data


'''

viewe example
1489489403: {'active_ssl_connections_count': 3,
             'active_tcp_connections_count': 3,
             'connection_times': 0.0,
             'failed_req_per_second': 0,
             'failed_rsp_per_second': 0,
             'failed_ssl_per_second': 0,
             'failed_tcp_per_second': 0,
             'failed_total_per_second': 0,
             'req_per_second': 0,
             'rsp_per_second': 0,
             'ssl_connections_per_second': 0,
             'ssl_handshake_times': 0.0,
             'tcp_connections_per_second': 0,
             'tcp_times': 0.0,
             'throughput_download': 1687552,
             'throughput_upload': 0,
             'ttfb_times': 0.0}}
'''


'''
12.7 Sample Attributes¶

The sample attributes have the following meaning:

Attribute	Content
by	Bytes
sby	Sent Bytes
de	Data encoding
dt	Data type
ec	Error count (0 or 1, unless multiple samples are aggregated)
hn	Hostname where the sample was generated
it	Idle Time = time not spent sampling (milliseconds) (generally 0)
lb	Label
lt	Latency = time to initial response (milliseconds) - not all samplers support this
ct	Connect Time = time to establish the connection (milliseconds) - not all samplers support this
na	Number of active threads for all thread groups
ng	Number of active threads in this group
rc	Response Code (e.g. 200)
rm	Response Message (e.g. OK)
s	Success flag (true/false)
sc	Sample count (1, unless multiple samples are aggregated)
t	Elapsed time (milliseconds)
tn	Thread Name
ts	timeStamp (milliseconds since midnight Jan 1, 1970 UTC)
varname	Value of the named variable

'''