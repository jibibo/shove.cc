import eventlet
eventlet.monkey_patch()  # required to patch modules for socketio

from convenience import *

from shove import Shove
from packet_sender import send_packets_loop
from packet_handler import handle_packets_loop
from user_pinging import ping_users_loop

sio = socketio.Server(
    cors_allowed_origins="*",
    logger=LOG_SOCKETIO,
    engineio_logger=LOG_ENGINEIO
)
app = socketio.WSGIApp(sio)
# threading.current_thread().setName("Main")
shove: Union[Shove, None] = None  # Union -> for editor (pycharm) type hint detection


# SocketIO events

@sio.on("connect")
def on_connect(sid, environ):
    Log.trace(f"Handling connect of {sid}, environ: {environ}", cutoff=True)
    user = shove.on_connect(sid)
    Log.info(f"{user} connected from {environ['REMOTE_ADDR']}")


@sio.on("disconnect")
def on_disconnect(sid):
    user = shove.get_user_from_sid(sid=sid)
    if not user:
        Log.warn(f"socketio.on('disconnect'): User object not found/already disconnected, ignoring call")
        return

    Log.trace(f"Handling disconnect of {user}")
    shove.on_disconnect(sid)
    Log.info(f"{user} disconnected")


# todo on connect, receive session cookie from user, check if session token valid, log in as that _account
@sio.on("message")
def on_message(sid, model: str, packet: dict):
    user = shove.get_user_from_sid(sid=sid)
    if not user:
        Log.warn(f"socketio.on('message') (model '{model}'): User object not found/already disconnected, sending no_pong packet to SID {sid}")
        sio.emit("error", {
            "error": "no_user_object",
            "description": "You don't exist anymore (not good), refresh!"
        }, to=sid)
        return

    packet_number = shove.get_next_packet_number()
    Log.debug(f"Received packet #{packet_number}: '{model}'\n from: {user}\n packet: {packet}")
    shove.incoming_packets_queue.put((user, model, packet, packet_number))


# main function

def main():
    print("\n\n\t\"Waazzaaaaaap\" - Michael Stevens\n\n")

    sio.start_background_task(Log.write_file_loop)

    global shove
    shove = Shove(sio)
    # threading.greenlet.greenlet.getcurrent().setName("test1")

    t = sio.start_background_task(send_packets_loop, shove, sio)
    Log.test(f"test1: {t}")
    sio.start_background_task(handle_packets_loop, shove)

    if PING_USERS_ENABLED:
        sio.start_background_task(ping_users_loop, shove)
    if STARTUP_CLEANUP_BACKEND_CACHE:
        cleanup_backend_youtube_cache()
    if STARTUP_EMPTY_FRONTEND_CACHE:
        empty_frontend_cache()

    Log.info(f"Running SocketIO on port {PORT}")

    eventlet_wsgi.server(eventlet.listen((HOST, PORT)), app, log_output=LOG_WSGI)


if __name__ == "__main__":
    while True:
        try:
            main()

        except Exception as ex:
            Log.fatal(f"UNHANDLED {type(ex).__name__} on main()", ex)
            Log.trace("Restarting in 10 s")
            time.sleep(10)
