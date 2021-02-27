from server_util import *
from player import Player


class PacketHandlerThread(threading.Thread):
    def __init__(self, server):
        self.server = server
        self.packets_handled = 0
        super().__init__(name=f"PacketHandler", daemon=True)

    def run(self):
        Log.debug("Ready")

        while True:
            client, packet = self.server.received_client_packets.get()

            try:
                self.packets_handled += 1
                Log.trace(f"Handling packet #{self.packets_handled}: {packet}")
                response_packet = self.handle_packet(client, packet)

                if response_packet:
                    self.server.outgoing_client_packets.put((client, response_packet))

            except InvalidPacket as ex:
                Log.error(f"Invalid packet handled: {ex.details}", ex)
                continue

            except Exception as ex:
                Log.fatal(f"UNHANDLED {type(ex).__name__} on handling packet", ex)
                continue

    @staticmethod
    def handle_packet(connected_client, packet) -> dict:
        if "model" not in packet.keys():
            raise InvalidPacket(f"No model set")

        model = packet["model"]

        if model == "join_table":  # todo implement
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
