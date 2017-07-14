from collections import defaultdict


class StanDict(dict):
    """
    Is an extended dict()
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
    Is a defaultdict with StanData as a default_factory.
    StanData is a dict() of metrics with custom method keys() for flexible key filtering.

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

    def relate(self, by: str):
        # TODO: Implement
        pass

    def append(self, timestamp, stan_dict: StanDict):
        if type(stan_dict) != StanDict:
            raise TypeError('The value must be StanDict')
        for metric in stan_dict:
            self.metrics.add(metric)
        self[timestamp] = stan_dict

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
