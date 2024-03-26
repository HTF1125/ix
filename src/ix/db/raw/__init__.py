import os
import pandas as pd

from ...misc.fmt import as_date


class RawData:

    def get_data(self, sheet: str) -> pd.DataFrame:
        filename = os.path.join(os.path.dirname(__file__), "database.xlsx")
        if not os.path.exists(filename):
            raise ValueError(f"file {filename} does not exist.")
        return pd.read_excel(filename, sheet)

    def get_meta(self) -> pd.DataFrame:
        """this is a pass through function"""
        return self.get_data(sheet="meta")

    def get_yahoo_data(
        self, tickers: list[str], start: str = "1900-1-1", end: str = "now"
    ) -> pd.DataFrame:
        import yfinance as yf

        data = yf.download(
            tickers=tickers, start=start, end=as_date(end), progress=False, actions=True
        )
        return data
