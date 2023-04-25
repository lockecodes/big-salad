"""
Shared utils for this tool
"""

import datetime
from dateutil.tz import tzutc
import json
import traceback
from big_salad.aws_metrics_collector import LogWrapper
from big_salad.aws_metrics_collector import get_utc_timestamp


def convert_unknown_obj(unknown_obj):
    """
    Converts an unknown object to a specific format.

    If the input object is of type datetime.date or datetime.datetime, the function converts it to a timestamp.
    For any other type of input, it converts it to its string representation.

    Parameters:
    unknown_obj: The object to be converted. It could be of any type.

    Returns:
    A float if the input is a datetime object (timestamp), otherwise a string representation of the input object.
    """
    if isinstance(unknown_obj, (datetime.date, datetime.datetime)):
        return unknown_obj.timestamp()
    else:
        return "{}".format(unknown_obj)


def dict_to_json(dict_obj: dict, log_wrapper: LogWrapper = LogWrapper()) -> str:
    """
    Converts a dictionary object to a JSON-formatted string.

    Args:
        dict_obj (dict): The dictionary object to be converted into a JSON string.
        log_wrapper (LogWrapper, optional): An instance of LogWrapper for logging. Defaults to a new instance of LogWrapper.

    Returns:
        str: A JSON-formatted string representation of the dictionary object. If an exception occurs or if the input
             is of an incorrect type, an empty string is returned.

    Behavior:
        - If the input is a dictionary, it will be converted to a JSON-formatted string with sorted keys and
          an indentation of 4 spaces.
        - If the input is not a dictionary, an error message will be logged.
        - Any exceptions during execution will be logged, and the function will return an empty string.
    """
    final_str = ""
    try:
        if isinstance(dict_obj, dict):
            final_str = json.dumps(dict_obj, default=convert_unknown_obj, indent=4, sort_keys=True)
        else:
            log_wrapper.error(message="dict_obj incorrect type: {}".format(type(dict_obj)))
    except:
        log_wrapper.error(message="EXCEPTION: {}".format(traceback.format_exc()))
    return final_str
