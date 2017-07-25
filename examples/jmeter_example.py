__author__ = 'borodenkov.e.a@gmail.com'

from pprint import pprint
from stan.parser import JmeterXmlParser
import os

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_XML = FILE_DIR + '/files/jmeter.b2b.xml'


if __name__ == '__main__':
    jm = JmeterXmlParser()
    jm.parse('files/2out.jm.xml')
    stat = jm.get_stat(data_format='flat')
    pprint(stat)






    #dt = [int(number/1000) for number in stat['ts']]
    # for dt  in stat['ts']:
    #     dt_o = dt/1000

    # dt = int(dt/1000)


