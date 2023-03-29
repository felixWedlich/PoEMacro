import configparser
import time

import ahkpy
from typing import Tuple, Callable
import subprocess
from multiprocessing.shared_memory import SharedMemory

import numpy as np




class FlaskBelt:

    def __init__(self, config: configparser.ConfigParser):
        self.MACRO_TRIGGER_KEY = config.get('hotkeys','MACRO_TRIGGER_KEY')
        self.FLASKS_ENABLED = False
        self.FLASKS_RUNNING = False
        self.FLASK_TIMEOUT = config.getfloat('flask','FLASK_TIMEOUT')
        self.FLASK_TIMEOUT_TIMER = ahkpy.set_countdown(self.FLASK_TIMEOUT, self.stop_auto_flask)
        self.FLASK_TIMEOUT_TIMER.stop()
        self.flasks = []
        self.CLIENT_EXE_NAME = config.get('poe', 'CLIENT_EXE_NAME')
        self.PATH_OF_EXILE_WINDOW = ahkpy.all_windows.first(exe=f"{self.CLIENT_EXE_NAME}")

        for _,flask_config in config['flask-setup'].items():
            flask_config = flask_config.split(',')
            if flask_config[0] == "F":
                self.flasks.append(Flask(duration=float(flask_config[1]),
                                         hotkey=flask_config[2],
                                         safe_send=self.safe_send)
                                   )
            elif flask_config[0] == "A":
                self.flasks.append(AlternatingFlask(durations=(float(flask_config[1]),float(flask_config[2])),
                                                    hotkeys=(flask_config[3],flask_config[4]),
                                                    safe_send=self.safe_send)
                                   )
            elif flask_config[0] == "M":
                subprocess.Popen(r"C:\Users\Felix\.virtualenvs\Macro\Scripts\python.exe .\src\flask\mana_life.py M")
                self.flasks.append(ManaFlask(duration=float(flask_config[1]),
                                             hotkey=flask_config[2],
                                             safe_send=self.safe_send)
                                   )
            elif flask_config[0] == "L":
                subprocess.Popen(r"C:\Users\Felix\.virtualenvs\Macro\Scripts\python.exe .\src\flask\mana_life.py L")
                self.flasks.append(LifeFlask(duration=float(flask_config[1]),
                                             hotkey=flask_config[2],
                                             safe_send=self.safe_send)
                                   )

    def stop_auto_flask(self, ):
        if ahkpy.is_key_pressed(f"{self.MACRO_TRIGGER_KEY}"):
            self.FLASK_TIMEOUT_TIMER.update(interval=self.FLASK_TIMEOUT)
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
                if isinstance(flask, (ManaFlask, LifeFlask, AlternatingFlask)):
                    flask.soft_start()
                    continue
                flask.hard_start()
            self.FLASKS_RUNNING = True

    def update_caps(self):
        for flask in self.flasks:
            if isinstance(flask, (ManaFlask, LifeFlask)):
                flask.update_cap()

    def timestamp_right_mouse_up(self, ):
        if self.FLASKS_ENABLED and self.FLASKS_RUNNING:
            self.FLASK_TIMEOUT_TIMER.update(interval=self.FLASK_TIMEOUT)

    def manual_toggle_flasks(self, ):
        self.FLASKS_ENABLED = not self.FLASKS_ENABLED
        print("manually toggled Flasks to: " + ("enabled" if self.FLASKS_ENABLED else "disabled"))

    def safe_send(self, hotkey: str) -> None:
        if self.PATH_OF_EXILE_WINDOW.is_active:
            ahkpy.sleep(np.random.uniform(0, 1) / 100)
            ahkpy.send(hotkey)
        else:
            self.PATH_OF_EXILE_WINDOW = ahkpy.all_windows.first(exe=f"{self.CLIENT_EXE_NAME}")
            print("not active")


class Flask:
    def __init__(self, duration: float, hotkey: str, safe_send):
        self.duration = duration
        self.hotkey = hotkey
        self.safe_send = safe_send
        self.timer = None
        self.setup_timer()

    def setup_timer(self):
        self.timer = ahkpy.set_timer(self.duration, self.safe_send, self.hotkey)
        self.timer.stop()

    def hard_start(self):
        if self.duration > 0:
            self.safe_send(self.hotkey)
            self.timer.update(interval=self.duration)  # force reset
            self.timer.start()

    def soft_start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()


class LifeFlask(Flask):
    def __init__(self, duration: float, hotkey: str, safe_send):
        super(LifeFlask, self).__init__(duration, hotkey, safe_send)
        self.cap = None
        self.low_life = None
        self.in_effect = False
        self.last_send = time.time()
        self.last_send_ll = time.time()
        try:
            self.mem = SharedMemory("LIFE", create=True, size=11)
        except FileExistsError:
            self.mem = SharedMemory("LIFE", create=False, size=11)
        time.sleep(0.5)
        self.update_cap()

    def setup_timer(self):
        self.timer = ahkpy.set_timer(self.duration, self._check_life)
        self.timer.stop()

    def update_cap(self):
        self.mem.buf[6] = 1
        time.sleep(0.1)
        self.cap = int.from_bytes(self.mem.buf[7:11], 'big')
        self.low_life = self.cap // 2
        self.threshold = int(self.cap * 0.8)
        print(f"updated life cap to {self.cap}")

    def _check_life(self):
        val = int.from_bytes(self.mem.buf[0:4], 'big')
        time_diff = (time.time() - self.last_send)
        time_diff_ll = (time.time() - self.last_send_ll)
        if val == self.cap:
            self.in_effect = False
        if time_diff > 3.5:
            self.in_effect = False

        if val < self.low_life and time_diff_ll > 0.1:
            self.safe_send(self.hotkey)
            self.last_send_ll = time.time()

        if val < self.threshold and not self.in_effect:
            print("pressing life flask")
            self.safe_send(self.hotkey)
            self.last_send = time.time()
            self.in_effect = True
        # TODO pannicked -> press when below self.low_life regardless of in_effect


class ManaFlask(Flask):
    def __init__(self, duration: float, hotkey: str, safe_send):
        super(ManaFlask, self).__init__(duration, hotkey, safe_send)
        self.cap = None
        self.in_effect = False
        self.last_send = time.time()
        try:
            self.mem = SharedMemory("MANA", create=True, size=11)
        except FileExistsError:
            self.mem = SharedMemory("MANA", create=False, size=11)
        time.sleep(0.5)
        self.update_cap()

    def setup_timer(self):
        self.timer = ahkpy.set_timer(self.duration, self._check_mana)
        self.timer.stop()

    def update_cap(self):
        self.mem.buf[6] = 1
        time.sleep(0.1)
        self.cap = int.from_bytes(self.mem.buf[7:11], 'big')
        print(f"updated mana cap to {self.cap}")

    def _check_mana(self):
        val = int.from_bytes(self.mem.buf[0:4], 'big')
        time_diff = (time.time() - self.last_send)
        if val == self.cap:
            self.in_effect = False
        if time_diff > 3.5:
            self.in_effect = False

        if val < 20 and not self.in_effect:
            print("pressing mana flask")
            self.safe_send(self.hotkey)
            self.last_send = time.time()
            self.in_effect = True

    def stop(self):
        super().stop()
        self.mem.buf[4] = 1

    def soft_start(self):
        self.mem.buf[4] = 0
        super().soft_start()


class AlternatingFlask(Flask):
    def __init__(self, durations: Tuple[float, float], hotkeys: Tuple[str, str], safe_send: Callable[[str], None]):
        self.durations = durations
        self.hotkeys = hotkeys
        self.index = 0

        self.timer = ahkpy.set_countdown(self.durations[self.index], self.swap_index_and_send)
        self.timer.stop()
        self.safe_send = safe_send

        #register for both flasks, hotkeys such that if the flask was manually pressed the timers are adjusted
        ahkpy.hotkey(f"~{hotkeys[0]}",self.manually_pressed_first_flask)
        ahkpy.hotkey(f"~{hotkeys[1]}",self.manually_pressed_second_flask)
        # set the timestamp back in time, to pretend that it was pressed so long ago, that it doesnt matter)
        self.manual_pres_timestamp = time.time() - (max(self.durations)  +1 )

    def swap_index_and_send(self):
        # swap index to other flask 0 -> 1, 1 -> 0
        self.index = (self.index + 1) %2

        #send keypress for other flask
        self.safe_send(self.hotkeys[self.index])
        #set timer to duration of other flask
        self.timer = ahkpy.set_countdown(self.durations[self.index],self.swap_index_and_send)

    def hard_start(self):
        self.index = (self.index + 1) %2
        self.safe_send(self.hotkeys[self.index])
        self.timer.update(interval=self.durations[self.index])  # force reset
        self.timer.start()

    def manually_pressed_second_flask(self):
        """
        called, when the player manually presses the flask.
        Updates the timestamp, sets the index to the second flask(1)
        and adapts the timer.
        :return:
        """
        self.index = 1
        self.timer.update(interval=self.durations[1])
        self.manual_pres_timestamp = time.time()

    def manually_pressed_first_flask(self):
        self.index = 0
        self.timer.update(interval=self.durations[0])
        self.manual_pres_timestamp = time.time()

    def soft_start(self):
        """
        Checks the timestamp to determine if a remaining duration of a flask exist
        and thus it need to be actually soft-started else hardstart it
        :return:
        """
        seconds_since_last_manual_press = time.time() - self.manual_pres_timestamp
        manual_pres_remaining_duration = self.durations[self.index] - seconds_since_last_manual_press
        if  manual_pres_remaining_duration > 0:
            self.timer.update(interval=manual_pres_remaining_duration)
            self.timer.start()
        else:
            self.hard_start()
