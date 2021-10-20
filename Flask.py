import ahkpy
from typing import Tuple
CLIENT_EXE_NAME = "PathofExileSteam.exe"
PATH_OF_EXILE_WINDOW = ahkpy.all_windows.first(exe=f"{CLIENT_EXE_NAME}")

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



def safe_send(hotkey:str):
    if PATH_OF_EXILE_WINDOW.is_active:
        ahkpy.send(hotkey)
    else:
        print("not active")
