"""
Click entrypoint functions
"""

import os
from typing import List

from big_salad.aws_metrics_collector import LogWrapper
from big_salad.aws_metrics_collector.aws import collect_aws_instance_data
from big_salad.aws_metrics_collector.utils import dict_to_json
from pathlib import Path
import click


@click.group()
def collect_metrics():
    pass


@collect_metrics.command()
def rds(
    aws_profile: str,
    service_list: List[str] = None,
    region_list: List[str] = None,
    all_regions: bool = False,
    dump_json: bool = True,
    json_destination: str = None,
    log: LogWrapper = None,
):
    """
    Command-line handler for collecting AWS RDS metrics.

    Parameters:
    aws_profile (str): The name of the AWS profile to use for authentication.
    service_list (List[str]): List of AWS services to collect metrics for. Defaults to ["rds"].
    region_list (List[str]): List of AWS regions to collect metrics from. Defaults to ["us-east-1"].
    all_regions (bool): Flag to specify whether to collect metrics from all AWS regions. Defaults to False.
    dump_json (bool): Flag to specify whether to export the data to a JSON file. Defaults to True.
    json_destination (str): File path for storing the exported JSON data. Defaults to a file named "aws-metrics.json" in the current directory.
    log (LogWrapper): Logger instance for logging messages. Defaults to a new LogWrapper instance.

    Behavior:
    - Collects AWS instance data for specified services and regions.
    - Exports data to a JSON file if dump_json is True.
    - Logs progress and key actions, such as file operations and start/end of the process.

    Raises:
    - Any exception encountered during data collection or file operations is propagated.
    """
    service_list = service_list or ["rds"]
    region_list = region_list or ["us-east-1"]
    json_destination = json_destination or Path(Path.cwd(), "aws-metrics.json")
    log = log or LogWrapper()
    log.info(message="START")
    # log_wrapper.info(message='Database file to be used: {}'.format(database_file))
    data = collect_aws_instance_data(
        services=service_list, all_regions=all_regions, regions=region_list, target_profile=aws_profile, log_wrapper=log
    )
    if dump_json is True:
        if os.path.exists(json_destination):
            log.info(message='Removing exiting data file "{}"'.format(json_destination))
            os.unlink(json_destination)
        log.info(message='Writing out raw data file to "{}"'.format(json_destination))
        with open(json_destination, "w") as f:
            f.write(dict_to_json(data.to_dict()))
    log.info(message="DONE")
