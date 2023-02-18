import os
import shutil
from collections import namedtuple
from os import path
from subprocess import run  # noqa: S404 Security implication noted and mitigated
from typing import Union

from jdk import extractor
from jdk.client import load_client
from jdk.enums import Architecture
from jdk.enums import Implementation
from jdk.enums import OperatingSystem
from jdk.enums import Vendor


_USER_DIR = path.expanduser("~")
_JRE_DIR = path.join(_USER_DIR, ".jre")
_JDK_DIR = path.join(_USER_DIR, ".jdk")

OS = OperatingSystem.detect()
ARCH = Architecture.detect()

_IS_WINDOWS = OS == OperatingSystem.WINDOWS
_UNPACK200 = "unpack200.exe" if _IS_WINDOWS else "unpack200"
_UNPACK200_ARGS = '-r -v -l ""' if _IS_WINDOWS else ""


_Path = namedtuple("_Path", "dir base name ext")


def _path_parse(file_path: str) -> _Path:
    dirname = path.dirname(file_path)
    base = path.basename(file_path)
    name, ext = path.splitext(base)
    return _Path(dir=dirname, base=base, name=name, ext=ext)


def _unpack_jars(fs_path: str, java_bin_path: str) -> None:
    if path.exists(fs_path):
        if path.isdir(fs_path):
            for f in os.listdir(fs_path):
                current_path = path.join(fs_path, f)
                _unpack_jars(current_path, java_bin_path)
        else:
            _, file_ext = path.splitext(fs_path)
            if file_ext.endswith("pack"):
                p = _path_parse(fs_path)
                name = path.join(p.dir, p.name)
                tool_path = path.join(java_bin_path, _UNPACK200)
                run(  # noqa: S603 Known arguments being passed into run
                    [tool_path, _UNPACK200_ARGS, f"{name}.pack", f"{name}.jar"]
                )


def _decompress_archive(
    repo_root: str, file_ending: str, destination_folder: str
) -> str:
    if not path.exists(destination_folder):
        os.mkdir(destination_folder)

    jdk_file = path.normpath(repo_root)

    if path.isfile(jdk_file):
        jdk_directory = extractor.extract_files(
            jdk_file, file_ending, destination_folder
        )
        jdk_bin = path.join(jdk_directory, "bin")
        _unpack_jars(jdk_directory, jdk_bin)

        return jdk_directory
    elif path.isdir(jdk_file):
        return jdk_file


def install(
    version: str,
    operating_system: str = OS,
    arch: str = ARCH,
    impl: str = Implementation.HOTSPOT,
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
    except BaseException as e:
        raise e
    finally:
        if jdk_file:
            os.remove(jdk_file)


def uninstall(version: str, jre: bool = False):
    version = f"jdk{version}"
    if jre:
        versions = (v for v in os.listdir(_JRE_DIR) if version in v.replace("-", ""))
        for v in versions:
            shutil.rmtree(path.join(_JRE_DIR, v))
    else:
        versions = (v for v in os.listdir(_JDK_DIR) if version in v.replace("-", ""))
        for v in versions:
            shutil.rmtree(path.join(_JDK_DIR, v))
