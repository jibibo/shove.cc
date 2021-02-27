from server_util import *


class PacketSenderThread(threading.Thread):
    def __init__(self, server):
        self.server = server
        super().__init__(name="PacketSenderThread", daemon=True)

    def run(self):
        Log.debug("Ready")

        while True:
            client, packet = self.server.outgoing_client_packets.get()

            try:
                self.send(client, packet)

            except Exception as ex:
                Log.fatal(f"UNHANDLED {type(ex).__name__} on sending packet", ex)
                continue

    @staticmethod
    def send(connected_client, packet):
        packet_str = json.dumps(packet)
        header = f"{len(packet_str):<{HEADER_SIZE}}"
        connected_client.connection.send(bytes(header + "test" + packet_str, encoding="utf-8"))
        Log.debug(f"Sent packet: {packet}")
