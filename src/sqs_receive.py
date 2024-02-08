import boto3
import time

aws_region = "ap-southeast-2"  # Replace with your desired AWS region

# Initialize an SQS client
# sqs = boto3.client('sqs', region_name=aws_region, aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
sqs = boto3.client("sqs", region_name=aws_region)

# The URL of the SQS queue
queue_url = "https://sqs.ap-southeast-2.amazonaws.com/193339706588/DemoQueue"  # Replace with your queue URL

while True:
    # Poll for messages from the queue
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=["All"],
        MaxNumberOfMessages=1,  # Adjust as needed
        WaitTimeSeconds=20,  # Adjust the wait time as needed
    )

    # Check if there are messages
    if "Messages" in response:
        for message in response["Messages"]:
            # Process the message content
            message_body = message["Body"]
            print(f"Received message: {message_body}")

            # Delete the message from the queue
            receipt_handle = message["ReceiptHandle"]
            sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
            print(f"Deleted message: {message_body}")

    else:
        print("No messages received. Waiting...")

    # Add a delay to control the polling rate
    time.sleep(5)  # Adjust as needed
