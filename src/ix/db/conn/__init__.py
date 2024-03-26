"""

"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from src.ix.misc import getLogger, getEnv


class Connection:

    logger = getLogger("Connection")
    cwd = os.path.dirname(os.path.abspath(__file__))

    url = getEnv(".env").get("DATABASE_URL")
    logger.critical(getEnv(".env"))
    if url is None:
        url = os.environ.get("DATABASE_URL", f"sqlite:///{cwd}/database.db")
    url = url.replace("postgres", "postgresql+psycopg2")
    logger.warning(url)
    Engine = create_engine(url=url, echo=False, pool_size=20)
    ScopedSession = scoped_session(sessionmaker(bind=Engine))


class ContextSession:

    def __enter__(self):
        """
        Enter the context and return a new session.
        """
        self.session = Connection().ScopedSession()
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
