from stan import StanJoinedData, StanDict
import pprint


if __name__ == '__main__':
    data = StanJoinedData()

    data[1499763757896]['metric_1'] = 1
    data[1499763757896]['metric_2'] = 2
    data[1499763757896]['metric_3'] = 3

    data[1499763759011]['metric_1'] = 1
    data[1499763759011]['metric_2'] = 2
    data[1499763759011]['metric_3'] = 3

    ts = 1499763762509
    metrics = StanDict(metric_1=1, metric_2=2, metric_3=3)
    data.append(ts, metrics)

    pprint.pprint(data)
    print()

    data = data.flat()
    pprint.pprint(data)
    print()

    data = data.join()
    pprint.pprint(data)
