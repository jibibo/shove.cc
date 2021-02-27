from server_util import *
from player import Player


class PacketHandler(threading.Thread):
    def __init__(self, server):
        self.server = server
        self.packets_handled = 0
        super().__init__(name=f"PackHand", daemon=True)

    def run(self):
        log("Ready")

        while True:
            client, packet = self.server.received_client_packets.get()

            try:
                self.packets_handled += 1
                log(f"Handling packet #{self.packets_handled}... {packet}")
                response_packet = self.handle_packet(client, packet)

                if response_packet:
                    self.server.outgoing_client_packets.put((client, response_packet))

            except InvalidPacket as ex:
                log(f"Invalid packet handled: {ex.details}", LOG_WARN, ex)
                continue

            except Exception as ex:
                log(f"UNHANDLED {type(ex).__name__} on handling packet", LOG_ERROR, ex)
                continue

    @staticmethod
    def handle_packet(connected_client, packet) -> dict:
        if "model" not in packet.keys():
            raise InvalidPacket(f"No model set")

        model = packet["model"]

        if model == "join_table":
            log("todo")
            return {}

        if model == "log_in":
            # player = self.server.get_player(packet["username"])
            #
            # if not player:
            #     return {
            #         "model": "error",
            #         "details": "invalid username"
            #     }
            #
            # if player["password"] != packet["password"]:
            #     return {
            #         "model": "error",
            #         "details": "invalid password"
            #     }

            player = Player.create_from_username(packet["username"])
            connected_client.logged_in(player)

            return {
                "model": "logged_in",
                "username": packet["username"]
            }

        raise InvalidPacket(f"Invalid model")
