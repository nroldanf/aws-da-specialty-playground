'''
Both of these should accept a properties object in the constructor that allows 
for full configurability, rather than relying on an environment variable on the target machine.
'''
class Config:
    kinesis_data_stream: str = "CadabraOrders"
    kinesis_retention_period: int = 24
    kinesis_shard_count: int = 1
    kinesis_delivery_stream: str = "DeliveryS3"
    
    s3_datalake_bucket: str = "S3DatalakeBucketNRF"
    ec2_producer_name: str = "KinesisProducer"
    ec2_key_name: str = "da-specialty"