import time

__author__ = 'borodenkov.e.a@gmail.com'

from stan.parser import JmeterCsvParser
class Profiler(object):
    def __enter__(self):
        self._startTime = time.time()

    def __exit__(self, type, value, traceback):
        print("Elapsed time: {:.3f} sec".format(time.time() - self._startTime))




# if __name__ == '__main__':
#
#     with Profiler() as p:
#         jm_parser = JmeterCsvParser()
#         print('JmeterCsvParser: ')
#     with Profiler() as p:
#         jm_parser.parse('files/jm2.csv')
#         # jm_parser.parse('files/jm_sg.csv')
#         print('parse jm log: ')
#     with Profiler() as p:
#         jm_stat = jm_parser.get_stat()
#         print('get stat jm log: ')
#     with Profiler() as p:
#         flat_stat = jm_stat.flat()
#         print('get stat float jm log: ')
#
#
#
#
#
#


def pars(file):
    jm_parser = JmeterCsvParser()
    jm_parser.parse2(file)
    # jm_stat = jm_parser.get_stat()
    # flat_stat = jm_stat.flat()





if __name__ == '__main__':
    pars('files/jm0.csv')
    pars('files/jm1.csv')
    pars('files/jm2.csv')
    pars('files/jm3.csv')
    pars('files/jm3.csv')

