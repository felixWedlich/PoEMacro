import sys
from functools import reduce
from typing import Tuple, Optional, List

from PIL import Image
import time
import numpy as np

from multiprocessing.shared_memory import SharedMemory
import mss

MANA_BBOX = (2255, 1012, 2547, 1139)
# LIFE_BBOX = (20, 1083, 295, 1105)
LIFE_BBOX = (50, 1110, 295, 1141) #offset due to EB
ES_BBOX = (50, 1119, 265, 1146)


class Detector:

    def __init__(self, bbox: Tuple[int, int, int, int], mem: SharedMemory):

        self.bbox = bbox
        self.mem = mem
        self.chiffres = {}
        self.chiffre_white_idxs = {}
        self.chiffre_white_count = {}

        self.sct = mss.mss()
        self.idx = None

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

        # loop until a slash was found
        while not self.find_slash_idx():
            pass
        print("finished init")

    def find_slash_idx(self) -> Optional[Tuple[int,int]]:
        im = self.sct.grab(self.bbox)
        arr = np.array(Image.frombytes("RGB", im.size, im.bgra, "raw", "BGRX").convert("L"))

        # set all non-white pixels black
        arr[arr != 254] = 0

        # iterate through every row of the image in search of white pixels, to check if the are the top of the slash
        # skip last 22 rows, as the slash is atleast 21 px rows wide
        for y in range(arr.shape[0]-21):

            potential_slash_idxs = np.argwhere(arr[y,])
            # if any white pixels found: change the 2d array to 1d
            if len(potential_slash_idxs):
                potential_slash_idxs = potential_slash_idxs[:, 0]
            # check every potential idx, if satisfies all the pixel-checks of a slash:
            for x in potential_slash_idxs:
                base = np.array((y, x))
                slash = True
                for slash_offset_check in self.SLASH_OFFSET_CHECKS:
                    check = base + slash_offset_check
                    if arr[tuple(check)] != 254:
                        slash = False
                        break
                if slash:
                    self.idx = y,x
                    return y,x
        return None

    def read_current_value(self) -> Optional[int]:
        im = self.sct.grab(self.bbox)
        arr = np.array(Image.frombytes("RGB", im.size, im.bgra, "raw", "BGRX").convert("L"))

        # set all non-white pixels black
        arr[arr != 254] = 0

        # quick check if the slash-start pixel is not white (e.g. in a loadingscreen/inv open)
        if arr[self.idx] != 254:
            return
        # all chifres that were detected from the slash to the left (so reversed order)
        detected: List[int] = []

        # only x moves and is decremented every iteration
        x_offset = -5 + self.idx[1]

        y_base = 1 + self.idx[0]
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
            return
        detected.reverse()
        val = reduce(lambda x, y: x * 10 + y, detected)
        # print(val)
        self.mem.buf[0:4] = val.to_bytes(4,byteorder="big")
        return val

    def read_cap(self):
        im = self.sct.grab(self.bbox)
        arr = np.array(Image.frombytes("RGB", im.size, im.bgra, "raw", "BGRX").convert("L"))

        # set all non-white pixels black
        arr[arr != 254] = 0


        detected = []
        # only x moves and is incremented every iteration
        x_offset = 2 + self.idx[1]

        y_base = 1 + self.idx[0]
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
        # set the shared memory responsible that indicates "update the cap" to 0 as it was successfully done
        self.mem.buf[6] = 0
        return val

    def _loop(self):
        while True:
            if self.mem.buf[4]:  # paused
                time.sleep(1)
                continue
            if self.mem.buf[5]:  # stopped
                break
            if self.mem.buf[6]: # update cap
                self.find_slash_idx()
                self.read_cap()
            self.read_current_value()



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
            shared_mem = SharedMemory("MANA", create=True, size=11)
        except FileExistsError:
            shared_mem = SharedMemory("MANA", create=False, size=11)
        detec = Detector(MANA_BBOX,shared_mem)
        detec.start()
