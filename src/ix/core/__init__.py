"""

"""

from .tech import *
from .perf import *
from .stat import *


def to_quantiles(
    x: pd.Series,
    quantiles: int = 5,
    zero_aware: int = 0,
) -> pd.Series:
    if len(x.dropna()) < quantiles:
        return pd.Series(data=None)
    try:
        if zero_aware:
            objs = [
                to_quantiles(x[x >= 0], quantiles=quantiles // 2) + quantiles // 2,
                to_quantiles(x[x < 0], quantiles=quantiles // 2),
            ]
            return pd.concat(objs=objs).sort_index()
        return pd.qcut(x=x, q=quantiles, labels=False) + 1
    except ValueError:
        return pd.Series(data=None)


def sum_to_one(x: pd.Series) -> pd.Series:
    return x / x.sum()


def demeaned(x: pd.Series) -> pd.Series:
    return x - x.mean()


def rebase(x: pd.Series) -> pd.Series:
    return x / x.dropna().iloc[0]
