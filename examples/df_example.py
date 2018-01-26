from pprint import pprint

import pandas as pd
from tqdm import tqdm
import time
import datetime


class Profiler(object):
    def __enter__(self):
        self._startTime = time.time()

    def __exit__(self, type, value, traceback):
        print(" {:.3f} sec".format(time.time() - self._startTime))


def read_csv_to_df(file_log):
    with Profiler() as p:
        print('\n\n\n\n')

        read_csv_param = dict(index_col=['timeStamp'],
                              low_memory=False,

                              na_values=[' ', '', 'null'],
                              converters={'timeStamp': lambda a: float(a) / 1000})

        with open(file_log) as f:
            stat_length = sum(1 for _ in f)
            print('Jmter log stat length {0:,}:    '.format(stat_length).replace(',', ' '))
            f.close()

        # with tqdm(desc='Analyzing sar stat', total=stat_length) as pbar:
        pandas_data_frame = pd.read_csv(file_log, **read_csv_param)
        pprint(pandas_data_frame.columns.values)
        print('len pd:  {0:,}'.format(len(pandas_data_frame.index)).replace(',', ' '))
        print('size pd: {0:,}'.format(pandas_data_frame.size).replace(',', ' '))
        # pbar.update(1)
        print('file in pd:  {}'.format(file_log))
        print('Время преобразования csv в DataFrame:')
        return pandas_data_frame


def analize_df(df):
    with Profiler() as p:
        print('\n')
        succes_sample = df['SampleCount'].sum()
        error_sample = df['ErrorCount'].sum()
        print('succes sample:   {0:,}'.format(succes_sample).replace(',', ' '))
        print('error sample:   {0:,}'.format(error_sample).replace(',', ' '))

        lt = len_test(df)
        print(lt)

        df2 = get_df_label(df)
        sample = get_df_sample(df)
        error_sample = get_df_error_sample(df)
        print('Список уникальных запросов:  ')
        for label in get_unique_label(df):
            print('label: {}    rps: {}     count_test: {}    error_count_test: {}    elapsed (ms) mean: {}       min: {}     max: {}'.format(
                label,
                round(sample[label].mean(), 1),
                round(sample[label].sum(), 1),
                round(error_sample[label].sum(), 1),
                round(df2[label].mean(), 1),
                round(df2[label].min(), 1),
                round(df2[label].max(), 1),
            ))

        print('Время анализа DataFrame: ')


def len_test(df):
    '''возвращает длину теста в секундах.'''
    quant = df['allThreads'].groupby(df.index.map(lambda a: round(a / 1) * 1)).mean()
    return len(quant)


def get_df_label(df):
    '''возвращает таблтцу длительности ответа по уникальным запросам'''
    df['timeStamp_round'] = [round(a / 1) * 1 for a in df.index]
    df = df.pivot_table(
        columns=['label'],
        index='timeStamp_round',
        values='elapsed',
        aggfunc=pd.np.mean,
    )
    return df


def get_df_sample(df):
    '''возвращает таблицу rps по уникальным запросам'''
    df['timeStamp_round'] = [round(a / 1) * 1 for a in df.index]
    df = df.pivot_table(
        columns=['label'],
        index='timeStamp_round',
        values='SampleCount',
        aggfunc=pd.np.sum,
    )
    return df

def get_df_error_sample(df):
    '''возвращает таблицу rps по уникальным запросам'''
    df['timeStamp_round'] = [round(a / 1) * 1 for a in df.index]
    df = df.pivot_table(
        columns=['label'],
        index='timeStamp_round',
        values='ErrorCount',
        aggfunc=pd.np.sum,
    )
    return df


def get_unique_label(pd):
    '''возвращает лист уникальных запросов '''
    label = set()
    for _ in pd['label'].unique():
        label.add(_)
    return label


if __name__ == '__main__':
    analize_df(read_csv_to_df(file_log='files/jm0.csv'))
    analize_df(read_csv_to_df(file_log='files/jm1.csv'))
    analize_df(read_csv_to_df(file_log='files/jm2.csv'))
    analize_df(read_csv_to_df(file_log='files/jm3.csv'))
#





#
# Jmter log stat length 1 071 795:
# Время преобразования csv в DataFrame:
#  1.706 sec
# Время анализа DataFrame:
#  4.643 sec
#
#
#
# Jmter log stat length 2 272 030:
# Время преобразования csv в DataFrame:
#  3.579 sec
# Время анализа DataFrame:
#  8.731 sec
#
#
# Jmter log stat length 4 728 422:
# Время преобразования csv в DataFrame:
#  7.480 sec#
# Время анализа DataFrame:
#  17.412 sec
#
#
# Jmter log stat length 23 071 142:
# Время преобразования csv в DataFrame:
#  93.031 sec
# Время анализа DataFrame:
#  79.410 sec
#
# Process finished with exit code 0
