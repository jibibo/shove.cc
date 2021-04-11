import eventlet
eventlet.monkey_patch()  # required to patch modules for using threads with socketio

from convenience import *

from shove import Shove
from packet_sender import send_packets_loop
from packet_handler import handle_packets_loop
from user_pinger import ping_users_loop

set_greenlet_name("Main")

flask_app = flask.Flask(__name__, root_path="")  # or it will be set to backend/src, can't access static files
flask_app.config["SECRET_KEY"] = os.urandom(24)  # https://stackoverflow.com/a/34903502/13216113
sio = SocketIO(
    app=flask_app,
    logger=LOG_SOCKETIO,
    async_mode="eventlet",
    cors_allowed_origins="*",
    engineio_logger=LOG_ENGINEIO
)
shove: Union[Shove, None] = None  # Union -> for editor (pycharm) type hint detection

# time.sleep() is patched by eventlet.monkey_patch(), no need to use eventlet.sleep()!
# -> https://stackoverflow.com/a/25315314/13216113


# Flask handlers TODO DELETE THIS TRASH

@flask_app.route("/")
def index():
    return "gamba"


last_request_id = 0


@flask_app.route(f"/<path:path>")
def flask_get(path):
    global last_request_id
    last_request_id += 1
    set_greenlet_name(f"Flask/request/#{last_request_id}")
    Log.trace(f"Handling request: {path}")

    try:
        # todo set X-Sendfile for performance
        # https://flask.palletsprojects.com/en/1.1.x/api/#flask.send_from_directory
        return flask.send_from_directory(STATIC_FOLDER, path)

    except Exception as ex:
        Log.trace(f"Request failed: {ex}")
        return f"Request failed {ex}"


@flask_app.errorhandler(Exception)
def flask_error(ex):
    set_greenlet_name("Flask/error")
    Log.fatal(f"Unhandled exception caught by Flask", ex=ex)
    return "Error not good"


# SocketIO handlers

@sio.on("connect")
def on_connect():
    set_greenlet_name("SIO/connect")
    sid = flask.request.sid
    environ = flask.request.environ
    Log.trace(f"Handling connect of SID '{sid}', environ: {environ}", cutoff=True)
    user = shove.on_connect(sid)
    Log.info(f"{user} connected from {environ['REMOTE_ADDR']}")


@sio.on("disconnect")
def on_disconnect():
    set_greenlet_name("SIO/disconnect")
    sid = flask.request.sid
    user = shove.get_user_by_sid(sid)
    if not user:
        Log.warn(f"socketio.on('disconnect'): User object not found/already disconnected, ignoring call")
        return

    Log.trace(f"Handling disconnect of {user}")
    shove.on_disconnect(user)
    Log.info(f"{user} disconnected")


@sio.on_error_default
def on_error_default(ex):
    set_greenlet_name("SIO/error")
    Log.fatal(f"Unhandled exception caught by SocketIO", ex=ex)


# todo on connect, receive session cookie from user, check if session token valid, log in as that _account
@sio.on("message")
def on_message(model: str, packet: Optional[dict]):
    set_greenlet_name("SIO/message")
    sid = flask.request.sid
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

    Log.info(f"Starting SocketIO WSGI on port {PORT}")
    # listen_socket = eventlet.listen((HOST, PORT))
    # wrap_ssl https://stackoverflow.com/a/39420484/13216113
    # listen_socket_ssl = eventlet.wrap_ssl(
    # listen_socket,
    # certfile="cert.pem",
    # keyfile="key.pem",
    # server_side=True
    # )
    # wsgi_app = socketio.WSGIApp(sio)
    # eventlet.wsgi.server(listen_socket_ssl, flask_app, log_output=LOG_WSGI)  # blocking
    sio.run(flask_app, host='0.0.0.0', port=777, debug=False, keyfile='key.pem', certfile='cert.pem')

    print("\n\n\t\"And as always, thanks for watching.\" - Michael Stevens\n\n")


if __name__ == "__main__":
    while True:
        try:
            main()

        except Exception as _ex:
            Log.fatal(f"Unhandled exception on main", ex=_ex)

        Log.trace(f"Restarting in {DELAY_BEFORE_RESTART} s")
        time.sleep(DELAY_BEFORE_RESTART)
