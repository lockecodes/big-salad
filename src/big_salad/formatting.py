"""
Module: format_cli

This module provides a CLI interface for managing and formatting JSON and YAML files using the Click framework. It allows users to perform various operations such as sorting, reformatting, and converting between JSON and YAML formats.

Modules and External Libraries:
- `json`: Standard library module for handling JSON data.
- `click`: Library for creating command-line interfaces.
- `orjson`: A fast JSON library for Python, used for efficient JSON serialization.
- `yaml`: PyYAML library for reading and writing YAML files.
- `collections`: Module for working with specialized container datatypes (e.g., OrderedDict).
- `context_mutate` (from `big_salad.config`): A project-specific utility to transform the file path prior to processing.

Public Functions:
1. `format_group`: Click command group named "format".
    - A CLI command group that acts as a container for JSON and YAML formatting commands.

2. `format_json(file_path, sort_file, to_yaml)`:
    - CLI command for formatting JSON files.
    - Options:
        * `--sort-file`: Sorts the JSON data alphabetically by keys.
        * `--to-yaml`: Converts JSON data to YAML format.

3. `format_yaml(file_path, sort_file, to_json)`:
    - CLI command for formatting YAML files.
    - Options:
        * `--sort-file`: Sorts the YAML data alphabetically by keys.
        * `--to-json`: Converts YAML data to JSON format.

Private Functions:
1. `_format_json(file_path, sort_file, to_yaml)`: Handles formatting actions for JSON files. Handles sorting and YAML conversions conditionally based on input arguments.
2. `_format_yaml(file_path, sort_file, to_json)`: Handles formatting actions for YAML files. Handles sorting and JSON conversions conditionally based on input arguments.

Usage:
- Use the `format` command group to group nested commands for JSON and YAML file formatting.
- Invoke `format json` or `format yaml` on the CLI with the appropriate arguments and flags to perform the desired transformations.

Examples:
- Sort a JSON file:
"""
import collections

import click
import orjson
import yaml

from big_salad.config import context_mutate


@click.group(name="format")
def format_group():
    """
    A Click command group for managing format-related commands.

    This is a Click group that acts as a container for various commands
    relating to formatting tasks. Use this group to organize commands
    hierarchically and logically group them under the "format" namespace.
    """
    pass


@format_group.command(name="json")
@click.argument("file_path", type=str)
@click.option("--sort-file", is_flag=True)
@click.option("--to-yaml", is_flag=True)
def format_json(file_path, sort_file: bool, to_yaml: bool):
    """
    CLI command to format a JSON file. Provides options to sort the JSON keys and convert the JSON data to YAML format.

    Arguments:
    - file_path (str): The path to the JSON file to be formatted.

    Options:
    - --sort-file (bool): If provided, sorts the JSON keys alphabetically.
    - --to-yaml (bool): If provided, converts the JSON data to YAML format.

    Functionality:
    The function processes the file at the given path, transforming its data based on the provided options. The formatted content is managed by invoking _format_json with the appropriate parameters.
    """
    _format_json(context_mutate(file_path), sort_file=sort_file, to_yaml=to_yaml)


def _format_json(file_path, sort_file: bool = False, to_yaml: bool = False):
    """
    Formats a JSON file by either sorting its content, converting it to YAML, or reformatting its structure.

    Parameters:
    file_path: The path to the JSON file to be formatted.
    sort_file: Optional; If True, the JSON content will be sorted based on keys.
    to_yaml: Optional; If True, the JSON file will be converted and saved as a YAML file.

    Behavior:
    - Reads the JSON content from the given file path.
    - If sort_file is True, sorts the JSON data by keys.
    - If to_yaml is True, converts the JSON content to YAML format and saves it in a new file with a `.yaml` extension.
    - If to_yaml is False, writes the reformatted JSON content back to the file. The content will have a 2-space indentation and a new line at the end.
    """
    with open(file_path, "r") as fd:
        src = orjson.loads(fd.read())
    content = src.copy()
    if sort_file:
        content = collections.OrderedDict(sorted(src.items()))
    if to_yaml:
        with open(file_path.replace(".json", ".yaml"), "w") as fd:
            yaml.safe_dump(dict(content), fd, allow_unicode=True)
    else:
        with open(file_path, "wb") as fd:
            fd.write(orjson.dumps(content, option=orjson.OPT_INDENT_2 | orjson.OPT_APPEND_NEWLINE))


@format_group.command(name="yaml")
@click.argument("file_path", type=str)
@click.option("--sort-file", is_flag=True)
@click.option("--to-json", is_flag=True)
def format_yaml(file_path, sort_file: bool, to_json: bool):
    """
    CLI command to format a YAML file.

    Arguments:
    file_path: Path to the YAML file to be formatted.

    Options:
    --sort-file: If provided, the YAML file will be sorted by its keys.
    --to-json: If provided, converts the YAML content to JSON format.

    This command processes the given YAML file and applies the respective formatting options such as sorting or converting it to JSON. It internally uses the _format_yaml function to handle the formatting logic.
    """
    _format_yaml(context_mutate(file_path), sort_file=sort_file, to_json=to_json)


def _format_yaml(file_path, sort_file: bool = False, to_json: bool = False):
    """
    Formats a given YAML file based on specified options.

    Parameters:
    file_path: str
        The path to the YAML file to be formatted.
    sort_file: bool, optional
        If True, sorts the YAML file content by key before saving. Default is False.
    to_json: bool, optional
        If True, converts the YAML content to JSON format and saves it with a .json extension. Default is False.

    Behavior:
    - Reads the content of the specified YAML file.
    - If sort_file is True, sorts the content alphabetically by keys.
    - If to_json is True, writes the content to a JSON file with specified formatting.
    - Otherwise, writes the modified content back to the original YAML file with proper formatting.
    """
    with open(file_path, "r") as fd:
        src = yaml.safe_load(fd)
    content = src.copy()
    if sort_file:
        content = collections.OrderedDict(sorted(src.items()))
    if to_json:
        with open(file_path.replace(".yaml", ".json"), "wb") as fd:
            fd.write(orjson.dumps(content, option=orjson.OPT_INDENT_2 | orjson.OPT_APPEND_NEWLINE))
    else:
        with open(file_path, "w") as fd:
            yaml.safe_dump(dict(content), fd, allow_unicode=True)
