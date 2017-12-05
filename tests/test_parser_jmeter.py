import unittest
from stan.parser import JmeterCsvParser


class TestStanDict(unittest.TestCase):
    def setUp(self):
        self.jm_parser = JmeterCsvParser()
        self.jm_parser.parse('_data/jm_sg.csv')
        self.jm_stat = self.jm_parser.get_stat()
        flat_stat = self.jm_stat.flat()

    def test_stat_len(self):
        self.assertEqual(len(self.jm_stat), 15)

    def test_stat_metrics(self):
        self.assertEqual(len(self.jm_stat.metrics), 7)

    def _succes_samples_per_time(self):
        # todo: Implement

        pass

    def __error_samples_per_time(self):
        # todo: Implement

        pass

    def __mean_per_time(self):
        # todo: Implement

        pass

    def __thread_per_time(self):
        # todo: Implement

        pass

    def __get_unique_label(self):
        # todo: Implement

        pass

    def __get_analize(self):
        # todo: Implement

        pass

    def __label_per_time(self):
        # todo: Implement

        pass

    def __get_df_label(self):
        # todo: Implement

        pass


if __name__ == '__main__':
    unittest.main()
