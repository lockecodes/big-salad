import click

from big_salad.load_file import load
from big_salad.rds import rds


@click.group()
def cli():
    pass


cli.add_command(load)
cli.add_command(rds)

if __name__ == "__main__":
    cli()
