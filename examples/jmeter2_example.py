import glob

__author__ = 'borodenkov.e.a@gmail.com'

from pprint import pprint
from stan.parser import JMeterXmlParser2
import os

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_XML = sorted(glob.glob('files/jm/*.xml'))


if __name__ == '__main__':

    jm = JMeterXmlParser2()
    jm.parse(TEST_XML)
    stat = jm.get_stat()

    pprint(stat)

