import os
import urllib
import json
import requests


class NVBLClient:
    service_location = "https://covid-ws-01.alcf.anl.gov"
    _valid_fields = ["key", "smiles", "inchi", "id"]

    def __init__(self, **kwargs):
        """
        Init function, currently does nothing
        """
        super().__init__(**kwargs)

    def search(self, source, dest, param):
        """
        Search functionality

        Args:
            source (str): field the search is converting from, must be in _valid_fields
            dest (str): field the search is converting to , must be in _valid_fields
            param: 
        """
        # Check for valid source and destination parameters
        if source not in self._valid_fields or dest not in self._valid_fields:
            print(
                "Valid options for source and destination: {}".format(
                    self._valid_fields
                )
            )
        # If the source and destination are the same, do nothing
        if source == dest:
            print("No search needed")

        # Prepare the request, send request
        data = urllib.parse.urlencode({"input": param})
        req = urllib.request.Request(
            f"{self.service_location}/rpc/{source}2{dest}", data.encode("ascii")
        )
        try:
            response = urllib.request.urlopen(req).read()
        except urllib.error.URLError as e:
            print(e.reason)

        # Handle the response and convert to return output
        results = json.loads(response.decode("ascii"))
        outputs = [v for d in results for k, v in d.items()]
        return outputs
