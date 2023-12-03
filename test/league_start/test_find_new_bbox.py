import unittest
from multiprocessing.shared_memory import SharedMemory

import mss

from src import Detector

class TestFindNewBBOX(unittest.TestCase):
    def test_es(self):

        pass
    def test_life(self):
        shared_mem = SharedMemory("LIFE", create=True, size=11)
        OLD_BBOX = (50, 1119, 295, 1141)
        detector = Detector(OLD_BBOX,shared_mem)
        detector._init_attrs()
        #first test  identical bbox sizes:
        OLD_HEIGHT = OLD_BBOX[3] - OLD_BBOX[1]
        OLD_WIDTH = OLD_BBOX[2] - OLD_BBOX[0]

        with mss.mss() as sct:
            for x in range(-30,30):
                for y in range(-30,30):
                    new_bbox = (OLD_BBOX[0]+x,OLD_BBOX[1]+y,OLD_BBOX[2]+x,OLD_BBOX[3]+y)
                    detector.bbox = new_bbox
                    val = detector.detect(sct,False)
                    if val:
                        print(f"LIFE: new bbox found {new_bbox}, val: {val}")
                        return

        pass
    def test_mana(self):
        shared_mem = SharedMemory("MANA", create=True, size=11)
        OLD_BBOX = (2285, 1119, 2513, 1146)
        detector = Detector(OLD_BBOX,shared_mem)
        detector._init_attrs()
        #first test  identical bbox sizes:
        OLD_HEIGHT = OLD_BBOX[3] - OLD_BBOX[1]
        OLD_WIDTH = OLD_BBOX[2] - OLD_BBOX[0]

        with mss.mss() as sct:
            # for x in range(-30,30):
            for x in range(-10,10):
                for y in range(-50,0):
                    new_bbox = (OLD_BBOX[0]+x,OLD_BBOX[1]+y,OLD_BBOX[2]+x,OLD_BBOX[3]+y)
                    detector.bbox = new_bbox
                    val = detector.detect(sct,False)
                    if val:
                        print(f"MANA: new bbox found {new_bbox}, val: {val}")
                        return



if __name__ == '__main__':
    unittest.main()
