from util_server import *
from client_listener import ClientListener


class ConnectionAcceptor(threading.Thread):
    def __init__(self, server):
        self.server = server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((SERVER_HOST, SERVER_PORT))
        super().__init__(name=f"ConnectionAcceptor", daemon=True)

    def run(self):
        log(f"Started on {SERVER_HOST}:{SERVER_PORT}", LogLevel.INFO)
        self.socket.listen(SERVER_BACKLOG)

        while True:
            connection, address = self.socket.accept()
            log(f"{address[0]}:{address[1]} connected")
            client_listener = ClientListener(self.server, connection, address)
            client_listener.start()
            self.server.client_listeners.append(client_listener)
