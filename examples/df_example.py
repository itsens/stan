from stan.parser import JmeterCsvParser
from stan.core import StanDict, StanData
from xml.etree.ElementTree import iterparse
import pandas as pd


def read_csv_to_df(file_path):
    read_csv_param = dict(index_col=['timeStamp'],
                          low_memory=True,
                          na_values=[' ', '', 'null'],
                          converters={'timeStamp': lambda a: float(a) / 1000})

    pandas_data_frame = pd.read_csv(file_path, **read_csv_param)
    return pandas_data_frame


def _rever_frame(jm):

    jm['timeStamp_round'] = jm.index
    jm = jm.pivot_table(columns=['label'],
                        index='timeStamp_round',
                        values='elapsed',
                        aggfunc=pd.np.mean)
    return jm

def get_stat(jm) -> StanData:
    result = StanData()
    for ts in jm.index:
        metrics = StanDict()
        for metric in jm[ts]:
            metrics[metric] = jm[ts][metric]
        result.append(ts, metrics)

    return result


if __name__ == '__main__':
    JM_RES = '/home/usr/stan/examples/files/jm_sg.csv'
    GRAPH_DIR = '/home/usr/Dropbox/projects/stan/examples/files/'

    __metrics = None
    data = StanData()

    jm = read_csv_to_df(JM_RES)
    print('1:   ', jm.shape)
    __metrics = jm['label'].unique()

    data = set()

    jm.index = [round(a / 1) * 1 for a in jm.index]
    for ts in jm.index:
        for _ in __metrics:
            data.add(ts, _, jm[ts][_])
