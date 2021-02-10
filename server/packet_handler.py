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
                log(f"Handled packet: {packet}")

            except InvalidPacket as ex:
                log(f"Invalid packet", LOG_WARN, traceback_print=True)
                continue

            except BaseException as ex:
                log(f"UNHANDLED {type(ex).__name__} on handling packet", LOG_ERROR, traceback_print=True)
                continue

    def handle(self, connection, packet):
        if "model" not in packet.keys():
            raise InvalidPacket(f"No model set")

        model = packet["model"]

        if model == "join_table":
            log(packet["table_name"])
            return

        if model == "log_in":
            player = self.server.get_player(packet["username"])

            if not player:
                self.server.send_single(connection, {
                    "model": "invalid_username"
                })
                return

            if player["password"] != packet["password"]:
                self.server.send_single(connection, {
                    "model": "invalid_password"
                })
                return

            if player["username"] in self.server.connections_players.values():
                self.server.send_single(connection, {
                    "model": "already_connected"
                })
                return

            self.server.connections_players[connection] = player
            self.server.send_single(connection, {
                "model": "logged_in",
                "username": packet["username"]
            })
            return

        raise InvalidPacket(f"Invalid model: {model}")
