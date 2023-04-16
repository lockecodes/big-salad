from dataclasses import dataclass, fields
from typing import Dict, List, Optional, Union


###
### TODO: If you were using attrs this would already be better
###

@dataclass(order=True, frozen=True)
class BaseDictKey:
    def __init_subclass__(cls, *args, **kwargs):
        for field, value in cls.__annotations__.items():
            cls.__annotations__[field] = Union[value, None]
            if not hasattr(cls, field):
                setattr(cls, field, None)
        super().__init_subclass__(*args, **kwargs)


@dataclass(order=True, frozen=True)
class RdsInstance(BaseDictKey):
    DBInstanceIdentifier: Optional[str]
    ReadReplicaSourceDBInstanceIdentifier: Optional[str]
    DBInstanceClass: Optional[str]
    Engine: Optional[str]
    DBInstanceStatus: Optional[str]
    MasterUsername: Optional[str]
    Endpoint: Optional[dict]
    AllocatedStorage: Optional[int]
    InstanceCreateTime: Optional[str]
    PreferredBackupWindow: Optional[str]
    BackupRetentionPeriod: Optional[int]
    DBSecurityGroups: Optional[list]
    VpcSecurityGroups: Optional[list]
    DBParameterGroups: Optional[list]
    AvailabilityZone: Optional[str]
    DBSubnetGroup: Optional[dict]
    PreferredMaintenanceWindow: Optional[str]
    PendingModifiedValues: Optional[dict]
    # LateOptionalStrestorableTime: Optional[str]
    MultiAZ: Optional[bool]
    EngineVersion: Optional[float]
    AutoMinorVersionUpgrade: Optional[bool]
    ReadReplicaDBInstanceIdentifiers: Optional[list]
    LicenseModel: Optional[str]
    # Iops: Optional[int]
    OptionGroupMemberships: Optional[list]
    # SecondaryAvailabilityZone: Optional[str]
    PubliclyAccessible: Optional[bool]
    StorageType: Optional[str]
    DbInstancePort: Optional[int]
    StorageEncrypted: Optional[bool]
    KmsKeyId: Optional[str]
    DbiResourceId: Optional[str]
    CACertificateIdentifier: Optional[str]
    DomainMemberships: Optional[list]
    CopyTagsToSnapshot: Optional[bool]
    # MonitoringOptionalInerval: Optional[int]
    EnhancedMonitoringResourceArn: Optional[str]
    MonitoringRoleArn: Optional[str]
    DBInstanceArn: Optional[str]
    IAMDatabaseAuthenticationEnabled: Optional[bool]
    PerformanceInsightsEnabled: Optional[bool]
    PerformanceInsightsKMSKeyId: Optional[str]
    PerformanceInsightsRetentionPeriod: Optional[int]
    EnabledCloudwatchLogsExports: Optional[list]
    DeletionProtection: Optional[bool]
    AssociatedRoles: Optional[list]
    MaxAllocatedStorage: Optional[int]
    TagList: List[Dict[Optional[str], Optional[str]]]
    CustomerOwnedIpEnabled: Optional[bool]
    # ActivityOptionalStreamStatus: Optional[str]
    BackupTarget: Optional[str]
    NetworkType: Optional[str]
    CertificateDetails: Optional[dict]

    @classmethod
    def fields(cls) -> List[str]:
        return [field.name for field in fields(cls)]
