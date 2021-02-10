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
                log(f"UNHANDLED {type(ex).__name__} on sending packet", LOG_ERROR, traceback_print=True)
                continue

    def send(self, connection, packet):
        packet_str = json.dumps(packet)
        header = f"{len(packet_str):<{HEADER_SIZE}}"
        connection.send(bytes(header + "test" + packet_str, encoding="utf-8"))

        log(f"Sent packet: {packet}")
