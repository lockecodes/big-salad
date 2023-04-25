"""
This module provides functionalities for interacting with AWS services, including EC2 and RDS,
to retrieve instance details, CloudWatch metrics, and related statistics. Through a
hierarchical structure of classes and utility functions, the module supports efficient
processing of AWS resources, logging, metric exploration, and data collections.

Classes:
--------
1. AwsInstance:
    Base class representing a generic AWS instance. Defines attributes and methods commonly
    used for managing instance data across multiple AWS services.

2. AwsEC2Instance:
    Represents an AWS EC2 instance. Extends `AwsInstance` to include processing of EC2-specific
    attributes and metrics.

3. AwsRDSInstance:
    Represents an AWS RDS instance. Extends `AwsInstance` to handle the specific attributes and
    metrics of RDS instances.

4. AWSInstanceCollection:
    Manages a collection of instances (EC2, RDS, or other services). Offers methods for processing
    and converting instance collections into dictionary representations.

Functions:
----------
1. get_service_client_default:
    Creates and returns a boto3 client for a specified AWS service and region. Optionally allows the use
    of a specific AWS profile when initiating the session.

2. get_instance_cloudwatch_metrics:
    Retrieves a list of CloudWatch metrics for a specific AWS service instance (e.g., EC2 or RDS).

3. get_regions_by_service:
    Retrieves all available regions for a specified AWS service.

4. _get_start_timestamp:
    Internal utility that calculates and returns the timestamp for the start of the previous day.

5. _get_end_timestamp:
    Internal utility that calculates and returns the timestamp for the end of the previous day.

6. get_instance_metric_statistics:
    Fetches metric statistics for an AWS instance and a specific metric, using AWS CloudWatch APIs.

7. get_ec2_instances:
    Fetches all EC2 instance details for a specific region using the AWS API. Includes logic to collect
    metrics and statistics.

8. get_rds_instance_tags:
    Retrieves all tags associated with an RDS instance.

9. get_rds_instances:
    Fetches all RDS instance details for a specific region, including tags, metrics, and statistics.

10. collect_aws_instance_data:
    Collects data from specified AWS services (EC2, RDS) across one or multiple regions. Returns
    an `AWSInstanceCollection` object encapsulating all the collected instance data.

Constants:
----------
1. INSTANCE_CLASSES:
    Tuple of supported AWS service classes (EC2, RDS, CloudWatch).

2. MAX_RESULTS_DEFAULT:
    Sets a default value for the maximum number of results per API call.

3. AWS_CLOUDWATCH_NAMESPACE_MAPPING:
    Dictionary that maps AWS service names to the corresponding CloudWatch namespace strings.

4. AWS_CLOUDWATCH_DIMENSION_NAME_MAPPING:
    Dictionary mapping AWS service names to their CloudWatch dimension identifier.

Dependencies:
-------------
1. boto3:
    AWS SDK for Python to interact with AWS services.

2. datetime:
    For managing timestamps required in metric queries and internal calculations.

3. traceback:
    For logging detailed exception traces.

4. big_salad.aws_metrics_collector:
    Internal library used for logging (`LogWrapper`), JSON serialization, and other utilities.

Usage:
------
This module is typically used in scenarios involving AWS data collection and reporting,
such as monitoring AWS instances (EC2 or RDS), reporting their metrics and status, or
building dashboards based on AWS resources data.

Example:
--------
```python
from big_salad.aws_metrics_collector import LogWrapper

# Initialize a log wrapper
log = LogWrapper()

# Collect data for EC2 instances in the "us-east-1" region
collection = collect_aws_instance_data(
    services=["ec2"],
    regions=["us-east-1"],
    log_wrapper=log
)

# Convert the collected data into a dictionary representation
data_dict = collection.to_dict()
print(data_dict)
```

Note:
-----
- Error handling is managed via internal logs triggered by `LogWrapper`.
- AWS service limits, region availability, and appropriate credentials are prerequisites for successful execution.
- Consult AWS documentation for service-specific requirements, especially for CloudWatch metrics and supported resources.

"""

import traceback
from datetime import datetime, timedelta

import boto3

from big_salad.aws_metrics_collector import LogWrapper
from big_salad.aws_metrics_collector import get_utc_timestamp
from big_salad.aws_metrics_collector.utils import dict_to_json

INSTANCE_CLASSES = (
    "ec2",
    "rds",
    "cloudwatch",
)
MAX_RESULTS_DEFAULT = 20
AWS_CLOUDWATCH_NAMESPACE_MAPPING = {
    # Refere to https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/aws-services-cloudwatch-metrics.html or (NEW): https://docs.aws.amazon.com/en_pv/AmazonCloudWatch/latest/monitoring/aws-services-cloudwatch-metrics.html
    "ec2": "AWS/EC2",
    "rds": "AWS/RDS",
}
AWS_CLOUDWATCH_DIMENSION_NAME_MAPPING = {
    "ec2": "InstanceId",
    "rds": "DBInstanceIdentifier",
}


class AwsInstance:
    """
    AwsInstance is a class that represents an AWS instance and provides functionalities for storing, managing, and processing instance-related data.

    __init__(instance_class: str = "ec2", log_wrapper: LogWrapper = LogWrapper())
    Initializes an AwsInstance object with default or provided parameters.
    Parameters:
    - instance_class: A string determining the class of the AWS instance (default "ec2").
    - log_wrapper: An instance of LogWrapper to handle logging.

    store_raw_instance_data(instance_data: dict)
    Stores the raw instance data if it is provided as a dictionary, and updates the timestamp to the current UTC value.
    Parameters:
    - instance_data: A dictionary containing raw instance data.

    to_dict()
    Returns the current state of the instance object represented as a dictionary. Contains instance metadata and associated attributes.

    _post_store_raw_instance_data_processing()
    An internal placeholder method designed for processing after storing raw instance data. Can be extended for implementing specific processing logic.
    """

    def __init__(self, instance_class: str = "ec2", log_wrapper: LogWrapper = LogWrapper()):
        self.instance_class = instance_class
        self.log_wrapper = log_wrapper
        self.last_update = None
        self.raw_instance_data = None
        self.instance_id = "unknown"
        self.instance_type = "unknown"
        self.state = "unknown"
        self.region = "unknown"
        self.tags = dict()
        self.metrics = list()
        self.metric_statistics = dict()

    def store_raw_instance_data(self, instance_data: dict):
        """
        Stores the provided raw instance data into the raw_instance_data attribute if it is a valid dictionary.

        Parameters:
        - instance_data (dict): The dictionary containing raw instance data to be stored.

        Functionality:
        - Checks if instance_data is not None.
        - Verifies if the provided instance_data is of type dict.
        - Updates the raw_instance_data attribute with the provided data.
        - Updates the last_update attribute with the current UTC timestamp without decimal precision.
        - Calls the _post_store_raw_instance_data_processing method for any additional operations.
        """
        if instance_data is not None:
            if isinstance(instance_data, dict):
                self.raw_instance_data = instance_data
                self.last_update = get_utc_timestamp(with_decimal=False)
        self._post_store_raw_instance_data_processing()

    def to_dict(self):
        """
        Converts the instance properties to a dictionary.

        Returns:
            dict: A dictionary containing the instance properties with the following keys:
                - "InstanceClass": The class of the instance.
                - "LastUpdate": The timestamp of the last update for the instance.
                - "InstanceId": The unique identifier of the instance.
                - "InstanceType": The type of the instance.
                - "InstanceState": The current state of the instance.
                - "InstanceRegion": The region where the instance is located.
                - "Tags": A dictionary of tags associated with the instance.
                - "Metrics": A collection of metrics related to the instance.
                - "MetricStatistics": Statistical data of the metrics for the instance.
        """
        return {
            "InstanceClass": self.instance_class,
            "LastUpdate": self.last_update,
            "InstanceId": self.instance_id,
            "InstanceType": self.instance_type,
            "InstanceState": self.state,
            "InstanceRegion": self.region,
            "Tags": self.tags,
            "Metrics": self.metrics,
            "MetricStatistics": self.metric_statistics,
        }

    def _post_store_raw_instance_data_processing(self):
        pass


class AwsEC2Instance(AwsInstance):
    """
    Represents an AWS EC2 instance with methods to process and store instance data.

    Attributes:
        instance_id (str): The unique identifier of the EC2 instance, extracted from raw data.
        instance_type (str): The type of the EC2 instance, extracted from raw data.
        state (str): The current state of the EC2 instance, such as "running" or "stopped".
        tags (dict): A dictionary of tags associated with the EC2 instance, extracted from raw data.

    Methods:
        __init__: Initializes the AwsEC2Instance object and sets up logging.
        _post_store_raw_instance_data_processing: Processes the raw EC2 instance data to populate instance attributes and logs the results.
    """

    def __init__(self, log_wrapper: LogWrapper = LogWrapper()):
        super().__init__(instance_class="ec2", log_wrapper=log_wrapper)

    def _post_store_raw_instance_data_processing(self):
        """
        Processes raw instance data obtained from an EC2 result and extracts relevant information.

        This method performs the following actions:
        - Logs the start of data processing.
        - Checks if `raw_instance_data` is not None; if None, logs an error message.
        - Extracts the "InstanceId" field from `raw_instance_data` and stores it in `instance_id`.
        - Extracts the "InstanceType" field from `raw_instance_data` and stores it in `instance_type`.
        - Extracts the state name from the "State" field in `raw_instance_data` and stores it in `state`, if available.
        - Iterates over "Tags" in `raw_instance_data` and populates the `tags` dictionary with key-value pairs.

        Logs the completion of processing with the processed instance ID or logs an error if no data is available.
        """
        self.log_wrapper.info(message="Processing a ec2 result")
        if self.raw_instance_data is not None:
            if "InstanceId" in self.raw_instance_data:
                self.instance_id = self.raw_instance_data["InstanceId"]
            if "InstanceType" in self.raw_instance_data:
                self.instance_type = self.raw_instance_data["InstanceType"]
            if "State" in self.raw_instance_data:
                if "Name" in self.raw_instance_data["State"]:
                    self.state = self.raw_instance_data["State"]["Name"]
            if "Tags" in self.raw_instance_data:
                for tag in self.raw_instance_data["Tags"]:
                    if "Key" in tag and "Value" in tag:
                        self.tags[tag["Key"]] = tag["Value"]
            self.log_wrapper.info(message='Processed instance ID "{}"'.format(self.instance_id))
        else:
            self.log_wrapper.error(message="raw_instance_data is None")


class AwsRDSInstance(AwsInstance):
    """
    Represents an AWS RDS instance that extends the functionality of the parent AwsInstance class.

    Methods:
        __init__: Initializes an instance of AwsRDSInstance with AWS-specific configurations for RDS.
        _post_store_raw_instance_data_processing: Processes raw instance data to populate properties specific to RDS instances.
    """

    def __init__(self, log_wrapper: LogWrapper = LogWrapper()):
        super().__init__(instance_class="rds", log_wrapper=log_wrapper)

    def _post_store_raw_instance_data_processing(self):
        """
        Processes raw instance data retrieved from the database and maps relevant fields to instance attributes.

        Logs the start of the processing operation and checks the existence of specific keys in the raw data.
        If the respective keys are found, assigns their values to corresponding instance attributes:
        - Maps the "DBInstanceIdentifier" field to the `instance_id` attribute.
        - Maps the "DBInstanceClass" field to the `instance_type` attribute.
        - Maps the "DBInstanceStatus" field to the `state` attribute.
        Does nothing if `raw_instance_data` is None.
        """
        self.log_wrapper.info(message="Processing a rds result")
        if self.raw_instance_data is not None:
            if "DBInstanceIdentifier" in self.raw_instance_data:
                self.instance_id = self.raw_instance_data["DBInstanceIdentifier"]
            if "DBInstanceClass" in self.raw_instance_data:
                self.instance_type = self.raw_instance_data["DBInstanceClass"]
            if "DBInstanceStatus" in self.raw_instance_data:
                self.state = self.raw_instance_data["DBInstanceStatus"]


class AWSInstanceCollection:
    """
    AWSInstanceCollection is a class designed to manage a collection of AWS instances.

    Attributes:
    - instances: A list that stores AWS instance objects.
    - log_wrapper: An instance of LogWrapper used for logging purposes.

    Methods:
    - __init__(log_wrapper: LogWrapper): Initializes the collection with an empty list of instances and an optional logging wrapper.
    - to_dict() -> dict: Converts the AWSInstanceCollection into a dictionary, where each instance inside the collection is also represented as a dictionary.
    """

    def __init__(self, log_wrapper: LogWrapper = LogWrapper()):
        self.instances = list()
        self.log_wrapper = log_wrapper

    def to_dict(self) -> dict:
        """
        Converts the data of the current object into a dictionary format.

        The method iterates over the instances of the current object, extracts their dictionary representation using their `to_dict` method, and appends the resulting dictionaries to a list. This list is then assigned to the key "InstanceDefinitions" in the resulting dictionary.

        Returns:
            dict: A dictionary representation of the current object, containing a key "InstanceDefinitions" that maps to a list of dictionaries representing the instances.
        """
        result = dict()
        result["InstanceDefitions"] = list()
        for instance in self.instances:
            result["InstanceDefitions"].append(instance.to_dict())
        return result


def get_service_client_default(
    service: str = "ec2",
    region: str = "us-east-1",
    target_profile: str = None,
    log_wrapper: LogWrapper = LogWrapper(),
):
    """
    Creates and returns a boto3 client for a specified AWS service and region. Optionally, allows the use of a specific AWS profile when initiating the session.

    Parameters:
    service: The name of the AWS service for which the client is to be created. Default is "ec2". Must be a valid and supported service.
    region: The AWS region where the client should be connected. Defaults to "us-east-1".
    target_profile: The name of the AWS CLI profile to use for creating the session. If not provided, the default profile is used.
    log_wrapper: A logging wrapper instance for logging debug, info, and error messages. Defaults to an instance of LogWrapper.

    Returns:
    A boto3 client for the specified service and region, or None if the client could not be created.

    Raises:
    Exception: If the provided service is not supported.
    Exception: If the specified region is not available for the given service.

    Logs relevant information and error messages using the given log wrapper.
    """
    client = None
    try:
        if service not in INSTANCE_CLASSES:
            raise Exception('Service "{}" not supported for this application yet'.format(service))
        if region not in get_regions_by_service(service=service, log_wrapper=log_wrapper):
            raise Exception('Service "{}" not available in selected region "{}"'.format(service, region))
        if target_profile is not None:
            session = boto3.Session(profile_name=target_profile)
            client = session.client(service, region_name=region)
        else:
            client = boto3.client(service, region_name=region)
    except:
        log_wrapper.error(message="EXCEPTION: {}".format(traceback.format_exc()))
    if client is not None:
        log_wrapper.info(message='AWS Client connected to region "{}" for service "{}"'.format(region, service))
    else:
        log_wrapper.error(
            message='AWS Client could NOT connected to region "{}" for service "{}"'.format(region, service)
        )
    return client


def get_instance_cloudwatch_metrics(
    aws_client: boto3.client,
    instance_id: str,
    service_name: str = "ec2",
    next_token: str = None,
    log_wrapper: LogWrapper = LogWrapper(),
) -> list:
    """
    Retrieves a list of CloudWatch metrics for a specific AWS service instance.

    Parameters:
    aws_client (boto3.client): The boto3 client used to interact with AWS services.
    instance_id (str): The ID of the instance for which metrics are to be fetched.
    service_name (str): The name of the AWS service (e.g., 'ec2'). Default is 'ec2'.
    next_token (str): A token to retrieve the next set of results, if available. Default is None.
    log_wrapper (LogWrapper): A logging wrapper instance for capturing logs. Default is a new LogWrapper instance.

    Returns:
    list: A list of metric names retrieved for the specified instance.

    Exceptions:
    Logs an error message if the service_name provided is invalid.
    Logs any exception that occurs during the process of fetching metrics.
    """
    instance_metrics = list()
    if service_name not in INSTANCE_CLASSES:
        log_wrapper.error(message="Invalid service name.")
    else:
        try:
            response = dict()
            if next_token is not None:
                response = aws_client.list_metrics(
                    Namespace=AWS_CLOUDWATCH_NAMESPACE_MAPPING[service_name],
                    Dimensions=[
                        {
                            "Name": AWS_CLOUDWATCH_DIMENSION_NAME_MAPPING[service_name],
                            "Value": instance_id,
                        }
                    ],
                    NextToken=next_token,
                )
            else:
                response = aws_client.list_metrics(
                    Namespace=AWS_CLOUDWATCH_NAMESPACE_MAPPING[service_name],
                    Dimensions=[
                        {
                            "Name": AWS_CLOUDWATCH_DIMENSION_NAME_MAPPING[service_name],
                            "Value": instance_id,
                        }
                    ],
                )
            if "Metrics" in response:
                for metric in response["Metrics"]:
                    if "MetricName" in metric:
                        instance_metrics.append(metric["MetricName"])
        except:
            log_wrapper.error(message="EXCEPTION: {}".format(traceback.format_exc()))
    log_wrapper.info(message='Metrics for "{}/{}": {}'.format(service_name, instance_id, instance_metrics))
    return instance_metrics


def get_regions_by_service(service="ec2", log_wrapper=LogWrapper()) -> list:
    """
    Retrieve a list of available regions for a given AWS service.

    Parameters:
    service (str): The name of the AWS service to query for available regions. Defaults to "ec2".
    log_wrapper (LogWrapper): A logging wrapper instance used for error logging. Defaults to a LogWrapper object.

    Returns:
    list: A list of region names where the specified service is available. If an exception occurs, it logs the error and returns a fallback list containing "us-east-1".
    """
    try:
        return list(boto3.session.Session().get_available_regions(service))
    except:
        log_wrapper.error(message="EXCEPTION: {}".format(traceback.format_exc()))
    return ["us-east-1"]


def _get_start_timestamp() -> datetime:
    """
    Returns the start of the previous day as a datetime object.

    This function calculates the timestamp for the start of the previous day by
    subtracting one day from the current datetime and resetting the hours, minutes,
    seconds, and microseconds to zero.

    Returns:
        datetime: A datetime object representing the start of the previous day.
    """
    yesterday = datetime.now() - timedelta(1)
    yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    return yesterday


def _get_end_timestamp() -> datetime:
    """
    Returns the timestamp for the end of the previous day.

    The timestamp corresponds to 11:59:59 PM (end of the day) of the day before the current date and time. The function calculates this value by subtracting one day from the current date and time and adjusting the time to match 23:59:59 with zeroed microseconds.

    Returns:
        datetime: The timestamp for the end of the previous day.
    """
    yesterday = datetime.now() - timedelta(1)
    yesterday = yesterday.replace(hour=23, minute=59, second=59, microsecond=0)
    return yesterday


def get_instance_metric_statistics(
    aws_client: boto3.client,
    instance_id: str,
    service_name: str = "ec2",
    metric_name: str = "CPUUtilization",
    start_timestamp: datetime = _get_start_timestamp(),
    end_timestamp: datetime = _get_end_timestamp(),
    period: int = 300,
    log_wrapper=LogWrapper(),
) -> dict:
    """
    Retrieves metric statistics for a given AWS instance and metric from AWS CloudWatch.

    Parameters:
    aws_client: The AWS client object used for making API calls to AWS services.
    instance_id: The ID of the instance for which to retrieve metric statistics.
    service_name: The name of the AWS service. Defaults to "ec2".
    metric_name: The name of the metric to retrieve data for. Defaults to "CPUUtilization".
    start_timestamp: The start timestamp for the metric statistics. Defaults to a pre-configured function to determine the start time.
    end_timestamp: The end timestamp for the metric statistics. Defaults to a pre-configured function to determine the end time.
    period: The granularity, in seconds, of the data points being retrieved. Defaults to 300 (5 minutes).
    log_wrapper: A logging wrapper object for logging information and errors. Defaults to an instance of LogWrapper.

    Returns:
    A dictionary containing the retrieved metric statistics. If the service name is invalid or an error occurs, an empty dictionary is returned.
    The dictionary includes the metric name as the key and a dictionary of data points as the value.

    Exceptions:
    Logs an error and returns an empty dictionary if an invalid service name is provided.
    Logs an error if an exception occurs while making the API call.
    """
    result = dict()
    result[metric_name] = dict()
    if service_name not in AWS_CLOUDWATCH_NAMESPACE_MAPPING:
        log_wrapper.error(message="Invalid service name.")
        return result
    dimension_name = AWS_CLOUDWATCH_DIMENSION_NAME_MAPPING[service_name]
    name_space = AWS_CLOUDWATCH_NAMESPACE_MAPPING[service_name]
    try:
        log_wrapper.info(
            'Retrieving metrics data for "{}/{}/{}/{}/{}"'.format(
                service_name, name_space, dimension_name, instance_id, metric_name
            )
        )
        response = aws_client.get_metric_statistics(
            Namespace=name_space,
            MetricName=metric_name,
            Dimensions=[
                {"Name": dimension_name, "Value": instance_id},
            ],
            StartTime=start_timestamp,
            EndTime=end_timestamp,
            Period=period,
            Statistics=[
                "Average",
                "Maximum",
            ],
        )
        if "Datapoints" in response:
            result[metric_name] = response["Datapoints"]
    except:
        log_wrapper.error(message="EXCEPTION: {}".format(traceback.format_exc()))
    log_wrapper.info(
        message='Metric Statistics for "{}/{}/{}/{}/{}": {} bytes of JSON data'.format(
            service_name,
            name_space,
            dimension_name,
            instance_id,
            metric_name,
            len(dict_to_json(result)),
        )
    )
    return result


def get_ec2_instances(
    aws_client,
    next_token: str = None,
    max_results_per_iteration: int = MAX_RESULTS_DEFAULT,
    log_wrapper=LogWrapper(),
) -> list:
    """
    Fetches and processes details of EC2 instances from a specified AWS account using the provided AWS client.

    Parameters:
    aws_client: The AWS client instance used to communicate with the AWS API. This must be an instance of boto3 client configured to access EC2.
    next_token: A string representing the pagination token for fetching the next batch of results. Defaults to None, which fetches the first set of results.
    max_results_per_iteration: An integer representing the maximum number of results returned in each API call. Defaults to MAX_RESULTS_DEFAULT.
    log_wrapper: An instance of the application-specific logging wrapper used to log messages and errors during processing. Defaults to an instance of LogWrapper.

    Returns:
    A list of AwsEC2Instance objects containing information about each EC2 instance, including raw instance data, associated metrics, and metric statistics.

    Behavior:
    - Retrieves EC2 instance data by calling the describe_instances API of the provided aws_client.
    - Parses the response for instance data and metrics available for each instance.
    - Stores raw instance data and additional information, such as associated CloudWatch metrics and metric statistics.
    - Handles pagination by recursively fetching more results if a NextToken is provided by the API response.
    - Logs any exceptions encountered during execution without halting further processing.
    - Returns an empty list if aws_client is not provided or in case of an error.
    """
    result = list()
    if aws_client is not None:
        try:
            if next_token is not None:
                response = aws_client.describe_instances(MaxResults=max_results_per_iteration, NextToken=next_token)
            else:
                response = aws_client.describe_instances(MaxResults=max_results_per_iteration)
            ### Main processing ###
            if "Reservations" in response:
                for reservation in response["Reservations"]:
                    if "Instances" in reservation:
                        for instance_data in reservation["Instances"]:
                            ec2instance = AwsEC2Instance(log_wrapper=log_wrapper)
                            ec2instance.store_raw_instance_data(instance_data=instance_data)
                            if ec2instance.raw_instance_data is not None:
                                ec2instance.region = aws_client.meta.region_name
                                ec2instance.metrics = get_instance_cloudwatch_metrics(
                                    aws_client=get_service_client_default(
                                        service="cloudwatch",
                                        region=aws_client.meta.region_name,
                                    ),
                                    instance_id=ec2instance.instance_id,
                                    service_name="ec2",
                                    next_token=None,
                                    log_wrapper=log_wrapper,
                                )
                                if len(ec2instance.metrics) > 0:
                                    for metric in ec2instance.metrics:
                                        metric_statistics = get_instance_metric_statistics(
                                            aws_client=get_service_client_default(
                                                service="cloudwatch",
                                                region=aws_client.meta.region_name,
                                            ),
                                            instance_id=ec2instance.instance_id,
                                            service_name="ec2",
                                            metric_name=metric,
                                            start_timestamp=_get_start_timestamp(),
                                            end_timestamp=_get_end_timestamp(),
                                            period=300,
                                            log_wrapper=log_wrapper,
                                        )
                                        ec2instance.metric_statistics[metric] = metric_statistics[metric]
                                result.append(ec2instance)

            ### end main processing ###
            if "NextToken" in response:
                if isinstance(response["NextToken"], str):
                    if len(response["NextToken"]) > 0:
                        next_result = get_ec2_instances(
                            aws_client=aws_client,
                            next_token=response["NextToken"],
                            max_results_per_iteration=max_results_per_iteration,
                            log_wrapper=log_wrapper,
                        )
                        result = result + next_result
        except:
            log_wrapper.error(message="EXCEPTION: {}".format(traceback.format_exc()))
    else:
        log_wrapper.warning(
            message="No EC2 instances were fetched because the aws_client was not defined - failing gracefully..."
        )
    return result


def get_rds_instance_tags(aws_client, db_instance_arn: str, log_wrapper=LogWrapper()) -> dict:
    """
    Retrieves all tags associated with a specified Amazon RDS instance.

    Parameters:
    aws_client: The AWS client object used to interact with AWS services.
    db_instance_arn: The ARN (Amazon Resource Name) of the RDS instance for which the tags are to be retrieved.
    log_wrapper: An optional logging wrapper for logging messages. Defaults to an instance of LogWrapper.

    Returns:
    A dictionary where the keys are tag keys and the values are tag values associated with the RDS instance.

    Exceptions:
    Logs any exceptions that occur during the process using the log wrapper and continues execution by returning an empty dictionary.
    """
    tags = dict()
    try:
        log_wrapper.info(message='Retrieving tags for RDS instance "{}"'.format(db_instance_arn))
        response = aws_client.list_tags_for_resource(ResourceName=db_instance_arn)
        if "TagList" in response:
            for tag in response["TagList"]:
                if "Key" in tag and "Value" in tag:
                    tags[tag["Key"]] = tag["Value"]

    except:
        log_wrapper.error(message="EXCEPTION: {}".format(traceback.format_exc()))
    return tags


def get_rds_instances(
    aws_client,
    next_token: str = None,
    max_results_per_iteration: int = MAX_RESULTS_DEFAULT,
    log_wrapper=LogWrapper(),
) -> list:
    """
    Retrieves a list of Amazon RDS instances, including their main properties, tags, metrics, and statistics.

    Parameters:
    aws_client: Boto3 client for interactions with the AWS RDS service.
    next_token: Optional token to retrieve the next set of RDS instances if the results are paginated.
    max_results_per_iteration: Number of instances to return per AWS API call.
    log_wrapper: Logger object for capturing and outputting logs and warnings.

    Returns:
    A list of RDS instances, encapsulating their details, tags, metrics, and metric statistics.

    Functionality:
    - Interacts with AWS API using the provided aws_client to retrieve RDS instance data.
    - Retrieves tags for each RDS instance if available.
    - Collects CloudWatch metrics and statistics for each RDS instance.
    - Handles paginated results, recursively invoking itself to collect the next set of instances.
    - Logs warnings and errors when expected parameters or data are missing.
    - Gracefully handles errors or undefined aws_client instances without crashing.
    """
    result = list()
    if aws_client is not None:
        try:
            if next_token is not None:
                response = aws_client.describe_db_instances(MaxRecords=max_results_per_iteration, Marker=next_token)
            else:
                response = aws_client.describe_db_instances(MaxRecords=max_results_per_iteration)
            ### Main processing ###

            if "DBInstances" in response:
                for db_instance_data in response["DBInstances"]:
                    rds_instance = AwsRDSInstance(log_wrapper=log_wrapper)
                    rds_instance.store_raw_instance_data(instance_data=db_instance_data)
                    if "DBInstanceArn" in db_instance_data:
                        rds_instance.tags = get_rds_instance_tags(
                            aws_client=aws_client,
                            db_instance_arn=db_instance_data["DBInstanceArn"],
                            log_wrapper=log_wrapper,
                        )
                    else:
                        log_wrapper.warning(message="The data set did not contain an ARN - tags will NOT be retrieved.")
                    if rds_instance.raw_instance_data is not None:
                        rds_instance.region = aws_client.meta.region_name
                        rds_instance.metrics = get_instance_cloudwatch_metrics(
                            aws_client=get_service_client_default(
                                service="cloudwatch", region=aws_client.meta.region_name
                            ),
                            instance_id=rds_instance.instance_id,
                            service_name="rds",
                            next_token=None,
                            log_wrapper=log_wrapper,
                        )
                        if len(rds_instance.metrics) > 0:
                            for metric in rds_instance.metrics:
                                metric_statistics = get_instance_metric_statistics(
                                    aws_client=get_service_client_default(
                                        service="cloudwatch",
                                        region=aws_client.meta.region_name,
                                    ),
                                    instance_id=rds_instance.instance_id,
                                    service_name="rds",
                                    metric_name=metric,
                                    start_timestamp=_get_start_timestamp(),
                                    end_timestamp=_get_end_timestamp(),
                                    period=300,
                                    log_wrapper=log_wrapper,
                                )
                                rds_instance.metric_statistics[metric] = metric_statistics[metric]
                        result.append(rds_instance)

            ### end main processing ###
            if "Marker" in response:
                if isinstance(response["Marker"], str):
                    if len(response["Marker"]) > 0:
                        next_result = get_rds_instances(
                            aws_client=aws_client,
                            next_token=response["Marker"],
                            max_results_per_iteration=max_results_per_iteration,
                            log_wrapper=log_wrapper,
                        )
                        result = result + next_result
        except:
            log_wrapper.error(message="EXCEPTION: {}".format(traceback.format_exc()))
    else:
        log_wrapper.warning(
            message="No RDS instances were fetched because the aws_client was not defined - failing gracefully..."
        )
    return result


def collect_aws_instance_data(
    services: list = ["rds"],
    all_regions: bool = False,
    regions: list = ["us-east-1"],
    target_profile: str = "acv-admin",
    log_wrapper=LogWrapper(),
) -> AWSInstanceCollection:
    """
    Collects AWS instance data for specified services and regions and returns an AWSInstanceCollection object containing the gathered data.

    Parameters:
    services: List of AWS services to gather instance data from. Default is ["rds"].
    all_regions: Boolean flag indicating whether to collect data from all available regions for the specified services. Default is False.
    regions: List of regions to collect instance data from if all_regions is False. Default is ["us-east-1"].
    target_profile: AWS CLI profile to be used for authentication. Default is "acv-admin".
    log_wrapper: A logging wrapper instance for logging messages.

    Returns:
    An instance of AWSInstanceCollection containing collected AWS instance data.

    Exceptions:
    Logs any exceptions encountered during the data collection process.
    """
    instance_data_collection = AWSInstanceCollection(log_wrapper=log_wrapper)
    try:
        for service in services:
            if all_regions is True:
                regions = get_regions_by_service(service=service, log_wrapper=log_wrapper)
            log_wrapper.info("Checking regions: {}".format(regions))
            for region in regions:
                log_wrapper.info('Now checking region "{}"'.format(region))
                client = get_service_client_default(
                    service=service,
                    region=region,
                    target_profile=target_profile,
                    log_wrapper=log_wrapper,
                )
                instances = list()
                if service == "ec2":
                    instances = get_ec2_instances(aws_client=client, log_wrapper=log_wrapper)
                if service == "rds":
                    instances = get_rds_instances(aws_client=client, log_wrapper=log_wrapper)
                if len(instances) > 0:
                    for instance in instances:
                        instance_data_collection.instances.append(instance)
                log_wrapper.info("Added {} instances".format(len(instances)))
    except:
        log_wrapper.error(message="EXCEPTION: {}".format(traceback.format_exc()))
    return instance_data_collection
