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

    def test_save_and_load(self):
        self.d1.save('out.pkl')

        dd1 = StanData.load('out.pkl')
        pprint(dd1)
        # print('d1:  ', d1)
        # self.assertEqual(d1, self.d1)
        ## TODO: сделать проверку созданного файла

    def test_append_not_StanDict(self):
        '''
        исключение если передаем структуру не Standict
        :return:
        '''
        pass

    def test_metrics_intersection(self):
        '''если в одно время прийдет две одинаковые метки'''
        pass

    def test_flat(self):
        pass

    def test_relate(self):
        pass  # relate


if __name__ == '__main__':
    unittest.main()
