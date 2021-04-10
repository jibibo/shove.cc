import eventlet
eventlet.monkey_patch()  # required to patch modules for using threads with socketio

from convenience import *

from shove import Shove
from packet_sender import send_packets_loop
from packet_handler import handle_packets_loop
from user_pinger import ping_users_loop

set_greenthread_name("Main")

# eventlet usage consequences:
# time.sleep() should become eventlet.sleep()
# instead of creating a threading.Thread, call eventlet.spawn(func, *args) etc
# these greenthreads should be named, like above

sio = socketio.Server(
    logger=LOG_SOCKETIO,
    async_mode="eventlet",
    cors_allowed_origins="*",
    engineio_logger=LOG_ENGINEIO
)
wsgi_app = socketio.WSGIApp(sio)
shove: Union[Shove, None] = None  # Union -> for editor (pycharm) type hint detection


# SocketIO events

@sio.on("connect")
def on_connect(sid, environ):
    set_greenthread_name("sio/on_connect")
    Log.trace(f"Handling connect of SID '{sid}', environ: {environ}", cutoff=True)
    user = shove.on_connect(sid)
    Log.info(f"{user} connected from {environ['REMOTE_ADDR']}")


@sio.on("disconnect")
def on_disconnect(sid):
    set_greenthread_name("sio/on_disconnect")
    user = shove.get_user_by_sid(sid)
    if not user:
        Log.warn(f"socketio.on('disconnect'): User object not found/already disconnected, ignoring call")
        return

    Log.trace(f"Handling disconnect of {user}")
    shove.on_disconnect(user)
    Log.info(f"{user} disconnected")


# todo on connect, receive session cookie from user, check if session token valid, log in as that _account
@sio.on("message")
def on_message(sid, model: str, packet: Optional[dict]):
    set_greenthread_name("sio/on_message")
    user = shove.get_user_by_sid(sid)
    if not user:
        Log.warn(f"socketio.on('message') (model '{model}'): User object not found/already disconnected, sending no_pong packet to SID {sid}")
        sio.emit("error", {
            "error": "no_user_object",
            "description": "You don't exist anymore (not good), refresh!"
        }, to=sid)
        return

    packet_id = shove.get_next_packet_id()
    Log.trace(f"Received packet #{packet_id} from {user}")
    shove.incoming_packets_queue.put((user, model, packet, packet_id))


# main function

def main():
    print("\n\n\t\"Waazzaaaaaap\" - Michael Stevens\n\n")
    eventlet.spawn(Log.write_file_loop)

    global shove
    shove = Shove(sio)

    eventlet.spawn(send_packets_loop, shove, sio)
    eventlet.spawn(handle_packets_loop, shove)

    if PING_USERS_ENABLED:
        eventlet.spawn(ping_users_loop, shove)
    if STARTUP_CLEANUP_BACKEND_CACHE:
        cleanup_backend_songs_folder()
    if STARTUP_EMPTY_FRONTEND_CACHE:
        empty_frontend_cache()

    Log.info(f"Starting SocketIO WSGI on port {PORT}")
    listen_socket = eventlet.listen((HOST, PORT))
    # wrap_ssl https://stackoverflow.com/a/39420484/13216113
    listen_socket_ssl = eventlet.wrap_ssl(
        listen_socket,
        certfile=f"backend/cert.pem",
        keyfile=f"backend/key.pem",
        server_side=True
    )
    # this is blocking, and reading console input is not compatible with greenthreads
    eventlet.wsgi.server(listen_socket_ssl, wsgi_app, log_output=LOG_WSGI)


if __name__ == "__main__":
    while True:
        try:
            main()

        except Exception as ex:
            Log.fatal(f"UNHANDLED {type(ex).__name__} on main", ex)

        Log.trace(f"Restarting in {DELAY_BEFORE_RESTART} s")
        time.sleep(DELAY_BEFORE_RESTART)
