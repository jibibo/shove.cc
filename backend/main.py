import eventlet
eventlet.monkey_patch()  # required, threading with socketio *****

from flask import Flask, request
from flask_socketio import SocketIO

from convenience import *
from shove import Shove
from packet_sending import PacketSendingThread
from packet_handler import PacketHandlerThread


HOST = "0.0.0.0"
PORT = 777
DEBUG = True

# how much red text in console
LOG_EVENTS = False
LOG_REQUESTS = False
LOG_ENGINEIO = False


threading.current_thread().setName("Main")
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", logger=LOG_REQUESTS, engineio_logger=LOG_ENGINEIO)
updated_socketio_thread_name = False
global shove
n_packets_received = 0


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


@socketio.on_error()
def on_error(e):
    update_socketio_thread_name()
    Log.fatal(f"UNHANDLED {type(e).__name__} caught", exception=e)


@socketio.on("message")
def on_message(packet: dict):  # all sent messages should always be a model-containing packet
    update_socketio_thread_name()
    global n_packets_received
    n_packets_received += 1
    sender_sid = request.sid
    client = shove.get_client(sender_sid)
    Log.debug(f"Received packet #{n_packets_received}")
    PacketHandlerThread(shove, client, packet, n_packets_received).start()


def update_socketio_thread_name():  # SocketIO doesn't let it's thread name to be changed easily
    global updated_socketio_thread_name
    if not updated_socketio_thread_name:
        threading.current_thread().setName("SocketIO")
        Log.trace("Updated SocketIO thread name")
        updated_socketio_thread_name = True


if __name__ == '__main__':
    Log.start_file_writer_thread()
    shove = Shove(socketio)
    PacketSendingThread(shove, socketio).start()
    Log.info(f"Starting SocketIO on port {PORT}")
    socketio.run(app, host=HOST, port=PORT, debug=DEBUG, log_output=LOG_REQUESTS, use_reloader=False)
