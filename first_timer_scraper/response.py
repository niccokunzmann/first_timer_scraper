import os
import json
from pprint import pprint

def url_to_path(url):
    url = url.replace("?", "_")
    url_path = url.split("//", 1)[1]
    return os.sep.join(url_path.split("/"))

class Response:

    file_name = "response.json"

    @classmethod
    def from_response(cls, response):
        headers = dict(response.headers)
        headers['Access-Control-Allow-Origin'] = '*'
        return cls(response.links, response.json(), headers, response.url)
        
    @classmethod
    def from_path(cls, path, url):
        file = os.path.join(path, url_to_path(url), cls.file_name)
        if os.path.exists(file):
            with open(file) as f:
                try:
                    return cls.from_json(json.load(f))
                except ValueError:
                    # JSON could not decode
                    return None
        return None
        
    @classmethod
    def from_json(cls, json):
        return cls(json["links"], json["json"], json["headers"], json["url"])

    def __init__(self, links, json, headers, url):
        self._links = links
        self._json = json
        self._headers = headers
        self._url = url
        
    @property
    def next_page(self):
        return self.links.get("next", {}).get("url")
    
    @property
    def links(self):
        """The links of the reponse."""
        return self._links

    @property
    def headers(self):
        """The headers of the reponse."""
        return self._headers

    @property
    def json(self):
        """The json of the reponse."""
        return self._json

    @property
    def url(self):
        """The url of the reponse."""
        return self._url
        
    def to_path(self, path):
        """Save the request at a path."""
        folder = os.path.join(path, url_to_path(self._url))
        os.makedirs(folder, exist_ok=True)
        file = os.path.join(folder, self.file_name)
        with open(file, "w") as f:
            json.dump(self.to_json(), f)

    def to_json(self):
        return {"links": self._links, "headers": self._headers,
                "json": self._json, "url": self._url}

    def print(self):
        pprint(self.to_json())

