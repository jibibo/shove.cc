import eventlet
# eventlet.sleep()  # https://stackoverflow.com/questions/43801884/how-to-run-python-socketio-in-thread
eventlet.monkey_patch()  # required, threading with socketio is ******
from eventlet import wsgi

from convenience import *
from shove import Shove
from packet_sender import PacketSenderThread, send_packets_loop
from packet_handler import PacketHandlerThread, handle_packets_loop
# from ping_users import PingUsersThread
from tools import cleanup_backend_youtube_cache, clear_frontend_audio_cache

import socketio

HOST = "0.0.0.0"
PORT = 777

# how much red text in console todo use logging module for proper logging
LOG_SOCKETIO = False
LOG_ENGINEIO = False
LOG_WSGI = False

# async_mode="threading" is less performant - https://python-socketio.readthedocs.io/en/latest/server.html#standard-threads
sio = socketio.Server(cors_allowed_origins="*", logger=LOG_SOCKETIO, engineio_logger=LOG_ENGINEIO)
app = socketio.WSGIApp(sio)

threading.current_thread().setName("Main")
shove: Union[Shove, None] = None  # Union for editor type hints


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


def main():
    print("\n\n\t\"Waazzaaaaaap\" - Michael Stevens\n\n")

    # Log.start_file_writer_thread()
    sio.start_background_task(Log.write_file_loop)
    global shove
    shove = Shove(sio)
    # PacketSenderThread(shove, sio).start()
    sio.start_background_task(send_packets_loop, shove, sio)
    # PacketHandlerThread(shove).start()
    sio.start_background_task(handle_packets_loop, shove)
    # PingUsersThread(shove).start()  # comment out to disable pinging

    cleanup_backend_youtube_cache()
    # clear_frontend_audio_cache()

    Log.test(f"threading patched: {eventlet.patcher.is_monkey_patched('threading')}")
    Log.test(f"threading patched: {eventlet.patcher.is_monkey_patched('thread')}")
    Log.test(f"threading patched: {eventlet.patcher.is_monkey_patched('socket')}")

    Log.info(f"Running SocketIO on port {PORT}")

    wsgi.server(eventlet.listen((HOST, PORT)), app, log_output=LOG_WSGI)
    # socketio.run(app, host=HOST, port=PORT, debug=DEBUG, log_output=LOG_SOCKETIO, use_reloader=False)
    # time.sleep(60)


if __name__ == "__main__":
    while True:
        try:
            main()

        except Exception as ex:
            Log.fatal(f"UNHANDLED {type(ex).__name__} on main()", ex)
            Log.trace("Restarting in 10 s")
            time.sleep(10)
