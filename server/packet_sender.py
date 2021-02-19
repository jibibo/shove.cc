from server_util import *


class PacketSender(threading.Thread):
    def __init__(self, server):
        self.server = server
        super().__init__(name="PacketSender", daemon=True)

    def run(self):
        log("Ready")

        while True:
            client, packet = self.server.outgoing_client_packets.get()

            try:
                self.send(client, packet)

            except Exception as ex:
                log(f"UNHANDLED {type(ex).__name__} on sending packet", LOG_ERROR, ex)
                continue

    @staticmethod
    def send(connected_client, packet):
        packet_str = json.dumps(packet)
        header = f"{len(packet_str):<{HEADER_SIZE}}"
        connected_client.connection.send(bytes(header + "test" + packet_str, encoding="utf-8"))
        log(f"Sent packet: {packet}")
