__author__ = 'borodenkov.e.a@gmail.com'

from pprint import pprint
from stan.parser import JmeterXmlParser
import os


'''
pprint(stat.keys())
dict_keys(['t', 'it', 'lt', 'ct', 'lb', 'by', 'sby', 'ec', 'ts'])

'''

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_XML = FILE_DIR + '/files/jm_results.xml'
# TEST_XML = FILE_DIR + '/files/jmeter.b2b.xml'

if __name__ == '__main__':
    jm = JmeterXmlParser()
    jm.parse(TEST_XML)
    stat = jm.get_stat(data_format='flat')

    pprint(stat.keys())
    pprint(jm.get_stat()[10:10])
