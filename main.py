"""
HTTP Server Shell
"""

from src.server import Server

IP = "0.0.0.0"
PORT = 80
DEFAULT_URL = "./webroot"

def main():
    """Open a socket and loop forever while waiting for clients
    """

    server = Server(DEFAULT_URL)
    server.start()

if __name__ == "__main__":
    # Call the main handler function
    try:
        main()
    except KeyboardInterrupt:
        pass
