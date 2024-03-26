import pandas as pd
from ..conn import ContextSession
from ..models import Meta, PxData


def get_px(ticker: str, field: str = "adj_close") -> pd.Series:
    px_col = getattr(PxData, field)
    if px_col is None:
        raise ValueError(f"field {field} does not exist.")
    with ContextSession() as session:
        query = session.query(PxData.date, px_col)
        query = query.join(Meta, Meta.id == PxData.meta_id)
        query = query.filter(Meta.ticker == ticker)
        query = query.order_by(PxData.date)  # Sort by date ascending
        data = pd.read_sql(
            sql=query.statement,
            con=session.connection(),
            parse_dates=[PxData.date.name],
            index_col=[PxData.date.name],
        ).squeeze()
        data.name = ticker
        return data


def get_oecd_cli_us() -> pd.Series:
    px = get_px(ticker="USALOLITONOSTSAM.Index", field="adj_close")
    return px.resample("M").last()
