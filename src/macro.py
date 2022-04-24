import asyncio
import ahkpy
from src.config import SIMULACRUM_PLACES, AUTOFLASK_DISABLED_PLACES, CLIENT_TXT_REFRESH_DURATION, AUTO_TOGGLE
from flask import FlaskBelt
from inventory import InventoryManager
class Macro:

    def __init__(self,client_txt_fp:str):

        self.FLASKS_ENABLED = False
        self.IN_TOWN = True
        self.IN_SIMULACRUM = False
        self.client_txt = open(client_txt_fp,"r", encoding="utf-8")
        self.flask_belt = FlaskBelt()
        self.inv = InventoryManager()



    def start_looping(self):
        asyncio.run(self.read_client_txt())




    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client_txt.close()

    async def read_client_txt(self,):
        # JUST_DIED = False
        loop = asyncio.get_running_loop()
        loop.call_soon(self.sleeper, loop)
        self.client_txt.readlines()
        while True:
            new_lines = self.client_txt.readlines()
            for line in new_lines:
                # if f"SniixedMinionCuck has been slain." in line:
                #     print("death")
                #     JUST_DIED = True
                if "You have entered" in line:
                    print("changed place")
                    # if JUST_DIED:
                    #     print("now i would reactivate auras")
                    #     ahkpy.sleep(1)
                    #     reactivate_auras()
                    #     JUST_DIED = False
                    if not AUTO_TOGGLE:
                        break
                    else:
                        self.FLASKS_ENABLED = True
                        self.IN_TOWN = False
                        self.IN_SIMULACRUM = False

                    for place in AUTOFLASK_DISABLED_PLACES:
                        if place in line:
                            if AUTO_TOGGLE:
                                self.flask_belt.stop_auto_flask()
                                self.FLASKS_ENABLED = False
                            IN_TOWN = True
                            break
                    for place in SIMULACRUM_PLACES:
                        if place in line:
                            IN_SIMULACRUM = True
                            if AUTO_TOGGLE:
                                FLASKS_ENABLED = True
                                IN_TOWN = False
                            break
                    print("automatically toggled Flasks to: " + ("enabled" if self.FLASKS_ENABLED else "disabled"))

            await asyncio.sleep(CLIENT_TXT_REFRESH_DURATION)

    def sleeper(self,loop):
        ahkpy.sleep(0.01)
        self.inv.root.update()
        loop.call_soon(self.sleeper, loop)


    def stash_all_non_empty_cells(self,):
        if not self.IN_TOWN and not self.IN_SIMULACRUM:
            print("not in town, ignored inv-stash")
            return
        self.inv.stash_all_non_empty_cells()

    def toggle_open_lock_gui(self,):
        if not self.IN_TOWN:  # in a map nobody wants to config the inventory
            print("not in town, ignored opening inv-lock GUI")
            return
        self.inv.toggle_open_lock_gui()


