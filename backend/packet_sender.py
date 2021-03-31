from convenience import *

from user import User, FakeUser


class PacketSenderThread(threading.Thread):
    def __init__(self, shove, socketio):
        super().__init__(name="PSend", daemon=True)
        self.shove = shove
        self.socketio = socketio

    def run(self):
        Log.trace("Ready")

        while True:
            users, model, packet, skip, is_response = self.shove.outgoing_packets_queue.get()

            try:
                send_packet(self.socketio, users, model, packet, skip, is_response)

            except Exception as ex:
                Log.fatal(f"UNHANDLED {type(ex).__name__} on packet_sender.send_packet", ex)


def send_packet(socketio, users, model: str, packet: dict, skip, is_response: bool):
    try:
        if type(users) == User:
            users = [users]

        elif type(users) == list:
            if users and type(users[0]) != User:
                raise ValueError(f"'users' does not contain 'User' object(s), but: {type(users[0])}")

        elif type(users) == FakeUser:
            Log.trace("Fake user provided, ignoring")
            return

        else:
            raise ValueError(f"Invalid 'users' type: {type(users)}")

        if skip:
            if type(skip) == User:
                skip = [skip]

            elif type(skip) == list:
                if skip and type(skip[0]) != User:
                    raise ValueError(f"'skip' does not contain 'User' object(s), but: {type(users[0])}")

            else:
                raise ValueError(f"Invalid 'skip' type: {type(users)}")

            for skip_user in skip:
                users.remove(skip_user)

        if not users:
            Log.trace(f"No recipients for outgoing {'response' if is_response else 'packet'} '{model}', not queueing\n packet: {packet}")
            return

        Log.trace(f"Sending {'response' if is_response else 'packet'}: '{model}'")

        sids = [user.sid for user in users]
        for sid in sids:
            socketio.emit(model, packet, room=sid)

        Log.debug(f"Sent {'response' if is_response else 'packet'}: '{model}'\n to: {[str(user)[1:-1] for user in users]}\n packet: {packet}")

    except Exception as ex:
        Log.fatal(f"UNHANDLED {type(ex).__name__} on packet_sender.send_packet", ex)
