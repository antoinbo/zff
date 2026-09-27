import json
import requests

# https://trpc.io/docs/rpc

class Client:
    def __init__(self, url):
        if not url.endswith("/"):
            url = url + "/"

        self.__base_url = url

    @staticmethod
    def __json_payload(data):
        return json.dumps({"json": data})

    def query(self, procedure, data=None, json=None):
        url = self.__base_url + procedure

        if data is not None and json is not None:
            raise Exception("Please pass 'data' or 'json', but not both for the same call.")
        elif data is not None:
            params = {
                "input": data
            }
        elif json is not None:
            params = {
                "input": self.__json_payload(json)
            }

        response = requests.get(url, params=params)

        assert response.status_code in [200, 207], response.text

        return response.json().get("result").get("data").get("json")

    def batch(self, calls):
        procedures = list()
        arguments = dict()

        index = 0
        for call in calls:
            procedures.append(call.get("procedure"))

            arguments[str(i)] = call.get("arguments")

            index = index + 1

        url = self.__base_url + ",".join(procedures)

        params = {
            "batch": 1,
            "input": json.dumps(arguments)
        }

        response = requests.get(url, params=params)

        assert response.status_code == 200, response.text

        result = response.json()
        assert len(result) == len(calls)

        return [item.get("result").get("data").get("json") for item in result]

    def mutation(self):
        pass

    def subscription(self):
        pass
