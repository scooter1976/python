import requests
import json
import logging
import os

_SERVER = "https://home.sensibo.com/api/v2"
_APIKEY = os.environ.get("SENSIBO_API_KEY")  

logger = logging.getLogger()
logger.setLevel("INFO")
logging.basicConfig(level=logging.INFO)


class SensiboClientAPI(object):
    def __init__(self):

        self._api_key = _APIKEY

    def _get(self, path, **params):
        url = _SERVER + path
        params["apiKey"] = self._api_key
 
        logging.debug("###############################")
        logging.debug(url)
        logging.debug(json.dumps(params, indent=4))
        logging.debug("###############################")

        response = requests.get(url, params=params)
        response.raise_for_status()

        return response.json()

    def _patch(self, path, data, **params):

        url = _SERVER + path
        params["apiKey"] = self._api_key

        logging.debug("###############################")
        logging.debug(url)
        logging.debug(json.dumps(params, indent=4))
        logging.debug(json.dumps(json.loads(data), indent=4))
        logging.debug("###############################")

        response = requests.patch(url, params=params, data=data)
        response.raise_for_status()

        return response.json()

    def devices(self):
        result = self._get("/users/me/pods", fields="id,room")

        return {x["room"]["name"]: x["id"] for x in result["result"]}

    def pod_location(self):
        result = self._get("/users/me/pods", fields="location")

        return result["result"]

    def pod_all(self):
        logging.error("##")
        result = self._get("/users/me/pods", fields="")

        return result["result"]

    def pod_measurement(self, podUid):
        result = self._get("/pods/%s/measurements" % podUid)

        return result["result"]

    def pod_ac_state(self, podUid):
        result = self._get(
            "/pods/%s/acStates" % podUid, limit=1, fields="status,reason,acState"
        )

        return result["result"][0]["acState"]

    def pod_change_ac_state(self, podUid, currentAcState, propertyToChange, newValue):
        result = self._patch(
            "/pods/%s/acStates/%s" % (podUid, propertyToChange),
            json.dumps({"currentAcState": currentAcState, "newValue": newValue}),
        )

        return result["result"]


if __name__ == "__main__":

    # Log into Sensibo API Client
    logging.info("Try Connection")
    client = SensiboClientAPI()
    logging.info("Connection Successful")
    logging.info("")

    # Get Device UID
    logging.info("Getting Devices")
    devices = client.devices()
    logging.info("_________ Devices __________")
    logging.info(devices)

    # Save UID and Name for Device
    deviceName = list(devices.keys())[0]
    deviceUID = devices[deviceName]

    logging.info(" ")
    logging.info("Getting Air Condition Details")
    ac_state = client.pod_ac_state(deviceUID)

    logging.info(f"__________ AC State of {deviceName} __________")
    logging.info(json.dumps(ac_state, indent=4))

    logging.info(" ")
    logging.info("Getting Sensibo POD Details")

    # print("$$$$$$$$$$$$$$-start")
    # pod_all = client.pod_all()
    # logging.info(" ")
    # logging.info (f"__________ Pod State of {deviceName} __________")
    # logging.info(json.dumps(pod_all,indent=4))
    # print("$$$$$$$$$$$$$$-end")

    pod_state = client.pod_measurement(deviceUID)
    logging.info(" ")
    logging.info(f"__________ Pod State of {deviceName} __________")
    logging.info(json.dumps(pod_state, indent=4))

    logging.info("")
    loc_state = client.pod_location()

    logging.info(f"___________ Location of {deviceName} ___________")
    logging.info(json.dumps(loc_state, indent=4))

    logging.info("###########################################################")
    logging.info("Setting Temp to 24")
    new_ac_state = client.pod_change_ac_state(
        deviceUID, ac_state, "targetTemperature", 24
    )

    # ac_state = client.pod_ac_state(uid)

    logging.info(f"__________ NEW AC State of {deviceName} __________")
    logging.info(json.dumps(new_ac_state, indent=4))

    # client.pod_change_ac_state(uid, ac_state, "on", not ac_state['on'])
    # logging.info("Truning ON")
    # new_ac_state = client.pod_change_ac_state(deviceUID, ac_state, "on", True)
    # logging.info (f"__________ NEW AC State of {deviceName} __________")
    # logging.info(json.dumps(new_ac_state,indent=4))
    # client.pod_change_ac_state(uid, ac_state, "fanLevel", 'high')
