import cgi
import shutil
import tempfile
from os import path
from abc import ABC, abstractmethod
from typing import List, Optional, Callable, Union
from urllib import request
from urllib.parse import urlsplit
from collections.abc import Iterable

from jdk.enums import Architecture, OperatingSystem, JvmImpl, Implementation, Vendor


_vendor_clients = dict()


class ClientException(Exception):
    pass


class Client(ABC):
    @staticmethod
    def normalize_version(version: str) -> str:
        if version == "1.8":
            return "8"
        return version

    @abstractmethod
    def get_download_url(
        self,
        version: str,
        operating_system: OperatingSystem,
        arch: Architecture,
        impl: JvmImpl = Implementation.HOTSPOT,
        jre: bool = False,
    ) -> str:
        pass

    def download(self, download_url: str) -> Optional[str]:
        req = request.Request(download_url, headers={"User-Agent": "Mozilla/5.0"})

        jdk_file = None
        with request.urlopen(req) as open_request:
            info = open_request.info()
            if "Content-Disposition" in info:
                content_disposition = info["Content-Disposition"]
                _, params = cgi.parse_header(content_disposition)
                if "filename" in params:
                    jdk_file = params["filename"]
            else:
                url_path = urlsplit(download_url).path
                jdk_file = path.basename(url_path)

            if jdk_file:
                jdk_file = path.join(tempfile.gettempdir(), jdk_file)
                with open(jdk_file, "wb") as out_file:
                    shutil.copyfileobj(open_request, out_file)
        return jdk_file


def vendor_client(
    vendor: Union[Vendor, str, List[Vendor], List[str]]
) -> Callable[[Client], Client]:
    def wrapper(client: Client) -> Client:
        if isinstance(vendor, Iterable):
            unique_vendors = set(vendor)
            for unique_vendor in unique_vendors:
                _vendor_clients[str(unique_vendor)] = client
        else:
            _vendor_clients[str(vendor)] = client
        return client

    return wrapper


def load_client(vendor: Union[Vendor, str]) -> Optional[Client]:
    vendor_name = str(vendor)
    if vendor_name in _vendor_clients:
        return _vendor_clients[vendor_name]
