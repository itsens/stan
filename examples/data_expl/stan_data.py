from stan import StanData, StanDict
from pprint import pprint


if __name__ == '__main__':
    data_1 = StanData()
    data_1[1499763761]['metric_1'] = 1
    data_1[1499763761]['metric_2'] = 2
    data_1[1499763761]['metric_3'] = 3
    data_1.append(1499763762, StanDict(metric_1=1, metric_2=2, metric_3=3))

    data_2 = StanData()
    data_2.append(1499763762, StanDict(metric_4=4, metric_5=5, metric_6=6))
    data_2.append(1499763763, StanDict(metric_4=4, metric_5=5, metric_6=6))

    print('\n************* data_1 *************')
    pprint(data_1)
    print('\n************* data_2 *************')
    pprint(data_2)
    print('\n********* data_3 = data_1 + data_2 *********')
    data_3 = data_1 + data_2
    pprint(data_3)

    print('\n********* metric_1 from data_3 *********')
    for ts in data_3:
        print('metric_1={}'.format(data_3[ts]['metric_1']))

    print('\n********* data_3.flat() *********')
    pprint(data_3.flat())

    data_3.save('/tmp/test.pkl')

    data_4 = StanData.load('/tmp/test.pkl')
    # data_4 = StanData()
    # data_4.load('/tmp/test.pkl')

    print('\n********* Loaded from file *********')
    pprint(data_4)
