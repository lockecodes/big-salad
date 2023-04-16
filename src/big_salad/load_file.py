import csv
from pathlib import Path

import click
from sqlalchemy import text

from big_salad.sqla import get_session

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
    Chunk generator. Take a CSV `reader` and yield
    `chunksize` sized slices.
    """
    chunk = []
    for i, line in enumerate(reader):
        if i % chunksize == 0 and i > 0:
            yield chunk
            del chunk[:]  # or: chunk = []
        chunk.append(line)
    yield chunk


@click.group()
def load():
    pass


@load.command()
@click.argument("file-path")
@click.option("--chunksize", default=1000)
@click.option("--exclude", multiple=True, default=[])
def mysql(file_path: str, chunksize: int, exclude: list):
    file_path = Path(file_path)
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
            with get_session(local_mysql)() as session:
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
