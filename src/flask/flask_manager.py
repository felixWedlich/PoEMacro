import time

import ahkpy
from typing import Tuple
import subprocess
from multiprocessing.shared_memory import SharedMemory

CLIENT_EXE_NAME = "PathofExileSteam.exe"
PATH_OF_EXILE_WINDOW = ahkpy.all_windows.first(exe=f"{CLIENT_EXE_NAME}")
import numpy as np

from src.config import FLASKS, FLASK_TIMEOUT, MACRO_TRIGGER_KEY


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
                subprocess.Popen(r"C:\Users\Felix\.virtualenvs\Macro\Scripts\python.exe C:\Users\Felix\IdeaProjects\Macro\src\flask\mana_life.py M")
                self.flasks.append(ManaFlask(duration=flask_config[1],
                                             hotkey=flask_config[2]))
            elif flask_config[0] == "L":
                subprocess.Popen(r"C:\Users\Felix\.virtualenvs\Macro\Scripts\python.exe C:\Users\Felix\IdeaProjects\Macro\src\flask\mana_life.py L")
                self.flasks.append(LifeFlask(duration=flask_config[1],
                                             hotkey=flask_config[2]))

    def stop_auto_flask(self, ):
        if ahkpy.is_key_pressed(f"{MACRO_TRIGGER_KEY}"):
            self.FLASK_TIMEOUT_TIMER.update(interval=FLASK_TIMEOUT)
            return
        for flask in self.flasks:
            flask.stop()
        self.FLASKS_RUNNING = False
        print("stopped auto flasking")
        self.FLASK_TIMEOUT_TIMER.stop()

    def trigger_auto_flask(self, ):  # TODO consider only triggering if PoE is the main window
        if self.FLASKS_ENABLED and not self.FLASKS_RUNNING:
            print("started macro, due to pressing the macro trigger key")
            for flask in self.flasks:
                if isinstance(flask, (ManaFlask,LifeFlask)):
                    flask.soft_start()
                    continue
                flask.hard_start()
            self.FLASKS_RUNNING = True

    def update_caps(self):
        for flask in self.flasks:
            if isinstance(flask, (ManaFlask,LifeFlask)):
                flask.update_cap()


    def timestamp_right_mouse_up(self, ):
        if self.FLASKS_ENABLED and self.FLASKS_RUNNING:
            self.FLASK_TIMEOUT_TIMER.update(interval=FLASK_TIMEOUT)

    def manual_toggle_flasks(self, ):
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


class LifeFlask(Flask):
    def __init__(self, duration:float, hotkey: str):
        self.hotkey = hotkey
        self.duration = duration
        self.cap = None
        self.low_life = None
        self.in_effect = False
        self.last_send = time.time()
        try:
            self.mem = SharedMemory("LIFE", create=True, size=11)
        except FileExistsError:
            self.mem = SharedMemory("LIFE", create=False, size=11)

        self.timer = ahkpy.set_timer(self.duration, self._check_life)
        self.timer.stop()
        time.sleep(0.5)
        self.update_cap()

    def update_cap(self):
        self.mem.buf[6] = 1
        time.sleep(0.1)
        self.cap = int.from_bytes(self.mem.buf[7:11], 'big')
        self.low_life = self.cap // 2
        self.threshold = int(self.cap * 0.8)

    def _check_life(self):
        val = int.from_bytes(self.mem.buf[0:4], 'big')
        time_diff = (time.time() - self.last_send)
        if val == self.cap:
            self.in_effect = False
        if time_diff > 3.5:
            self.in_effect = False

        if val < self.threshold and not self.in_effect:
            print("pressing life flask")
            safe_send(self.hotkey)
            self.last_send = time.time()
            self.in_effect = True
        # TODO pannicked -> press when below self.low_life regardless of in_effect
class ManaFlask(Flask):
    def __init__(self, duration:float, hotkey: str):
        self.hotkey = hotkey
        self.duration = duration
        self.cap = None
        self.in_effect = False
        self.last_send = time.time()
        try:
            self.mem = SharedMemory("MANA", create=True, size=11)
        except FileExistsError:
            self.mem = SharedMemory("MANA", create=False, size=11)

        self.timer = ahkpy.set_timer(self.duration, self._check_mana)
        self.timer.stop()
        time.sleep(0.5)
        self.update_cap()

    def update_cap(self):
        self.mem.buf[6] = 1
        time.sleep(0.1)
        self.cap = int.from_bytes(self.mem.buf[7:11], 'big')
        print(f"updated cap to {self.cap}")

    def _check_mana(self):
        val = int.from_bytes(self.mem.buf[0:4], 'big')
        time_diff = (time.time() - self.last_send)
        if val == self.cap:
            self.in_effect = False
        if time_diff > 3.5:
            self.in_effect = False

        if val < 30 and not self.in_effect:
            print("pressing mana flask")
            safe_send(self.hotkey)
            self.last_send = time.time()
            self.in_effect = True

    def stop(self):
        super().stop()
        self.mem.buf[4] = 1

    def soft_start(self):
        self.mem.buf[4] = 0
        super().soft_start()

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
