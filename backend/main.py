import eventlet
eventlet.monkey_patch()  # required, threading with socketio is ******

from flask import Flask, request
from flask_socketio import SocketIO

from convenience import *
from shove import Shove
from packet_sender_thread import PacketSenderThread
from packet_handler_thread import PacketHandlerThread


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
updated_socketio_thread_name = False
global shove


# Flask requests

@app.route("/")
def get_request_777():
    return "Stop trying to hack the website please. Thank you."


# SocketIO events

@socketio.on("connect")
def on_connect():
    update_socketio_thread_name()

    sid = request.sid
    Log.info(f"SID {sid} connected")
    shove.on_connect(sid)


@socketio.on("disconnect")
def on_disconnect():
    update_socketio_thread_name()

    sid = request.sid
    Log.info(f"SID {sid} disconnected")
    shove.on_disconnect(sid)


# todo BrokenPipeErrors?? check out https://stackoverflow.com/questions/47875007/flask-socket-io-frequent-time-outs
@socketio.on_error_default
def on_error(_ex):
    update_socketio_thread_name()

    Log.fatal(f"UNHANDLED {type(_ex).__name__} caught by socketio.on_error_default", _ex)


# todo on connect, receive session cookie from user, check if session token valid, log in as that _account
@socketio.on("message")
def on_message(model: str, packet: dict):
    update_socketio_thread_name()

    sender_sid = request.sid
    user = shove.get_user_from_sid(sid=sender_sid)
    packet_number = shove.get_next_packet_number()
    Log.debug(f"Received packet #{packet_number}: '{model}'\n from: {user}\n packet: {packet}")
    shove.incoming_packets_queue.put((user, model, packet, packet_number))


def update_socketio_thread_name():  # SocketIO doesn't let its thread name to be changed easily
    global updated_socketio_thread_name
    if updated_socketio_thread_name:
        return

    threading.current_thread().setName("SocketIO")
    Log.trace("Updated SocketIO thread name")
    updated_socketio_thread_name = True


if __name__ == "__main__":
    print("\"Waazzaaaaaap.\" - Michael Stevens")
    Log.start_file_writer_thread()
    shove = Shove(socketio)
    PacketSenderThread(shove, socketio).start()
    PacketHandlerThread(shove).start()

    Log.info(f"Running SocketIO on port {PORT}")

    if DEBUG:
        Log.warn("*** DEBUG MODE ENABLED ***")

    try:
        socketio.run(app, host=HOST, port=PORT, debug=DEBUG, log_output=LOG_SOCKETIO, use_reloader=False)

    except Exception as ex:
        Log.fatal(f"UNHANDLED {type(ex).__name__} on socketio.run", ex)
