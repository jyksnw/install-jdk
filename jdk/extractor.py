from typing import Optional, Union, Iterable
from os import path, listdir
from tarfile import open as tarfile_open, TarFile
from lzma import open as lzma_open, LZMAFile
from zipfile import ZipFile, ZipInfo


_TAR = ".tar"
_TAR_GZ = ".tar.gz"
_ZIP = ".zip"
_SEVEN_ZIP = ".7z"


class ExtractorException(Exception):
    pass


def _is_within_directory(directory: str, target: str):
    abs_directory = path.abspath(directory)
    abs_target = path.abspath(target)

    prefix = path.commonprefix([abs_directory, abs_target])
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
            member_path = path.join(path, member.name)
            if not _is_within_directory(path, member_path):
                raise ExtractorException("Attempted Path Traversal in Archive File")
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


def extract_files(file: str, file_ending: str, destination_folder: str) -> str:
    if path.isfile(file):
        start_listing = set(listdir(destination_folder))

        if file_ending == _TAR:
            with tarfile_open(file, "r:") as tar:
                _safe_extract(tar, path=destination_folder)
        elif file_ending == _TAR_GZ:
            with tarfile_open(file, "r:gz") as tar:
                _safe_extract(tar, path=destination_folder)
        elif file_ending == _ZIP:
            with ZipFile(file) as z:
                _safe_extract(z, path=destination_folder)
        elif file_ending == _SEVEN_ZIP:
            with lzma_open(file) as z:
                _safe_extract(z, path=destination_folder)

        end_listing = set(listdir(destination_folder))
        jdk_directory = next(iter(end_listing.difference(start_listing)))

        return path.join(destination_folder, jdk_directory)
