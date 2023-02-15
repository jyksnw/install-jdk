import json
from typing import Any, Optional
from urllib.request import urlopen
from jdk.enums import (
    BaseEnum,
    BaseDetectableEnum,
    OperatingSystem,
    Architecture,
    JvmImpl,
    ImageType,
)
from jdk.extension import extends
from .client import Client, ClientException, vendor_client

_INDEX_MAP_URL = "https://raw.githubusercontent.com/corretto/corretto-downloads/main/latest_links/indexmap_with_checksum.json"


@extends(OperatingSystem)
class CorrettoOperatingSystem(BaseDetectableEnum):
    @classmethod
    def detect(cls) -> "CorrettoOperatingSystem":
        detected_os = OperatingSystem.detect()
        return cls.transform(detected_os)

    @classmethod
    def transform(
        cls, operating_system: OperatingSystem
    ) -> Optional["CorrettoOperatingSystem"]:
        if operating_system == OperatingSystem.MAC:
            return CorrettoOperatingSystem.MACOS
        elif operating_system == OperatingSystem.ALPINE_LINUX:
            return CorrettoOperatingSystem.ALPINE
        else:
            return CorrettoOperatingSystem(operating_system.value)

    AL2 = "al2"
    AL2022 = "al2022"
    ALPINE = "alpine"
    JMC = "jmc"
    MACOS = "macos"


class CorrettoEnvironment(BaseEnum):
    PRODUCTION = "https://corretto.aws"


@vendor_client(["Corretto", "Amazon", "AWS"])
class CorrettoClient(Client):
    _index_map = None

    @classmethod
    def load_index_map(cls) -> Optional[Any]:
        from collections import namedtuple

        def _object_hook(data: dict) -> namedtuple:
            def fix_key(key: Any):
                key_str = str(key)
                if key_str.isnumeric():
                    return f"v{key}"
                elif key_str == "arm-musl":
                    return "arm_musl"
                elif key in (
                    "tar.gz",
                    "tar.gz.pub",
                    "tar.gz.sig",
                    "zip.pub",
                    "zip.sig",
                ):
                    if key_str == "tar.gz":
                        return "tar"
                    else:
                        return key_str.replace(".", "_")
                else:
                    return key

            return namedtuple(
                "CorrettoData",
                [fix_key(key) for key in data.keys()],
            )(*data.values())

        try:
            if cls._index_map is None:
                cls._index_map = json.loads(
                    urlopen(_INDEX_MAP_URL).read().decode("utf-8"),
                    object_hook=_object_hook,
                )
        except Exception as e:
            raise ClientException(e)
        else:
            return cls._index_map

    def __init__(
        self, environment: CorrettoEnvironment = CorrettoEnvironment.PRODUCTION
    ) -> None:
        self._base_url = environment.value
        self._index_map = CorrettoClient.load_index_map()

    def get_download_url(
        self,
        version: str,
        operating_system: Optional[CorrettoOperatingSystem] = None,
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

        data = self._index_map
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
            print(f"DEBUG: Could not find operating_system - {operating_system.value}")
