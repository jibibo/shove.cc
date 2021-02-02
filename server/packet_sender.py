from util_server import *


class PacketSender(threading.Thread):
    def __init__(self, server):
        self.server = server
        super().__init__(name="PacketSender", daemon=True)

    def run(self):
        log("Ready")

        while True:
            connection, packet = self.server.outgoing_packets.get()

            try:
                self.send(connection, packet)

            except BaseException as ex:
                log(f"Unhandled exception on handling packet: {ex}", LogLevel.ERROR)
                continue

    def send(self, connection, packet):
        packet_str = json.dumps(packet)
        header = f"{len(packet_str):<{HEADER_SIZE}}"

        connection.send(bytes(header + packet_str, encoding="utf-8"))
        log(f"Sent packet: {packet}")
