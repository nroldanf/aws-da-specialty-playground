import os
from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_iam as iam,
    aws_ec2 as ec2,
)
from constructs import Construct
from config import Config


class ETLStack(Stack):
    def __init__(
        self, 
        scope: Construct, 
        construct_id: str, 
        config: Config, 
        data_stream,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # IAM Role (EC2 instance profile)
        producer_role: iam.Role = iam.Role(
            self,
            f"{config.ec2_producer_name}Role",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com")
        )
        data_stream.grant_write(producer_role)
        # delivery_stream.grant_put(producer_role) 
        vpc = ec2.Vpc.from_lookup(
            self,
            f"{config.ec2_producer_name}VPC",
            is_default=True
        )
        
        sg: ec2.SecurityGroup = ec2.SecurityGroup(
            self,
            f"{config.ec2_producer_name}SG",
            vpc=vpc
        )
        sg.add_ingress_rule(ec2.Peer.ipv4(os.environ.get("IP_ADDRESS")), ec2.Port.tcp(22), "allow ssh access from the world")
        
        producer_instance: ec2.Instance = ec2.Instance(
            self, 
            config.ec2_producer_name,
            vpc=vpc,
            key_name=config.ec2_key_name,
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux(
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
            ),
            security_group=sg,
            role=producer_role
        )