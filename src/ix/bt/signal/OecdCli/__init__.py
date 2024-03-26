"""

"""

import numpy as np
import pandas as pd
from src.ix.bt.signal.base import Signal
from src.ix.db import get_oecd_cli_us


class OecdCliRoCC(Signal):
    """
    Why OECD US Composite Leading Indicators?
        The paramount driver of the market is undoubtedly investor expectations.
        Market rallies are often fueled by optimistic projections of economic
        improvements, rather than when the economy is already at its peak.
        Consequently, utilizing a forward-looking indicator with comprehensive
        economic coverage becomes highly relevant.

        The OECD US Composite Leading Indicators present a compelling choice
        in this regard. By encompassing a diverse array of economic indicators
        and data, these indicators offer valuable insights into the future
        direction of the economy. As a result, they serve as a crucial tool
        for investors seeking to anticipate market trends and make informed decisions.

        In summary, opting for the OECD US Composite Leading Indicators is a
        logical and strategic move, given their ability to provide early signals
        of economic shifts, which can substantially enhance investment strategies
        and outcomes.
    """

    normalize_window: int = 12

    def compute(self) -> pd.Series:
        data = get_oecd_cli_us()
        data.index = data.index + pd.DateOffset(months=1)
        data = data.diff().diff()
        return data


class OecdCliRoGG(Signal):

    normalize_window: int = 12

    def compute(self) -> pd.Series:

        data = get_oecd_cli_us()
        data.index = data.index + pd.DateOffset(months=1)
        data = data.rolling(12).apply(lambda x: np.gradient(np.gradient(x))[-1])
        return data


class OecdCliRoG(Signal):
    normalize_window: int = 12

    def compute(self) -> pd.Series:
        data = get_oecd_cli_us()
        data.index = data.index + pd.DateOffset(months=1)
        data = data.rolling(12).apply(lambda x: np.gradient(x)[-1])
        return data
