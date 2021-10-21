import ahkpy

import asyncio
from tkinter import *
from PIL import ImageGrab
from config import *
from typing import List, Tuple


async def read_client_txt():
    global FLASKS_ENABLED, IN_TOWN
    with open(CLIENT_TXT_LOCATION, "r", encoding="utf-8") as client_txt:
        client_txt.readlines()
        loop = asyncio.get_running_loop()
        loop.call_soon(sleeper, loop)
        while True:
            new_lines = client_txt.readlines()
            for line in new_lines:
                if "You have entered" in line:
                    if not AUTO_TOGGLE:
                        break
                    if AUTO_TOGGLE:
                        FLASKS_ENABLED = True
                        IN_TOWN = False
                    for place in AUTOFLASK_DISABLED_PLACES:
                        if place in line:
                            if AUTO_TOGGLE:
                                stop_auto_flask()
                                FLASKS_ENABLED = False
                            IN_TOWN = True
                            break
                    print("automatically toggled Flasks to: " + ("enabled" if FLASKS_ENABLED else "disabled"))

            await asyncio.sleep(CLIENT_TXT_REFRESH_DURATION)


def sleeper(loop):
    ahkpy.sleep(0.01)
    root.update()
    loop.call_soon(sleeper, loop)


def stop_auto_flask():
    global FLASKS_RUNNING
    if ahkpy.is_key_pressed(f"{MACRO_TRIGGER_KEY}"):
        FLASK_TIMEOUT_TIMER.update(interval=FLASK_TIMEOUT)
        return
    for flask in FLASKS:
        flask.stop()
        FLASKS_RUNNING = False
    print("stopped auto flasking")
    FLASK_TIMEOUT_TIMER.stop()


FLASKS_ENABLED = False
FLASKS_RUNNING = False
FLASK_TIMEOUT_TIMER = ahkpy.set_countdown(FLASK_TIMEOUT, stop_auto_flask)
FLASK_TIMEOUT_TIMER.stop()


@ahkpy.hotkey(f"~{MACRO_TRIGGER_KEY}")
def trigger_auto_flask():  # TODO consider only triggering if PoE is the main window
    global FLASKS_RUNNING
    if FLASKS_ENABLED and not FLASKS_RUNNING:
        print("started macro, due to pressing the macro trigger key")
        for flask in FLASKS:
            flask.hard_start()
        FLASKS_RUNNING = True


CHAT_PAUSE = False

"""
2 Functions to disable chat,because the decorators cant be stacked
pause/restart of flasking is desired on shift enter and normal enter
"""

if DISABLE_MACRO_WHILE_CHAT:
    @ahkpy.hotkey("~Enter")
    def pause_flask():
        global CHAT_PAUSE
        if not FLASKS_RUNNING:
            return
        if CHAT_PAUSE:  # reenable flasks
            print("reenabling flasks, after chat")
            for flask in FLASKS:
                flask.hard_start()
                FLASK_TIMEOUT_TIMER.start()
        else:
            print("disabling flasks, due to chat")
            for flask in FLASKS:
                flask.stop()
                FLASK_TIMEOUT_TIMER.stop()
        CHAT_PAUSE = not CHAT_PAUSE

if DISABLE_MACRO_WHILE_CHAT:
    @ahkpy.hotkey("~+Enter")
    def pause_flask2():
        global CHAT_PAUSE
        if not FLASKS_RUNNING:
            return
        if CHAT_PAUSE:  # reenable flasks
            print("reenabling flasks, after chat")
            for flask in FLASKS:
                flask.hard_start()  # TODO consider if soft start is fine here?
                FLASK_TIMEOUT_TIMER.start()

        else:
            print("disabling flasks, due to chat")
            for flask in FLASKS:
                flask.stop()
                FLASK_TIMEOUT_TIMER.stop()
        CHAT_PAUSE = not CHAT_PAUSE

if GET_POS_KEY:
    @ahkpy.hotkey(GET_POS_KEY)
    def get_pos():
        print("Position (x,y):", ahkpy.get_mouse_pos("screen"))

if LEVEL_GEM_KEY:
    @ahkpy.hotkey(f"{LEVEL_GEM_KEY}")
    def level_up_gem():

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

if HIDEOUT_KEY:
    @ahkpy.hotkey(f"{HIDEOUT_KEY}")
    def hideout_macro():
        ahkpy.send("{Enter}")
        ahkpy.send("/hideout {Enter}")

if LOGOUT_KEY:
    @ahkpy.hotkey(f"{LOGOUT_KEY}")
    def logout_macro():
        ahkpy.send("{Enter}")
        ahkpy.send("/exit {Enter}")

if GUILD_HIDEOUT_KEY:
    @ahkpy.hotkey(f"{GUILD_HIDEOUT_KEY}")
    def guild_hideout_macro():
        ahkpy.send("{Enter}")
        ahkpy.send("/hideout {Enter}")  # TODO


@ahkpy.hotkey(f"~{MACRO_TRIGGER_KEY} Up")
def timestamp_right_mouse_up():
    global FLASK_TIMEOUT_TIMER
    if FLASKS_ENABLED and FLASKS_RUNNING:
        FLASK_TIMEOUT_TIMER.update(interval=FLASK_TIMEOUT)


def get_row_col_from_x_y(x: int, y: int) -> (int, int):
    assert x >= 0
    assert y >= 0

    return x // INV_CELL_WIDTH, y // INV_CELL_HEIGHT


def mark_locked_cell(event: Event):
    x, y = event.x, event.y
    i, j = get_row_col_from_x_y(x, y)
    if inv_locked[i][j]:
        cell_gui.delete(inv_locked[i][j])
        inv_locked[i][j] = 0
    else:
        ret = cell_gui.create_rectangle(i * INV_CELL_WIDTH, j * INV_CELL_HEIGHT, (1 + i) * INV_CELL_WIDTH,
                                        (1 + j) * INV_CELL_HEIGHT, fill='red')

        inv_locked[i][j] = ret


def scuffed_image_to_cells_1080p(matrix: np.array) -> List[Tuple[int, int, np.array]]:
    cells = []
    base_x = 0
    for c in range(12):  # iterate through columns
        base_y = 0
        w = INV_CELL_WIDTH_SCUFFED if c in SCUFFED_COLUMNS else INV_CELL_WIDTH
        for r in range(5):  # iterate through rows:
            h = INV_CELL_HEIGHT_SCUFFED if r in SCUFFED_ROWS else INV_CELL_HEIGHT
            slice_m = matrix[base_y:base_y + h, base_x:base_x + w]
            cells.append((c, r, slice_m))
            # Image.fromarray(slice_m).save(f"pics/cells_c{c}_r{r}.png")
            base_y += h
        base_x += w
    return cells


@ahkpy.hotkey(f"{MANUAL_TOGGLE_FLASK_KEY}")
def toggle_flasks():
    global FLASKS_ENABLED
    FLASKS_ENABLED = not FLASKS_ENABLED
    print("manually toggled Flasks to: " + ("enabled" if FLASKS_ENABLED else "disabled"))


def clear_highlights(event: Event):
    for i in range(INV_COLUMNS):
        for j in range(INV_ROWS):
            cell = inv_highlighted[i][j]
            if cell:
                cell_gui.delete(cell)
                inv_highlighted[i][j] = 0


@ahkpy.hotkey(f"{INV_LOCK_TOGGLE_MENU_KEY}")
def toggle_open_lock_gui():
    if not IN_TOWN:  # in a map nobody wants to config the inventory
        print("not in town, ignored opening inv-lock GUI")
        return
    global LOCK_GUI_SHOWN
    if LOCK_GUI_SHOWN:
        root.withdraw()
    else:
        root.deiconify()
    LOCK_GUI_SHOWN = not LOCK_GUI_SHOWN


@ahkpy.hotkey("F3")
def screenshot_inv():
    im = ImageGrab.grab(bbox=(INV_START_X, INV_START_Y, INV_START_X + INV_WIDTH, INV_START_Y + INV_HEIGHT))
    im.save(f"pics/full.png")
    im = im.convert("L")
    print(np.array(im).shape)
    for c, r, cell in scuffed_image_to_cells_1080p(np.array(im)):
        # cell = cell.astype(int)
        Image.fromarray(cell).save(f"pics/cell_c{c}_r{r}.png")


@ahkpy.hotkey(f"{STASH_KEY}")
def stash_all_non_empty_cells():
    ahkpy.sleep(0.2)
    if not IN_TOWN:  # in a map nobody wants to autostash
        print("not in town, ignored inv-stash")
        return
    ahkpy.block_input()
    im = ImageGrab.grab(bbox=(INV_START_X, INV_START_Y, INV_START_X + INV_WIDTH, INV_START_Y + INV_HEIGHT)).convert("L")
    for c, r, cell in scuffed_image_to_cells_1080p(np.array(im)):
        cell = cell.astype(int)
        if c in SCUFFED_COLUMNS and r in SCUFFED_ROWS:
            diff = np.subtract(cell, EMPTY_CELL_XY_SCUFFED)
        elif c in SCUFFED_COLUMNS:
            diff = np.subtract(cell, EMPTY_CELL_X_SCUFFED)
        elif r in SCUFFED_ROWS:
            diff = np.subtract(cell, EMPTY_CELL_Y_SCUFFED)
        else:
            diff = np.subtract(cell, EMPTY_CELL)
        # Image.fromarray(diff).save(f"pics/diff_c{c}_r{r}.png")
        s = np.sqrt(np.sum(np.abs(diff)))

        if s > STASH_DIFF_THRESH:
            print(c,r,s)
            if inv_locked[c][r]:
                continue

            ahkpy.mouse_move(INV_START_X + (0.5 + c) * INV_CELL_WIDTH, INV_START_Y + (0.5 + r) * INV_CELL_HEIGHT,
                             relative_to="screen", speed=MOUSESPEED)
            ahkpy.send("{Ctrl down}")
            ahkpy.mouse_press("left")
            ahkpy.mouse_release("left")
            ahkpy.send("{Ctrl up}")


root = Tk()

root.geometry("400x400")

root.attributes('-alpha', 0.1)
root.overrideredirect(True)
cell_gui = Canvas(root, width=INV_WIDTH, height=INV_HEIGHT)
cell_gui.pack()
root.geometry('%dx%d+%d+%d' % (INV_WIDTH, INV_HEIGHT, INV_START_X, INV_START_Y))
root.attributes('-topmost', True)  # note - before topmost
root.bind("<Button-1>", mark_locked_cell)
root.withdraw()
# root.mainloop()

asyncio.run(read_client_txt())
