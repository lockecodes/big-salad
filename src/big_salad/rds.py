import datetime
import json
from collections import Counter

import boto3
import click

from big_salad.rds_models import RdsInstance


def serialize_datetime(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")


def dump(client=None):
    client = client or boto3.client("rds")
    paginator = client.get_paginator("describe_db_instances")
    dbs = []
    for page in paginator.paginate():
        for db in page["DBInstances"]:
            tags = db["TagList"]
            try:
                env = [t["Value"].lower() for t in tags if t["Key"].lower() == "environment"][0]
                if env in ("prod", "production"):
                    dbs.append(db)
            except IndexError:
                print("tags missing for %s", db["DBInstanceIdentifier"])
    with open("files/rds.json", "w") as fp:
        json.dump(dbs, fp, indent=2, default=serialize_datetime)
    return dbs


def get_performance_insights(rds: RdsInstance, client=None):
    client = client or boto3.client("pi")
    metrics = client.get_resource_metrics(
        ServiceType="RDS",
        Identifier=rds.DbiResourceId,
        MaxResults=10,
        StartTime=datetime.datetime.utcnow() - datetime.timedelta(weeks=2),
        EndTime=datetime.datetime.utcnow(),
        PeriodInSeconds=60,
        MetricQueries=[
            {
                "Metric": "db.load.avg",
            },
        ],
    )
    print(metrics)


@click.group()
def rds():
    pass


@rds.command()
@click.option("--from-file", type=str, default=None, help="file path")
@click.option("--filter-size", type=click.Choice(["db.t4g.large"]), default="db.t4g.large")
def stats(from_file, filter_size):
    if from_file:
        with open(from_file, "r") as fp:
            dbs = json.load(fp)
    else:
        dbs = dump()

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
        get_performance_insights(db)
