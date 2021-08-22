import configparser
import json
import os
import ssl

from typing import Any, Dict, Type, TypeVar
from urllib import request

import hue.utils as U

_T = TypeVar("_T", bound="Config")


class Config:
    _CREDENTIALS = ".hue"
    _DISCOVERY = "https://discovery.meethue.com/"

    def __init__(self, address: str, username: str) -> None:
        self._address = address
        self._username = username
        self._url: str = U.make_url(address, username)

    @property
    def username(self) -> str:
        return self._username

    @property
    def address(self) -> str:
        return self._address

    @property
    def url(self) -> str:
        return self._url

    def write(self) -> None:
        config = configparser.ConfigParser()
        config["default"] = {"ipaddr": self._address, "passkey": self._username}
        path = self._find_credentials_path()
        with open(path, "w") as file:
            config.write(file)

    @classmethod
    def find_available_devices(cls) -> Dict[str, Any]:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        response = request.urlopen(cls._DISCOVERY, context=context)
        return json.loads(response.read().decode())

    @classmethod
    def from_file(cls: Type[_T]) -> _T:
        config = configparser.ConfigParser()
        path = cls._find_credentials_path()
        if not os.path.exists(path):
            raise FileNotFoundError(
                "Could not locate hue configuration file on disk"
            )

        config.read(path)
        address = config["default"]["ipaddr"]
        username = config["default"]["passkey"]
        return cls(address, username)

    @classmethod
    def _find_credentials_path(cls) -> str:
        return os.path.join(os.path.expanduser("~"), cls._CREDENTIALS)
