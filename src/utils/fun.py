from typing import List, Tuple, Union, Dict

import numpy as np
import ahkpy


class CellInfo:

    def __init__(self, n_c: int,
                 n_r: int,
                 width_c: int,
                 height_r: int,
                 alt_width_c: int,
                 alt_height_r: int,
                 alt_c: List[int],
                 alt_r: List[int],
                 start_x,
                 start_y,
                 ):
        self.n_c = n_c
        self.n_r = n_r
        self.width_c = width_c
        self.height_r = height_r
        self.alt_width_c = alt_width_c
        self.alt_height_r = alt_height_r
        self.alt_c = alt_c
        self.alt_r = alt_r
        self.start_x = start_x
        self.start_y = start_y

    def get_inv_width(self) -> int:
        return (self.n_c - len(self.alt_c)) * self.width_c + len(self.alt_c) * self.alt_width_c

    def get_inv_height(self) -> int:
        return (self.n_r - len(self.alt_r)) * self.height_r + len(self.alt_r) * self.alt_height_r

    def get_bbox(self) -> Tuple[int, int, int, int]:
        return (self.start_x, self.start_y, self.start_x + self.get_inv_width(), self.start_y + self.get_inv_height())


def images_to_cells(matrix: np.array, cell_info: CellInfo) -> List[Tuple[int, int, np.array]]:
    cells = []
    base_x = 0
    for c in range(cell_info.n_c):  # iterate through columns
        base_y = 0
        w = cell_info.alt_width_c if c in cell_info.alt_c else cell_info.width_c
        for r in range(cell_info.n_r):  # iterate through rows:
            h = cell_info.alt_height_r if r in cell_info.alt_r else cell_info.height_r
            slice_m = matrix[base_y:base_y + h, base_x:base_x + w]
            cells.append((c, r, slice_m))
            base_y += h
        base_x += w
    return cells


def gem_swap():
    GEMS_SWAP_SPEED = 1
    print("gem swap")
    ahkpy.wait_key_released("RButton")
    ahkpy.wait_key_released("LButton")

    with ahkpy.block_input():
        ahkpy.sleep(0.1)
        ahkpy.send("i")
        ahkpy.mouse_move(1731, 1090, relative_to="screen", speed=GEMS_SWAP_SPEED)
        ahkpy.sleep(0.1)
        ahkpy.mouse_press("left")
        ahkpy.mouse_release("left")
        ahkpy.mouse_move(2150, 178, relative_to="screen", speed=GEMS_SWAP_SPEED)
        ahkpy.sleep(0.1)
        ahkpy.mouse_press("left")
        ahkpy.mouse_release("left")
        ahkpy.mouse_move(1731, 1090, relative_to="screen", speed=GEMS_SWAP_SPEED)
        ahkpy.sleep(0.1)
        ahkpy.mouse_press("left")
        ahkpy.mouse_release("left")
        ahkpy.sleep(0.1)
        ahkpy.send("i")
        ahkpy.sleep(0.2)
