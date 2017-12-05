from collections import defaultdict
import pickle


class MetricsIntersection(KeyError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class StanDict(dict):
    """
    Is an extended dict() with custom method keys() for flexible key filtering
    and with the ability to stack two entities.
    """

    def __init__(self, index_method=None, **kwargs):
        super().__init__(**kwargs)
        self.index_method = index_method

    def __reduce__(self):
        return super().__reduce__()

    def __add__(self, other):
        if type(other) != type(self):
            raise TypeError('Different types')

        result = StanDict()
        result.index_method = self.index_method

        for key in self:
            result[key] = self[key]

        for key in other:
            if key not in result:
                result[key] = other[key]
            else:
                # print('[WARNING] Keys intersection (Key: {})'.format(key))
                raise MetricsIntersection(key)

        return result

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if self.index_method:
            self.index_method(self)

    def __missing__(self, key):
        return None

    def set_index_method(self, method):
        self.index_method = method

    def keys(self, starts=None, contains=None):
        """
        Custom method for flexible keys filtering
        :param starts: return keys that starts with
        :param contains: return keys that contains
        :return: Iterable of keys
        """
        if starts and not contains:
            return [key for key in super().keys() if key.startswith(starts)]
        elif contains and not starts:
            return [key for key in super().keys() if contains in key]
        elif starts and contains:
            return [key for key in super().keys() if key.startswith(starts) and contains in key]
        else:
            return super().keys()


class StanData(defaultdict):
    """
    Is an extended defaultdict() with only StanDict as a default_factory.

    Format:
    StanData(timestamp1: StanDict,
             timestamp2: StanDict,
             timestamp3: StanDict,
             ...)
    """

    def __init__(self):
        super().__init__(StanDict)
        self.metrics = set()

    def __repr__(self):
        return dict.__repr__(self)

    def __setitem__(self, key, value: StanDict):
        if type(key) is not int or key > 253402289999:
            raise KeyError('The key is not Unix time')
        if type(value) != StanDict:
            raise TypeError('The value must be StanDict')

        if value.index_method is None:
            for metric in value:
                self.metrics.add(metric)
        value.set_index_method(self._index)  # TODO: Double indexing if adding as StanDict

        super().__setitem__(key, value)

    def __add__(self, other):
        if type(other) != type(self):
            raise TypeError('Different types')

        result = StanData()

        for key in self:
            result[key] = self[key]

        for key in other:
            try:
                result[key] = result[key] + other[key]
            except MetricsIntersection as metric:
                print('[WARNING] Metrics intersection (Metric: {metric}) in timestamp {ts}'.format(metric=metric,
                                                                                                   ts=key))

        return result

    def __getstate__(self):
        return self.__dict__.copy()

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __reduce__(self):
        t = super().__reduce__()
        return (t[0], ()) + (self.__getstate__(),) + t[3:]

    def _index(self, stan_dict: StanDict):
        if type(stan_dict) != StanDict:
            raise TypeError('Can indexing only StanDict')

        for metric in stan_dict:
            self.metrics.add(metric)

    def rename(self, old_name, new_name):
        # TODO: implement
        pass

    def relate(self, by_metric: str, flat=True):  # TODO: Can be slow. Need for test with big data.
        """
        Builds the dependency of the remaining metrics on the selected
        :param by_metric: a metric on which the dependence will be built
        :param flat: return format
        :return:
        """
        if by_metric not in self.metrics:
            raise KeyError('No such metric in data')

        related_data = defaultdict(StanDict)

        for ts in self:
            if by_metric in self[ts]:
                for metric in self.metrics:
                    if metric != by_metric:
                        related_data[self[ts][by_metric]].setdefault(metric, []).append(self[ts][metric])

        for key in related_data:
            for metric in related_data[key]:
                if related_data[key] is not None:
                    filtered = [val for val in related_data[key][metric] if val is not None]
                    if len(filtered) > 0:
                        related_data[key][metric] = sum(filtered) / len(filtered)
                    else:
                        related_data[key][metric] = None

        if flat:
            flt = StanFlatData()
            for key in sorted(related_data):
                flt[by_metric].append(key)
                for metric in related_data[key]:
                    flt[metric].append(related_data[key][metric])
            return flt

        return related_data

    def save(self, file_path: str):
        # todo: parameter save to JSON
        with open(file_path, 'wb') as pkl:
            pickle.dump(self, pkl, pickle.HIGHEST_PROTOCOL)

    @classmethod
    def load(cls, file_path: str):
        with open(file_path, 'rb') as pkl:
            return pickle.load(pkl)

    def append(self, timestamp, stan_dict: StanDict):
        if type(stan_dict) != StanDict:
            raise TypeError('The value must be StanDict')
        for metric in stan_dict:
            self.metrics.add(metric)
        try:
            self[timestamp] += stan_dict
        except MetricsIntersection as metric:
            print('[WARNING] Keys intersection (Metric: {metric}) in timestamp {ts}'.format(metric=metric,
                                                                                            ts=timestamp))

    def flat(self):
        """
        Convert to flat data format
        """
        flat = StanFlatData()
        for index, ts in enumerate(sorted(self.keys())):
            flat['timestamp'].append(ts)
            flat['index'].append(index)
            for metric in self.metrics:
                flat[metric].append(self[ts][metric])
        return flat


class StanFlatData(defaultdict):
    """
    Is a defaultdict with list() as a default_factory.
    Extended with StanData methods for flexible key filtering.
    All metrics must have a positional relationship.

    Format:
    StanFlatData(metric1=[],
                 metric2=[],
                 ...)
    """

    def __init__(self):
        super().__init__(list)

    def __repr__(self):
        return dict.__repr__(self)

    def append(self, metrics: dict):
        for metric in metrics:
            self[metric].append(metrics[metric])

    def relate(self, by: str):
        # TODO: Implement?

        pass

    def keys(self, starts=None, contains=None):
        """
        Custom method for flexible keys filtering
        :param starts: return keys that starts with
        :param contains: return keys that contains
        :return: Iterable of keys
        """
        if starts and not contains:
            return [key for key in super().keys() if key.startswith(starts)]
        elif contains and not starts:
            return [key for key in super().keys() if contains in key]
        elif starts and contains:
            return [key for key in super().keys() if key.startswith(starts) and contains in key]
        else:
            return super().keys()
