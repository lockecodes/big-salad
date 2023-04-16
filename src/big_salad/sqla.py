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


def get_session(database_connection_dict: typing.Dict[str, str]) -> sessionmaker:
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
