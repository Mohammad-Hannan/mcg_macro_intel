import numpy as np


def percentile_rank(series, value):
    if not series:
        return 50

    array = np.array(series)
    return float(np.sum(array <= value) / len(array) * 100)