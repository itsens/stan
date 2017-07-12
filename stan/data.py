from collections import defaultdict


class StanDict(dict):
    """
    Is a dict() of metrics with custom method keys() for flexible key filtering.
    """
    def keys(self, starts=None, contains=None):
        if starts and not contains:
            return [key for key in super().keys() if key.startswith(starts)]
        elif contains and not starts:
            return [key for key in super().keys() if contains in key]
        elif starts and contains:
            return [key for key in super().keys() if key.startswith(starts) and contains in key]
        else:
            return super().keys()


class StanJoinedData(defaultdict):
    """
    Is a defaultdict with StanData as a default_factory.
    StanData is a dict() of metrics with custom method keys() for flexible key filtering.

    Format:
    StanJoinedData(timestamp1: StanData,
                   timestamp2: StanData,
                   timestamp3: StanData,
                   ...)
    """
    def __init__(self):
        super().__init__(StanDict)

    def __repr__(self):
        return dict.__repr__(self)

    def append(self, timestamp, stan_dict: StanDict):
        if timestamp in self:
            raise KeyError('Existing timestamp')
        self[timestamp] = stan_dict

    def flat(self):
        """
        Convert to flat data format
        """
        flat = StanFlatData()
        for ts in sorted(self.keys()):
            flat['timestamp'].append(ts)
            for metric in self[ts]:
                flat[metric].append(self[ts][metric])
        return flat


class StanFlatData(StanDict, defaultdict):
    """
    Is a defaultdict with list() as a default_factory.
    Extended with StanData methods for flexible key filtering.
    All metrics must have a positional relationship.

    Format:
    StanFlatData(timestamp=[],
                 metric1=[],
                 metric2=[],
                 ...)
    """
    def __init__(self):
        super().__init__(list)
        self['timestamp'] = []

    def __repr__(self):
        return dict.__repr__(self)

    def append(self, metrics: dict):
        if 'timestamp' not in metrics:
            raise KeyError('metrics dict must have "timestamp"')
        self['timestamp'].append(metrics['timestamp'])
        for metric in metrics:
            if metric != 'timestamp':
                self[metric].append(metrics[metric])

    def join(self):
        """
        Convert to joined data format
        """
        data = StanJoinedData()
        for offset, ts in enumerate(self['timestamp']):
            for metric in self.keys():
                if metric != 'timestamp':
                    data[ts][metric] = self[metric][offset]
        return data
