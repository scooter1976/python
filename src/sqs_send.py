import boto3

aws_region = "ap-southeast-2"  # Replace with your desired AWS region

# Initialize an SQS client
# sqs = boto3.client('sqs', region_name=aws_region, aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
sqs = boto3.client("sqs", region_name=aws_region)

# The URL of the SQS queue
queue_url = "https://sqs.ap-southeast-2.amazonaws.com/193339706588/DemoQueue"  # Replace with your queue URL

# Message to send
message_body = "Hello, AWS SQS!"

# Send a message to the queue
response = sqs.send_message(QueueUrl=queue_url, MessageBody=message_body)

# Print the message ID and response
print(f"Message ID: {response['MessageId']}")
print(f"Response: {response}")
