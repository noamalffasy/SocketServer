"""
HTTP Server Shell
"""

import socket
import asyncio

from threading import Thread

from src.utils.http import generate_response, validate_http_request
from src.utils.files import get_file_data, compress_data


class Server:
    """Server object
    """

    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    loop = asyncio.get_event_loop()

    ip_to_accept = "0.0.0.0"
    port = 80
    serve_dir = "./webroot"

    routes = {"/": "index.html"}

    def __init__(self, serve_dir, port=80, ip_to_accept="0.0.0.0"):
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

        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.ip_to_accept, self.port))
        self.socket.setblocking(False)

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

    def add_route(self, route, filename):
        """Adds a custom route to the server

        :param route: The new route (e.g. '/hi')
        :type route: str
        :param filename: The filename to go to (e.g. '/hi.html')
        :type filename: str
        """

        self.routes[route] = filename

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
        :type client_socket: socket
        """

        filename = self.serve_dir + resource

        if resource in self.routes:
            filename = f"{self.serve_dir}/{self.routes[resource]}"

        data = get_file_data(filename)
        gzip_data = compress_data(data)

        http_response = generate_response(filename, len(gzip_data))
        http_response += gzip_data

        await self.loop.sock_sendall(client_socket, http_response)

    async def handle_client(self, client_socket):
        """Handles client requests: verifies client"s requests are legal HTTP,
        calls function to handle the requests

        :param client_socket: The client socket
        :type client_socket: socket
        """

        print("Client connected")
        while True:
            client_request = await self.loop.sock_recv(client_socket, 1024)
            valid_http, resource = validate_http_request(client_request)

            if valid_http:
                await self.handle_client_request(resource, client_socket)
            else:
                break
        print("Closing connection")
        client_socket.close()

    @asyncio.coroutine
    async def handle_server(self):
        """Handles the server socket
        """

        while True:
            client_socket, (client_address, _) = await self.loop.sock_accept(self.socket)
            self.loop.create_task(self.handle_client(client_socket))

            print(f"New connection received from {client_address}")
