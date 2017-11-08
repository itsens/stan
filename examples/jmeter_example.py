__author__ = 'borodenkov.e.a@gmail.com'

from pprint import pprint
from stan.parser import JmeterXmlParser
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
        '''
        Динамика подачи нагрузки
        :param qq:
        :param GRAPH_DIR:
        :return:
        '''

        ss = qq['SampleCount'].groupby(qq.index.map(lambda a: round(a / 60) * 60)).sum()
        ee = qq['ErrorCount'].groupby(qq.index.map(lambda a: round(a / 1) * 1)).sum()

        gr1 = MYPLOT(title=u'Динамика подачи нагрузки',
                     y_label_name=u'Количество запросов, с',
                     title_loc=self.TITLE_LOC,
                     tick_step=3600,
                     x_label_type=self.X_LABEL_TYPE,
                     ytick_qty=self.YTICK_QTY)
        gr1.plot(ss / 60, color='g', label=u'Успешные запросы')
        gr1.plot(ee, color='r', label=u'Не успешные запросы')
        gr1.add_legend()
        gr1.save(GRAPH_DIR + '/sample_count_long.png')

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



FILE_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_XML = FILE_DIR + '/files/jm_results.xml'
# TEST_XML = FILE_DIR + '/files/jmeter.b2b.xml'

if __name__ == '__main__':
    jm = jmeter.JMETER(JM_RES).df
    ff = JmeterGraph()
    ff.sample_count_long()
    ff.label_quantile_long

