import eventlet
eventlet.monkey_patch()  # required, threading with socketio *****

from flask import Flask, request
from flask_socketio import SocketIO

from convenience import *
from shove import Shove
from packet_sender import PacketSenderThread
from packet_handler import PacketHandlerThread


HOST = "0.0.0.0"
PORT = 777
DEBUG = True

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
    Log.debug(f"{sid} connected")
    shove.on_connect(sid)


@socketio.on("disconnect")
def on_disconnect():
    update_socketio_thread_name()
    sid = request.sid
    Log.debug(f"{sid} disconnected")
    shove.on_disconnect(sid)


# todo BrokenPipeErrors?? check out https://stackoverflow.com/questions/47875007/flask-socket-io-frequent-time-outs
@socketio.on_error_default
def on_error(e):
    update_socketio_thread_name()
    Log.fatal(f"UNHANDLED {type(e).__name__} caught", exception=e)


# todo on connect, receive session cookie from client, check if session token valid, log in as that account
@socketio.on("message")
def on_message(model: str, packet: dict):
    update_socketio_thread_name()
    sender_sid = request.sid
    client = shove.get_client(sender_sid)
    packet_number = shove.get_next_packet_number()
    Log.debug(f"Received packet #{packet_number}\nfrom: {client}\npacket: {packet}")
    shove.incoming_packets_queue.put((client, model, packet, packet_number))


def update_socketio_thread_name():  # SocketIO doesn't let it's thread name to be changed easily
    global updated_socketio_thread_name
    if updated_socketio_thread_name:
        return

    threading.current_thread().setName("SocketIO")
    Log.trace("Updated SocketIO thread name")
    updated_socketio_thread_name = True


if __name__ == "__main__":
    print("\"waazzaaaaaap\" - Michael Stevens")
    Log.start_file_writer_thread()
    shove = Shove(socketio)
    PacketSenderThread(shove, socketio).start()
    PacketHandlerThread(shove).start()

    Log.info(f"Running SocketIO on port {PORT}")

    if DEBUG:
        Log.warn("*** DEBUG MODE ENABLED ***")

    try:
        socketio.run(app, host=HOST, port=PORT, debug=DEBUG, log_output=LOG_SOCKETIO, use_reloader=False)
    except BaseException as ex:
        Log.fatal(f"UNHANDLED {type(ex).__name__} on running SocketIO", exception=ex)
