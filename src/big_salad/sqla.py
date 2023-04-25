import logging
import typing

from sqlalchemy.engine import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__file__)


def get_sqla_eng_str(engine_str: str) -> str:
    """
    Get sqlalchemy engine string for the connection string. e.g. for postgres postgresql+psycopg2://

    :param engine_str: mysql or postgres
    :return: engine portion of the database connection uri
    :raises KeyError: raises KeyError when
    """
    try:
        return {"mysql": "mysql+pymysql", "postgres": "postgresql+psycopg2", "postgresql": "postgresql+psycopg2"}[
            engine_str.lower()
        ]
    except KeyError as e:
        logger.exception(e)
        raise KeyError("Unsupported sql dialect") from e


def get_session_dict(database_connection_dict: typing.Dict[str, str]) -> sessionmaker:
    """
    Get a database session uninstantiated class from the database connection dictionary provided in vault

    :param database_connection_dict: vault provided json dictionary of the database connection
    :return: uninstantiated session class for the database
    """
    # The json vault information defines engine slightly differently than what we need in the sqlalchemy
    # engine part of the uri.
    logger.info("Get sqlalchemy session")
    engine_str = database_connection_dict.pop("engine")
    url_object = URL.create(get_sqla_eng_str(engine_str), **database_connection_dict)
    engine = create_engine(url_object)
    return sessionmaker(engine)


def get_session_factory(engine):
    """
    Creates and configures a session factory for database interactions.

    Parameters:
    engine: The SQLAlchemy engine instance to bind the session factory to.

    Returns:
    A configured session factory instance that can be used to create database sessions.
    """
    factory = sessionmaker()
    factory.configure(bind=engine)
    return factory


def get_session(engine):
    """
    Creates and returns a new SQLAlchemy session object.

    Parameters:
    engine: SQLAlchemy engine instance used to bind the session factory.

    Returns:
    A new SQLAlchemy session instance.
    """
    factory = get_session_factory(engine)
    return factory()


def get_session_from_url(db_url, echo=False):
    """
    Establishes a database session from a provided database URL.

    Parameters:
    db_url (str): The database connection URL.
    echo (bool): If True, enables the SQLAlchemy engine logging.

    Returns:
    Session: A configured SQLAlchemy session connected to the database.
    """
    engine = get_engine(db_url, echo)
    session = get_session(engine)
    return session


def get_session_and_engine_from_url(db_url, echo=False):
    """
    Creates a database engine and session from the given database URL.

    Parameters:
    db_url (str): The database URL for establishing a connection.
    echo (bool): If True, the SQLAlchemy engine will log all SQL statements. Default is False.

    Returns:
    Session: The SQLAlchemy session object for interacting with the database.
    Engine: The SQLAlchemy engine object responsible for database connection.
    """
    engine = get_engine(db_url, echo)
    session = get_session(engine)
    return session, engine


def get_engine(db_url, echo=False, isolation_level="READ COMMITTED"):
    """
    Create and return a SQLAlchemy engine instance.

    Arguments:
    db_url (str): The database connection URL.
    echo (bool): Flag to enable or disable SQL query logging. Default is False.
    isolation_level (str): The transaction isolation level for the database connection. Default is "READ COMMITTED".

    Returns:
    engine (sqlalchemy.engine.Engine): An instance of the SQLAlchemy engine.
    """
    engine = create_engine(db_url, echo=echo, isolation_level=isolation_level)
    return engine
