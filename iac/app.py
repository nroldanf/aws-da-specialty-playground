#!/usr/bin/env python3
import os

import aws_cdk as cdk

from stacks.stateful_stack import StateFulStack
from config import Config


app = cdk.App()
StateFulStack(app, "StateFulStack", Config)

app.synth()
