from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_kinesis as kinesis,
    aws_kinesisfirehose as kinesisfirehose,
    aws_s3 as s3,
    aws_iam as iam,
    aws_ec2 as ec2,
)
from constructs import Construct
from config import Config

class StateFulStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, config: Config, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Kinesis data stream
        self.data_stream: kinesis.Stream = kinesis.Stream(
            self,
            config.kinesis_data_stream,
            stream_mode=kinesis.StreamMode.PROVISIONED,
            shard_count=config.kinesis_shard_count,
            retention_period=Duration.hours(config.kinesis_retention_period),
            encryption=kinesis.StreamEncryption.MANAGED,      
        )
        # kinesis data firehose
        # S3 bucket (data lake)
        datalake_bucket: s3.Bucket = s3.Bucket(
            self,
            config.s3_datalake_bucket,
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy.RETAIN,
            auto_delete_objects=False,
            versioned=True,
            lifecycle_rules=[
                s3.LifecycleRule(
                    enabled=True,
                    # abort_incomplete_multipart_upload_after=Duration.minutes(30),
                    expiration=Duration.days(100),
                    noncurrent_version_transitions=[
                        s3.NoncurrentVersionTransition(
                            storage_class=s3.StorageClass.GLACIER,
                            transition_after=Duration.days(30),
                            noncurrent_versions_to_retain=1,
                        )
                    ],
                    # 'Days' in the Expiration action for filter '(prefix=)' must be greater than 'Days' in the Transition action (Service: Amazon S3; Status Code:
                    # object_size_greater_than=100,
                    transitions=[
                        s3.Transition(
                            storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                            transition_after=Duration.days(30),
                        ),
                        s3.Transition(
                            storage_class=s3.StorageClass.GLACIER,
                            transition_after=Duration.days(60),
                        ),
                    ],
                )
            ]
        )
        # IAM Role
        firehose_role: iam.Role = iam.Role(
            self,
            f"{config.kinesis_delivery_stream}Role",
            assumed_by=iam.ServicePrincipal("firehose.amazonaws.com")
        )
        datalake_bucket.grant_put(firehose_role)
        self.data_stream.grant_read(firehose_role)
        # delivery stream
        delivery_stream = kinesisfirehose.CfnDeliveryStream(
            self,
            config.kinesis_delivery_stream,
            kinesis_stream_source_configuration=kinesisfirehose.CfnDeliveryStream.KinesisStreamSourceConfigurationProperty(
                kinesis_stream_arn=self.data_stream.stream_arn,
                role_arn=firehose_role.role_arn
            ),
            s3_destination_configuration=kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                bucket_arn=datalake_bucket.bucket_arn,
                role_arn=firehose_role.role_arn,
                prefix="year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/hour=!{timestamp:HH}/",
                error_output_prefix="fherroroutputbase/!{firehose:random-string}/!{firehose:error-output-type}/!{timestamp:yyyy/MM/dd}"
            )
        )