from functools import reduce

from PIL import Image
import time
import numpy as np
from multiprocessing import Process, Value

import mss

MANA_BBOX = (*(2285, 1119), *(2513, 1146))
LIFE_BBOX = (*(50, 1090), *(265, 1112))
ES_BBOX = (*(50, 1119), *(265, 1146))


class Detector:

    def __init__(self, bbox=MANA_BBOX):
        self.bbox = bbox
        self.p = Process(target=self._work, )
        self.paused = Value("i", 0)
        self.stopped = Value("i", 0)
        self.chiffres = {}
        self.chiffre_white_idxs = {}
        self.chiffre_white_count = {}

    def _init_attrs(self):

        for i in range(10):
            ex = np.ascontiguousarray(np.array(Image.open(f"data/chars/{i}.png")))
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
                              }

        self.SLASH_OFFSET_CHECKS = [(6, -1), (10, -2), (14, -3), (18, -4), (21, -5)]

    def _loop(self):
        print("entered _loop")
        with mss.mss() as sct:
            monitor = sct.monitors[0]

            while True:
                if self.paused.value:
                    time.sleep(1)
                    continue
                if self.stopped.value:
                    break
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
                    continue
                if len(valid_idx) == 0:
                    print("ERROR: found no valid idx")
                    continue
                valid_idx = valid_idx[0]
                detected = []

                # only x moves and is decremented every iteration
                x_offset = -5 + valid_idx

                y_base = 1
                while True:
                    found = False
                    for n, y_offset, x_offset_after in zip(range(10), self.OFFSETS_Y.values(),
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
                            detected.append(n)
                            found = True
                            break
                    if not found:
                        break
                if not len(detected):
                    print("ERROR: did not detect")
                detected.reverse()
                print(reduce(lambda x, y: x * 10 + y, detected))

    def _work(self):
        self._init_attrs()
        print("inited, now looping")
        self._loop()

    def start(self):
        self.p.start()

    def pause(self):
        self.paused.value = 1

    def resume(self):
        self.paused.value = 0

    def stop(self):
        self.stopped.value = 1
        self.p.join()
