from typing import Optional

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
from .client import vendor_client


@extends(Architecture)
class AdoptiumArchitecture(BaseDetectableEnum):
    @classmethod
    def detect(cls) -> Optional["AdoptiumArchitecture"]:
        return Architecture.detect()

    @classmethod
    def transform(cls, other: Architecture) -> Optional["AdoptiumArchitecture"]:
        return AdoptiumArchitecture(other.value)

    X32 = "x32"
    PPC64LE = "ppc64le"
    S390X = "s390x"
    SPARCV9 = "sparcv9"
    RISCV64 = "riscv64"


class CLib(BaseEnum):
    MUSL = "musl"
    GLIBC = "glibc"


class HeapSize(BaseEnum):
    NORMAL = "normal"
    LARGE = "large"


class ReleaseType(BaseEnum):
    GA = "ga"
    EA = "ea"


class Project(BaseEnum):
    JDK = "jdk"
    VALHALLA = "valhalla"
    METROPOLIS = "metropolis"
    JFR = "jfr"
    SHENANDOAH = "shenandoah"


@extends(ImageType)
class AdoptiumImageType(BaseEnum):
    TEST_IMAGE = "testimage"
    DEBUG_IMAGE = "debugimage"
    STATIC_LIBS = "staticlibs"
    SOURCES = "sources"
    SBOM = "sbom"


@extends(Vendor)
class AdoptiumVendor(BaseEnum):
    ADOPTIUM = "Adoptium"
    TEMURIN = "Temurin"
    ADOPTOPENJDK = "AdoptOpenJDK"
    ECLIPSE = "eclipse"


@extends(Environment)
class AdoptiumEnvironment(BaseEnum):
    PRODUCTION = "https://api.adoptium.net"
    STAGE = "https://staging-api.adoptium.net"


@vendor_client(AdoptiumVendor)
class AdoptiumClient(Client):
    def __init__(
        self, environment: Environment = AdoptiumEnvironment.PRODUCTION
    ) -> None:
        if environment == Environment.DEFAULT:
            base_url = AdoptiumEnvironment.PRODUCTION.value
        else:
            base_url = environment.value
        super().__init__(base_url)

    def get_download_url(
        self,
        version: str,
        operating_system: Optional[OperatingSystem] = None,
        arch: Optional[Architecture] = None,
        impl: JvmImpl = JvmImpl.HOTSPOT,
        jre: bool = False,
        *,
        heap_size: HeapSize = HeapSize.NORMAL,
        image_type: ImageType = ImageType.JDK,
        release_type: ReleaseType = ReleaseType.GA,
        vendor: Vendor = AdoptiumVendor.ECLIPSE,
        c_lib: Optional[CLib] = None,
        project: Optional[Project] = None,
    ) -> str:
        version = Client.normalize_version(version)

        if operating_system is None:
            operating_system = OperatingSystem.detect()

        if arch is None:
            arch = Architecture.detect()
        arch = AdoptiumArchitecture.transform(arch)

        # Handle edge case for MacOS w/Apple M1 or M2
        if operating_system is OperatingSystem.MAC and arch == AdoptiumArchitecture.ARM:
            arch = AdoptiumArchitecture.AARCH64

        if jre:
            image_type = ImageType.JRE

        if c_lib:
            image_type = AdoptiumImageType.STATIC_LIBS

        base_url = self._base_url
        download_url = f"{base_url}/v3/binary/latest/{version}/{release_type}/{operating_system}/{arch}/{image_type}/{impl}/{heap_size}/{vendor}"  # noqa: B950
        if c_lib:
            download_url = f"{download_url}?c_lib={c_lib}"

        if project:
            download_url = (
                f"{download_url}{'&' if '?' in download_url else '?'}{project}"
            )

        return download_url
