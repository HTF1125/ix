import inspect
from src.ix.bt.indicator import Indicator
from src.ix.bt.indicator import MACDSignal
import pandas as pd
from src.ix.db import get_px


class IndicatorManager(dict[str, Indicator]): ...


class Asset:

    def __init__(self, name: str) -> None:
        self.name = name
        self.data = pd.DataFrame()
        self.indicators = IndicatorManager()

    def add_indicator(self, name: str, indicator: type[Indicator]) -> None:
        indicator_ins = indicator()

        kwargs = {}
        for param, _ in inspect.signature(indicator_ins.compute).parameters.items():
            kwargs[param] = self.get(param)
        indicator_ins.compute(**kwargs)
        self.indicators[name] = indicator_ins

    def __repr__(self) -> str:
        return self.name

    def get(self, item: str) -> pd.Series:
        if item not in self.data.columns:
            self.data[item] = get_px(self.name, item)
        out = self.data[item]
        return out


class Universe(list[Asset]):

    def __init__(self, *assets: str) -> None:
        super().__init__()
        if assets is not None:
            self.extend([Asset(ticker) for ticker in assets])

    def __getitem__(self, item: str) -> pd.DataFrame:
        data = {asset.name: asset.get(item) for asset in self}
        return pd.DataFrame(data).sort_index(ascending=True)


class Strategy:

    indicators = (("macd", MACDSignal),)
    frequency = 1
    principal = cash = 10_000

    def __init__(self, *assets: str) -> None:
        self.book = {}

        self.universe = Universe(*assets)
        for asset in self.universe:
            for name, indicator in self.indicators:
                asset.add_indicator(name=name, indicator=indicator)

    def buy(self, asset: Asset, shares: float) -> None:
        if asset not in self.book:
            self.book[asset] = {
                "shares": 0,
                "bookprice": 0,
                "marketvalue": 0,
                "order": 0,
            }
        print(f"buy {self.date}, {asset} {shares}")

        self.book[asset]["order"] = shares

    def sell(self, asset: Asset, shares: float) -> None:
        print(f"sell {self.date}, {asset} {shares}")
        self.book[asset]["order"] -= shares

    def run(self) -> "Strategy":

        for self.date in self.universe["adj_close"].index:
            self.execute()
            for asset in self.universe:
                bullish = asset.indicators["macd"].bullish().get(self.date)
                if bullish == True:
                    p = asset.get("adj_close").get(self.date)
                    if not isinstance(p, (int, float)):
                        continue
                    self.buy(asset, self.cash // p)
                    continue
                bearish = asset.indicators["macd"].bearish().get(self.date)
                if bearish == True:
                    b = self.book.get(asset)
                    if b is None:
                        continue
                    self.sell(asset, self.book[asset]["shares"])
                    continue

        return self

    def execute(self):

        for asset, _b in self.book.items():
            if _b["order"] != 0:
                p = asset.get("adj_close").get(self.date)
                s = _b["order"]
                self.cash -= s * p
                _b["order"] = 0
                self.book[asset]["shares"] += s

    def value(self) -> float:

        v = self.cash
        for asset, _b in self.book.items():
            v += asset.get("adj_close").get(self.date) * _b["shares"]
        return v


from src.ix.bt.signal import OecdCliRoGG


class OecdCliStrategy(Strategy):
    assets = ["SPY.US.Equity"]
    signal = OecdCliRoGG().normalize().resample("D").last().ffill()

    def run(self) -> "Strategy":

        for self.date in self.universe["adj_close"].index:
            self.execute()

            s = self.signal.get(self.date, None)

            if s is None:
                continue

            for asset in self.universe:
                bullish = s > 0

                if bullish == True:
                    p = asset.get("adj_close").get(self.date)
                    if p is None:
                        continue
                    s = self.cash // p

                    if s > 0:
                        self.buy(asset, s)
                    continue
                bearish = s < 0
                if bearish == True:
                    b = self.book.get(asset)

                    if b is None:
                        continue
                    s = int(b["shares"])
                    if s >= 2:
                        self.sell(asset, s)
                    continue

        return self


from src.ix.bt import RSIRange


class RsiRange(Strategy):

    indicators = (("rsirange", RSIRange),)
    frequency = 1
    principal = cash = 10_000

    def buy(self, asset: Asset, shares: float) -> None:
        if asset not in self.book:
            self.book[asset] = {
                "shares": 0,
                "bookprice": 0,
                "marketvalue": 0,
                "order": 0,
            }
        print(f"buy {self.date}, {asset} {shares}")

        self.book[asset]["order"] = shares

    def sell(self, asset: Asset, shares: float) -> None:
        print(f"sell {self.date}, {asset} {shares}")
        self.book[asset]["order"] -= shares

    def run(self) -> "Strategy":

        for self.date in self.universe["adj_close"].index:
            self.execute()
            for asset in self.universe:

                bullish = asset.indicators["rsirange"].bullish().get(self.date)

                if bullish == True:
                    p = asset.get("adj_close").get(self.date)
                    if p is None:
                        continue
                    self.buy(asset, self.cash // p)
                    continue
                bearish = asset.indicators["rsirange"].bearish().get(self.date)
                if bearish == True:
                    b = self.book.get(asset)
                    if b is None:
                        continue
                    self.sell(asset, self.book[asset]["shares"])
                    continue
        return self

    def execute(self):

        for asset, _b in self.book.items():
            if _b["order"] != 0:
                p = asset.get("adj_close").get(self.date)
                s = _b["order"]
                self.cash -= s * p
                _b["order"] = 0
                self.book[asset]["shares"] += s

    def value(self) -> float:

        v = self.cash
        for asset, _b in self.book.items():
            v += asset.get("adj_close").get(self.date) * _b["shares"]
        return v
