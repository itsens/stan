from collections import defaultdict
import pickle


class StanDict(dict):
    """
    Is an extended dict() with custom method keys() for flexible key filtering
    and with the ability to stack two entities.
    """

    def __add__(self, other):
        if type(other) != type(self):
            raise TypeError('Different types')

        result = StanDict()

        for key in self:
            result[key] = self[key]

        for key in other:
            if key not in result:
                result[key] = other[key]
            else:
                raise KeyError('Keys intersection')

        return result

    def __missing__(self, key):
            return None

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

    def __setitem__(self, key, value):
        if type(key) is not int or key > 253402289999:
            raise KeyError('The key is not Unix time')
        if type(value) != StanDict:
            raise TypeError('The value must be StanDict')
        for metric in value:
            self.metrics.add(metric)
        super().__setitem__(key, value)

    def __add__(self, other):
        if type(other) != type(self):
            raise TypeError('Different types')

        result = StanData()

        for key in self:
            result[key] = self[key]

        for key in other:
            result[key] = result[key] + other[key]

        return result

    def __reduce__(self):
        t = super().__reduce__()
        return (t[0], ()) + t[2:]

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
        self[timestamp] = self[timestamp] + stan_dict

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
