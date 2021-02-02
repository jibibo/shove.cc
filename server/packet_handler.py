from util_server import *


class PacketHandler(threading.Thread):
    def __init__(self, server):
        self.server = server
        super().__init__(name=f"PacketHandler", daemon=True)

    def run(self):
        log("Ready")

        while True:
            connection, packet = self.server.incoming_packets.get()

            try:
                self.handle(connection, packet)

            except UnknownPacketModel:
                log(f"Unknown packet model: {packet['model']}", LogLevel.WARN)
                continue

            except BaseException as ex:
                log(f"Unhandled exception on handling packet: {ex}", LogLevel.ERROR)
                continue

    def handle(self, connection, packet):
        assert "model" in packet.keys(), "no model set"

        model = packet["model"]

        if model == "join_table":
            log(packet["table_name"])
            return

        if model == "log_in":
            player = self.server.get_player(packet["username"])

            if not player:
                self.server.outgoing(connection, {
                    "model": "invalid_username"
                })
                return

            if player["password"] != packet["password"]:
                self.server.outgoing(connection, {
                    "model": "invalid_password"
                })
                return

            if player["username"] in self.server.connections_players.values():
                self.server.outgoing(connection, {
                    "model": "already_connected"
                })
                return

            self.server.outgoing(connection, {
                "model": "logged_in",
                "username": packet["username"]
            })
            return

        raise UnknownPacketModel
