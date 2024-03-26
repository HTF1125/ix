# This class represents a signal related to the OECD US Composite Leading Indicators.


import numpy as np
import pandas as pd
from .base import Signal
from src.ix.db import get_px
# from src.ix.core import to_macd_signal

class AudCadMom(Signal):

    def compute(self) -> pd.Series:
        data = get_px("AUDCAD.Curncy")
        return data * (-1)


class ISC(Signal):

    corr_win: int = 500

    def compute(self) -> pd.Series:

        data = get_px("T10YIE.Index, DGS10.Index, THREEFFTP10.Index").dropna()
        data["ShortTerm.Index"] = (
            data["DGS10.Index"] - data["THREEFFTP10.Index"] - data["T10YIE.Index"]
        )
        data = (
            data.rolling(self.corr_win)
            .corr()
            .unstack()["ShortTerm.Index"]["T10YIE.Index"]
        )
        data = data.multiply(-1)
        return data
