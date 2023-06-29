import aws_cdk as core
import aws_cdk.assertions as assertions

from stacks.stateful_stack import StateFulStack
from config import Config

def test_kinesis_data_stream_created():
    app = core.App()
    stack = StateFulStack(app, "state", Config)
    template = assertions.Template.from_stack(stack)
    template.has_resource_properties(
        "AWS::Kinesis::Stream", {
            "RetentionPeriodHours": Config.kinesis_retention_period,
            "ShardCount": Config.kinesis_shard_count
        }
    )
