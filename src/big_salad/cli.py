"""
CLI entrypoint
"""
import click

from big_salad.compare import compare_group
from big_salad.formatting import format_group
from big_salad.host import ho
from big_salad.rds import rds
from big_salad.sql import sql
from big_salad.aws_metrics_collector.rds import collect_metrics


@click.group()
def cli():
    pass


cli.add_command(compare_group)
cli.add_command(format_group)
cli.add_command(ho)
cli.add_command(rds)
cli.add_command(sql)
cli.add_command(collect_metrics)

if __name__ == "__main__":
    cli()
