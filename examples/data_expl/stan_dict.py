from stan import StanDict


if __name__ == '__main__':
    dict_1 = StanDict()
    dict_2 = StanDict()

    dict_1['metric_1'] = 1
    dict_1['metric_2'] = 2

    dict_2['metric_3'] = 3
    dict_2['metric_4'] = 4

    print(dict_1)
    print(dict_2)
    print(dict_1 + dict_2)
    print(dict_1['missing_key'])
