import json
from typing import Optional
from urllib.request import urlopen
from jdk.enums import BaseEnum, OperatingSystem, Architecture, JvmImpl, ImageType
from .client import Client, ClientException

_INDEXMAP_URL = "https://raw.githubusercontent.com/corretto/corretto-downloads/main/latest_links/indexmap_with_checksum.json"


class CorrettoEnvironment(BaseEnum):
    PRODUCTION = "https://corretto.aws"


class CorrettoClient(Client):
    def __init__(
        self, environment: CorrettoEnvironment = CorrettoEnvironment.PRODUCTION
    ) -> None:
        self._base_url = environment.value

    def get_download_url(
        self,
        version: str,
        operating_system: Optional[OperatingSystem] = None,
        arch: Optional[Architecture] = None,
        impl: JvmImpl = JvmImpl.HOTSPOT,
        jre: bool = False,
    ) -> str:
        version = self.normalize_version(version)

        if operating_system is None:
            operating_system = OperatingSystem.detect()

        if arch is None:
            arch = Architecture.detect()

        image_type = ImageType.JRE.value if jre else ImageType.JDK.value

        try:
            data = json.loads(urlopen(_INDEXMAP_URL).read().decode("utf-8"))
        except Exception as e:
            raise ClientException(e)
        else:
            _operating_system = (
                "macos"
                if operating_system == OperatingSystem.MAC
                else operating_system.value
            )
            if _operating_system in data:
                os_data = data[_operating_system]
                if arch.value in os_data:
                    arch_data = os_data[arch.value]
                    if image_type in arch_data:
                        image_type_data = arch_data[image_type]
                        if version in image_type_data:
                            version_data = image_type_data[version]
                            file_format = (
                                "zip"
                                if operating_system == OperatingSystem.WINDOWS
                                else "tar.gz"
                            )
                            if file_format in version_data:
                                return f"{self._base_url}{version_data[file_format]['resource']}"
                            else:
                                print(f"DEBUG: Could not find version - {file_format}")
                        else:
                            print(f"DEBUG: Could not find version - {version}")
                    else:
                        print(f"DEBUG: Could not find image_type - {image_type}")
                else:
                    print(f"DEBUG: Could not find arch - {arch.value}")
            else:
                print(
                    f"DEBUG: Could not find operating_system - {operating_system.value}"
                )
