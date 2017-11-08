__author__ = 'borodenkov.e.a@gmail.com'

from pprint import pprint
from stan.parser import JmeterCsvParser
from stan.plotter import PlotlyGraph
import os


'''
pprint(stat.keys())
dict_keys(['t', 'it', 'lt', 'ct', 'lb', 'by', 'sby', 'ec', 'ts'])

'''


class JmeterGraph():
    def __init__(self):
        self.YTICK_QTY = 11
        self.TITLE_LOC = 'center'
        self.TICK_STEP = 60
        self.TICK_STEP_LONG = 3600
        self.X_LABEL_TYPE = 'time0'

    def sample_count_long(self, qq, GRAPH_DIR):
        pass

"""
    def label_quantile_long(self, qq, GRAPH_DIR):
        qq['timeStamp_round'] = [round(a / 1) * 1 for a in qq.index]
        df1 = qq.pivot_table(columns=['label'],  # Колонка из которой будут браться названия для колонок сводной таблицы
                             index='timeStamp_round',  # Значения по которым будут групироваться тсроки
                             values='elapsed',  # Название колонки для которой будем вычислять среднее
                             aggfunc=pd.np.mean)  # Функция которая будет вычисляться для значений из elapsed

        per95 = qq['elapsed'].groupby(qq.index.map(lambda a: round(a / 60) * 60)).quantile(0.95)
        gr1 = MYPLOT(title=u'95 перцентилей длительности отлика',
                     y_label_name=u'Длительность отклика, мс',
                     title_loc=self.TITLE_LOC,
                     tick_step=self.TICK_STEP_LONG,
                     x_label_type=self.X_LABEL_TYPE,
                     ytick_qty=self.YTICK_QTY)
        gr1.plot(per95 / 60, label=u'95 перцентиль')
        gr1.add_legend()
        gr1.save(GRAPH_DIR + '/label_quantile_long.png')
"""

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_XML = FILE_DIR + '/files/jm_results.xml'
TEST_CSV = FILE_DIR + '/files/jm_results.csv'
GRAPH_FILE = FILE_DIR + '/files/samples.html'
# TEST_XML = FILE_DIR + '/files/jmeter.b2b.xml'

if __name__ == '__main__':
    jm_parser = JmeterCsvParser()
    jm_parser.parse(TEST_CSV)
    jm_stat = jm_parser.get_stat()
    flat_stat = jm_stat.flat()
    pprint(jm_stat)

    graph = PlotlyGraph('Интенсивность запросов')
    graph.append_data(name='SuccessSamples', x=flat_stat['index'], y=flat_stat['SampleCount'])
    graph.append_data(name='ErrorSamples', x=flat_stat['index'], y=flat_stat['ErrorCount'])
    graph.sign_axes(x_sign='time, s', y_sign='Samples per second')
    graph.plot(GRAPH_FILE)


    # ff = JmeterGraph()
    # ff.sample_count_long()
    # ff.label_quantile_long
