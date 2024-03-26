# Robert Han

import numpy as np
import pandas as pd


def to_pri_return(px: pd.Series, periods: int = 1, forward: bool = False) -> pd.Series:

    out = px / px.shift(periods=periods) - 1
    if forward:
        out = out.shift(periods=-periods)
    return out


def to_log_return(px: pd.Series, periods: int = 1, forward: bool = False) -> pd.Series:
    return to_pri_return(px=px, periods=periods, forward=forward).apply(np.log1p)


def to_cum_return(px: pd.Series) -> pd.Series:
    px = px.dropna()  # Remove NaN values
    return px.iloc[-1] / px.iloc[0] - 1


def to_ann_return(px: pd.Series, ann_factor: float = 252.0) -> float:
    ann_log_return = to_log_return(px).mean() * ann_factor
    return np.exp(ann_log_return) - 1


def to_ann_volatility(px: pd.Series, ann_factor: float = 252.0) -> float:
    std = to_log_return(px=px).std()
    return std * ann_factor**0.5


def to_ann_sharpe(
    px: pd.Series,
    risk_free: float = 0.0,
    ann_factor: float = 252.0,
) -> float:
    ar = to_ann_return(px, ann_factor=ann_factor)
    av = to_ann_volatility(px, ann_factor=ann_factor)
    return (ar - risk_free) / av


def to_drawdown(px: pd.Series) -> pd.Series:
    return px.divide(px.expanding().max()) - 1


def to_max_drawdown(px: pd.Series) -> float:
    return to_drawdown(px).min()
