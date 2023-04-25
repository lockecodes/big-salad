from typing import Dict, List, Optional, Any

from attrs import define, fields, field, asdict


@define
class Base:
    """
    Class Base serving as a base class with methods to handle class fields and creation of objects.

    fields:
        Class method that returns a list of field names defined for the class.
        Uses Python's dataclasses.fields to extract the fields.

    from_values:
        Class method that generates an instance of the class using a dictionary of values.
        Filters the dictionary to match the class-defined fields and initializes the class with the matching values.
    """

    @classmethod
    def fields(cls) -> List[str]:
        """
        Retrieves the names of all fields defined in the dataclass.

        Returns:
            List[str]: A list containing the names of fields in the dataclass.
        """
        return [field.name for field in fields(cls)]

    @classmethod
    def from_values(cls, values: Dict[str, Any]):
        """
        Creates an instance of the class using a dictionary of values.

        Parameters:
            values (Dict[str, Any]): A dictionary containing key-value pairs to create the class instance, where keys match the class fields.

        Returns:
            An instance of the class initialized with the specified values extracted from the provided dictionary. Only keys present in the class fields are considered.
        """
        return cls(
            **{k: v for k, v in values.items() if k in cls.fields()},
        )


@define
class RdsInstance(Base):
    """
    RdsInstance is a data class that represents an Amazon RDS (Relational Database Service) instance with a wide range of attributes describing its configuration and state.

    Attributes:
    - DBInstanceIdentifier: A unique identifier for the database instance.
    - DBInstanceClass: The compute and memory capacity instance class.
    - Engine: The database engine used by the instance (e.g., MySQL, PostgreSQL).
    - DBInstanceStatus: Provides the current status of the database instance.
    - MasterUsername: The master username for the database instance.
    - Endpoint: Contains connection details such as address and port.
    - AllocatedStorage: The allocated storage for the instance in gigabytes.
    - InstanceCreateTime: The timestamp when the instance was created.
    - PreferredBackupWindow: The daily time range for automated backups.
    - BackupRetentionPeriod: The number of days that automated backups are retained.
    - DBSecurityGroups: A list of DB security group memberships.
    - VpcSecurityGroups: A list of VPC security group memberships.
    - DBParameterGroups: A list of DB parameter group memberships.
    - AvailabilityZone: The availability zone where the instance resides.
    - DBSubnetGroup: Information about the DB subnet group.
    - PreferredMaintenanceWindow: The time range for system maintenance.
    - PendingModifiedValues: Changes awaiting application to the instance.
    - MultiAZ: Indicates if Multi-AZ deployment is enabled.
    - EngineVersion: The version of the database engine.
    - AutoMinorVersionUpgrade: Specifies whether automatic minor version upgrades are enabled.
    - LicenseModel: Licensing model used for the database instance.
    - OptionGroupMemberships: List of option group memberships for the instance.
    - PubliclyAccessible: Indicates if the instance is publicly accessible.
    - StorageType: The storage type (e.g., standard, gp2, io1).
    - DbInstancePort: The port the database instance is listening on.
    - StorageEncrypted: Specifies if storage encryption is enabled.
    - KmsKeyId: The KMS key identifier used for encryption.
    - DbiResourceId: The unique identifier for the DB resource instance.
    - CACertificateIdentifier: Identifier of the CA certificate for the instance.
    - DomainMemberships: List of Active Directory domain memberships.
    - CopyTagsToSnapshot: Indicates if tags are copied to snapshots of the instance.
    - DBInstanceArn: The Amazon Resource Name (ARN) of the DB instance.
    - IAMDatabaseAuthenticationEnabled: Specifies if IAM database authentication is enabled.
    - PerformanceInsightsEnabled: Indicates if Performance Insights is enabled.
    - DeletionProtection: Specifies if deletion protection is enabled for the instance.
    - AssociatedRoles: List of associated roles for the instance.
    - MaxAllocatedStorage: The maximum allocated storage allowed for the instance.
    - TagList: A list of key-value pairs used for tagging the instance.
    - CustomerOwnedIpEnabled: Details if customer-owned IP is enabled.
    - BackupTarget: Indicates the backup target for backups.
    - NetworkType: Specifies the type of network associated with the instance.
    - CertificateDetails: Details of the certificate used by the instance.
    - LateOptionalStrestorableTime: Indicates the last restore time for the instance.
    - Iops: Number of provisioned IOPS for the instance.
    - ReadReplicaSourceDBInstanceIdentifier: Identifier of the source DB instance for a read replica.
    - ReadReplicaDBInstanceIdentifiers: Identifiers of read replicas associated with the instance.
    - SecondaryAvailabilityZone: Secondary availability zone for Multi-AZ instances.
    - MonitoringOptionalInterval: Interval between enhanced monitoring metrics collection.
    - ActivityOptionalStreamStatus: Status for the Activity Stream.
    - EnhancedMonitoringResourceArn: ARN for enhanced monitoring resource.
    - MonitoringRoleArn: ARN of the IAM role for monitoring.
    - PerformanceInsightsKMSKeyId: Identifier of the KMS key for Performance Insights.
    - PerformanceInsightsRetentionPeriod: Retention period for Performance Insights.
    - EnabledCloudwatchLogsExports: Log types exported to CloudWatch Logs.

    Class Methods:
    - from_values_collection: Creates a dictionary of RdsInstance objects from a collection of dictionaries containing instance attributes. The key of the dictionary is the DBInstanceIdentifier.

    Static Methods:
    - get_instance_type_counts: Returns a dictionary where each key represents an instance class and its value is the count of instances of that class in the provided list of RdsInstance objects.
    - get_instance_types_by_engine: Groups RdsInstance objects by their database engine. For each engine, a dictionary of instance classes and their counts is provided.
    """

    DBInstanceIdentifier: Optional[str]
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
    MultiAZ: Optional[bool]
    EngineVersion: Optional[float]
    AutoMinorVersionUpgrade: Optional[bool]
    LicenseModel: Optional[str]
    OptionGroupMemberships: Optional[list]
    PubliclyAccessible: Optional[bool]
    StorageType: Optional[str]
    DbInstancePort: Optional[int]
    StorageEncrypted: Optional[bool]
    KmsKeyId: Optional[str]
    DbiResourceId: Optional[str]
    CACertificateIdentifier: Optional[str]
    DomainMemberships: Optional[list]
    CopyTagsToSnapshot: Optional[bool]
    DBInstanceArn: Optional[str]
    IAMDatabaseAuthenticationEnabled: Optional[bool] = field(default=None)
    PerformanceInsightsEnabled: Optional[bool] = field(default=None)
    DeletionProtection: Optional[bool] = field(default=None)
    AssociatedRoles: Optional[list] = field(default=None)
    MaxAllocatedStorage: Optional[int] = field(default=None)
    TagList: List[Dict[Optional[str], Optional[str]]] = field(default=None)
    CustomerOwnedIpEnabled: Optional[bool] = field(default=None)
    BackupTarget: Optional[str] = field(default=None)
    NetworkType: Optional[str] = field(default=None)
    CertificateDetails: Optional[dict] = field(default=None)
    LateOptionalStrestorableTime: Optional[str] = field(default=None)
    Iops: Optional[int] = field(default=None)
    ReadReplicaSourceDBInstanceIdentifier: Optional[str] = field(default=None)
    ReadReplicaDBInstanceIdentifiers: Optional[list] = field(default=None)
    SecondaryAvailabilityZone: Optional[str] = field(default=None)
    MonitoringOptionalInterval: Optional[int] = field(default=None)
    ActivityOptionalStreamStatus: Optional[str] = field(default=None)
    EnhancedMonitoringResourceArn: Optional[str] = field(default=None)
    MonitoringRoleArn: Optional[str] = field(default=None)
    PerformanceInsightsKMSKeyId: Optional[str] = field(default=None)
    PerformanceInsightsRetentionPeriod: Optional[int] = field(default=None)
    EnabledCloudwatchLogsExports: Optional[list] = field(default=None)

    @classmethod
    def from_values_collection(cls, values: List[Dict[str, Any]]) -> Dict[str, "RdsInstance"]:
        """
        Constructs a dictionary of RdsInstance objects indexed by their DBInstanceIdentifier.

        This class method takes a collection of values, where each value is a dictionary
        representing the attributes of an RdsInstance. It creates an RdsInstance object
        from each dictionary and stores it in a dictionary, with the DBInstanceIdentifier
        attribute as the key.

        Parameters:
            values (List[Dict[str, Any]]): A list of dictionaries containing the attributes of RdsInstance objects.

        Returns:
            Dict[str, RdsInstance]: A dictionary where keys are DBInstanceIdentifier strings
            and values are the corresponding RdsInstance objects.
        """
        result = {}
        for value in values:
            inst: RdsInstance = cls.from_values(value)
            result[inst.DBInstanceIdentifier] = inst
        return result

    @staticmethod
    def get_instance_type_counts(db_instances: List["RdsInstance"]) -> Dict[str, Any]:
        """
        Returns a dictionary containing counts of each unique type of database instance in the provided list.

        The method takes a list of RdsInstance objects, extracts their instance types, and calculates the count for each unique type. It first sorts the instance types for consistent ordering and then generates a dictionary where the keys are the unique instance types and the values are their respective count.

        Args:
            db_instances (List[RdsInstance]): A list of RdsInstance objects whose instance types are to be counted.

        Returns:
            Dict[str, Any]: A dictionary where the keys are instance types (str) and the values are counts (int).
        """
        instance_sizes = sorted([r.DBInstanceClass for r in db_instances])
        instance_size_counts = {key: 0 for key in sorted(set(instance_sizes))}
        for inst in instance_sizes:
            instance_size_counts[inst] = instance_size_counts[inst] + 1
        return instance_size_counts

    @staticmethod
    def get_instance_types_by_engine(db_instances: List["RdsInstance"]) -> Dict[str, Any]:
        """
        Retrieves a dictionary mapping database engine types to their respective instance type counts.

        Parameters:
        db_instances (List[RdsInstance]): A list of RdsInstance objects to process.

        Returns:
        Dict[str, Any]: A dictionary where the keys are database engine names (str) and the values are
                        dictionaries indicating the instance type counts for each engine.
        """
        engines = sorted(set(r.Engine for r in db_instances))
        results = {
            engine: RdsInstance.get_instance_type_counts([r for r in db_instances if r.Engine == engine])
            for engine in engines
        }
        return results


@define
class VCpuInfo(Base):
    """
    Represents information about virtual CPU (vCPU) configuration in a virtualized environment.

    Attributes:
    DefaultVCpus (int): Default number of vCPUs assigned.
    DefaultCores (int): Default number of cores per vCPU.
    DefaultThreadsPerCore (int): Default number of threads per core.
    ValidCores (List[int], optional): A list of valid core counts. Defaults to None.
    ValidThreadsPerCore (List[int], optional): A list of valid thread-per-core counts. Defaults to None.
    """

    DefaultVCpus: int
    DefaultCores: int
    DefaultThreadsPerCore: int
    ValidCores: List[int] = field(default=None)
    ValidThreadsPerCore: List[int] = field(default=None)


@define
class MemoryInfo(Base):
    """
    Represents the memory information of a system or component.

    Attributes:
    SizeInMiB (int): The size of memory in mebibytes.
    """

    SizeInMiB: int


@define
class DbInstanceType(Base):
    """
    Represents a database instance type with specific configuration options and capabilities.

    Attributes:
    InstanceType: A string representing the type of the instance.
    DefaultVCpus: An integer specifying the default number of vCPUs for this instance type. Default is None.
    DefaultCores: An integer specifying the default number of CPU cores for this instance type. Default is None.
    DefaultThreadsPerCore: An integer specifying the default number of threads per core for this instance type. Default is None.
    ValidCores: A list of integers representing the valid number of CPU cores that can be configured for this instance type. Default is None.
    ValidThreadsPerCore: A list of integers representing the valid number of threads per core that can be configured for this instance type. Default is None.
    MemorySizeInMiB: An integer specifying the memory size in MiB for this instance type. Default is None.
    """

    InstanceType: str
    DefaultVCpus: int = field(default=None)
    DefaultCores: int = field(default=None)
    DefaultThreadsPerCore: int = field(default=None)
    ValidCores: List[int] = field(default=None)
    ValidThreadsPerCore: List[int] = field(default=None)
    MemorySizeInMiB: int = field(default=None)


@define
class RdsPricingProduct(Base):
    """
    Represents an RDS Pricing Product entity.

    This class is used to define the structure of an RDS Pricing Product with its associated product family, SKU, and additional attributes.

    Attributes:
    productFamily: A string representing the product family of the RDS pricing product.
    sku: A string representing the SKU (Stock Keeping Unit) of the RDS pricing product.
    attributes: A dictionary containing additional attributes related to the RDS pricing product. Defaults to None.
    """

    productFamily: str
    sku: str
    attributes: Dict[str, Any] = field(default=None)


@define
class RdsTermPriceDimensions(Base):
    """
    Represents the price dimensions of an RDS term.

    Attributes:
        unit: The unit of measurement associated with the price dimension.
        endRange: The upper limit of the range for the price dimension.
        description: A brief description of the price dimension.
        rateCode: The unique identifier for the rate associated with the price dimension.
        beginRange: The lower limit of the range for the price dimension.
        appliesTo: A list indicating additional applicability details for the price, if any. Defaults to None.
        pricePerUnit: The per-unit price in USD for the price dimension. Defaults to None.

    Methods:
        from_values(cls, values) -> RdsTermPriceDimensions:
            Factory method to construct an RdsTermPriceDimensions instance from a dictionary of values.
            Extracts and converts the "pricePerUnit" value into a float, while retaining other relevant fields.
    """

    unit: str
    endRange: str
    description: str
    rateCode: str
    beginRange: str
    appliesTo: List[Any] = field(default=None)
    pricePerUnit: float = field(default=None)

    @classmethod
    def from_values(cls, values) -> "RdsTermPriceDimensions":
        """
        Creates an instance of the class from a given dictionary of values.

        This method extracts specific keys and values from the input dictionary and
        processes the pricePerUnit key to convert its USD value to a float. It then
        uses the extracted and processed data to initialize an instance of the class.

        Parameters:
            values (dict): A dictionary containing keys and values to initialize the instance.
                           It is expected to contain a nested dictionary for the "pricePerUnit" key
                           with a subkey "USD".

        Returns:
            RdsTermPriceDimensions: An instance of the class, initialized with values extracted
                                    and processed from the input dictionary.
        """
        return cls(
            pricePerUnit=float(values["pricePerUnit"]["USD"]),
            **{k: v for k, v in values.items() if k in cls.fields() and k not in ("pricePerUnit",)},
        )


@define
class RdsTerm(Base):
    """
    Represents an RDS (Relational Database Service) Term entity that includes pricing and term information.

    Attributes:
        sku: A unique identifier for the term's stock-keeping unit.
        effectiveDate: The date when the term becomes effective.
        offerTermCode: Code representing the type of offer term.
        priceDimensions: A list of pricing dimensions associated with the term, represented as RdsTermPriceDimensions objects.
        termAttributes: A dictionary containing additional attributes related to the term.

    Methods:
        fields():
            Retrieves a list of field names defined in the class.

        from_values_keyed(values):
            Creates a list of RdsTerm instances from a dictionary where the key represents a specific term type
            and the value contains relevant term details. Mainly processes "OnDemand" term types and their pricing dimensions.
    """

    sku: str
    effectiveDate: str
    offerTermCode: str
    priceDimensions: List[RdsTermPriceDimensions] = field(default=None)
    termAttributes: Dict[str, Any] = field(default=None)

    @classmethod
    def fields(cls) -> List[str]:
        """
        Returns a list of field names defined in the dataclass.

        This method uses the `fields` function from the `dataclasses` module to
        retrieve the metadata about the dataclass and extracts the names of each field.

        Returns:
            List[str]: A list of strings where each string is the name of a field in the dataclass.
        """
        return [field.name for field in fields(cls)]

    @classmethod
    def from_values_keyed(cls, values: Dict[str, Any]) -> List["RdsTerm"]:
        """
        Creates a list of RdsTerm objects from a dictionary containing structured data.

        This method parses and processes the input dictionary to extract relevant information
        related to pricing dimensions and other associated fields. It generates a list of RdsTerm
        instances by iterating through the data and initializing objects with appropriate values.

        Parameters:
            values (Dict[str, Any]): A dictionary containing hierarchical pricing data keyed by the string "OnDemand".
                                     This includes price dimensions and other relevant attributes.

        Returns:
            List["RdsTerm"]: A list of RdsTerm objects created from the structured pricing data.

        Notes:
            - This method expects the input dictionary to have a specific structure, primarily including
              the "OnDemand" key with corresponding values.
            - The method utilizes the `RdsTermPriceDimensions` class to process "priceDimensions" key
              and extracts relevant fields for `RdsTerm` initialization.
        """
        on_demands = list(values["OnDemand"].values())
        dims = []
        for od in on_demands:
            dims.extend(od["priceDimensions"].values())
        return [
            cls(
                priceDimensions=[RdsTermPriceDimensions.from_values(dim) for dim in dims],
                **{k: v for k, v in od.items() if k in cls.fields() and k not in ("priceDimensions",)},
            )
            for od in on_demands
        ]


@define
class RdsPricing(Base):
    """
    Represents pricing details for an Amazon RDS instance.

    Attributes:
        serviceCode: The unique identifier for the AWS service.
        version: The version of the pricing data.
        publicationDate: The date the pricing data was published.
        product: An instance of RdsPricingProduct representing product details.
        terms: A list of RdsTerm instances representing the terms of the pricing.

    Methods:
        from_values(cls, values):
            Creates an RdsPricing instance from a dictionary of values. Extracts
            and maps values for product and terms and initializes the class with
            the remaining relevant fields from the input.

        from_values_collection(cls, values):
            Creates a dictionary of RdsPricing instances from a list of
            dictionaries. Each instance is keyed by its service code.

        as_dict():
            Converts the object into a dictionary representation.
    """

    serviceCode: str
    version: str
    publicationDate: str
    product: RdsPricingProduct = field(default=None)
    terms: List[RdsTerm] = field(default=None)

    @classmethod
    def from_values(cls, values: Dict[str, Any]) -> "RdsPricing":
        """
        Constructs an instance of the RdsPricing class using the provided dictionary of values.

        Args:
            cls: The class itself, passed automatically by the Python runtime.
            values (Dict[str, Any]): A dictionary containing the data required to initialize
                                     an instance of RdsPricing. This includes:
                                     - 'product': Uses RdsPricingProduct.from_values to create the product.
                                     - 'terms': Uses RdsTerm.from_values_keyed to create the terms.
                                     Remaining fields are dynamically extracted based on cls.fields().

        Returns:
            RdsPricing: A new instance of the RdsPricing class.
        """
        result = cls(
            product=RdsPricingProduct.from_values(values["product"]),
            terms=RdsTerm.from_values_keyed(values["terms"]),
            **{k: v for k, v in values.items() if k in cls.fields() and k not in ("product", "terms")},
        )
        return result

    @classmethod
    def from_values_collection(cls, values: List[Dict[str, Any]]) -> Dict[str, "RdsPricing"]:
        """
        Creates a dictionary of RdsPricing objects from a collection of values.

        Parameters:
            values (List[Dict[str, Any]]): A list of dictionaries where each dictionary
                                           contains the attributes needed to create an
                                           instance of RdsPricing using the `from_values`
                                           method.

        Returns:
            Dict[str, RdsPricing]: A dictionary where the keys are 'serviceCode' attributes
                                   of the created instances, and the values are the corresponding
                                   RdsPricing instances.
        """
        result = {}
        for value in values:
            inst = cls.from_values(value)
            result[inst.serviceCode] = inst
        return result

    def as_dict(self):
        return asdict(self)


@define
class InstanceType(Base):
    """
    Represents the configuration details of an instance type, including its specifications, capabilities, and supported features.

    Attributes:
        InstanceType: The identifier for the instance type.
        CurrentGeneration: Indicates whether this instance type is of the current generation.
        FreeTierEligible: Specifies whether the instance type is eligible for the free tier.
        SupportedUsageClasses: List of usage classes supported by the instance type (e.g., spot, on-demand).
        SupportedRootDeviceTypes: List of root device types supported by the instance type (e.g., ebs, instance-store).
        SupportedVirtualizationTypes: List of virtualization types supported by the instance type (e.g., hvm, paravirtual).
        BareMetal: Indicates if the instance type is bare metal.
        Hypervisor: Specifies the hypervisor used by the instance type.
        ProcessorInfo: Details about the processor, such as architecture and capabilities.
        VCpuInfo: Information related to the vCPUs, including counts and configurations.
        MemoryInfo: Memory specifications, such as total size in MiB.
        InstanceStorageSupported: Indicates whether instance storage is supported.
        EbsInfo: Information about the Elastic Block Store (EBS) for the instance type.
        NetworkInfo: Network-related specifications and capabilities.
        PlacementGroupInfo: Details about placement group support for the instance type.
        HibernationSupported: Indicates whether hibernation is supported for this instance type.
        BurstablePerformanceSupported: Indicates if burstable performance is supported.
        DedicatedHostsSupported: Specifies whether the instance type supports dedicated hosts.
        AutoRecoverySupported: Indicates if the instance type supports automatic recovery.
        SupportedBootModes: Specifies supported boot modes of the instance type.
        NitroEnclavesSupport: Indicates the Nitro Enclaves support level, if applicable.

    Methods:
        from_values(cls, values):
            Creates an InstanceType object using a dictionary of values, initializing nested properties like VCpuInfo and MemoryInfo.

        from_values_collection(cls, values):
            Initializes a collection of InstanceType objects from a list of dictionaries and returns them as a dictionary, indexed by InstanceType.

        from_values_collection_as_db(cls, values):
            Converts a collection of instance types into a database-friendly format. Each entry is indexed by a modified key prefixed with "db.".

        transform_to_db_instance_type(self):
            Transforms the current InstanceType object into a DbInstanceType, suitable for database storage, with modifications to nested attributes.
    """

    InstanceType: str
    CurrentGeneration: Optional[bool] = field(default=None)
    FreeTierEligible: Optional[bool] = field(default=None)
    SupportedUsageClasses: Optional[List[str]] = field(default=None)
    SupportedRootDeviceTypes: Optional[List[str]] = field(default=None)
    SupportedVirtualizationTypes: Optional[List[str]] = field(default=None)
    BareMetal: Optional[bool] = field(default=None)
    Hypervisor: Optional[str] = field(default=None)
    ProcessorInfo: Optional[Dict[str, Any]] = field(default=None)
    VCpuInfo: Optional[VCpuInfo] = field(default=None)
    MemoryInfo: Optional[MemoryInfo] = field(default=None)
    InstanceStorageSupported: Optional[bool] = field(default=None)
    EbsInfo: Optional[Dict[str, Any]] = field(default=None)
    NetworkInfo: Optional[Dict[str, Any]] = field(default=None)
    PlacementGroupInfo: Optional[Dict[str, Any]] = field(default=None)
    HibernationSupported: Optional[bool] = field(default=None)
    BurstablePerformanceSupported: Optional[bool] = field(default=None)
    DedicatedHostsSupported: Optional[bool] = field(default=None)
    AutoRecoverySupported: Optional[bool] = field(default=None)
    SupportedBootModes: Optional[Dict[str, Any]] = field(default=None)
    NitroEnclavesSupport: Optional[str] = field(default=None)

    @classmethod
    def from_values(cls, values: Dict[str, Any]) -> "InstanceType":
        """
        Creates and returns an instance of the class using the provided dictionary of values.

        Parameters:
        values (Dict[str, Any]): A dictionary containing the key-value pairs required for initializing the class instance.
                                 Keys "VCpuInfo" and "MemoryInfo" are expected to map to dictionaries that are used
                                 to create respective objects.

        Returns:
        InstanceType: An instance of the class initialized with the provided values.

        Notes:
        - The method uses the "VCpuInfo" and "MemoryInfo" entries in the dictionary to create specific objects for
          these attributes.
        - Any additional keys in the `values` dictionary that match the class's fields except "VCpuInfo" and
          "MemoryInfo", will also be included while creating the object.
        """
        return cls(
            VCpuInfo=VCpuInfo(**values["VCpuInfo"]),
            MemoryInfo=MemoryInfo(SizeInMiB=values["MemoryInfo"]["SizeInMiB"]),
            **{k: v for k, v in values.items() if k in cls.fields() and k not in ("VCpuInfo", "MemoryInfo")},
        )

    @classmethod
    def from_values_collection(cls, values: List[Dict[str, Any]]) -> Dict[str, "InstanceType"]:
        """
        Creates a dictionary of instances from a collection of value dictionaries.

        This class method takes a list of dictionaries, where each dictionary contains data to create an instance of the class. It uses the `from_values` class method to create an instance for every dictionary in the list, and maps each instance in the result dictionary using its `InstanceType` attribute as the key.

        Parameters:
        values (List[Dict[str, Any]]): A list of dictionaries, each containing the data required to create an instance of the class.

        Returns:
        Dict[str, "InstanceType"]: A dictionary where the keys are the `InstanceType` attributes of the created instances, and the values are the instances themselves.
        """
        result = {}
        for value in values:
            inst: InstanceType = cls.from_values(value)
            result[inst.InstanceType] = inst
        return result

    @classmethod
    def from_values_collection_as_db(cls, values: List[Dict[str, Any]]) -> Dict[str, dict]:
        """
        Converts a collection of values into a dictionary formatted to resemble database records.

        This class method processes a list of dictionaries where each dictionary contains data representing individual records or objects. It first transforms the input values using a helper method `from_values_collection` and then orders the resulting records by keys. Each entry is further transformed into a dictionary matching a database instance structure before being returned in a new dictionary, with keys prefixed as "db.<original_key>".

        Parameters:
        values (List[Dict[str, Any]]): A list where each item is a dictionary representing attributes of a potential record.

        Returns:
        Dict[str, dict]: A dictionary with keys prefixed as "db.<original_key>" and values as their corresponding transformed database instances.
        """
        db_values = cls.from_values_collection(values)
        keys = sorted(db_values.keys())
        return {f"db.{key}": asdict(db_values[key].transform_to_db_instance_type()) for key in keys}

    def transform_to_db_instance_type(self):
        """
        Transforms the current object instance into a DbInstanceType object.

        Returns:
            DbInstanceType: A database instance type object populated with
            information from the current instance, including instance type,
            vCPU details, memory size, and valid configuration options.
        """
        return DbInstanceType(
            InstanceType=f"db.{self.InstanceType}",
            DefaultVCpus=self.VCpuInfo.DefaultVCpus,
            DefaultCores=self.VCpuInfo.DefaultCores,
            DefaultThreadsPerCore=self.VCpuInfo.DefaultThreadsPerCore,
            ValidCores=self.VCpuInfo.ValidCores,
            ValidThreadsPerCore=self.VCpuInfo.ValidThreadsPerCore,
            MemorySizeInMiB=self.MemoryInfo.SizeInMiB,
        )
