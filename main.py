import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, send_from_directory, request
from flask_socketio import SocketIO

from util import *
from server import Server
from packet_sender_thread import PacketSenderThread, send_packets
from packet_handler_thread import PacketHandlerThread, handle_packets, _handle

HOST = "0.0.0.0"
PORT = 80
DEBUG = False
USE_RELOADER = False

threading.current_thread().setName("Main")
app = Flask(__name__, template_folder="web/html")
app.config["SECRET_KEY"] = secrets.token_urlsafe()
socketio = SocketIO(app)


global server
updated_socketio_thread_name = False


def update_socketio_thread_name():  # SocketIO doesn't let it's thread name to be changed easily
    global updated_socketio_thread_name
    if not updated_socketio_thread_name:
        threading.current_thread().setName("SocketIO")
        Log.trace("Updated SocketIO thread name")
        updated_socketio_thread_name = True


# Flask requests

@app.route("/")
def get_index_html():
    return render_template("index.html")


@app.route("/js/client.js")
def get_client_js():
    return send_from_directory("web/js", "client.js")


@app.route("/css/index.css")
def get_index_css():
    return send_from_directory("web/css", "index.css")


@app.route("/img/icon.png")
def get_icon_png():
    return send_from_directory("web/img", "icon.png")


# SocketIO events

@socketio.on("connect")
def on_connect():
    update_socketio_thread_name()
    sid = request.sid
    Log.debug(f"{sid} connected")
    server.on_connect(sid)


@socketio.on("disconnect")
def on_disconnect():
    update_socketio_thread_name()
    sid = request.sid
    Log.debug(f"{sid} disconnected")
    server.on_disconnect(sid)


@socketio.on_error()
def on_error(e):
    update_socketio_thread_name()
    Log.fatal(f"UNHANDLED {type(e).__name__} caught", exception=e)


@socketio.on("message")
def packet_received(packet: dict):
    update_socketio_thread_name()
    sender_sid = request.sid
    client = server.get_client(sender_sid)
    Log.trace(f"Received packet from {client.sid}: {packet}")

    server.incoming_packets_queue.put((client, packet))

    # Log.trace(f"Handling packet from {client}: {packet}")
    # response_packet = _handle(server, client, packet)
    # if response_packet:
    #     server.send_packet(client, response_packet, is_response=True)


if not USE_RELOADER or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':  # runs when run by Werkzeug subprocess
    Log.start_file_writer_thread()
    server = Server(socketio)
    # socketio.start_background_task(target=lambda: handle_packets(server, 0))
    # socketio.start_background_task(target=lambda: send_packets(server, socketio, 0))
    PacketHandlerThread(server).start()
    PacketSenderThread(server, socketio).start()
    Log.trace("Starting SocketIO")

else:
    Log.trace("Starting reloader child process")  # runs the first time, before Werkzeug starts subprocess


socketio.run(app, host=HOST, port=PORT, debug=DEBUG, use_reloader=USE_RELOADER)
