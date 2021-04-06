from convenience import *

from user import User, FakeUser


def send_packets_loop(shove, sio: socketio.Server):
    """Blocking loop for sending packets (that were added to the queue)"""

    set_greenthread_name("PSender")
    Log.trace("Send packets loop ready")

    while True:
        users, model, packet, skip, is_response = shove.outgoing_packets_queue.get()

        try:
            send_packet(sio, users, model, packet, skip, is_response)

        except Exception as ex:
            Log.fatal(f"UNHANDLED {type(ex).__name__} on packet_sender.send_packet", ex)


def send_packet(sio, users, model: str, packet: dict, skip, is_response: bool):
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
            Log.trace(f"No recipients for outgoing {'response' if is_response else 'packet'} '{model}', not sending\n packet: {packet}")
            return

        Log.trace(f"Sending {'response' if is_response else 'packet'}: '{model}'")

        sids = [user.sid for user in users]
        for sid in sids:
            sio.emit(model, packet, to=sid, callback=sid_received_callback)

        Log.debug(f"Sent {'response' if is_response else 'packet'}: '{model}'\n to: {[str(user)[1:-1] for user in users]}\n packet: {packet}")

    except Exception as ex:
        Log.fatal(f"UNHANDLED {type(ex).__name__} on packet_sender.send_packet", ex)


def sid_received_callback(*args, **kwargs):
    Log.test(f"CALLBACK args={args}, kwargs={kwargs}")