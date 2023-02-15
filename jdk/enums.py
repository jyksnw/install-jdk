from enum import Enum
from typing import Any, Optional, SupportsIndex


class BaseEnum(str, Enum):
    def __contains__(self: type[Enum], obj: object) -> bool:
        try:
            self(obj)
        except ValueError:
            return False
        else:
            return True

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Enum):
            return self.value == other.value
        return False


class BaseDetectableEnum(BaseEnum):
    @classmethod
    def detect(cls) -> Optional[Any]:
        raise NotImplementedError("detect")

    @classmethod
    def transform(cls, other: "BaseDetectableEnum") -> Optional["BaseDetectableEnum"]:
        raise NotImplementedError("transform")


class JvmImpl(BaseEnum):
    HOTSPOT = "hotspot"


Implementation = JvmImpl


class Vendor(BaseEnum):
    ECLIPSE = "eclipse"


class Architecture(BaseDetectableEnum):
    @classmethod
    def detect(cls) -> Optional["Architecture"]:
        from platform import machine

        machine_arch = machine().lower()
        if "arm" in machine_arch:
            return Architecture.ARM
        if "aarch64" in machine_arch:
            return Architecture.AARCH64
        elif machine_arch == "ppc64":
            return Architecture.PPC64
        else:
            from sys import maxsize

            if maxsize > 2**32:
                return Architecture.X64
            else:
                return Architecture.X86

    @classmethod
    def transform(cls, other: "Architecture") -> Optional["Architecture"]:
        return other

    X64 = "x64"
    X86 = "x86"
    X32 = "x32"
    PPC64 = "ppc64"
    PPC64LE = "ppc64le"
    S390X = "s390x"
    AARCH64 = "aarch64"
    ARM = "arm"
    SPARCV9 = "sparcv9"
    RISCV64 = "riscv64"


class CLib(BaseEnum):
    MUSL = "musl"
    GLIBC = "glibc"


class HeapSize(BaseEnum):
    NORMAL = "normal"
    LARGE = "large"


class ImageType(BaseEnum):
    JDK = "jdk"
    JRE = "jre"
    TEST_IMAGE = "testimage"
    DEBUG_IMAGE = "debugimage"
    STATIC_LIBS = "staticlibs"
    SOURCES = "sources"
    SBOM = "sbom"


class OperatingSystem(BaseDetectableEnum):
    @classmethod
    def detect(cls) -> Optional["OperatingSystem"]:
        from sys import platform

        if "linux" in platform:
            return OperatingSystem.LINUX
        elif "win32" in platform or "cygwin" in platform:
            return OperatingSystem.WINDOWS
        elif "darwin" in platform:
            return OperatingSystem.MAC
        elif "aix" in platform:
            return OperatingSystem.AIX

    @classmethod
    def transform(cls, other: "OperatingSystem") -> Optional["OperatingSystem"]:
        return other

    LINUX = "linux"
    WINDOWS = "windows"
    MAC = "mac"
    SOLARIS = "solaris"
    AIX = "aix"
    ALPINE_LINUX = "alpine-linux"


class ReleaseType(BaseEnum):
    GA = "ga"
    EA = "ea"


class Project(BaseEnum):
    JDK = "jdk"
    VALHALLA = "valhalla"
    METROPOLIS = "metropolis"
    JFR = "jfr"
    SHENANDOAH = "shenandoah"
