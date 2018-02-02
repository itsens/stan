__author__ = 'borodenkov.e.a@gmail.com'
import time
from stan.core import StanDict, StanData
from .parser import Parser, ParserError
from xml.etree.ElementTree import iterparse
import pandas as pd


class Profiler(object):
    def __enter__(self):
        self._startTime = time.time()

    def __exit__(self, type, value, traceback):
        print("Time: {:.3f} sec".format(time.time() - self._startTime))


class JmeterCsvParser(Parser):
    def __init__(self):
        self.file_path = None
        self.pandas_data_frame = None
        self.sec = 1000
        self.sampling_time = 1

        self.label = set()

        self.data = StanData()

        self.__metrics = None

    def __read_csv_to_df(self):
        """

        :return:
        """
        with Profiler() as p:
            print('\n\n')
            read_csv_param = dict(
                index_col=['timeStamp'],
                low_memory=True,
                na_values=[' ', '', 'null'],
                converters={'timeStamp': lambda a: float(a) / self.sec}
            )

            with open(self.file_path) as f:
                self.stat_length = sum(1 for _ in f)
                print('\tJmter log stat length {0:,}:    '.format(self.stat_length).replace(',', ' '))
                f.close()

            self.pandas_data_frame = pd.read_csv(self.file_path, **read_csv_param)
            print('\tВремя преобразования csv в DataFrame:')

    def __success_samples_per_time(self):
        """

        :return:
        """
        samples_per_time = self.pandas_data_frame['SampleCount'].groupby(
            self.pandas_data_frame.index.map(
                lambda a: round(a / self.sampling_time) * self.sampling_time)).sum()  # TODO: round?

        for ts in samples_per_time.keys():
            self.data.append(ts, StanDict(SampleCount=samples_per_time.get(ts)))

    def __error_samples_per_time(self):
        """

        :return:
        """
        samples_per_time = self.pandas_data_frame['ErrorCount'].groupby(
            self.pandas_data_frame.index.map(
                lambda a: round(a / self.sampling_time) * self.sampling_time)).sum()

        for ts in samples_per_time.keys():
            self.data.append(ts, StanDict(ErrorCount=samples_per_time.get(ts)))

    def __mean_per_time(self):
        """
        Сренднее значение по полю elapsed с аггрегацией self.sampling_time
        :return:
        """
        _elapsed = self.pandas_data_frame['elapsed'].groupby(
            self.pandas_data_frame.index.map(
                lambda a: round(a / self.sampling_time) * self.sampling_time)).mean()

        for ts in _elapsed.keys():
            self.data.append(ts, StanDict(elapsed_mean_all=_elapsed.get(ts)))

    def __thread_per_time(self):
        """

        :return:
        """
        quant = self.pandas_data_frame['allThreads'].groupby(
            self.pandas_data_frame.index.map(
                lambda a: round(a / self.sampling_time) * self.sampling_time)).mean()

        for ts in quant.keys():
            self.data.append(ts, StanDict(allThreads=quant.get(ts)))

    def __get_unique_label(self):
        '''Получение списка уникальных операций'''
        for _ in self.pandas_data_frame['label'].unique():
            self.label.add(_)
        return self.label

    def __get_analize(self):
        """
        Анализ результатов теста по логу jmeter.
        Считает минимальные\максимальные значение

        :return:
        """
        with Profiler() as p:
            print(self.pandas_data_frame.columns.values)
            print('\tlen pd:  {0:,}'.format(len(self.pandas_data_frame.index)).replace(',', ' '))
            print('\tsize pd: {0:,}'.format(self.pandas_data_frame.size).replace(',', ' '))
            print('\tfile in pd:  {}'.format(self.file_path))

            print('\n')
            succes_sample = self.pandas_data_frame['SampleCount'].sum()
            error_sample = self.pandas_data_frame['ErrorCount'].sum()
            print('\tsucces sample:   {0:,}'.format(succes_sample).replace(',', ' '))
            print('\terror sample:   {0:,}'.format(error_sample).replace(',', ' '))
            df2 = self.__get_df_label(self.pandas_data_frame)
            sample = self.__get_df_sample(self.pandas_data_frame)
            error_sample = self.__error_samples_per_time(self.pandas_data_frame)
            print('\tСписок уникальных запросов:  ')
            for label in self.__get_unique_label(self.pandas_data_frame):
                print(
                    '\tlabel: {}\n\t\t'
                    'rps: {}\n\t\t'
                    'count_test: {}\n\t\t'
                    'error_count_test: {}\n\t\t'
                    'elapsed (ms) mean: {}\n\t\t'
                    'min: {}\n\t\t'
                    'max: {}\n'.format(
                        label,
                        round(sample[label].mean(), 1),
                        round(sample[label].sum(), 1),
                        round(error_sample[label].sum(), 1),
                        round(df2[label].mean(), 1),
                        round(df2[label].min(), 1),
                        round(df2[label].max(), 1),
                    ))
            print('Время анализа DataFrame: ')

    def __label_per_time(self):
        """

        :return:
        """

        df = self.__get_df_label()
        for ts in df.index:
            record = StanDict()
            for label in self.__get_unique_label():
                record[label] = df.get_value(ts, label)
            self.data.append(ts, record)
        print(self.__get_unique_label())

    def __get_df_label(self):
        """
        Раварачиваем таблицу по уникальным label
        timestam/label|label1|label2|
        1233          |elapsed|elapse|
        :return:
        """
        self.pandas_data_frame['timeStamp_round'] = [round(a / 1) * 1 for a in self.pandas_data_frame.index]

        df = self.pandas_data_frame.pivot_table(
            columns=['label'],
            index='timeStamp_round',
            values='elapsed',
            aggfunc=pd.np.mean,
        )

        return df

    def __get_df_error_sample(self):
        """
        возвращает таблицу ошибочных запросов в секунду. В заголовке уникальные запросы

        :return:
        """
        self.pandas_data_frame['timeStamp_round'] = [round(a / 1) * 1 for a in self.pandas_data_frame.index]
        df = self.pandas_data_frame.pivot_table(
            columns=['label'],
            index='timeStamp_round',
            values='ErrorCount',
            aggfunc=pd.np.sum,
        )
        return df

    def __len_test(self):
        """
        возвращает длину теста в секундах.

        :return:
        """
        _ = self.pandas_data_frame['allThreads'].groupby(
            self.pandas_data_frame.index.map(lambda a: round(a / 1) * 1)).mean()
        return len(_)

    def get_df_sample(self):
        """
        возвращает таблицу rps. В заголовке уникальные запросы

        :return:
        """
        self.pandas_data_frame['timeStamp_round'] = [round(a / 1) * 1 for a in self.pandas_data_frame.index]
        df = self.pandas_data_frame.pivot_table(
            columns=['label'],
            index='timeStamp_round',
            values='SampleCount',
            aggfunc=pd.np.sum,
        )
        return df

    def __analyze(self):
        with Profiler() as p:
            self.__success_samples_per_time()
            self.__error_samples_per_time()
            self.__mean_per_time()
            self.__thread_per_time()
            # self.__label_per_time()
            self.__get_analize()
            print('Время преобразование DataFrame to StanData: ')

    def get_stat(self) -> StanData:
        return self.data

    def parse(self, file_path: str):
        self.file_path = file_path
        self.__read_csv_to_df()
        self.__analyze()

    def parse2(self, file_path: str):
        '''Парсинг больших файлов'''
        self.file_path = file_path
        self.__read_csv_to_df()
        self.__analyze()


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
