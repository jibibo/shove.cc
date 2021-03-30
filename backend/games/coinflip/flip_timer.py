from convenience import *


class FlipTimerThread(threading.Thread):
    def __init__(self, game, duration):
        super().__init__(name=f"{game.room.name}/FlipTimer", daemon=True)
        self.game = game
        self.game.time_left = duration

    def run(self):
        Log.trace(f"Timer started, seconds: {self.game.time_left}")

        while self.game.time_left:
            time.sleep(1)
            self.game.time_left -= 1
            if self.game.time_left:
                self.game.events.put("timer_ticked")
            else:
                self.game.time_left = None

        Log.trace("Timer finished")
        self.game.events.put("timer_finished")
