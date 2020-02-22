"""
HTTP Server Shell
"""

from src.server import Server

IP = "0.0.0.0"
PORT = 80
DEFAULT_URL = "./webroot"

def calculate_area(query):
    height = int(query["height"])
    width = int(query["width"])

    return str(height * width / 2).encode()

def calculate_next(query):
    num = int(query["num"])

    return str(num + 1).encode()

def main():
    """Open a socket and loop forever while waiting for clients
    """

    server = Server(DEFAULT_URL, PORT)
    server.start()

    server.add_route("/calculate-area", calculate_area)
    server.add_route("/calculate-next", calculate_next)

if __name__ == "__main__":
    # Call the main handler function
    try:
        main()
    except KeyboardInterrupt:
        pass
