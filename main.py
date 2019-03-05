"""
HTTP Server Shell
"""

import socket
import asyncio
import zlib

import mmap
from os.path import exists
from email.utils import formatdate
from datetime import datetime
from time import mktime

IP = "0.0.0.0"
PORT = 80
DEFAULT_URL = "./webroot"
REDIRECTION_DICTIONARY = ""


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

    with open(filename, "rb") as file_obj:
        return mmap.mmap(file_obj.fileno(), 0, access=mmap.ACCESS_READ)


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
    if not status.startswith("404"):
        headers.append(f"Content-Length: {data_len}")
        if get_file_type(filename).startswith("text"):
            headers.append(
                f"Content-Type: {get_file_type(filename)}; charset=utf-8")
        else:
            headers.append(f"Content-Type: {get_file_type(filename)}")
    headers.append("Connection: keep-alive")

    headers.append("\r\n")

    return "\r\n".join(headers).encode()


async def handle_client_request(loop, resource, client_socket):
    """Check the required resource, generate proper HTTP response and send to client

    :param loop: The event loop
    :type loop: asyncio.BaseEventLoop
    :param resource: The path to the requested resource
    :type resource: str
    :param client_socket: The client socket
    :type client_socket: socket
    """

    filename = ""

    if resource == "/":
        filename = DEFAULT_URL + "/index.html"
    else:
        filename = DEFAULT_URL + resource

    data = get_file_data(filename)
    gzip_data = compress_data(data)

    http_response = generate_response(filename, len(gzip_data))
    http_response += gzip_data

    await loop.sock_sendall(client_socket, http_response)


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


async def handle_client(loop, client_socket):
    """Handles client requests: verifies client"s requests are legal HTTP,
    calls function to handle the requests

    :param loop: The cyrrent loop
    :type loop: asyncio.BaseEventLoop
    :param server_socket: The client socket
    :type server_socket: socket
    """

    print("Client connected")
    while True:
        client_request = await loop.sock_recv(client_socket, 1024)
        valid_http, resource = validate_http_request(client_request)

        if valid_http:
            await handle_client_request(loop, resource, client_socket)
        else:
            break
    print("Closing connection")
    client_socket.close()


async def handle_server(loop, server_socket):
    """Handles the server socket

    :param loop: The cyrrent loop
    :type loop: asyncio.BaseEventLoop
    :param server_socket: The server socket
    :type server_socket: socket
    """

    while True:
        client_socket, client_address = await loop.sock_accept(server_socket)
        loop.create_task(handle_client(loop, client_socket))

        print(f"New connection received from {client_address}")


def main():
    """Open a socket and loop forever while waiting for clients
    """

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen(10)
    server_socket.setblocking(False)

    print("Listening for connections on port %d" % PORT)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(handle_server(loop, server_socket))


if __name__ == "__main__":
    # Call the main handler function
    main()
