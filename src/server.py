"""
HTTP Server Shell
"""

import socket
import asyncio
from urllib import parse
from os.path import exists

from threading import Thread

from src.utils.http import generate_response, validate_http_request
from src.utils.files import get_file_data, compress_data, get_file_type


def callback_template(query):
    """A template for the callback

    :param query: The query (if any)
    :type query: dict
    :return: The response
    :rtype: bytes
    """

    pass

class Server:
    """Server object
    """

    socket = None # type: socket.socket

    loop = asyncio.get_event_loop()

    ip_to_accept = "0.0.0.0"
    port = 80
    serve_dir = "./webroot"

    routes = {"/": "index.html"}

    def __init__(self, serve_dir, port=443, ip_to_accept="0.0.0.0"):
        """Creates a server object

        :param serve_dir: The directory to serve
        :type serve_dir: str
        :param port: The port to serve on, defaults to 80
        :param port: int, optional
        :param ip_to_accept: What ip to accept, defaults to "0.0.0.0" (all ips)
        :param ip_to_accept: str, optional
        """

        self.serve_dir = serve_dir
        self.port = port
        self.ip_to_accept = ip_to_accept

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.ip_to_accept, self.port))
        sock.setblocking(False)

        self.socket = sock

    def start(self):
        """Starts the server
        """

        self.socket.listen(10)

        print("Listening for connections on port %d" % self.port)

        def server_loop(loop):
            asyncio.set_event_loop(loop)
            self.loop.run_until_complete(self.handle_server())

        bg_thread = Thread(target=server_loop,
                           args=(asyncio.get_event_loop(),))
        bg_thread.start()

    def add_route_file(self, route, filename):
        """Adds a custom route to the server

        :param route: The new route (e.g. '/hi')
        :type route: str
        :param filename: The filename to go to (e.g. '/hi.html')
        :type filename: str
        """

        self.routes[route] = filename

    def add_route(self, route, callback):
        """Adds a custom route to the server

        :param route: The new route (e.g. '/hi')
        :type route: str
        :param callback: A function to run when that route is accessed
        :type callback: callback_template
        """

        self.routes[route] = callback

    def remove_route(self, route):
        """Removes a custom route from the server

        :param route: The route to remove (e.g. '/hi')
        :type route: str
        """

        if route in self.routes:
            del self.routes[route]

    async def handle_client_request(self, resource, client_socket):
        """Check the required resource, generate proper HTTP response and send to client

        :param resource: The path to the requested resource
        :type resource: str
        :param client_socket: The client socket
        :type client_socket: socket.socket
        :return: Whether to close the connection or not
        :rtype: boolean
        """

        pathname = resource.split("?")[0]
        filename = self.serve_dir + pathname

        if pathname in self.routes:
            if isinstance(self.routes[pathname], str):
                filename = f"{self.serve_dir}/{self.routes[pathname]}"
            else:
                query = dict(parse.parse_qsl(resource.split("?")[1]))
                data = self.routes[pathname](query)
                gzip_data = compress_data(data)

                # get_file_type("") -> text/plain (the default)
                http_response = generate_response("200 OK", get_file_type(""), len(gzip_data))
                http_response += gzip_data

                await self.loop.sock_sendall(client_socket, http_response)

        data = get_file_data(filename)
        gzip_data = compress_data(data)

        status = "200 OK" if exists(filename) else "404 Not Found"
        http_response = generate_response(status, get_file_type(filename), len(gzip_data))
        http_response += gzip_data

        await self.loop.sock_sendall(client_socket, http_response)

        if b"Connection: Closed" in http_response:
            return True
        return False

    async def handle_client(self, client_socket):
        """Handles client requests: verifies client"s requests are legal HTTP,
        calls function to handle the requests

        :param client_socket: The client socket
        :type client_socket: socket.socket
        """

        print("Client connected")
        while True:
            client_request = await self.loop.sock_recv(client_socket, 1024)
            valid_http, resource = validate_http_request(client_request)

            if valid_http:
                should_close = await self.handle_client_request(resource, client_socket)

                if should_close:
                    print("Client disconnected")
                    break
            else:
                break
        client_socket.close()

    @asyncio.coroutine
    async def handle_server(self):
        """Handles the server socket
        """

        while True:
            client_socket, (client_address, _) = await self.loop.sock_accept(self.socket)
            self.loop.create_task(self.handle_client(client_socket))

            print(f"New connection received from {client_address}")
