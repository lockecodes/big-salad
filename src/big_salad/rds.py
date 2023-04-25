import csv
import datetime
import json
from collections import Counter
from pathlib import Path
from typing import List, Dict

import boto3
import click

from big_salad.config import context_mutate
from big_salad.rds_models import RdsInstance, InstanceType, RdsPricing, DbInstanceType


def serialize_datetime(obj):
    """
    Serialize a datetime object into ISO 8601 format.

    This function checks if the provided object is an instance of the datetime.datetime class.
    If so, it serializes the object into a valid ISO 8601 string. If the object is not serializable,
    a TypeError is raised.

    Parameters:
    obj: The object to serialize.

    Returns:
    A string representing the datetime in ISO 8601 format if the input is a datetime object.

    Raises:
    TypeError: If the provided object is not serializable.
    """
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    print(obj)
    raise TypeError("Type not serializable")


def write_json(file_path, value):
    """
    Writes a JSON-serializable object to a file.

    Parameters:
    file_path: The file path where the JSON content will be written.
    value: The JSON-serializable Python object to write to the file.

    The function formats the JSON output with an indentation of 2 spaces and supports custom serialization for datetime objects using the serialize_datetime function.
    """
    with open(file_path, "w") as fp:
        json.dump(value, fp, indent=2, default=serialize_datetime)


def describe_db_instances(client=None):
    """
    Retrieve a list of all RDS database instances from the AWS account.

    Parameters:
    client: boto3 RDS client instance. Defaults to creating a new client for the "us-east-1" region if not provided.

    Returns:
    A list of RDS database instances, where each instance is represented as a dictionary containing its details.
    """
    client = client or boto3.client("rds", region_name="us-east-1")
    paginator = client.get_paginator("describe_db_instances")
    dbs = []
    for page in paginator.paginate():
        for db in page["DBInstances"]:
            dbs.append(db)
    return dbs


def describe_instance_ec2_instance_types(client=None):
    """
    Fetches and returns a list of EC2 instance types available in the specified AWS region.

    Parameters:
    client (boto3.client, optional): An optional boto3 EC2 client. If not provided, a default client is instantiated using the "us-east-1" region.

    Returns:
    list: A list of dictionaries where each dictionary represents an EC2 instance type with its attributes.
    """
    client = client or boto3.client("ec2", region_name="us-east-1")
    paginator = client.get_paginator("describe_instance_types")
    dbs = []
    for page in paginator.paginate():
        for db in page["InstanceTypes"]:
            dbs.append(db)
    return dbs


def describe_instance_rds_instance_types(client=None):
    """
    Describes available RDS instance types using pagination.

    This function retrieves a list of all available RDS instance types by using the
    'describe_instances_types' API call with the provided or default RDS client.
    It uses a paginator to handle responses that are split into multiple pages.

    Parameters:
    client (boto3.client, optional): A boto3 RDS client instance. If not provided,
                                      a new client with the default region 'us-east-1' will be created.

    Returns:
    list: A list containing all pages of RDS instance types.
    """
    client = client or boto3.client("rds", region_name="us-east-1")
    paginator = client.get_paginator("describe_instances_types")
    inst_types = []
    for page in paginator.paginate():
        inst_types.append(page)
    return inst_types


def describe_rds_pricing(client=None):
    """
    Retrieves and returns Amazon RDS pricing information by querying the AWS Pricing API.

    Parameters:
    client (boto3.Client, optional): An optional boto3 Pricing client.
                                      If not provided, a new client will be created
                                      with the default region set to "us-east-1".

    Returns:
    list: A list of pricing information for Amazon RDS services in the specified region,
          with each element represented as a dictionary parsed from the JSON price list.
    """
    client = client or boto3.client("pricing", region_name="us-east-1")
    paginator = client.get_paginator("get_products")
    pricing = []
    for page in paginator.paginate(
        ServiceCode="AmazonRDS",
        Filters=[
            {"Type": "TERM_MATCH", "Field": "regionCode", "Value": "us-east-1"},
        ],
    ):
        price_list = page["PriceList"]
        price_list_json = [json.loads(price) for price in price_list]
        pricing.extend(price_list_json)
    return pricing


def dump_rds_instances(dump_path: Path, client=None, limit_production: bool = False):
    """
    Dumps the RDS (Relational Database Service) instances to the specified file path in JSON format.

    Parameters:
    dump_path: Path
        The file path where the RDS instance details will be dumped.

    client: boto3 client, optional
        The boto3 RDS client used to interact with the AWS RDS service. If not provided, a default client configuration will be used.

    limit_production: bool, optional
        A flag to restrict dumping to production environment only. If True, only RDS instances with an environment tag indicating 'prod' or 'production' will be included. Defaults to False.

    Returns:
    list
        A list of RDS instance details that have been dumped to the specified file path.

    Raises:
    IndexError
        If RDS instances are missing the required "environment" tag.

    Notes:
    Tags must include a key 'environment' for filtering when the limit_production flag is enabled. If a tag is missing, a message will be printed to indicate the missing tag for the corresponding DB instance identifier.
    """
    dump_path = context_mutate(dump_path)
    instances = describe_db_instances(client=client)
    dbs = []
    for db in instances:
        tags = db["TagList"]
        try:
            env = [t["Value"].lower() for t in tags if t["Key"].lower() == "environment"][0]
            if not limit_production or (env in ("prod", "production")):
                dbs.append(db)
        except IndexError:
            print("tags missing for %s", db["DBInstanceIdentifier"])
    write_json(dump_path, dbs)
    return dbs


def get_performance_insights(
    rds_instance: RdsInstance,
    client=None,
    period_in_minutes: int = 60,
    end_time: datetime = datetime.datetime.utcnow(),
    time_delta: datetime.timedelta = datetime.timedelta(weeks=2),
    metric_queries: List[Dict[str, str]] = None,
    max_results: int = None,
):
    """
    Retrieves performance insights metrics for the specified RDS instance.

    Parameters:
    rds_instance (RdsInstance): The RDS instance for which to retrieve performance insights metrics.
    client (boto3.client, optional): A boto3 Performance Insights client. If not provided, a default client will be created.
    period_in_minutes (int, optional): The granularity in minutes of the performance data to retrieve. Default is 60.
    end_time (datetime, optional): The end timestamp for the metric query. Default is the current UTC time.
    time_delta (datetime.timedelta, optional): Time range for the query, starting from end_time minus the time_delta. Default is 2 weeks.
    metric_queries (List[Dict[str, str]], optional): List of metric specifications to retrieve. If None, defaults to querying "db.load.avg".
    max_results (int, optional): The maximum number of results to retrieve. If None, this parameter is omitted.

    Returns:
    List[Dict[str, Any]]: A list of metrics retrieved, as dictionaries, from the Performance Insights service.

    Raises:
    botocore.exceptions.ClientError: If there is an issue with the Performance Insights client or the query parameters.
    """
    kwargs = {"MaxResults": max_results} if max_results else {}
    period_in_seconds = period_in_minutes * 60
    metric_queries = metric_queries or [
        {
            "Metric": "db.load.avg",
        },
    ]
    client = client or boto3.client("pi")
    metrics = client.get_resource_metrics(
        ServiceType="RDS",
        Identifier=rds_instance.DbiResourceId,
        StartTime=end_time - time_delta,
        EndTime=end_time,
        PeriodInSeconds=period_in_seconds,
        MetricQueries=metric_queries,
        **kwargs,
    )
    return metrics["MetricList"]


@click.group()
def rds():
    """
    Defines a Click command group named 'rds'.

    This function serves as a placeholder for grouping related subcommands
    under the 'rds' command namespace. It does not contain any logic on its own
    but allows subcommands to be attached to it.
    """
    pass


@rds.command()
@click.option("--file-path", type=str, default=Path("/opt/context/rds.json"), help="file path")
@click.option("--dest-path", type=str, default=Path("/opt/context/rds.json"), help="file path")
@click.option("--filter-size", type=click.Choice(["db.t4g.large"]), default="db.t4g.large")
@click.option("--limit-production", is_flag=True)
def stats(file_path, dest_path, filter_size, limit_production):
    """
    Command-line interface function to display statistics of RDS instances.

    This function reads RDS instance information from a JSON file, processes it, and outputs statistics regarding production RDS instance sizes. It also provides options to filter instances based on specified criteria and retrieves performance insights for the filtered instances.

    Parameters:
    file_path: Path to the input JSON file containing RDS instance data. Default is '/opt/context/rds.json'.
    dest_path: Path to save the RDS instance data if the file is not found or invalid. Default is '/opt/context/rds.json'.
    filter_size: Instance class to filter RDS instances. Default is 'db.t4g.large'.
    limit_production: Boolean flag to restrict processing to production instances only.

    Functionality:
    - Reads RDS instance data from the specified file.
    - If the file is missing or invalid, dumps RDS instance data to `dest_path`.
    - Converts raw instance data into `RdsInstance` objects.
    - Counts and displays sizes of production RDS instances.
    - Filters instances by the specified `filter_size` and excludes read replicas.
    - Retrieves and displays performance insights for the filtered instances.

    Raises:
    FileNotFoundError: If the specified file_path does not exist.
    TypeError: If the file content is invalid or improperly formatted.
    """
    try:
        with open(file_path, "r") as fp:
            dbs = json.load(fp)
    except (FileNotFoundError, TypeError):
        dbs = dump_rds_instances(dump_path=dest_path, limit_production=limit_production)

    db_instances = [RdsInstance(**{k: v for k, v in db.items() if k in RdsInstance.fields()}) for db in dbs]
    instance_sizes = sorted([r.DBInstanceClass for r in db_instances if not r.ReadReplicaSourceDBInstanceIdentifier])
    size_counts = Counter(instance_sizes)
    print(
        f"""
Production RDS Instance sizes:
{json.dumps(size_counts, indent=2)}
"""
    )
    filtered = [
        inst
        for inst in db_instances
        if inst.DBInstanceClass == filter_size and not inst.ReadReplicaSourceDBInstanceIdentifier
    ]
    print("filtered dbs")
    print([l.DBInstanceIdentifier for l in filtered])
    for db in filtered:
        metrics = get_performance_insights(db)
        print(metrics)


@rds.command()
@click.option("--rds-path", type=str, default=Path("/opt/context/rds.json"), help="file path")
@click.option("--dest-path", type=str, default=Path("/opt/context/rds-summary.json"), help="file path")
@click.option("--from-cache", is_flag=True)
@click.option("--as-md", is_flag=True)
@click.option("--as-csv", is_flag=True)
def instance_summary(rds_path, dest_path, from_cache, as_md, as_csv):
    """
    This function generates a summary of RDS instances and outputs the data in JSON format, and optionally in Markdown or CSV formats.

    Decorators:
        @rds.command(): Marks this function as a command within the Click CLI framework.

    Parameters:
        --rds-path (str): The file path to the RDS JSON data. Defaults to "/opt/context/rds.json".
        --dest-path (str): The file path to save the summary data in JSON format. Defaults to "/opt/context/rds-summary.json".
        --from-cache (bool): A flag to indicate whether to use cached data. Defaults to False.
        --as-md (bool): A flag to include an output in Markdown format. Defaults to False.
        --as-csv (bool): A flag to include an output in CSV format. Defaults to False.

    Functionality:
        - Reads RDS instance data from a file or fetches fresh data if `from_cache` is not specified.
        - Processes the RDS instance data into a structured summary. Includes details such as region, instance name, instance type, CPU, RAM, and storage details.
        - Calculates the total instance count and total CPU count.
        - Optionally, generates a Markdown-formatted table or a CSV file from the summary data.
        - Outputs the summary data as a JSON file at the specified destination path.
        - If Markdown output is requested, the summary is also saved to a file named "rds-summary.md" in the same directory as the destination path.
        - If CSV output is requested, the summary is also saved to a file named "rds-summary.csv" in the same directory as the destination path.

    Notes:
        - This function expects the RDS instance data to conform to a specific schema which is validated using the `RdsInstance` class.
        - The `_instance_type_options_from_cache` function is used to fetch instance type configurations.
        - The `write_json` function is used for saving JSON data.
        - Handles scenarios where the input file is not found or data cannot be read properly.
    """
    MD = """|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|**Region**|**Instance Name**|**Instance Count**|**Database Type**|**Single AZ**|**Multi AZs**|**RTO/RPO**|**INSTANCE-TYPE**|**CPU**|**RAM**|**Disk Type**|**Storage Size**|**IOPs**|**Throughput (Mb/s)**|**Monthly**|**Annually**|"""
    if from_cache:
        try:
            with open(rds_path, "r") as fp:
                dbs = json.load(fp)
        except (FileNotFoundError, TypeError):
            dbs = dump_rds_instances(dump_path=rds_path)
    else:
        dbs = dump_rds_instances(dump_path=rds_path)
    db_instances = [RdsInstance(**{k: v for k, v in db.items() if k in RdsInstance.fields()}) for db in dbs]
    inst_types = _instance_type_options_from_cache()
    results = []
    md_results = MD
    instance_count = len(db_instances)
    cpu_counts = 0
    for inst in db_instances:
        result = {
            "Region": inst.AvailabilityZone[:-1],
            "Instance Name": inst.DBInstanceIdentifier,
            "Instance Count": 1,
            # not grouping anything yet
            "Database Type": inst.Engine,
            "Single AZ": not inst.MultiAZ,
            "Multi AZ": inst.MultiAZ,
            "RTO/RPO": "TBD",
            "Instance Type": inst.DBInstanceClass,
            "CPU": inst_types[inst.DBInstanceClass].DefaultVCpus,
            "RAM": inst_types[inst.DBInstanceClass].MemorySizeInMiB,
            "Disk Type": inst.StorageType,
            "Storage Size": inst.AllocatedStorage,
            "IOPs": inst.Iops,
            "Throughput (Mb/s)": "TBD",
            "Monthly": None,
            "Annually": None,
        }
        cpu_counts += inst_types[inst.DBInstanceClass].DefaultVCpus
        results.append(result)
        if as_md:
            md_results += "\n|"
            md_results += "|".join([str(v) for v in result.values()]) + "|"
    md_results += f"\n| | |{str(instance_count)}| | | | | |{str(cpu_counts)}| | | | | | | |\n"
    write_json(dest_path, results)
    if as_md:
        md_path = Path(Path(dest_path).parent, "rds-summary.md")
        with open(md_path, "w") as fd:
            fd.write(md_results)
    if as_csv:
        csv_path = Path(Path(dest_path).parent, "rds-summary.csv")
        with open(csv_path, "w") as f:
            w = csv.DictWriter(f, results[0].keys())
            w.writeheader()
            w.writerows(results)


@rds.command()
@click.option("--dest-path", type=str, default=Path("/opt/context/rds-instance-type-options.json"), help="file path")
def instance_type_options(dest_path):
    """
    This function is registered as an RDS CLI command. It retrieves EC2 instance type options using the boto3 EC2 client and writes the output to a specified file. The file path can be customized through the --dest-path option.

    Parameters:
      dest_path: A string representing the file path where the instance type options will be saved. Defaults to "/opt/context/rds-instance-type-options.json".

    This command internally calls the _instance_type_options function to perform the main logic of fetching and saving the instance type options.
    """
    client = boto3.client("ec2")
    _instance_type_options(client=client, dest_path=dest_path)


def _instance_type_options(client, dest_path):
    """
    Retrieves EC2 instance type details, processes the data, and writes it to a specified JSON file.

    Parameters:
    client (boto3.Client): The boto3 client used to describe EC2 instance types.
    dest_path (str): The file path where the processed EC2 instance type data will be saved as a JSON file.

    Returns:
    list: A list of processed EC2 instance types.
    """
    its = describe_instance_ec2_instance_types(client=client)
    ec2_instances = InstanceType.from_values_collection_as_db(its)
    write_json(dest_path, ec2_instances)
    return ec2_instances


def _instance_type_options_from_cache(inst_types_file_path=None):
    """
    Loads RDS instance type options from a cache file or fetches them from AWS EC2 service if the cache is unavailable.

    Parameters:
    inst_types_file_path (str or Path, optional): Path to the file containing cached RDS instance type options.
                                                  Defaults to "/opt/context/rds-instance-type-options.json".

    Returns:
    dict: A dictionary where each key is an instance type and the value is a DbInstanceType object.

    Raises:
    FileNotFoundError: If the specified file path does not exist and no cached data is available.
    TypeError: If an invalid type is provided for the file path.
    """
    inst_type_file_path = inst_types_file_path or Path("/opt/context/rds-instance-type-options.json")
    try:
        with open(inst_types_file_path, "r") as fp:
            inst_types_dict = json.load(fp)
    except (FileNotFoundError, TypeError):
        ec2_client = boto3.client("ec2")
        inst_types_dict = _instance_type_options(client=ec2_client, dest_path=inst_type_file_path)
    return {key: DbInstanceType.from_values(values) for key, values in inst_types_dict.items()}


def _instance_types(client, file_path, inst_types_file_path, dest_path):
    """
    This function processes and summarizes Amazon RDS instance information and instance type configurations.

    Parameters:
     - client: The AWS client object used to interface with AWS services.
     - file_path: Path to a JSON file containing RDS instances data.
                  If the file is not found or invalid, it will fetch the RDS data and save it to the specified or default path.
     - inst_types_file_path: Path to a JSON file containing EC2 instance type configurations.
                             If the file is not found or invalid, it will fetch the instance type data from AWS.
     - dest_path: The destination path where the processed summary data will be written.

    Functionality:
     - Loads RDS instances data from a file or fetches it if the file is invalid or missing.
     - Filters and processes the RDS instances into a structured format.
     - Counts the occurrences of each RDS instance type.
     - Loads EC2 instance type configurations from a file or fetches them if the file is invalid or missing.
     - Matches RDS instance counts with corresponding EC2 instance type configurations, adding vCPU and memory details.
     - Generates a summary of RDS instances by database engine type.
     - Computes the total count of databases and vCPUs across all instances.
     - Assembles the results into a structured summary including counts and breakdowns by instance type.
     - Writes the resulting summary data to the specified destination path in JSON format.
    """
    try:
        with open(file_path, "r") as fp:
            dbs = json.load(fp)
    except (FileNotFoundError, TypeError):
        file_path = file_path or Path("/opt/context/rds.json")
        dbs = dump_rds_instances(dump_path=file_path, limit_production=False, client=client)

    db_instances = [RdsInstance(**{k: v for k, v in db.items() if k in RdsInstance.fields()}) for db in dbs]
    instance_size_counts = RdsInstance.get_instance_type_counts(db_instances)

    try:
        with open(inst_types_file_path, "r") as fp:
            inst_types = json.load(fp)
    except (FileNotFoundError, TypeError):
        inst_type_file_path = inst_types_file_path or Path("/opt/context/rds-instance-type-options.json")
        ec2_client = boto3.client("ec2")
        inst_types = _instance_type_options(client=ec2_client, dest_path=inst_type_file_path)

    instance_types_result = {
        inst_type_name: {
            "count": instance_size_count,
            "vcpus": inst_types[inst_type_name]["DefaultVCpus"],
            "MemorySizeInMiB": inst_types[inst_type_name]["MemorySizeInMiB"],
        }
        for inst_type_name, instance_size_count in instance_size_counts.items()
    }

    summary_by_engine = RdsInstance.get_instance_types_by_engine(db_instances)

    summary = {
        "database_count": len(db_instances),
        "vcpu_count": sum(
            [
                int(inst_types[inst_type_name]["DefaultVCpus"])
                for inst_type_name, instance_size_count in instance_size_counts.items()
            ]
        ),
        "instance_types": instance_types_result,
        "summary_by_engine": summary_by_engine,
    }

    write_json(dest_path, summary)


@rds.command()
@click.option("--file-path", type=str, default=None, help="file path")
@click.option("--inst-types-file-path", type=str, default=None, help="file path")
@click.option("--dest-path", type=str, default=Path("/opt/context/rds-instance-types.json"), help="file path")
def instance_types(file_path, inst_types_file_path, dest_path):
    """
    Handles the CLI command to process and retrieve RDS instance types and store the results in a specified file.

    Parameters:
    file_path: str
        Path to the input file containing relevant data. Optional.

    inst_types_file_path: str
        Path to the instance types file which contains additional information required for processing. Optional.

    dest_path: str
        Path where the processed instance types data will be stored. Defaults to '/opt/context/rds-instance-types.json'.

    Functionality:
    This function initializes an RDS client using boto3 and invokes the internal _instance_types function to process and save RDS instance type data based on the provided file paths.
    """
    client = boto3.client("rds")
    _instance_types(client=client, file_path=file_path, inst_types_file_path=inst_types_file_path, dest_path=dest_path)


@rds.command()
@click.option("--dest-path", type=str, default=Path("/opt/context/rds-pricing.json"), help="file path")
@click.option("--from-cache", is_flag=True)
def rds_pricing(dest_path, from_cache):
    """
    Command-line interface (CLI) command for retrieving and processing RDS pricing information.

    Uses the boto3 SDK to interact with AWS Pricing services and generates a JSON file containing
    formatted pricing data. Optionally retrieves data from a previously cached JSON file to
    avoid repeated API calls.

    Parameters:
    dest_path: File path where the resulting RDS pricing JSON file will be saved. Defaults to '/opt/context/rds-pricing.json'.
    from_cache: Boolean flag indicating whether to load data from a cached file instead of fetching from the AWS Pricing service.

    Behavior:
    - If 'from_cache' is True, attempts to load JSON data from the specified file path. If not found or invalid, it falls back to fetching data from AWS.
    - Fetches pricing data from the AWS Pricing service if 'from_cache' is False or if loading from the file fails.
    - Processes the pricing data and writes it to a temporary JSON file at the specified file path using the format provided by the RdsPricing class.

    Dependencies:
    - boto3
    - Path from pathlib
    - json
    - describe_rds_pricing (must be implemented elsewhere in the codebase)
    - RdsPricing class (must be implemented elsewhere to define the pricing model)
    - write_json function (must be implemented elsewhere to write data to a JSON file)
    """
    client = boto3.client("pricing", region_name="us-east-1")
    if from_cache:
        try:
            with open(dest_path, "r") as fp:
                values = json.load(fp)
        except (FileNotFoundError, TypeError):
            values = describe_rds_pricing(client=client)
    else:
        values = describe_rds_pricing(client=client)

    dest_path = Path(dest_path)
    pricing_inst = RdsPricing.from_values_collection(values)
    tmp_path = Path(dest_path.parent.absolute(), f'{dest_path.name.replace(".json", "")}-tmp.json')
    write_json(tmp_path, {k: v.as_dict() for k, v in pricing_inst.items()})


@rds.command()
@click.option("--dest-path", type=str, default=Path("/opt/context/rds-performance.json"), help="file path")
@click.option("--file-path", type=str, default=Path("/opt/context/rds.json"), help="file path")
def insights(dest_path, file_path):
    """
    Generates RDS performance insights and writes the results to a JSON file.

    Parameters:
    - dest_path: Specifies the destination file path to save the RDS performance metrics as a JSON file.
    - file_path: Specifies the file path to the input JSON file containing RDS instance information.

    The function retrieves the RDS instances from the input file if present; otherwise, it fetches the instances using the AWS RDS client and stores this information in the destination file. It then collects performance insights data for the RDS instances over the past 13 weeks with a granularity of 60-minute intervals, focusing on metrics such as average and maximum database load. The gathered metrics are then written to the specified destination file.

    Dependencies:
    - Requires boto3 to interact with AWS RDS and Performance Insights services.
    - Depends on external functionalities such as dump_rds_instances, RdsInstance, get_performance_insights, and write_json.
    """
    rds_client = boto3.client("rds", region_name="us-east-1")
    pi_client = boto3.client("pi", region_name="us-east-1")
    try:
        with open(file_path, "r") as fp:
            dbs = json.load(fp)
    except (FileNotFoundError, TypeError):
        dbs = dump_rds_instances(client=rds_client, dump_path=dest_path, limit_production=False)

    db_instances = [RdsInstance(**{k: v for k, v in db.items() if k in RdsInstance.fields()}) for db in dbs]
    end_time = datetime.datetime.utcnow()
    time_delta = datetime.timedelta(weeks=13)
    period_in_minutes = 60
    metric_queries = [
        {
            "Metric": "db.load.avg",
        },
        {
            "Metric": "db.load.max",
        },
    ]
    metrics = {
        db.DBInstanceIdentifier: get_performance_insights(
            client=pi_client,
            rds_instance=db_instances[0],
            period_in_minutes=period_in_minutes,
            end_time=end_time,
            time_delta=time_delta,
            metric_queries=metric_queries,
        )
        for db in db_instances
    }
    write_json(dest_path, metrics)
