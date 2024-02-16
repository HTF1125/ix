"""



"""

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, VARCHAR, Text, ForeignKey, Date, Float
import pandas as pd
from .conn import Connection, ContextSession
from .raw import RawData
from ..core.terminal import getLogger


Base = declarative_base()


def create() -> bool:

    try:

        Base.metadata.create_all(Connection.Engine)
        return True
    except Exception as e:
        print(e)
        return False


def drop() -> bool:

    try:

        Base.metadata.drop_all((Connection.Engine))
        return True
    except Exception as e:
        print(e)
        return False


class ModelBase(Base):
    __abstract__ = True

    @classmethod
    def create(cls) -> bool:
        try:
            cls.__table__.create(Connection.Engine)
            return True
        except:
            return False

    @classmethod
    def drop(cls) -> bool:
        try:
            cls.__table__.drop(Connection.Engine)
            return True
        except:
            return False

    @classmethod
    def insert(
        cls,
        records: list | pd.DataFrame,
    ) -> bool:

        if isinstance(records, pd.DataFrame):
            records = records.to_dict("records")

        with ContextSession() as session:
            session.bulk_insert_mappings(cls, records)
            session.commit()
            return True

    @classmethod
    def get(cls, **kwargs) -> pd.DataFrame:
        with ContextSession() as session:
            query = session.query(cls)
            if kwargs:
                query = query.filter_by(**kwargs)
            return pd.read_sql(sql=query.statement, con=query.session.connection())

    @classmethod
    def delete(cls, **kwargs) -> bool:
        from sqlalchemy import delete

        query = delete(cls)
        if kwargs:
            query = query.filter_by(**kwargs)
        with ContextSession() as session:
            session.execute(query)
            session.commit()
            return True


class Meta(ModelBase):
    __tablename__ = "meta"
    id = Column(Integer, autoincrement=True, primary_key=True)
    ticker = Column(VARCHAR(30), unique=True)
    exchange = Column(VARCHAR(30), nullable=True)
    market = Column(VARCHAR(30))
    sec_type = Column(VARCHAR(30), nullable=True)
    name = Column(VARCHAR(255), nullable=False)
    remark = Column(Text, nullable=True)
    source = Column(VARCHAR(30), nullable=True)
    code = Column(VARCHAR(50), nullable=True)
    freq = Column(VARCHAR(5), nullable=True)
    link = Column(Text, nullable=True)
    detail = Column(Text, nullable=True)
    remark = Column(Text, nullable=True)

    @classmethod
    def update_px(cls, source: str = "", chunksize: int = 10_000) -> bool:

        logger = getLogger(cls.update_px)

        logger.debug("hello world")

        if source == "" or source.upper() == "YAHOO":
            with ContextSession() as session:
                query = session.query(Meta.code, Meta.id)
                query = query.filter(Meta.source == "YAHOO")
                meta = pd.read_sql(
                    sql=query.statement,
                    con=query.session.connection(),
                    index_col=["code"],
                )
                meta = meta.squeeze().to_dict()
                # data = RawData().get_yahoo_data(tickers=list(meta.keys()))
                # data = data.rename(columns=meta)
                # data.columns.names = ["columns", "meta_id"]
                # data = data.stack().reset_index()
                # data.columns = data.columns.str.lower().str.replace(" ", "_")
                # print(data)
                # session.query(PxData).filter(PxData.meta_id.in_(list(meta.values()))).delete()
                # session.flush()
                # records = data.to_dict(orient="records")
                # session.bulk_insert_mappings(PxData, records)
                # session.flush()


class PxData(ModelBase):

    __tablename__ = "px_data"

    meta_id = Column(
        ForeignKey(f"{Meta.__tablename__}.id"),
        primary_key=True,
    )
    date = Column(Date, primary_key=True)
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=True)
    adj_close = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    dividends = Column(Float, nullable=True)
    stock_splits = Column(Float, nullable=True)
    capital_gains = Column(Float, nullable=True)
