from convenience import *


# todo could be an abstract timer (many games use timers, more organized)
def flip_timer(game):
    set_greenthread_name(f"FlipTimer/{game.room}")
    game.time_left = game.flip_timer_duration
    Log.trace(f"Timer started, duration: {game.flip_timer_duration} s")

    while game.time_left:
        eventlet.sleep(1)  # not time.sleep(1)
        game.time_left -= 1
        if game.time_left:
            game.events.put("timer_ticked")
        else:
            game.time_left = 0

    Log.trace("Timer finished")
    game.events.put("timer_finished")
