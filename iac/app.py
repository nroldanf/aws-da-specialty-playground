#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import aws_cdk as cdk
from stacks.stateful_stack import StateFulStack
from stacks.etl_stack import ETLStack
from config import Config

load_dotenv()

app = cdk.App()
env = cdk.Environment(
    account=os.environ.get("AWS_ACCOUNT_ID", "123"),
    region=os.environ.get("AWS_REGION", "us-east-1"),
)

stateful_stack: StateFulStack = StateFulStack(app, "StateFulStack", Config, env=env)
etl_stack = ETLStack(app, "ETLStack", Config, stateful_stack.data_stream, env=env)

app.synth()
