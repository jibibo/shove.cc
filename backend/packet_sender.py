from convenience import *

from user import User


def send_packets_loop(shove, sio: socketio.Server):
    """Blocking loop for sending packets (that were added to the queue)"""

    set_greenthread_name("PacketSender")
    Log.trace("Send packets loop ready")

    while True:
        users, model, packet, skip, is_response = shove.outgoing_packets_queue.get()

        try:
            send_packet(sio, users, model, packet, skip, is_response)

        except Exception as ex:
            Log.fatal(f"UNHANDLED {type(ex).__name__} on send_packet", ex)


def send_packet(sio, users: Union[User, Set[User]], model: str, packet: dict, skip: Union[User, Set[User]], is_response: bool):
    if type(users) == User:
        users = [users]

    elif type(users) == set:
        pass

    else:
        raise ValueError(f"Invalid 'users' type: {type(users)}")

    if skip:
        if type(skip) == User:
            skip = [skip]

        elif type(skip) == set:
            pass

        else:
            raise ValueError(f"Invalid 'skip' type: {type(users)}")

        for skip_user in skip:
            users.remove(skip_user)

    if not users:
        Log.trace(f"No recipients for outgoing {'response' if is_response else 'packet'} '{model}', not sending\n packet: {packet}")
        return

    Log.trace(f"Sending {'response' if is_response else 'packet'}: '{model}'")

    for user in users:
        sio.emit(model, packet, to=user.sid)

    Log.debug(f"Sent {'response' if is_response else 'packet'}: '{model}'\n to: {[str(user)[1:-1] for user in users]}\n packet: {packet}")
