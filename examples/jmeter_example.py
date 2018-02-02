import time

__author__ = 'borodenkov.e.a@gmail.com'

from stan.parser import JmeterCsvParser
class Profiler(object):
    def __enter__(self):
        self._startTime = time.time()

    def __exit__(self, type, value, traceback):
        print("Elapsed time: {:.3f} sec".format(time.time() - self._startTime))

def pars(file):
    jm_parser = JmeterCsvParser()
    jm_parser.parse2(file)
    jm_parser.get_stat()

if __name__ == '__main__':
    pars('files/jm_sg.csv')
    pars('files/jm0.csv')
    pars('files/jm1.csv')
    pars('files/jm2.csv')
    pars('files/jm3.csv')
