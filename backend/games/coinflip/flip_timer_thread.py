from convenience import *


class FlipTimerThread(threading.Thread):
    def __init__(self, game, flip_timer_duration):
        super().__init__(name=f"{game.room.name}/FlipTimer", daemon=True)
        self.game = game
        self.time_left = flip_timer_duration

    def run(self):
        Log.trace(f"Timer started, seconds: {self.time_left}")

        while self.time_left:
            time.sleep(1)
            self.time_left -= 1
            if self.time_left:
                self.game.events.put("timer_ticked")

        Log.trace("Timer finished")
        self.game.events.put("timer_finished")
