from typing import Optional
from jdk.enums import (
    BaseEnum,
    OperatingSystem,
    Architecture,
    JvmImpl,
    ImageType,
    HeapSize,
    ReleaseType,
    Vendor,
    CLib,
    Project,
)
from .client import Client


AdoptiumJvmImpl = JvmImpl
AdoptiumVendor = Vendor


class AdoptiumEnvironment(BaseEnum):
    PRODUCTION = "https://api.adoptium.net"
    STAGE = "https://staging-api.adoptium.net"


class AdoptiumClient(Client):
    def __init__(
        self, environment: AdoptiumEnvironment = AdoptiumEnvironment.PRODUCTION
    ) -> None:
        self._base_url = environment.value

    def get_download_url(
        self,
        version: str,
        operating_system: Optional[OperatingSystem] = None,
        arch: Optional[Architecture] = None,
        impl: JvmImpl = AdoptiumJvmImpl.HOTSPOT,
        jre: bool = False,
        *,
        heap_size: HeapSize = HeapSize.NORMAL,
        image_type: ImageType = ImageType.JDK,
        release_type: ReleaseType = ReleaseType.GA,
        vendor: Vendor = AdoptiumVendor.ECLIPSE,
        c_lib: Optional[CLib] = None,
        project: Optional[Project] = None,
    ) -> str:
        version = self.normalize_version(version)

        if operating_system is None:
            operating_system = OperatingSystem.detect()

        if arch is None:
            arch = Architecture.detect()

        if jre:
            image_type = ImageType.JRE

        if c_lib:
            image_type = ImageType.STATIC_LIBS

        download_url = f"{self._base_url}/v3/binary/latest/{version}/{release_type}/{operating_system}/{arch}/{image_type}/{impl}/{heap_size}/{vendor}"
        if c_lib:
            download_url = f"{download_url}?c_lib={c_lib}"

        if project:
            download_url = (
                f"{download_url}{'&' if '?' in download_url else '?'}{project}"
            )

        return download_url
