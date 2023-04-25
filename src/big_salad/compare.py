"""
Module: compare

This module provides CLI commands for comparing JSON and CSV files, utilizing the Click library.
It is designed for use as part of a CLI application and provides the following functionalities:

1. **Comparison of JSON files**:
   - The `compare_json` command allows users to compare two specified JSON files.

2. **Comparison of CSV files**:
   - The `compare_csv` command allows users to compare two specified CSV files using advanced options,
     such as case-insensitive key comparison and ignoring specific key patterns.

Modules and Libraries Used:
- `csv`: For reading and parsing CSV files.
- `re`: For regex operations like ignoring keys based on patterns.
- `pathlib.Path`: For managing file paths.
- `click`: For creating a command-line interface.
- `orjson`: For efficient JSON parsing.
- `deepdiff.DeepDiff`: For performing deep-difference comparison between data structures.
- `deepdiff.serialization.save_content_to_path`: For saving comparison results to a file.
- `big_salad.config.context_mutate`: For pre-processing file paths.
- `big_salad.formatting._format_json`: For formatting the JSON output.

Commands:

1. `compare`:
   - A Click command group that serves as a container for subcommands related to data comparison.

2. `compare json`:
   - Command to compare two JSON files.
      * Arguments:
        - `old`: Path to the first JSON file.
        - `new`: Path to the second JSON file.
      * Processes the input files' paths and parses their content but lacks the final implementation for comparison.

3. `compare csv`:
   - Command to compare two CSV files.
      * Arguments:
        - `old`: Path to the first CSV file.
        - `new`: Path to the second CSV file.
      * Options:
        - `--destination`: Path to save the comparison result as a JSON file. Default: './_files/diff.json'.
        - `--ignore-key-case`: Whether to ignore case differences in keys during comparison.
        - `--ignore-key-pattern`: Regex pattern to ignore keys during comparison. Default: '\_fivetran*'.
      * Compares the rows between the old and new CSV files, applies the specified options during processing,
        computes the differences using `deepdiff.DeepDiff`, and saves the output to the specified location.

"""
import csv
import re
from pathlib import Path

import click
import orjson
from deepdiff import DeepDiff
from deepdiff.serialization import save_content_to_path

from big_salad.config import context_mutate
from big_salad.formatting import _format_json


@click.group(name="compare")
def compare_group():
    """
    Defines a Click command group named 'compare'.

    This group serves as a container for related CLI commands,
    grouping them together under the 'compare' namespace. Commands added to
    this group can be invoked as subcommands of 'compare'.

    No specific functionality is implemented in this function itself.
    It acts as a decorator to define command grouping.
    """
    pass


@compare_group.command(name="json")
@click.argument("old", type=str)
@click.argument("new", type=str)
def compare_json(old: str, new: str):
    """
    This function registers a CLI command named "json" under the `compare_group` group.
    The command is used to compare the content of JSON files specified by two paths.

    Arguments:
    - old (str): The path to the first JSON file to compare (original).
    - new (str): The path to the second JSON file to compare (new).

    The function performs the following steps:
    1. Processes the `old` and `new` file paths using the `context_mutate` function.
    2. Reads and parses the content of the first JSON file (old).
    3. Reads and parses the content of the second JSON file (new).

    Note:
    The implementation of the comparison logic for the loaded JSON content is incomplete.
    """
    old = context_mutate(old)
    new = context_mutate(new)
    with open(old, "r") as fd:
        src_old = orjson.loads(fd.read())

    with open(new, "r") as fd:
        src_two = orjson.loads(fd.read())
    # It looks as if I did not finish this comparison function


@compare_group.command(name="csv")
@click.argument("old", type=str)
@click.argument("new", type=str)
@click.option("--destination", type=str, default="./_files/diff.json")
@click.option("--ignore-key-case", is_flag=True)
@click.option("--ignore-key-pattern", type=str, default="\_fivetran*")
def compare_csv(old: str, new: str, destination: str, ignore_key_case: bool, ignore_key_pattern: str):
    """
    Command to compare two CSV files and generate differences.

    Arguments:
    old: Path to the old CSV file.
    new: Path to the new CSV file.

    Options:
    --destination: Path to save the output of the comparison as a JSON file. Default is './_files/diff.json'.
    --ignore-key-case: Flag to specify whether key comparison should ignore case.
    --ignore-key-pattern: Pattern to exclude keys from comparison. Default pattern is '\_fivetran*'.

    Description:
    The command reads two provided CSV files, processes their data according to the options, and computes the differences
    between the two files. Differences are computed using a deep comparison approach.

    The optional '--ignore-key-case' flag allows reducing keys to lowercase during comparison. The '--ignore-key-pattern'
    option can be used to provide a regex pattern to ignore specific keys in the comparison process.

    The output is saved as a JSON file at the specified '--destination' path. Additionally, the JSON output is formatted,
    and any previous backup files are not retained.
    """
    old = context_mutate(old)
    new = context_mutate(new)
    destination = Path(destination)
    with open(old, "r", newline="") as fd:
        reader = csv.DictReader(fd)
        src_old = [
            {
                key.lower() if ignore_key_case else key: value
                for key, value in row.items()
                if ignore_key_pattern is None or re.match(ignore_key_pattern, key) is None
            }
            for row in reader
        ]

    with open(new, "r", newline="") as fd:
        reader = csv.DictReader(fd)
        src_two = [
            {
                key.lower() if ignore_key_case else key: value
                for key, value in row.items()
                if ignore_key_pattern is None or re.match(ignore_key_pattern, key) is None
            }
            for row in reader
        ]

    diff = DeepDiff(src_old, src_two)
    print(diff)
    destination.touch(exist_ok=True)
    save_content_to_path(content=diff, path=destination, file_type="json", keep_backup=False)
    _format_json(destination)
