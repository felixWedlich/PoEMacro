import configparser
import time
import threading
import ahkpy
from .flask import FlaskBelt
from .inventory import InventoryManager

AUTOFLASK_DISABLED_PLACES = ["Hideout",
                             "Rogue Harbour",
                             "Oriath",
                             "Lioneye's Watch",
                             "The Forest Encampment",
                             "The Sarn Encampment",
                             "Highgate",
                             "Overseer's Tower",
                             "The Bridge Encampment",
                             "Oriath Docks",
                             "Karui Shores"
                             ]

SIMULACRUM_PLACES = ["Lunacy's Watch", "The Bridge Enraptured", "The Syndrome Encampment",
                     "Hysteriagate", "Oriath Delusion"]


class Macro:

    def __init__(self, config: configparser.ConfigParser):

        self.IN_TOWN = True
        self.IN_SIMULACRUM = False
        self.client_txt = open(config['poe']['CLIENT_TXT_LOCATION'], "r", encoding="utf-8")
        self.flask_belt = FlaskBelt(config)
        self.inv = InventoryManager(config)
        self.client_txt_refresh_duration = int(config['poe']['CLIENT_TXT_REFRESH_DURATION'])
        self.auto_toggle = config.getboolean('flask', 'AUTO_TOGGLE')
        self.disable_while_chat = config.getboolean('flask', 'DISABLE_MACRO_WHILE_CHAT')

    def start_looping(self):

        # asyncio.run(self.read_client_txt())
        th = threading.Thread(target=self.read_client_txt)
        th.start()
        while th.is_alive():
            self.sleeper()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client_txt.close()

    def read_client_txt(self, ):
        # JUST_DIED = False
        self.client_txt.readlines()
        while True:
            new_lines = self.client_txt.readlines()
            for line in new_lines:
                if "is now level" in line:
                    print("leveled up updating caps")
                    self.flask_belt.update_caps()
                if "You have entered" in line:
                    print("changed place")
                    # if JUST_DIED:
                    #     print("now i would reactivate auras")
                    #     ahkpy.sleep(1)
                    #     reactivate_auras()
                    #     JUST_DIED = False
                    if not self.auto_toggle:
                        break
                    else:
                        self.flask_belt.FLASKS_ENABLED = True
                        self.IN_TOWN = False
                        self.IN_SIMULACRUM = False

                    for place in AUTOFLASK_DISABLED_PLACES:
                        if place in line:
                            if self.auto_toggle:
                                self.flask_belt.stop_auto_flask()
                                self.flask_belt.FLASKS_ENABLED = False
                            self.IN_TOWN = True
                            break
                    for place in SIMULACRUM_PLACES:
                        if place in line:
                            self.IN_SIMULACRUM = True
                            if self.auto_toggle:
                                self.flask_belt.FLASKS_ENABLED = True
                                self.IN_TOWN = False
                            break
                    print("automatically toggled Flasks to: " + ("enabled" if self.flask_belt.FLASKS_ENABLED else "disabled"))

            time.sleep(self.client_txt_refresh_duration)

    def sleeper(self):
        ahkpy.sleep(0.01)
        self.inv.root.update()

    def stash_all_non_empty_cells(self, ):
        if not self.IN_TOWN and not self.IN_SIMULACRUM:
            print("not in town, ignored inv-stash")
            return
        self.inv.stash_all_non_empty_cells()

    def toggle_open_lock_gui(self, ):
        if not self.IN_TOWN:  # in a map nobody wants to config the inventory
            print("not in town, ignored opening inv-lock GUI")
            return
        self.inv.toggle_open_lock_gui()
