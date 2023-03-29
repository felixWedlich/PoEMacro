import sys
from functools import reduce
from typing import Tuple, Optional, List

from PIL import Image
import time
import numpy as np

from multiprocessing.shared_memory import SharedMemory
import mss

MANA_BBOX = (2285, 1119, 2513, 1146)
LIFE_BBOX = (50, 1090, 265, 1112)
ES_BBOX = (50, 1119, 265, 1146)


class Detector:

    def __init__(self, bbox: Tuple[int, int, int, int], mem: SharedMemory):

        self.bbox = bbox
        self.mem = mem
        self.chiffres = {}
        self.chiffre_white_idxs = {}
        self.chiffre_white_count = {}

    def _init_attrs(self):

        for i in range(11):
            ex = np.ascontiguousarray(np.array(Image.open(rf"C:\Users\Felix\IdeaProjects\Macro\data\chars\{i}.png")))
            self.chiffres[i] = ex
            self.chiffre_white_idxs[i] = np.where(ex == 254)
            self.chiffre_white_count[i] = np.count_nonzero(self.chiffres[i][self.chiffre_white_idxs[i]])

        self.OFFSETS_Y = {0: 0,
                          1: 0,
                          2: 0,
                          3: 0,
                          4: 0,
                          5: 0,
                          6: -2,
                          7: 0,
                          8: -2,
                          9: 0,
                          10: 13, #commata
                          }

        self.OFFSETS_AFTER = {0: 0,
                              1: 1,
                              2: 0,
                              3: 0,
                              4: 0,
                              5: 0,
                              6: 0,
                              7: 0,
                              8: 0,
                              9: 1,
                              10: 0 #commata
                              }

        self.SLASH_OFFSET_CHECKS = [(6, -1), (10, -2), (14, -3), (18, -4), (21, -5)]

    def detect(self, sct, update_cap:bool):
        im = sct.grab(self.bbox)
        arr = np.array(Image.frombytes("RGB", im.size, im.bgra, "raw", "BGRX").convert("L"))

        # set all non-white pixels black
        arr[arr != 254] = 0
        potential_slash_idxs = np.argwhere(arr[0,])
        if len(potential_slash_idxs):
            potential_slash_idxs = potential_slash_idxs[:, 0]
        valid_idx = []
        for idx in potential_slash_idxs:
            base = np.array((0, idx))
            slash = True
            for slash_offset_check in self.SLASH_OFFSET_CHECKS:
                check = base + slash_offset_check
                if arr[tuple(check)] != 254:
                    slash = False
                    break
            if slash:
                valid_idx.append(idx)
        if len(valid_idx) > 1:
            print("ERROR: found multiple valid_idx")

            # TODO save image
            return
        if len(valid_idx) == 0:
            # print("ERROR: found no valid idx")
            return
        valid_idx = valid_idx[0]
        detected = []

        # only x moves and is decremented every iteration
        x_offset = -5 + valid_idx

        y_base = 1
        while True:
            found = False
            for n, y_offset, x_offset_after in zip(self.OFFSETS_Y.keys(), self.OFFSETS_Y.values(),
                                                   self.OFFSETS_AFTER.values()):
                idx = self.chiffre_white_idxs[n]
                x = x_offset - (self.chiffres[n].shape[1] + x_offset_after)
                idx_offsetted = tuple(idx + np.array([[y_offset + y_base], [x]]))
                try:
                    arr_at_idx = arr[idx_offsetted]
                except IndexError:
                    continue
                non_zero = np.count_nonzero(arr_at_idx)
                # print(n,non_zero)
                if non_zero == self.chiffre_white_count[n]:
                    x_offset -= (self.chiffres[n].shape[1] + x_offset_after)
                    if n != 10:
                        detected.append(n)
                    found = True
                    break
            if not found:
                break
        if not len(detected):
            print("ERROR: did not detect")
            return
        detected.reverse()
        val = reduce(lambda x, y: x * 10 + y, detected)
        # print(val)
        self.mem.buf[0:4] = val.to_bytes(4,byteorder="big")

        if update_cap:
            self.update_cap(valid_idx,arr)
        return val

    def update_cap(self,valid_idx,arr):
        detected = []
        # only x moves and is incremented every iteration
        x_offset = 2 + valid_idx

        y_base = 1
        while True:
            found = False
            for n, y_offset, x_offset_after in zip(self.OFFSETS_Y.keys(), self.OFFSETS_Y.values(),
                                                   self.OFFSETS_AFTER.values()):
                idx = self.chiffre_white_idxs[n]
                idx_offsetted = tuple(idx + np.array([[y_offset + y_base], [x_offset]]))
                try:
                    arr_at_idx = arr[idx_offsetted]
                except IndexError:
                    continue
                non_zero = np.count_nonzero(arr_at_idx)
                # print(n,non_zero)
                if non_zero == self.chiffre_white_count[n]:
                    x_offset += (self.chiffres[n].shape[1] + x_offset_after)
                    if n != 10:
                        detected.append(n)
                    found = True
                    break
            if not found:
                break
        val = reduce(lambda x, y: x * 10 + y, detected)
        # print(val)
        self.mem.buf[7:11] = val.to_bytes(4,byteorder="big")
        print("new cap", val)
        self.mem.buf[6] = 0
        return val

    def _loop(self):
        print("entered _loop")
        with mss.mss() as sct:
            while True:
                if self.mem.buf[4]:  # paused
                    time.sleep(1)
                    continue
                if self.mem.buf[5]:  # stopped
                    break
                val = self.detect(sct, update_cap=self.mem.buf[6])
                if val:
                    self.mem.buf[0:4] = val.to_bytes(4,byteorder="big")

    def _work(self):
        self._init_attrs()
        print("inited, now looping")
        self._loop()

    def start(self):
        self._work()

    def pause(self):
        self.paused.value = 1

    def resume(self):
        self.paused.value = 0

    def stop(self):
        self.stopped.value = 1


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"wrong number of args, was {len(sys.argv)}")
        exit(-1)
    if sys.argv[1] == "L":
        try:
            shared_mem = SharedMemory("LIFE", create=True, size=11)

        except FileExistsError:
            shared_mem = SharedMemory("LIFE", create=False, size=11)

        shared_mem.buf[6] = 1
        detec = Detector(LIFE_BBOX,shared_mem)
        detec.start()
    elif sys.argv[1] == "M":
        try:
            shared_mem = SharedMemory("MANA", create=True, size=6)
        except FileExistsError:
            shared_mem = SharedMemory("MANA", create=False, size=6)
        detec = Detector(MANA_BBOX,shared_mem)
        detec.start()
