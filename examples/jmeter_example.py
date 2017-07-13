__author__ = 'borodenkov.e.a@gmail.com'

from pprint import pprint
from stan.stan.parser import jmeter
import os

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_XML = FILE_DIR + '/files/jmeter.b2b.xml'

if __name__ == '__main__':
    jm = jmeter.JmeterXmlParser()
    jm.parse(TEST_XML)
    stat = jm.get_stat(data_format='flat')
    pprint(stat)
