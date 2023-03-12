import os
import shutil
from collections import namedtuple
from os import path as ospath
from subprocess import run  # noqa: S404 Security implication noted and mitigated
from typing import Optional
from typing import Union

from jdk import extractor
from jdk.client import load_client
from jdk.enums import Architecture
from jdk.enums import JvmImpl
from jdk.enums import OperatingSystem
from jdk.enums import Vendor
from jdk.extension import deprecated


_USER_DIR = ospath.expanduser("~")
_JRE_DIR = ospath.join(_USER_DIR, ".jre")
_JDK_DIR = ospath.join(_USER_DIR, ".jdk")

OS = OperatingSystem.detect()
ARCH = Architecture.detect()

_IS_WINDOWS = OS == OperatingSystem.WINDOWS
_UNPACK200 = "unpack200.exe" if _IS_WINDOWS else "unpack200"
_UNPACK200_ARGS = '-r -v -l ""' if _IS_WINDOWS else ""


_Path = namedtuple("_Path", "dir base name ext")


class JdkError(Exception):
    pass


def _path_parse(file_path: str) -> _Path:
    dirname = ospath.dirname(file_path)
    base = ospath.basename(file_path)
    name, ext = ospath.splitext(base)
    return _Path(dir=dirname, base=base, name=name, ext=ext)


def _unpack_jars(fs_path: str, java_bin_path: str) -> None:
    if ospath.exists(fs_path):
        if ospath.isdir(fs_path):
            for f in os.listdir(fs_path):
                current_path = ospath.join(fs_path, f)
                _unpack_jars(current_path, java_bin_path)
        else:
            _, file_ext = ospath.splitext(fs_path)
            if file_ext.endswith("pack"):
                p = _path_parse(fs_path)
                name = ospath.join(p.dir, p.name)
                tool_path = ospath.join(java_bin_path, _UNPACK200)
                run(  # noqa: S603 Known arguments being passed into run
                    [tool_path, _UNPACK200_ARGS, f"{name}.pack", f"{name}.jar"]
                )


def _decompress_archive(
    repo_root: str, file_ending: str, destination_folder: str
) -> str:
    if not ospath.exists(destination_folder):
        os.mkdir(destination_folder)

    jdk_file = ospath.normpath(repo_root)

    if ospath.isfile(jdk_file):
        jdk_directory = extractor.extract_files(
            jdk_file, file_ending, destination_folder
        )
        jdk_bin = ospath.join(jdk_directory, "bin")
        _unpack_jars(jdk_directory, jdk_bin)

        return jdk_directory
    elif ospath.isdir(jdk_file):
        return jdk_file


def install(
    version: str,
    operating_system: Union[OperatingSystem, str] = OS,
    arch: Union[Architecture, str] = ARCH,
    impl: Union[JvmImpl, str] = JvmImpl.HOTSPOT,
    jre: bool = False,
    path: str = None,
    *,
    vendor: Union[Vendor, str] = "Adoptium",
) -> str:
    jdk_client = load_client(vendor)()

    url = jdk_client.get_download_url(version, operating_system, arch, impl, jre)

    if not path:
        path = _JRE_DIR if jre else _JDK_DIR

    jdk_file = None
    try:
        jdk_file = jdk_client.download(url)
        jdk_ext = extractor.get_compressed_file_ext(jdk_file)
        jdk_dir = _decompress_archive(jdk_file, jdk_ext, path)
        return jdk_dir
    except Exception as e:
        raise JdkError(e) from e
    finally:
        if jdk_file:
            os.remove(jdk_file)


@deprecated(
    "Manually delete from the .jre or .jdk directory. Will be removed in a future version"
)
def uninstall(version: str, jre: bool = False):
    version = f"jdk{version}"
    if jre:
        versions = (v for v in os.listdir(_JRE_DIR) if version in v.replace("-", ""))
        for v in versions:
            shutil.rmtree(ospath.join(_JRE_DIR, v))
    else:
        versions = (v for v in os.listdir(_JDK_DIR) if version in v.replace("-", ""))
        for v in versions:
            shutil.rmtree(ospath.join(_JDK_DIR, v))


def get_download_url(
    version: str,
    operating_system: Union[OperatingSystem, str] = OS,
    arch: Union[Architecture, str] = ARCH,
    impl: Union[JvmImpl, str] = JvmImpl.HOTSPOT,
    jre: bool = False,
    *,
    vendor: Union[Vendor, str] = "Adoptium",
) -> Optional[str]:
    jdk_client = load_client(vendor)()
    return jdk_client.get_download_url(version, operating_system, arch, impl, jre)


def download(
    download_url: Optional[str] = None,
    *,
    version: str,
    operating_system: Union[OperatingSystem, str] = OS,
    arch: Union[Architecture, str] = ARCH,
    impl: Union[JvmImpl, str] = JvmImpl.HOTSPOT,
    jre: bool = False,
    vendor: Union[Vendor, str] = "Adoptium",
) -> Optional[str]:
    jdk_client = load_client(vendor)()

    if not download_url:
        download_url = jdk_client.get_download_url(
            version, operating_system, arch, impl, jre
        )
    return jdk_client.download(download_url)
