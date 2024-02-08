import logging
import json
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel("INFO")
logging.basicConfig(level=logging.INFO)


class SnsWrapper:
    """Encapsulates Amazon SNS topic and subscription functions."""

    def __init__(self):
        """
        :param sns_resource: A Boto3 Amazon SNS resource.
        """
        logger.info("Allocating Resource")
        self.sns_resource = boto3.resource("sns")

    def list_topics(self):
        """
        Lists topics for the current account.

        :return: An iterator that yields the topics.
        """
        logger.info("Listing Topics")
        try:
            topics_iter = self.sns_resource.topics.all()
            logger.info("Got topics.")
        except ClientError:
            logger.error("Couldn't get topics.")
            raise
        else:
            return topics_iter

    @staticmethod
    def publish_multi_message(
        topic, subject, default_message, sms_message, email_message
    ):
        """
        Publishes a multi-format message to a topic. A multi-format message takes
        different forms based on the protocol of the subscriber. For example,
        an SMS subscriber might receive a short version of the message
        while an email subscriber could receive a longer version.

        :param topic: The topic to publish to.
        :param subject: The subject of the message.
        :param default_message: The default version of the message. This version is
                                sent to subscribers that have protocols that are not
                                otherwise specified in the structured message.
        :param sms_message: The version of the message sent to SMS subscribers.
        :param email_message: The version of the message sent to email subscribers.
        :return: The ID of the message.
        """
        try:
            message = {
                "default": default_message,
                "sms": sms_message,
                "email": email_message,
            }
            response = topic.publish(
                Message=json.dumps(message), Subject=subject, MessageStructure="json"
            )
            message_id = response["MessageId"]
            logger.info("Published multi-format message to topic %s.", topic.arn)
        except ClientError:
            logger.exception("Couldn't publish message to topic %s.", topic.arn)
            raise
        else:
            return message_id


if __name__ == "__main__":
    client = SnsWrapper()

    sns = client.list_topics()

    for topic in sns:
        print(topic.arn)
        if str(topic.arn).endswith("Sensibo"):
            SNStopic = topic
            print(topic)

    sns.publish_multi_message(
        SNStopic,
        "Hello World",
        "HellowWorldDefault",
        "HellowWorldSMs",
        "HellowWorldEmail",
    )
