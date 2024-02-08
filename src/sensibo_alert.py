import logging
import json
import sys

#sys.path.insert(0, "./AWS/")
import sns_publish
import sensibo_code

logger = logging.getLogger()
logger.setLevel("INFO")
logging.basicConfig(level=logging.INFO)


def notifyme(temperature: str, humidity: str, feels_like: str, room_location: str):
    # Create the SNS Client Class
    sns_client = sns_publish.SnsWrapper()

    # List topics to find the Sensibo Topic
    sns_topics = sns_client.list_topics()

    for topic in sns_topics:
        logging.info(topic.arn)
        if str(topic.arn).endswith("Sensibo"):
            sensibotopicARN = topic
            logging.info(sensibotopicARN)

    # Create Message
    message = f"""{room_location}\n
    Temperature {temperature}C\n
    Humidty {humidity}%\n
    Feels like {feels_like}C"""

    # Publish
    response = sns_client.publish_multi_message(
        SensiboTopicARN,
        "Hello World",
        "HellowWorldDefault",
        message,
        "HellowWorldEmail",
    )

    return response


if __name__ == "__main__":

    # Log into Sensibo API Client
    logging.debug("Try Connection")
    client = sensibo_code.SensiboClientAPI()
    logging.debug("Connection Successful")
    logging.debug(" ")

    # Get Device UID
    logging.debug("Getting Devices")
    devices = client.devices()
    logging.debug("_________ Devices __________")
    logging.debug(devices)

    # Save UID and Name for Device
    DeviceName = list(devices.keys())[0]
    DeviceUID = devices[DeviceName]

    Pod_State = client.pod_measurement(DeviceUID)
    logging.debug(Pod_State)
    logging.info(f"Temperature :  {Pod_State[0]['temperature']}")
    logging.info(f"humidity    :  {Pod_State[0]['humidity']}")
    logging.info(f"feelsLike   :  {Pod_State[0]['feelsLike']}")

    # logging.info(json.dumps(pod_state,indent=4))
    Temperature = Pod_State[0]["temperature"]
    Humidity = Pod_State[0]["humidity"]
    Feelslike = Pod_State[0]["feelsLike"]

    AC_status = client.pod_ac_state(DeviceUID)
    logging.debug(json.dumps(AC_status, indent=4))
    logging.info(f"Aircon state : {AC_status['on']}")

    ac_state_on = AC_status["on"]

    if not ac_state_on and Temperature > 26:
        logging.info("We should turn on")
        return_message_id = notifyme(Temperature, Humidity, Feelslike, DeviceName)
        logging.info("----------")
        logging.info(return_message_id)
        logging.info("----------")

    elif ac_state_on and Temperature > 26:
        logging.info("All Good")
