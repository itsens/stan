__author__ = 'borodenkov.e.a@gmail.com'

import pandas as pd

from stan.core import StanDict, StanData
from .parser import Parser


class JmeterCsvParser(Parser):
    def __init__(self):
        self.file_path = None
        self.pandas_data_frame = None
        self.sec = 1000
        self.sampling_time = 1

        self.data = StanData()
        self.data_rps = StanData()

        self.__metrics = None

    def __read_csv_to_df(self):
        """
        # TODO: Описать возможные параметры для парсинга
        :return:
        """
        read_csv_param = dict(
            index_col=['timeStamp'],
            low_memory=True,
            na_values=[' ', '', 'null'],
            converters={'timeStamp': lambda a: float(a) / self.sec},
        )
        self.pandas_data_frame = pd.read_csv(self.file_path, **read_csv_param)
        self.pandas_data_frame = self.pandas_data_frame[self.pandas_data_frame['success'] == True]
        return self.pandas_data_frame

    def __get_df_elapsed(self):
        """

        :return: Таблица с elapsed в заголовке название запросов/операций
        """
        self.pandas_data_frame['timeStamp_round'] = [round(a / 1) * 1 for a in self.pandas_data_frame.index]
        df_elapsed = self.pandas_data_frame.pivot_table(
            columns=['label'],
            index='timeStamp_round',
            values='elapsed',
            aggfunc=pd.np.mean,
        )
        return df_elapsed

    def __get_df_rps(self):
        """

        :return: таблица с rps в заголовке название запросов/операций
        """
        self.pandas_data_frame['timeStamp_round'] = [round(a / 1) * 1 for a in self.pandas_data_frame.index]
        df_rps = self.pandas_data_frame.pivot_table(
            columns=['label'],
            index='timeStamp_round',
            values='SampleCount',
            aggfunc=pd.np.sum,
        )
        return df_rps

    def __label_per_time(self):
        """
        Наполнение структуры StanDict длительности отклика в заголовке название запросов/операций
        :return:
        """
        df = self.__get_df_elapsed()
        for ts in df.index:
            record = StanDict()
            for label in self.__get_unique_label():
                record[label] = df.get_value(ts, label)
            self.data.append(ts, record)

    def __rps_per_time(self):
        """
        Наполнение структуры StanData rps по запросам/операциям
        :return:
        """
        df = self.__get_df_rps()
        for ts in df.index:
            record = StanDict()
            for label in self.__get_unique_label():
                record[label] = df.get_value(ts, label)
            self.data_rps.append(ts, record)

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
        Время отклика
        :return:
        """
        _elapsed = self.pandas_data_frame['elapsed'].groupby(
            self.pandas_data_frame.index.map(
                lambda a: round(a / self.sampling_time) * self.sampling_time)).mean()

        for ts in _elapsed.keys():
            self.data.append(ts, StanDict(elapsed_mean_all=_elapsed.get(ts)))

    def __thread_per_time(self):
        """
        количество тредов
        :return:
        """
        quant = self.pandas_data_frame['allThreads'].groupby(
            self.pandas_data_frame.index.map(
                lambda a: round(a / self.sampling_time) * self.sampling_time)).mean()

        for ts in quant.keys():
            self.data.append(ts, StanDict(allThreads=quant.get(ts)))

    def __get_unique_label(self):
        """

        :return: список уникальных запросов/транзакций
        """
        label = set()
        for _ in self.pandas_data_frame['label'].unique():
            label.add(_)
        return label

    def __get_analize(self):
        """
        #TODO: пенести в отдельный модуль

        <label>: 95% rps:<>; 95% elapsed: <>
        :return:
        """
        df = self.__get_df_elapsed()
        df_rps = self.__get_df_rps()
        print(' ')
        print('#results jmeter:')

        sample_count = self.pandas_data_frame['SampleCount'].sum()
        error_count = self.pandas_data_frame['ErrorCount'].sum()
        percent_error = error_count / (sample_count + error_count) * 100
        print('Успешных запросов: ', sample_count, '  ', 'Ошибки:  ', error_count)
        print('Недоступность продукта: {} %;'.format(percent_error),
              ' Доступность продукта: {} %;\n'.format(100 - percent_error))

        print('Перцентиль – это накопленный (суммированный) процент встречаемости конкретного результата, \n'
              'который складывается из процента встречаемости выбранного результата и всех предшествующих \n'
              'ему результатов, т.е. стоящих ниже данного по своей величине.\n')
        print('{:<50}: mean rps: {:<10}| 95% elapsed: {:<10}|'.
              format('\tlabel',
                     'rps',
                     'elapsed'))

        for label in self.__get_unique_label():
            print('{:>30}: mean rps: {:>10}| 95% elapsed: {:>10}|'
                  .format(label,
                          round(df_rps[label].mean(), 2),
                          round(df[label].quantile(0.95), 2),
                          ))

    def __analyze(self):
        """

        :return:
        """
        self.__success_samples_per_time()
        self.__error_samples_per_time()
        self.__mean_per_time()
        self.__thread_per_time()
        self.__label_per_time()
        self.__get_analize()

    def get_stat(self) -> StanData:
        return self.data

    def get_rps_stat(self) -> StanData:
        return self.data_rps

    def parse(self, file_path: str):
        self.file_path = file_path
        self.__read_csv_to_df()
        self.__analyze()

    def parser_rps(self, file_path: str):
        self.file_path = file_path
        self.__read_csv_to_df()
        self.__rps_per_time()

        # self.
