import ahkpy
from typing import Tuple

CLIENT_EXE_NAME = "PathofExileSteam.exe"
PATH_OF_EXILE_WINDOW = ahkpy.all_windows.first(exe=f"{CLIENT_EXE_NAME}")
import numpy as np

from src.config import FLASKS, FLASK_TIMEOUT,MACRO_TRIGGER_KEY


class FlaskBelt:

    def __init__(self):

        self.FLASKS_ENABLED = False
        self.FLASKS_RUNNING = False
        self.FLASK_TIMEOUT_TIMER = ahkpy.set_countdown(FLASK_TIMEOUT, self.stop_auto_flask)
        self.FLASK_TIMEOUT_TIMER.stop()
        self.flasks = []

        for flask_config in FLASKS:
            if flask_config[0] == "F":
                self.flasks.append(Flask(duration=flask_config[1],
                                         hotkey=flask_config[2]),
                                   )
            elif flask_config[0] == "A":
                self.flasks.append(AlternatingFlask(durations=flask_config[1],
                                                    hotkeys=flask_config[2]),
                                   )
            elif flask_config[0] == "M":
                pass

    def stop_auto_flask(self, ):
        if ahkpy.is_key_pressed(f"{MACRO_TRIGGER_KEY}"):
            self.FLASK_TIMEOUT_TIMER.update(interval=FLASK_TIMEOUT)
            return
        for flask in self.flasks:
            flask.stop()
        self.FLASKS_RUNNING = False
        print("stopped auto flasking")
        self.FLASK_TIMEOUT_TIMER.stop()



    def trigger_auto_flask(self,):  # TODO consider only triggering if PoE is the main window
        if self.FLASKS_ENABLED and not self.FLASKS_RUNNING:
            print("started macro, due to pressing the macro trigger key")
            for flask in self.flasks:
                flask.hard_start()
            self.FLASKS_RUNNING = True

    def timestamp_right_mouse_up(self, ):
        if self.FLASKS_ENABLED and self.FLASKS_RUNNING:
            self.FLASK_TIMEOUT_TIMER.update(interval=FLASK_TIMEOUT)

    def manual_toggle_flasks(self,):
        self.FLASKS_ENABLED = not self.FLASKS_ENABLED
        print("manually toggled Flasks to: " + ("enabled" if self.FLASKS_ENABLED else "disabled"))


class Flask:
    def __init__(self, duration: float, hotkey: str):
        self.duration = duration
        self.hotkey = hotkey
        self.timer = ahkpy.set_timer(self.duration, safe_send, hotkey)
        self.timer.stop()

    def hard_start(self):
        if self.duration > 0:
            safe_send(self.hotkey)
            self.timer.update(interval=self.duration)  # force reset
            self.timer.start()

    def soft_start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()


class AlternatingFlask(Flask):
    def __init__(self, durations: Tuple[float, float], hotkeys: Tuple[str, str]):
        self.duration_cur, self.duration_alternative = durations
        self.hotkey_cur, self.hotkey_alternative = hotkeys
        self.timer = ahkpy.set_countdown(self.duration_cur, self._swap_timer)
        self.timer.stop()

    def _swap_timer(self):
        self.duration_cur, self.duration_alternative = self.duration_alternative, self.duration_cur
        self.hotkey_cur, self.hotkey_alternative = self.hotkey_alternative, self.hotkey_cur
        safe_send(self.hotkey_cur)
        self.timer = ahkpy.set_countdown(self.duration_cur, self._swap_timer)

    def hard_start(self):
        if self.duration_cur > 0:
            safe_send(self.hotkey_cur)
            self.timer.update(interval=self.duration_cur)  # force reset
            self.timer.start()


def safe_send(hotkey: str):
    global PATH_OF_EXILE_WINDOW
    if PATH_OF_EXILE_WINDOW.is_active:
        ahkpy.sleep(np.random.uniform(0, 1) / 100)
        ahkpy.send(hotkey)
    else:
        PATH_OF_EXILE_WINDOW = ahkpy.all_windows.first(exe=f"{CLIENT_EXE_NAME}")
        print("not active")
