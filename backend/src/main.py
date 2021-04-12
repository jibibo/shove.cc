import eventlet
eventlet.monkey_patch()  # required to patch modules for using threads with socketio

from convenience import *

from shove import Shove
from packet_sender import send_packets_loop
from packet_handler import handle_packets_loop
from user_pinger import ping_users_loop

set_greenlet_name("Main")

sio = socketio.Server(
    logger=LOG_SOCKETIO,
    async_mode="eventlet",
    cors_allowed_origins="*",
    engineio_logger=LOG_ENGINEIO
)
shove: Union[Shove, None] = None  # Union -> for editor (pycharm) type hint detection

# time.sleep() should be patched by eventlet.monkey_patch(), no need to use eventlet.sleep()
# -> https://stackoverflow.com/a/25315314/13216113


# SocketIO handlers

@sio.on("connect")
def on_connect(sid: str, environ: dict):
    set_greenlet_name("SIO/connect")
    Log.trace(f"Handling connect of SID '{sid}', environ: {environ}", cutoff=True)
    user = shove.on_connect(sid)
    Log.info(f"{user} connected from {environ['REMOTE_ADDR']}")


@sio.on("disconnect")
def on_disconnect(sid: str):
    set_greenlet_name("SIO/disconnect")
    user = shove.get_user_by_sid(sid)
    if not user:
        Log.warn(f"socketio.on('disconnect'): User object not found/already disconnected, ignoring call")
        return

    Log.trace(f"Handling disconnect of {user}")
    shove.on_disconnect(user)
    Log.info(f"{user} disconnected")


# todo on connect, receive session cookie from user, check if session token valid, log in as that _account
@sio.on("message")
def on_message(sid: str, model: str, packet: Optional[dict]):
    set_greenlet_name("SIO/message")
    user = shove.get_user_by_sid(sid)
    if not user:
        Log.warn(f"socketio.on('message') (model '{model}'): User object not found/already disconnected, sending no_pong packet to SID {sid}")
        sio.emit("error", error_packet("You don't exist anymore (not good), refresh!"), to=sid)
        return

    # todo check if packet is >1MB here!

    packet_id = shove.get_next_packet_id()
    Log.trace(f"Received packet #{packet_id} from {user}")
    shove.incoming_packets_queue.put((user, model, packet, packet_id))


# main function

def main():
    print("\n\n\t\"Hey Vsauce, Michael here.\" - Michael Stevens\n\n")

    eventlet.spawn(Log.write_file_loop)
    global shove
    shove = Shove(sio)
    eventlet.spawn(send_packets_loop, shove, sio)
    eventlet.spawn(handle_packets_loop, shove)

    if PING_USERS_ENABLED:
        eventlet.spawn(ping_users_loop, shove)
    if STARTUP_CLEANUP_BACKEND_CACHE:
        cleanup_backend_songs_folder()

    https = "https" in sys.argv
    if not https:
        Log.warn("HTTPS DISABLED! Add 'https' to sys.argv to enable!")

    Log.info(f"Starting SocketIO WSGI, port={PORT}, https={https}")
    wsgi_app = socketio.WSGIApp(sio)
    http_socket = eventlet.listen((HOST, PORT))

    if https:
        # wrap_ssl https://stackoverflow.com/a/39420484/13216113
        https_socket = eventlet.wrap_ssl(
            http_socket,
            certfile="cert.pem",
            keyfile="key.pem",
            server_side=True
        )
        eventlet.wsgi.server(https_socket, wsgi_app, log_output=LOG_WSGI)
    else:
        eventlet.wsgi.server(http_socket, wsgi_app, log_output=LOG_WSGI)

    print("\n\n\t\"And as always, thanks for watching.\" - Michael Stevens\n\n")


if __name__ == "__main__":
    while True:
        try:
            main()

        except Exception as _ex:
            Log.fatal(f"Unhandled exception on main", ex=_ex)

        Log.trace(f"Restarting in {DELAY_BEFORE_RESTART} s")
        time.sleep(DELAY_BEFORE_RESTART)
