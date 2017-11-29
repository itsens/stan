import unittest
from stan.core import StanDict, StanData, StanFlatData


class TestStanDict(unittest.TestCase):

    def setUp(self):
        self.stan_dict_1 = StanDict(metric_1=1, metric_2=2)
        self.stan_dict_2 = StanDict(metric_3=3, metric_4=4)

    def test_addition(self):
        stan_dict_valid = StanDict(metric_1=1, metric_2=2, metric_3=3, metric_4=4)
        stan_dict_result = self.stan_dict_1 + self.stan_dict_2
        self.assertEqual(stan_dict_result, stan_dict_valid)


if __name__ == '__main__':
    unittest.main()
