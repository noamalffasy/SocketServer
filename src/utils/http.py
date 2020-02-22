"""
Module for HTTP utils
"""

from email.utils import formatdate
from datetime import datetime
from time import mktime

def generate_response(status, content_type, data_len):
    """Generates the response headers

    :param status: The status code to send (e.g. 200 OK)
    :type status: str
    :param content_type: The file's content type
    :type content_type: str
    :param data_len: The file's length
    :type data_len: str
    :return: The response headers
    :rtype: bytes
    """

    headers = []
    date = formatdate(timeval=mktime(
        datetime.now().timetuple()), localtime=False, usegmt=True)

    headers.append(f"HTTP/1.0 {status}")
    headers.append(f"Date: {date}")
    headers.append(f"Server: NoamServer/0.0.0")
    headers.append("Content-Encoding: gzip")
    headers.append(f"Content-Length: {data_len}")
    if content_type.startswith("text"):
        headers.append(
            f"Content-Type: {content_type}; charset=utf-8")
    else:
        headers.append(f"Content-Type: {content_type}")
    if not status.startswith("404"):
        headers.append("Connection: keep-alive")
    else:
        headers.append("Connection: Closed")

    headers.append("\r\n")

    return "\r\n".join(headers).encode()


def validate_http_request(request):
    """Check if request is a valid HTTP request and returns True or False along with the requested URL

    :param request: The HTTP Request
    :type request: bytes
    :return: Whether the request is valid or not and the requested path
    :rtype: tuple
    """

    headers = [header for header in request.decode().split("\r\n")]
    basic_info = headers[0].split(" ")

    if basic_info[0] == "GET" and basic_info[1].startswith("/") and basic_info[2] == "HTTP/1.1":
        return True, basic_info[1]
    return False, None
