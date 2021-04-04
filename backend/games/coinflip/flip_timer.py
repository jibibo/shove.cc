from convenience import *


class FlipTimerThread(threading.Thread):
    def __init__(self, game, duration):
        super().__init__(name=f"{game.room.name}/FlipTimer", daemon=True)
        self.game = game
        self.duration = duration

    def run(self):
        flip_timer(self.game, self.duration)


# todo could be an abstract timer (many games use timers, more organized)
def flip_timer(game, duration):
    game.time_left = duration
    Log.trace(f"Timer started, duration: {duration} s")

    while game.time_left:
        eventlet.sleep(1)  # not time.sleep(1)
        game.time_left -= 1
        if game.time_left:
            game.events.put("timer_ticked")
        else:
            game.time_left = None

    Log.trace("Timer finished")
    game.events.put("timer_finished")
