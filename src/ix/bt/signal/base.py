import pandas as pd
# from src.ix.bt.asset import Asset
from src.ix.core import StandardScaler, to_log_return


class Signal:

    normalize_window: int = 200

    def compute(self) -> pd.Series:
        raise NotImplementedError(f"Must Implement `{self.compute.__name__}` method.")

    def normalize(self) -> pd.Series:
        data = self.compute()
        normalized = (
            data.rolling(self.normalize_window)
            .apply(StandardScaler(lower=-2, upper=2).latest)
            .divide(2)
        )
        return normalized

    # def get_performance(self, asset: Asset, periods: int = 1) -> pd.Series:

    #     px = asset.get_data(field="adj_close")
    #     log_return = to_log_return(px=px, periods=periods, forward=True)
    #     log_return = log_return.divide(periods)
    #     w = self.normalize().reindex(log_return.index).ffill().shift(1)
    #     p = log_return.mul(w).cumsum()
    #     return p
