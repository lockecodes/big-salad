import csv
from pathlib import Path

import click
from sqlalchemy import text

from big_salad.config import context_mutate
from big_salad.sqla import get_session_dict

LOCAL_MYSQL = {
    "database": "dbname",
    "engine": "mysql",
    "host": "localhost",
    "password": "",
    "port": 3306,
    "username": "root",
}


def gen_chunks(reader, chunksize=100):
    """
    Generator function to yield chunks of lines from an iterable reader.

    Parameters:
    reader: An iterable object, typically a file or list, from which lines are read.
    chunksize: The number of lines to include in each yielded chunk. Default is 100.

    Yields:
    List of lines, representing a chunk of the specified size from the reader.

    Function behavior:
    - Iterates through the given reader line by line.
    - Collects lines into a list ("chunk") until the specified chunksize is reached.
    - Yields the accumulated chunk and resets it to an empty list for further collection.
    - Continues this process until all lines in the reader have been processed.
    - Yields any remaining lines at the end that do not make up a full chunk.
    """
    chunk = []
    for i, line in enumerate(reader):
        if i % chunksize == 0 and i > 0:
            yield chunk
            del chunk[:]  # or: chunk = []
        chunk.append(line)
    yield chunk


@click.group()
def sql():
    """
    Defines a Click command group for SQL-related commands.

    This serves as a parent group to organize related subcommands under a single namespace for better management of SQL-related operations.
    """
    pass


@sql.command()
@click.argument("file-path")
@click.option("--chunksize", default=1000)
@click.option("--exclude", multiple=True, default=[])
@click.option("--dialect", type=click.types.Choice(["postgres", "mysql"]))
def load_csv(file_path: str, chunksize: int, exclude: list, dialect: str):
    """
    Command-line interface function for loading CSV data into a database.

    Arguments:
    - file_path: Path to the CSV file to be loaded.
    - chunksize: Number of rows to process per batch (default is 1000).
    - exclude: List of columns to exclude during processing.
    - dialect: Specifies which database type (either "mysql" or "postgres") to target.

    Behavior:
    - If the dialect is "mysql", the function calls a helper function `_load_mysql` to handle the file loading process with the specified parameters.
    - If the dialect is "postgres", a NotImplementedError is raised since PostgreSQL is not yet supported.

    Decorators:
    - Marked as an SQLAlchemy command with @sql.command.
    - Accepts arguments and options via command-line interface using the Click library.
    """
    file_path = context_mutate(Path(file_path))
    if dialect == "mysql":
        _load_mysql(file_path=file_path, chunksize=chunksize, exclude=exclude)
    else:
        raise NotImplementedError("still need to write postgresql")


def _load_mysql(file_path: Path, chunksize: int, exclude: list):
    """
    _load_mysql(file_path: Path, chunksize: int, exclude: list)

    Loads data from a CSV file into a MySQL database table. The CSV file is parsed and inserted into the corresponding database table where the table name is derived from the file name without the extension. Rows are inserted in chunks to optimize performance, and specified fields can be excluded from the insertion.

    Parameters:
    - file_path: Path object representing the path to the CSV file to be loaded.
    - chunksize: The number of rows to process and insert into the database at a time.
    - exclude: A list of field names to be excluded from the insertion.

    Functionality:
    - Reads the CSV file and extracts the header fields while excluding the specified fields.
    - Constructs a SQL INSERT query based on the file structure and specified field names.
    - Processes the CSV data in chunks and inserts the data into the MySQL database while temporarily disabling and enabling foreign key checks for each transaction.
    - Utilizes a session-based connection to execute the query and commit the transaction for each processed chunk.
    - Logs the field names and query to the console during execution for debugging purposes.
    """
    table_name = file_path.name.split(".")[0]
    with open(file_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        field_names = [field for field in reader.fieldnames if field not in exclude]
        column_names = ",".join(field_names)
        markers = ",".join(f":{col}" for col in field_names)
        query = f"""
        insert into {table_name} ({column_names})
        values ({markers})
        """
        click.echo(f"field names: {field_names}")
        click.echo(f"query: {query}")
        for chunk in gen_chunks(reader, chunksize=chunksize):
            local_mysql = LOCAL_MYSQL.copy()
            with get_session_dict(local_mysql)() as session:
                session.execute(text("SET FOREIGN_KEY_CHECKS=0"))
                session.execute(
                    text(query),
                    params=[
                        {key: val if val else None for key, val in val_dict.items() if key not in exclude}
                        for val_dict in chunk
                    ],
                )
                click.echo("commit")
                session.execute(text("commit"))
                session.execute(text("SET FOREIGN_KEY_CHECKS=1"))
