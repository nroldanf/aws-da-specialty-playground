from aws_cdk import (
    Stack,
    Duration,
    aws_kinesis as kinesis
)
from constructs import Construct
from config import Config

class StateFulStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, config: Config, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Kinesis data stream
        first_stream = kinesis.Stream(
            self,
            config.kinesis_data_stream,
            stream_mode=kinesis.StreamMode.PROVISIONED,
            shard_count=config.kinesis_shard_count,
            retention_period=Duration.hours(config.kinesis_retention_period),
            encryption=kinesis.StreamEncryption.MANAGED,      
        )