import eventlet
eventlet.monkey_patch()  # required, threading with socketio is ******

from flask import Flask, request
from flask_socketio import SocketIO

from convenience import *
from shove import Shove
from packet_sender import PacketSenderThread
from packet_handler import PacketHandlerThread
from ping_users import PingUsersThread
from tools import remove_non_mp3_files_from_cache, clear_frontend_audio_cache


HOST = "0.0.0.0"
PORT = 777
DEBUG = False

# how much red text in console todo use logging module for proper logging
LOG_EMITS = False
LOG_SOCKETIO = False
LOG_ENGINEIO = False


threading.current_thread().setName("Main")
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", logger=LOG_EMITS, engineio_logger=LOG_ENGINEIO)
shove: Union[Shove, None] = None  # Union for editor type hints


# Flask requests

@app.route("/")
def get_request_777():
    return "Stop trying to hack the website please. Thank you."


# SocketIO events

@socketio.on("connect")
def on_connect():
    sid = request.sid
    Log.trace(f"Handling connect of SID '{sid}'")
    shove.on_connect(sid)
    Log.info(f"SID '{sid}' connected")


@socketio.on("disconnect")
def on_disconnect():
    sid = request.sid
    user = shove.get_user_from_sid(sid=sid)
    if not user:
        Log.warn(f"socketio.on('disconnect'): User object not found/already disconnected, ignoring call")
        return

    Log.trace(f"Handling disconnect of {user}")
    shove.on_disconnect(sid)
    Log.info(f"{user} disconnected")


# todo BrokenPipeErrors?? check out https://stackoverflow.com/questions/47875007/flask-socket-io-frequent-time-outs
@socketio.on_error_default
def on_error(_ex):
    Log.fatal(f"UNHANDLED {type(_ex).__name__} caught by socketio.on_error_default", _ex)


# todo on connect, receive session cookie from user, check if session token valid, log in as that _account
@socketio.on("message")
def on_message(model: str, packet: dict):
    sid = request.sid
    user = shove.get_user_from_sid(sid=sid)
    if not user:
        Log.warn(f"socketio.on('message') (model '{model}'): User object not found/already disconnected, sending no_pong packet to SID {sid}")
        socketio.emit("error", {
            "error": "no_user_object",
            "description": "You don't exist anymore (not good), refresh!"
        }, room=sid)
        return

    packet_number = shove.get_next_packet_number()
    Log.debug(f"Received packet #{packet_number}: '{model}'\n from: {user}\n packet: {packet}")
    shove.incoming_packets_queue.put((user, model, packet, packet_number))


def main():
    print("\n\n\t\"Waazzaaaaaap\" - Michael Stevens\n\n")

    Log.start_file_writer_thread()
    global shove
    shove = Shove(socketio)
    PacketSenderThread(shove, socketio).start()
    PacketHandlerThread(shove).start()
    PingUsersThread(shove)  # .start()  # comment out to disable pinging

    remove_non_mp3_files_from_cache()
    # clear_frontend_audio_cache()

    Log.info(f"Running SocketIO on port {PORT}")

    if DEBUG:
        Log.warn("*** DEBUG MODE ENABLED ***")

    socketio.run(app, host=HOST, port=PORT, debug=DEBUG, log_output=LOG_SOCKETIO, use_reloader=False)
    # time.sleep(60)


if __name__ == "__main__":
    while True:
        try:
            main()

        except Exception as ex:
            Log.fatal(f"UNHANDLED {type(ex).__name__} on main()", ex)
            Log.trace("Restarting in 10 s")
            time.sleep(10)
