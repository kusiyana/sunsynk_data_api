import requests


class SunsynkData:
    """This Class provides a basic means for interrogating the Sunsynk HTTP API
    to get information about battery, panels and general info. You will need:
     1. Your username (at the time of sign-up/installation)
     2. Your password
     3. Your device serial number (viewable after you sign into your account online)
    """

    api_base = "https://api.sunsynk.net/api/v1/inverter/"
    loginurl = "https://api.sunsynk.net/oauth/token"

    def __init__(self, serial_number: int, username: str, password: str) -> None:
        self.api_base = SunsynkData.api_base
        self.loginurl = SunsynkData.loginurl
        self.serial_number = serial_number
        self.username = username
        self.password = password
        self.bearer_token = self.get_bearer_token(username, password)
        self.headers_and_token = {
            "Content-type": "application/json",
            "Accept": "application/json",
            "Authorization": self.bearer_token,
        }

    def get_bearer_token(self, username: str, password: str) -> str:
        """Get a bearer token and return it as a string"""
        headers = {"Content-type": "application/json", "Accept": "application/json"}

        payload = {
            "username": username,
            "password": password,
            "grant_type": "password",
            "client_id": "csp-web",
        }
        raw_data = requests.post(self.loginurl, json=payload, headers=headers).json()
        my_access_token = raw_data["data"]["access_token"]
        the_bearer_token_string = f"Bearer {my_access_token}"
        return the_bearer_token_string

    # Get plant id and current generation in Watts
    def get_battery(self):
        """Get the details of the battery state
        battery_result =
        {
            "charge_current": <float> The charge going into your batteries (will be negative in a discharge state),
            "charge_power": <int> The charge power (will be negative in a discharge state),
            "voltage": <int> The present voltage of the battery,
            "temp": <int> The present temperature of the battery,
            "soc": <int> The state of charge of the battery (%),
            "charge_volt": <int> The voltage at which the battery charges,
        }
        """

        endpoint = f"{self.api_base}battery/{self.serial_number}/realtime?sn={self.serial_number}&lan=en"

        request_result = requests.get(endpoint, headers=self.headers_and_token)
        data_response = self.__unpack_response(request_result)
        if "error" in data_response:
            return data_response["error"]

        battery_result = {
            "charge_current": float(data_response["current"]) * -1,
            "charge_power": int(
                round(
                    float(data_response["current"])
                    * float(data_response["voltage"])
                    * -1,
                    0,
                )
            ),
            "voltage": data_response["voltage"],
            "temp": data_response["temp"],
            "soc": data_response["soc"],
            "charge_volt": data_response["chargeVolt"],
        }

        return battery_result

    def get_load(self) -> dict:
        """Get the details of load on the inverter
        load_result =
        {
            "total_power": <int> The total power draw from your inverter,
        }
        """

        endpoint = (
            f"{self.api_base}load/{self.serial_number}/realtime?sn={self.serial_number}"
        )
        request_result = requests.get(endpoint, headers=self.headers_and_token)
        data_response = self.__unpack_response(request_result)
        if "error" in data_response:
            return data_response["error"]

        load_result = {"total_power": data_response["totalPower"]}
        return load_result

    def get_pv(self) -> dict:
        """Get the details of power generation from the solar panels
        output =
        {
            "pv_incoming_power": <int> Solar power coming off your panels ,
            "pv_consumed_power": <int> Solar power consumed by your household base load,
            "pv_surplus_power": <int> Solar surplus available for charging and powering the inverter,
        }
        """
        endpoint = f"{self.api_base}{self.serial_number}/realtime/output"
        request_result = requests.get(endpoint, headers=self.headers_and_token)
        data_response = self.__unpack_response(request_result)
        if "error" in data_response:
            return data_response["error"]

        pv_result = {
            "pv_incoming_power": data_response["pInv"],
            "pv_consumed_power": data_response["pac"],
            "pv_surplus_power": data_response["pInv"] - data_response["pac"],
        }
        return pv_result

    def get_info(self) -> dict:
        """Get the details of general inverter/account information"""
        endpoint = f"{self.api_base}{self.serial_number}"
        request_result = requests.get(endpoint, headers=self.headers_and_token)
        data_response = self.__unpack_response(request_result)
        if "error" in data_response:
            return data_response["error"]

        info_result = {
            "e_total": data_response["etotal"],
            "e_month": data_response["emonth"],
            "e_today": data_response["etoday"],
            "eyear": data_response["eyear"],
            "sn": data_response["sn"],
            "alias": data_response["alias"],
            "gsn": data_response["gsn"],
            "status": data_response["status"],
            "run_status": data_response["runStatus"],
            "type": data_response["type"],
            "thumb_url": data_response["thumbUrl"],
            "opened": data_response["opened"],
            "version": data_response["version"],
            "plant": data_response["plant"],
            "user": data_response["user"],
        }
        return info_result

    @staticmethod
    def __unpack_response(response: requests.Response) -> dict:
        """Unpack the Response class and return error if there's no data field"""
        try:
            data_response = response.json()["data"]
        except Exception as err:
            data_response = {"error": err}
        return data_response
