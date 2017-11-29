__author__ = 'borodenkov.e.a@gmail.com'

from stan.core import StanDict, StanData
from .parser import Parser, ParserError
from xml.etree.ElementTree import iterparse
import pandas as pd


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
        self.load_time = list()  # Load time: 115
        self.it = list()
        self.latency = list()  # Latency: 89
        self.connect_time = list()  # Connect Time: 51
        self.timestamp = list()
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
                        self.timestamp.append(int(attributes[attribute]))
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
                        ts=self.timestamp)
        elif data_format == 'joined':
            # TODO: реализовать
            return self.data


class JmeterCsvParser(Parser):
    def __init__(self):
        self.file_path = None
        self.pandas_data_frame = None
        self.sec = 1000
        self.sampling_time = 1

        self.data = StanData()

        self.__metrics = None

    def __read_csv_to_df(self):
        read_csv_param = dict(index_col=['timeStamp'],
                              low_memory=True,
                              na_values=[' ', '', 'null'],
                              converters={'timeStamp': lambda a: float(a) / self.sec})

        self.pandas_data_frame = pd.read_csv(self.file_path, **read_csv_param)

    def __success_samples_per_time(self):
        samples_per_time = self.pandas_data_frame['SampleCount'].groupby(
            self.pandas_data_frame.index.map(
                lambda a: round(a / self.sampling_time) * self.sampling_time)).sum()  # TODO: round?

        for ts in samples_per_time.keys():
            self.data.append(ts, StanDict(SampleCount=samples_per_time.get(ts)))

    def __error_samples_per_time(self):
        samples_per_time = self.pandas_data_frame['ErrorCount'].groupby(
            self.pandas_data_frame.index.map(
                lambda a: round(a / self.sampling_time) * self.sampling_time)).sum()

        for ts in samples_per_time.keys():
            self.data.append(ts, StanDict(ErrorCount=samples_per_time.get(ts)))

    def __mean_per_time(self):
        _elapsed = self.pandas_data_frame['elapsed'].groupby(
            self.pandas_data_frame.index.map(
                lambda a: round(a / self.sampling_time) * self.sampling_time)).quantile(0.95)

        for ts in _elapsed.keys():
            self.data.append(ts, StanDict(elapsed_mean_all=_elapsed.get(ts)))

    def __quantile_all(self):
        pass

    def __thread_per_time(self):
        quant = self.pandas_data_frame['allThreads'].groupby(
            self.pandas_data_frame.index.map(
                lambda a: round(a / self.sampling_time) * self.sampling_time)).mean()

        for ts in quant.keys():
            self.data.append(ts, StanDict(allThreads=quant.get(ts)))

    def __get_unique_label(self):
        label = set()
        for _ in self.pandas_data_frame['label'].unique():
            label.add(_)
        return label

    def __analyze(self):
        self.__success_samples_per_time()
        self.__error_samples_per_time()
        self.__mean_per_time()
        self.__thread_per_time()
        self.__get_unique_label()

    def get_stat(self) -> StanData:
        return self.data

    def parse(self, file_path: str):
        self.file_path = file_path
        self.__read_csv_to_df()
        self.__analyze()
