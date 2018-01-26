import pprint

from tqdm import tqdm

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

        with open(self.file_path) as f:
            self.stat_length = sum(1 for _ in f)
            print('Jmter log stat length {0:,}:    '.format(self.stat_length).replace(',', ' '))
            f.close()

        self.pandas_data_frame = pd.read_csv(self.file_path, **read_csv_param)
        print('len pd:  {0:,}'.format(len(self.pandas_data_frame.index)).replace(',', ' '))
        print('size pd: {0:,}'.format(self.pandas_data_frame.size).replace(',', ' '))
        # pbar.update(1)

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

    def __get_analize(self):
        df = self.__get_df_label()
        print(' ')
        print('#results jmeter:')

        sample_count = self.pandas_data_frame['SampleCount'].sum()
        error_count = self.pandas_data_frame['ErrorCount'].sum()
        percent_error = error_count / (sample_count + error_count) * 100
        print('Успешных запросов: ', sample_count, '  ', 'Ошибки:  ', error_count)
        print('Недоступность продукта: {} %;'.format(percent_error),
              ' Доступность продукта: {} %;'.format(100 - percent_error))
        for label in self.__get_unique_label():
            quantle_9 = df[label].quantile(0.9)
            quantle_95 = df[label].quantile(0.95)
            quantle_99 = df[label].quantile(0.99)
            mm = df[label].mean()
            print('label: "{}"'.format(label))
            print('90: {}'.format(round(quantle_9, 2)),
                  ';  95: {}'.format(round(quantle_95, 2)),
                  ';  99: {}'.format(round(quantle_99, 2)),
                  ';  mean: {}'.format(round(mm, 2)))
        print(' ')

    def __label_per_time(self):
        df = self.__get_df_label()
        for ts in df.index:
            record = StanDict()
            for label in self.__get_unique_label():
                record[label] = df.get_value(ts, label)
            self.data.append(ts, record)
        print(self.__get_unique_label())

    def __get_df_label(self):
        self.pandas_data_frame['timeStamp_round'] = [round(a / 1) * 1 for a in self.pandas_data_frame.index]
        df = self.pandas_data_frame.pivot_table(columns=['label'],
                                                index='timeStamp_round',
                                                values='elapsed',
                                                aggfunc=pd.np.mean)
        return df

    def __get_df_error_sample(self):
        '''возвращает таблицу ошибочных запросов в секунду. В заголовке уникальные запросы'''
        self.pandas_data_frame['timeStamp_round'] = [round(a / 1) * 1 for a in self.pandas_data_frame.index]
        df = self.pandas_data_frame.pivot_table(
            columns=['label'],
            index='timeStamp_round',
            values='ErrorCount',
            aggfunc=pd.np.sum,
        )
        return df

    def __len_test(self):
        '''возвращает длину теста в секундах.'''
        _ = self.pandas_data_frame['allThreads'].groupby(
            self.pandas_data_frame.index.map(lambda a: round(a / 1) * 1)).mean()
        return len(_)

    def get_df_sample(self):
        '''возвращает таблицу rps. В заголовке униклаьные запросы'''
        self.pandas_data_frame['timeStamp_round'] = [round(a / 1) * 1 for a in self.pandas_data_frame.index]
        df = self.pandas_data_frame.pivot_table(
            columns=['label'],
            index='timeStamp_round',
            values='SampleCount',
            aggfunc=pd.np.sum,
        )
        return df

    def __analyze(self):
        self.__success_samples_per_time()
        self.__error_samples_per_time()
        self.__mean_per_time()
        self.__thread_per_time()
        self.__label_per_time()
        self.__get_analize()

    def get_stat(self) -> StanData:
        return self.data

    def parse(self, file_path: str):
        self.file_path = file_path
        self.__read_csv_to_df()
        self.__analyze()

    def parse2(self, file_path: str):
        self.file_path = file_path
        self.__read_csv_to_df()
