"""

"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session


class Connection:
    cwd = os.path.dirname(os.path.abspath(__file__))
    url = os.environ.get("DATABASE_URL", f"sqlite:///{cwd}/database.db").replace(
        "postgres", "postgresql+psycopg2"
    )
    Engine = create_engine(url=url, echo=False, pool_size=20)
    ScopedSession = scoped_session(sessionmaker(bind=Engine))

    def __init__(self, url: str | None = None) -> None:
        if url is not None:
            self.url = url


class ContextSession:

    def __enter__(self, url: str | None = None):
        """
        Enter the context and return a new session.
        """
        self.session = Connection(url=url).ScopedSession()
        return self.session

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the context and handle session commits, rollbacks, and closures.
        """
        if exc_type is None:
            self.session.commit()
        else:
            self.session.rollback()
            raise exc_value
        self.session.close()
