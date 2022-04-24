import ahkpy
from macro import Macro
from src.config import CLIENT_TXT_LOCATION,MANUAL_TOGGLE_FLASK_KEY, HIDEOUT_KEY, GUILD_HIDEOUT_KEY, STASH_KEY, LOGOUT_KEY, GEM_SWAP_KEY, LEVEL_GEM_KEY, INV_LOCK_TOGGLE_MENU_KEY, MACRO_TRIGGER_KEY, GET_POS_KEY
from src.config import FAST_CLICK_TOGGLE, GEM_LEVEL_X, GEM_LEVEL_Y, LEVEL_GEM_CLICK_OLD_MOUSE_POS
if __name__ == '__main__':
    MOUSESPEED = 2
    macro = Macro(client_txt_fp=CLIENT_TXT_LOCATION)


    @ahkpy.hotkey(f"{STASH_KEY}")
    def wrap_stash_all_non_empty_cells():
        macro.stash_all_non_empty_cells()


    @ahkpy.hotkey(f"~{MACRO_TRIGGER_KEY}")
    def wrap_trigger_auto_flask():
        macro.flask_belt.trigger_auto_flask()


    @ahkpy.hotkey(GET_POS_KEY)
    def get_pos():
        print("Position (x,y):", ahkpy.get_mouse_pos("screen"))


    @ahkpy.hotkey(f"{LEVEL_GEM_KEY}")
    def level_up_gem():
        with ahkpy.block_mouse_move(), ahkpy.block_input():
            print("leveling gem")
            prev_x, prev_y = ahkpy.get_mouse_pos("screen")
            ahkpy.mouse_move(GEM_LEVEL_X, GEM_LEVEL_Y,
                             relative_to="screen", speed=MOUSESPEED)
            ahkpy.send("{Ctrl down}")
            ahkpy.mouse_press("left")
            ahkpy.mouse_release("left")
            ahkpy.mouse_move(prev_x, prev_y, relative_to="screen", speed=MOUSESPEED)
            if LEVEL_GEM_CLICK_OLD_MOUSE_POS:
                ahkpy.mouse_press("left")
                ahkpy.mouse_release("left")


    @ahkpy.hotkey(f"{HIDEOUT_KEY}")
    def hideout_macro():
        ahkpy.send("{Enter}")
        ahkpy.send("/hideout {Enter}")


    @ahkpy.hotkey(f"{LOGOUT_KEY}")
    def logout_macro():
        ahkpy.send("{Enter}")
        ahkpy.send("/exit {Enter}")


    @ahkpy.hotkey(f"~{MACRO_TRIGGER_KEY} Up")
    def wrap_timestamp_right_mouse_up():
        macro.flask_belt.timestamp_right_mouse_up()


    @ahkpy.hotkey(f"{MANUAL_TOGGLE_FLASK_KEY}")
    def wrap_manual_toggle_flasks():
        macro.flask_belt.manual_toggle_flasks()


    @ahkpy.hotkey(f"{INV_LOCK_TOGGLE_MENU_KEY}")
    def wrap_toggle_open_lock_gui():
        print("inv locking toggle")
        macro.toggle_open_lock_gui()

    @ahkpy.hotkey(f"{FAST_CLICK_TOGGLE}")
    def fast_click_toggle():
        ahkpy.sleep(0.05) # sleep a bit till the hotkey is up again, TODO prolly do this with waiting till up
        macro.inv.fast_click_toggle()


    macro.start_looping()