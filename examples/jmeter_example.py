import time

__author__ = 'borodenkov.e.a@gmail.com'

from stan.parser import JmeterCsvParser
class Profiler(object):
    def __enter__(self):
        self._startTime = time.time()

    def __exit__(self, type, value, traceback):
        print("Elapsed time: {:.3f} sec".format(time.time() - self._startTime))




if __name__ == '__main__':

    with Profiler() as p:
        jm_parser = JmeterCsvParser()
        print('JmeterCsvParser: ')
    with Profiler() as p:
        # jm_parser.parse('files/jm_results.csv')
        jm_parser.parse('files/jm_sg.csv')
        print('parse jm log: ')
    with Profiler() as p:
        jm_stat = jm_parser.get_stat()
        print('get stat jm log: ')
    with Profiler() as p:
        flat_stat = jm_stat.flat()
        print('get stat float jm log: ')

