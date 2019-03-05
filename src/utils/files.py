"""
Module for file utils
"""

import zlib
import mmap

def compress_data(data):
    """Gzip data

    :param data: The data to compress
    :type data: bytes
    :return: The compressed data
    :rtype: bytes
    """

    z_obj = zlib.compressobj(-1, zlib.DEFLATED, 31)
    return z_obj.compress(data) + z_obj.flush()


def get_file_type(filename):
    """Get type of file

    :param filename: The file name
    :type filename: str
    :return: The file's type
    :rtype: str
    """

    file_ext = filename.split(".")[-1]
    img_ext = ["jpeg", "png", "gif", "tiff"]
    txt_ext = ["css", "csv", "html", "xml"]

    file_type = "text/plain"

    if file_ext == "jpg":
        file_type = "image/jpeg"
    if file_ext == "ico":
        file_type = "image/x-icon"
    if file_ext == "svg":
        file_type = "image/svg+xml"
    if file_ext in img_ext:
        file_type = f"image/{file_ext}"
    if file_ext == "js":
        file_type = "application/javascript"
    if file_ext in txt_ext:
        file_type = f"text/{file_ext}"
    return file_type


def get_file_data(filename):
    """Get data from file

    :param filename: The file name
    :type filename: str
    :return: The file's data
    :rtype: str
    """

    try:
        with open(filename, "rb") as file_obj:
            return mmap.mmap(file_obj.fileno(), 0, access=mmap.ACCESS_READ)
    except FileNotFoundError:
        return b"Not Found"
