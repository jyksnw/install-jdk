from contextlib import closing
from lzma import LZMAFile
from lzma import open as lzma_open
from os import listdir
from os import path as ospath
from os import stat
from tarfile import TarFile
from tarfile import open as tarfile_open
from typing import Iterable
from typing import Optional
from typing import Union
from zipfile import ZipFile
from zipfile import ZipInfo


_TAR = ".tar"
_TAR_GZ = ".tar.gz"
_ZIP = ".zip"
_SEVEN_ZIP = ".7z"


class ExtractorError(Exception):
    pass


def _is_within_directory(directory: str, target: str):
    abs_directory = ospath.abspath(directory)
    abs_target = ospath.abspath(target)

    prefix = ospath.commonprefix([abs_directory, abs_target])
    return prefix == abs_directory


def _safe_extract(
    tar: Union[TarFile, ZipFile, LZMAFile],
    path: Optional[str] = None,
    members: Optional[Iterable[Union[str, ZipInfo]]] = None,
    *,
    numeric_owner: bool = False,
):
    if isinstance(tar, ZipFile):
        tar.extractall(path)
    else:
        for member in tar.getmembers():
            member_path = ospath.join(path, member.name)
            if not _is_within_directory(path, member_path):
                raise ExtractorError("Attempted Path Traversal in Archive File")
        tar.extractall(path, members, numeric_owner=numeric_owner)


def get_compressed_file_ext(file: str) -> str:
    if file.endswith(_TAR):
        return _TAR
    elif file.endswith(_TAR_GZ):
        return _TAR_GZ
    elif file.endswith(_ZIP):
        return _ZIP
    else:
        return _SEVEN_ZIP


def extract_files(
    file: str, file_ending: str, destination_folder: str
) -> Optional[str]:
    if ospath.isfile(file):
        if file_ending == _TAR:
            with tarfile_open(file, "r:") as tar:
                _safe_extract(tar, path=destination_folder)
        elif file_ending == _TAR_GZ:
            with tarfile_open(file, "r:gz") as tar:
                _safe_extract(tar, path=destination_folder)
        elif file_ending == _ZIP:
            with closing(ZipFile(file)) as z:
                _safe_extract(z, path=destination_folder)
        elif file_ending == _SEVEN_ZIP:
            with lzma_open(file) as z:
                _safe_extract(z, path=destination_folder)

        jdk_directory = max(
            listdir(destination_folder),
            key=lambda d: stat(ospath.join(destination_folder, d)).st_ctime,
        )
        return ospath.join(destination_folder, jdk_directory)
