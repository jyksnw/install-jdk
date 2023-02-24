import json
from typing import List
from typing import Optional
from typing import Union
from urllib.parse import urlencode
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


@extends(OperatingSystem)
class ZuluOperatingSystem(BaseDetectableEnum):
    @classmethod
    def detect(cls) -> Optional["ZuluOperatingSystem"]:
        operating_system = OperatingSystem.detect()
        return cls.transform(operating_system)

    @classmethod
    def transform(cls, other: OperatingSystem) -> Optional["ZuluOperatingSystem"]:
        if other == OperatingSystem.MAC:
            return ZuluOperatingSystem.MACOS
        return ZuluOperatingSystem(other.value)

    MACOS = "macos"
    QNX = "qnx"


@extends(Architecture)
class ZuluArchitecture(BaseDetectableEnum):
    @classmethod
    def detect(cls) -> Optional["ZuluArchitecture"]:
        arch = Architecture.detect()
        return cls.transform(arch)

    @classmethod
    def transform(cls, other: Architecture) -> Optional["ZuluArchitecture"]:
        if other == Architecture.X64:
            return ZuluArchitecture(Architecture.X86.value)
        return ZuluArchitecture(other.value)

    MIPS = "mips"
    PPC = "ppc"
    SPARCV9 = "sparcv9"


class ZuluBitness(BaseDetectableEnum):
    @classmethod
    def detect(cls) -> Optional["ZuluBitness"]:
        from sys import maxsize

        if maxsize > 2**32:
            return ZuluBitness.BITS_64
        else:
            return ZuluBitness.BITS_32

    @classmethod
    def transform(cls, other: "ZuluBitness") -> Optional["ZuluBitness"]:
        return other

    BITS_64 = "64"
    BITS_32 = "32"


class ZuluFloatingPointABI(BaseEnum):
    SOFT_FLOAT = "soft_float"
    HARD_FLOAT = "hard_float"


class ZuluExtension(BaseDetectableEnum):
    @classmethod
    def detect(cls) -> Optional["ZuluExtension"]:
        operating_system = ZuluOperatingSystem.detect()
        if operating_system == ZuluOperatingSystem.WINDOWS:
            return ZuluExtension.ZIP
        else:
            return ZuluExtension.TAR_GZ

    TAR_GZ = "tar.gz"
    ZIP = "zip"


@extends(ImageType)
class ZuluImageType(BaseEnum):
    pass


class ZuluReleaseType(BaseEnum):
    GA = "ga"
    EA = "ea"
    BOTH = "both"


class ZuluSupportTerm(BaseEnum):
    LTS = "lts"
    MTS = "mts"
    STS = "sts"


class ZuluFeature(BaseEnum):
    CP3 = "cp3"
    FX = "fx"
    HEADFUL = "headful"
    HEADFULL = "headfull"
    HEADLESS = "headless"
    JDK = "jdk"


@extends(Environment)
class ZuluEnvironment(BaseEnum):
    PRODUCTION = "https://api.azul.com/zulu/download/community/v1.0"


@extends(Vendor)
class ZuluVendor(BaseEnum):
    ZULU = "zulu"
    AZUL = "azul"


@vendor_client(ZuluVendor)
class ZuluClient(Client):
    def __init__(self, environment: Environment = ZuluEnvironment.PRODUCTION) -> None:
        if environment == Environment.DEFAULT:
            base_url = ZuluEnvironment.PRODUCTION.value
        else:
            base_url = environment.value
        super().__init__(base_url)

    def get_download_url(
        self,
        version: str,
        operating_system: Optional[ZuluOperatingSystem] = None,
        arch: Optional[ZuluArchitecture] = None,
        impl: JvmImpl = JvmImpl.HOTSPOT,
        jre: bool = False,
        *,
        zulu_version: Optional[str] = None,
        hw_bitness: Optional[ZuluBitness] = ZuluBitness.BITS_64,
        abi: Optional[ZuluFloatingPointABI] = None,
        javafx: bool = False,
        release_type: Optional[ZuluReleaseType] = ZuluReleaseType.GA,
        support_term: Optional[ZuluSupportTerm] = ZuluSupportTerm.LTS,
        features: Optional[List[Union[ZuluFeature, str]]] = [ZuluFeature.JDK],
    ) -> str:
        version = Client.normalize_version(version)

        if operating_system is None:
            operating_system = ZuluOperatingSystem.detect()

        if arch is None:
            arch = ZuluArchitecture.detect()

        if jre:
            image_type = ImageType.JRE
        else:
            image_type = ImageType.JDK

        if not hw_bitness:
            hw_bitness = ZuluBitness.detect()

        if abi and operating_system != ZuluOperatingSystem.ARM:
            abi = None

        params = dict()
        params["jdk_version"] = f"{version}.0" if ".0" not in version else version
        if zulu_version:
            params["zulu_version"] = zulu_version
        params["os"] = operating_system.value
        params["arch"] = arch.value
        params["hw_bitness"] = hw_bitness
        if arch == ZuluArchitecture.ARM and hw_bitness == ZuluBitness.BITS_32 and abi:
            params["abi"] = abi.value
        params["ext"] = str(ZuluExtension.detect())
        params["bundle_type"] = image_type.value
        params["javafx"] = javafx
        params["support_term"] = support_term if support_term else ZuluSupportTerm.LTS
        params["features"] = ",".join([str(feature).lower() for feature in features])

        qry_str = urlencode(params)
        qry_url = f"{self._base_url}/bundles/latest/?{qry_str}"

        try:
            data = json.loads(
                urlopen(qry_url).read().decode("utf-8")  # noqa: S310 Known URL
            )
        except Exception as e:
            raise ClientError(e) from e
        else:
            if data and "url" in data:
                return data["url"]
