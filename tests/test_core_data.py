import unittest
from pprint import pprint

from stan.core import StanDict, StanData, StanFlatData


class TestStanDict(unittest.TestCase):

    def setUp(self):
        self.stan_dict_1 = StanDict(metric_1=1, metric_2=2)
        self.stan_dict_2 = StanDict(metric_3=3, metric_4=4)

    def test_addition(self):
        stan_dict_valid = StanDict(metric_1=1, metric_2=2, metric_3=3, metric_4=4)
        stan_dict_result = self.stan_dict_1 + self.stan_dict_2
        self.assertEqual(stan_dict_result, stan_dict_valid)


class TestStanData(unittest.TestCase):

    def setUp(self):
        self.d1 = StanData()
        self.d1.append(1499763762, StanDict(m1=1, m2=1))
        self.d1.append(1499763761, StanDict(m1=2, m2=2))

        self.d2 = StanData()
        self.d2.append(1499763762, StanDict(m4=4, m5=5))
        self.d2.append(1499763763, StanDict(m4=4, m5=5))

        self.dd = StanData()
        self.dd.append(1499763762, StanDict(m1=1, m2=1, m4=4, m5=5))
        self.dd.append(1499763761, StanDict(m1=2, m2=2))
        self.dd.append(1499763763, StanDict(m4=4, m5=5))

    def test_len_dd(self):
        dd = self.d1 + self.d2
        self.assertEqual(dd, self.dd)

    def test_metrics_len(self):
        dd = self.d1 + self.d2
        self.assertEqual(len(dd.metrics), 4)

    def save_and_load(self):
        ''' TODO: dont work load'''
        self.d1.save('out.pkl')
        dd1 = StanData.load('out.pkl')
        self.assertEqual(dd1, self.d1)

    def test_append_not_StanDict(self):
        '''
        исключение если передаем структуру не Standict
        :return:
        '''
        pass

    def test_metrics_intersection(self):
        pass

    def test_flat(self):
        self.d1_f = StanFlatData()
        self.d1_f['timestamp'] = [1499763761, 1499763762]
        self.d1_f['index'] = [0, 1]
        self.d1_f['m2'] = [2, 1]
        self.d1_f['m1'] = [2, 1]

        self.assertEqual(self.d1.flat(), self.d1_f)

    def test_relate(self):
        self.rd = StanData()
        self.rd.append(1, StanDict(m4=4.0, m5=5.0, m2=1.0))
        self.rd.append(2, StanDict(m4=None, m5=None, m2=2.0))

        related_data = self.dd.relate(by_metric='m1', flat=False)
        self.assertEqual(self.rd, related_data)

    def test_relate_flat(self):
        self.rd_f = StanFlatData()
        self.rd_f['m1'] = [1, 2]
        self.rd_f['m2'] = [1.0, 2.0]
        self.rd_f['m4'] = [4.0, None]
        self.rd_f['m5'] = [5.0, None]

        related_data = self.dd.relate(by_metric='m1')
        self.assertEqual(related_data, self.rd_f)


if __name__ == '__main__':
    unittest.main()
