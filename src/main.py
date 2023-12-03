import configparser

import ahkpy
from src.macro import Macro
from src.utils import gem_swap

if __name__ == '__main__':
    MOUSESPEED = 2
    config = configparser.ConfigParser()
    config.read("settings.cfg")
    macro = Macro(config=config)
    hotkeys = config["hotkeys"]


    @ahkpy.hotkey(f"{hotkeys['STASH_KEY']}")
    def wrap_stash_all_non_empty_cells():
        macro.stash_all_non_empty_cells()


    def wrap_trigger_auto_flask():
        macro.flask_belt.trigger_auto_flask()


    @ahkpy.hotkey(f"{hotkeys['UPDATE_LIFE_MANA_CAPS']}")
    def wrap_update_caps():
        macro.flask_belt.update_caps()


    @ahkpy.hotkey(f"{hotkeys['GEM_SWAP_KEY']}")
    def wrap_gem_swap():
        gem_swap()


    @ahkpy.hotkey(f"~{hotkeys['SECOND_MACRO_TRIGGER_KEY']}")
    def wrap_trigger_auto_flask_1():
        wrap_trigger_auto_flask()


    @ahkpy.hotkey(f"~{hotkeys['MACRO_TRIGGER_KEY']}")
    def wrap_trigger_auto_flask_2():
        wrap_trigger_auto_flask()


    @ahkpy.hotkey(f"{hotkeys['GET_POS_KEY']}")
    def get_pos():
        print("Position (x,y):", ahkpy.get_mouse_pos("screen"))


    @ahkpy.hotkey(f"{hotkeys['LEVEL_GEM_KEY']}")
    def level_up_gem():
        with ahkpy.block_mouse_move(), ahkpy.block_input():
            print("leveling gem")
            prev_x, prev_y = ahkpy.get_mouse_pos("screen")
            ahkpy.mouse_move(config.getint('hotkeys','GEM_LEVEL_X'), config.getint('hotkeys','GEM_LEVEL_Y'),
                             relative_to="screen", speed=MOUSESPEED)
            ahkpy.send("{Ctrl down}")
            ahkpy.mouse_press("left")
            ahkpy.mouse_release("left")
            ahkpy.mouse_move(prev_x, prev_y, relative_to="screen", speed=MOUSESPEED)
            if config.getboolean('hotkeys', 'LEVEL_GEM_CLICK_OLD_MOUSE_POS'):
                ahkpy.mouse_press("left")
                ahkpy.mouse_release("left")


    @ahkpy.hotkey(f"{hotkeys['HIDEOUT_KEY']}")
    def hideout_macro():
        ahkpy.send("{Enter}")
        ahkpy.send("/hideout {Enter}")


    @ahkpy.hotkey(f"{hotkeys['LOGOUT_KEY']}")
    def logout_macro():
        ahkpy.send("{Enter}")
        ahkpy.send("/exit {Enter}")


    @ahkpy.hotkey(f"~{hotkeys['MACRO_TRIGGER_KEY']} Up")
    def wrap_timestamp_right_mouse_up():
        macro.flask_belt.timestamp_right_mouse_up()


    @ahkpy.hotkey(f"{hotkeys['MANUAL_TOGGLE_FLASK_KEY']}")
    def wrap_manual_toggle_flasks():
        macro.flask_belt.manual_toggle_flasks()


    @ahkpy.hotkey(f"{hotkeys['INV_LOCK_TOGGLE_MENU_KEY']}")
    def wrap_toggle_open_lock_gui():
        print("inv locking toggle")
        macro.toggle_open_lock_gui()


    @ahkpy.hotkey(f"{hotkeys['FAST_CLICK_TOGGLE']}")
    def fast_click_toggle():
        ahkpy.sleep(0.05)  # sleep a bit till the hotkey is up again, TODO prolly do this with waiting till up
        macro.inv.fast_click_toggle()


    macro.start_looping()
