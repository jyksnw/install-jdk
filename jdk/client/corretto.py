import json
from typing import Any
from typing import Optional
from urllib.request import urlopen

from jdk.enums import Architecture
from jdk.enums import BaseDetectableEnum
from jdk.enums import BaseEnum
from jdk.enums import Environment
from jdk.enums import ImageType
from jdk.enums import JvmImpl
from jdk.enums import OperatingSystem
from jdk.enums import Vendor
from jdk.extension import extends

from .client import Client
from .client import ClientError
from .client import vendor_client


_INDEX_MAP_URL = "https://raw.githubusercontent.com/corretto/corretto-downloads/main/latest_links/indexmap_with_checksum.json"  # noqa: B950


@extends(Vendor)
class CorrettoVendor(BaseEnum):
    CORRETTO = "Corretto"
    AMAZON = "Amazon"
    AWS = "AWS"


@extends(ImageType)
class CorrettoImageType(BaseEnum):
    HEADLESS = "headless"


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


@extends(Environment)
class CorrettoEnvironment(BaseEnum):
    PRODUCTION = "https://corretto.aws"


class CorrettoResourceBuilder:
    def __init__(self, index_map: dict) -> None:
        self._index_map = index_map
        self._file_format = "tar.gz"

        self.operating_system: CorrettoOperatingSystem = OperatingSystem.LINUX
        self.architecure: Architecture = Architecture.X64
        self.image_type: CorrettoImageType = ImageType.JDK
        self.versrion = None

    def _get_resource(self) -> Optional[str]:
        return self._index_map_position[self._file_format]["resource"]

    def set_operating_system(
        self, operating_system: CorrettoOperatingSystem
    ) -> "CorrettoResourceBuilder":
        if operating_system == OperatingSystem.WINDOWS:
            self._file_format = "zip"
        self.operating_system = operating_system
        return self

    def set_architecture(self, architecture: Architecture) -> "CorrettoResourceBuilder":
        self.architecure = architecture
        return self

    def set_image_type(
        self, image_type: CorrettoImageType
    ) -> "CorrettoResourceBuilder":
        self.image_type = image_type
        return self

    def set_version(self, version: str) -> "CorrettoResourceBuilder":
        self.versrion = version
        return self

    def build(self, version: Optional[str] = None) -> str:
        if version is not None:
            self.versrion = version

        return self._index_map[self.operating_system.value][self.architecure.value][
            self.image_type.value
        ][self.versrion][self._file_format]["resource"]


@vendor_client(CorrettoVendor)
class CorrettoClient(Client):
    _index_map = None

    @classmethod
    def load_index_map(cls) -> Optional[Any]:
        try:
            if cls._index_map is None:
                cls._index_map = json.loads(
                    urlopen(_INDEX_MAP_URL)  # noqa: S310 Known URL
                    .read()
                    .decode("utf-8")
                )
        except Exception as e:
            raise ClientError(e) from e
        else:
            return cls._index_map

    def __init__(
        self, environment: Environment = CorrettoEnvironment.PRODUCTION
    ) -> None:
        if environment == Environment.DEFAULT:
            base_url = CorrettoEnvironment.PRODUCTION.value
        else:
            base_url = environment.value
        super().__init__(base_url)

        self._index_map = CorrettoClient.load_index_map()

    def get_download_url(
        self,
        version: str,
        operating_system: Optional[CorrettoOperatingSystem] = None,
        arch: Optional[Architecture] = None,
        impl: JvmImpl = JvmImpl.HOTSPOT,
        jre: bool = False,
        *,
        image_type: CorrettoImageType = ImageType.JDK,
    ) -> str:
        builder = CorrettoResourceBuilder(self._index_map)

        version = Client.normalize_version(version)
        builder.set_version(version)

        if operating_system is None:
            operating_system = OperatingSystem.detect()
        else:
            operating_system = CorrettoOperatingSystem.transform(operating_system)
        builder.set_operating_system(operating_system)

        if arch is None:
            arch = Architecture.detect()
        builder.set_architecture(arch)

        if image_type is None or jre:
            if jre:
                image_type = ImageType.JRE
            elif image_type is None:
                image_type = ImageType.JDK
        builder.set_image_type(image_type)
        resource = builder.build()

        return f"{self._base_url}{resource}"
