"""
Module for HTTP utils
"""

from email.utils import formatdate
from datetime import datetime
from os.path import exists
from time import mktime

from src.utils.files import get_file_type

def generate_response(filename, data_len):
    """Generates the response headers

    :param filename: The file's name and path
    :type filename: str
    :return: The response headers
    :rtype: bytes
    """

    headers = []
    date = formatdate(timeval=mktime(
        datetime.now().timetuple()), localtime=False, usegmt=True)

    status = "200 OK" if exists(filename) else "404 Not Found"

    headers.append(f"HTTP/1.1 {status}")
    headers.append(f"Date: {date}")
    headers.append(f"Server: NoamServer/0.0.0")
    headers.append("Content-Encoding: gzip")
    headers.append(f"Content-Length: {data_len}")
    if get_file_type(filename).startswith("text"):
        headers.append(
            f"Content-Type: {get_file_type(filename)}; charset=utf-8")
    else:
        headers.append(f"Content-Type: {get_file_type(filename)}")
    if not status.startswith("404"):
        headers.append("Connection: keep-alive")
    else:
        headers.append("Connection: Closed")

    headers.append("\r\n")

    return "\r\n".join(headers).encode()


def validate_http_request(request):
    """Check if request is a valid HTTP request and returns TRUE / FALSE and the requested URL

    :param request: The HTTP Request
    :type request: bytes
    :return: valid
    :rtype: bytes
    """

    # GET / HTTP/1.1
    # Host: 127.0.0.1
    # User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0
    # Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    # Accept-Language: en-US,en;q=0.5
    # Accept-Encoding: gzip, deflate
    # DNT: 1
    # Connection: keep-alive
    # Upgrade-Insecure-Requests: 1
    #
    #

    headers = [header for header in request.decode().split("\r\n")]

    if len(headers[0].split(" ")) == 3:
        basic_request_header = headers[0].split(" ")
        return True, basic_request_header[1]
    return False, None
