import boto3

session = boto3.Session(aws_access_key_id="mock", aws_secret_access_key="mock", region_name="us-east-1")
s3 = session.client('s3', endpoint_url='http://localhost:4566')
dynamodb = session.client('dynamodb', endpoint_url='http://localhost:4566')

try:
    s3.create_bucket(Bucket='medical-images')
except Exception:
    pass

try:
    dynamodb.create_table(
        TableName='MedicalImageMetadata',
        AttributeDefinitions=[
            {'AttributeName': 'image_id', 'AttributeType': 'S'}
        ],
        KeySchema=[
            {'AttributeName': 'image_id', 'KeyType': 'HASH'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
except Exception:
    pass
