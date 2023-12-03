from multiprocessing.shared_memory import SharedMemory

import ahkpy
import mss

from src import Detector


MANA_BBOX = (2255, 1012, 2547, 1139)
LIFE_BBOX = (50, 1119, 295, 1141)
# MANA_BBOX = (2255, 1111, 2483, 1139)
# shared_mem = SharedMemory("MANA", create=True, size=11)
shared_mem = SharedMemory("LIFE", create=True, size=11)
# detector = Detector(MANA_BBOX,shared_mem)
detector = Detector(LIFE_BBOX,shared_mem)
detector._init_attrs()

@ahkpy.hotkey(f"F4")
def d():
    idx = detector.find_slash_idx()
    cap = detector.read_cap()
    val = detector.read_current_value()
    print(f"idx: {idx}, cap: {cap}, val: {val}")

@ahkpy.hotkey(f"!a")
def get_pos():
    print("Position (x,y):", ahkpy.get_mouse_pos("screen"))