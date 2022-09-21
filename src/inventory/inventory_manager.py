import configparser
from typing import List, Tuple

import ahkpy
import numpy as np
from tkinter import Tk, Canvas

from PIL import Image, ImageGrab
from dataclasses import dataclass


@dataclass
class CellInfo:
    n_c: int
    n_r: int
    width_c: int
    height_r: int
    alt_width_c: int
    alt_height_r: int
    alt_c: List[int]
    alt_r: List[int]
    start_x: int
    start_y: int

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

# 1440p specific
inv_cell_info = CellInfo(n_c=12,
                         n_r=5,
                         width_c=70,
                         height_r=70,
                         alt_width_c=71,
                         alt_height_r=71,
                         alt_c=[4, 9],
                         alt_r=[2],
                         start_x=1696,
                         start_y=784
                         )

class InventoryManager:

    def __init__(self, config: configparser.ConfigParser):

        self.MOUSE_SPEED = config.getint('inventory', 'MOUSE_SPEED')

        self.spam_click_timer = ahkpy.set_timer(0.1, self._ctrl_click)
        self.spam_click_timer.stop()
        self.FAST_CLICKING = False

        # gui and hooks for locking stash cells to not be autodumped
        first_n_locked_cells = config.getint('inventory', 'FIRST_N_CELLS_LOCKED')
        self.inv_locked = [[1 if first_n_locked_cells < row + col * 5 else 0 for row in range(5)] for col in range(12)]

        self.root = Tk()

        self.root.geometry("400x400")

        self.root.attributes('-alpha', 0.1)
        self.root.overrideredirect(True)
        self.cell_gui = Canvas(self.root, width=inv_cell_info.get_inv_width(), height=inv_cell_info.get_inv_height())
        self.cell_gui.pack()
        self.root.geometry('%dx%d+%d+%d' % (inv_cell_info.get_inv_width(),
                                            inv_cell_info.get_inv_height(),
                                            inv_cell_info.start_x,
                                            inv_cell_info.start_y))
        self.root.attributes('-topmost', True)  # note - before topmost
        self.root.bind("<Button-1>", self.mark_locked_cell)
        self.root.withdraw()

        self.LOCK_GUI_SHOWN = False
        self.empty_cell_ref = {(70, 70): np.array(Image.open("data/empty_cells/empty70x70.png").convert("L")).astype(int),
                               (71, 70): np.array(Image.open("data/empty_cells/empty70x71.png").convert("L")).astype(int),
                               (70, 71): np.array(Image.open("data/empty_cells/empty71x70.png").convert("L")).astype(int),
                               (71, 71): np.array(Image.open("data/empty_cells/empty71x71.png").convert("L")).astype(int)}

    @staticmethod
    def _ctrl_click():
        ahkpy.mouse_press()
        ahkpy.mouse_release()

    @staticmethod
    def _get_row_col_from_x_y(x: int, y: int) -> (int, int):
        assert x >= 0
        assert y >= 0

        return x // inv_cell_info.width_c, y // inv_cell_info.height_r

    def mark_locked_cell(self, event):
        x, y = event.x, event.y
        i, j = self._get_row_col_from_x_y(x, y)
        if self.inv_locked[i][j]:
            self.cell_gui.delete(self.inv_locked[i][j])
            self.inv_locked[i][j] = 0
        else:
            ret = self.cell_gui.create_rectangle(i * inv_cell_info.width_c,
                                                 j * inv_cell_info.height_r,
                                                 (1 + i) * inv_cell_info.width_c,
                                                 (1 + j) * inv_cell_info.height_r,
                                                 fill='red')

            self.inv_locked[i][j] = ret

    def fast_click_toggle(self):
        if self.FAST_CLICKING:
            self.spam_click_timer.stop()
            self.FAST_CLICKING = False
        else:
            self.spam_click_timer.start()
            self.FAST_CLICKING = True

    def toggle_open_lock_gui(self, ):
        if self.LOCK_GUI_SHOWN:
            self.root.withdraw()
        else:
            self.root.deiconify()
        self.LOCK_GUI_SHOWN = not self.LOCK_GUI_SHOWN

    def stash_all_non_empty_cells(self, ):
        STASH_DIFF_THRESH = 100
        print("=" * 40)
        ahkpy.sleep(0.2)

        im = ImageGrab.grab(bbox=inv_cell_info.get_bbox()).convert("L")
        split_image = images_to_cells(np.array(im), inv_cell_info)
        large_item_need_not_click = [[0 for _ in range(inv_cell_info.n_r)] for _ in range(inv_cell_info.n_c)]
        for c, r, cell in split_image:
            cell = cell.astype(int)

            diff = np.subtract(cell, self.empty_cell_ref[cell.shape])

            s = np.sqrt(np.sum(np.abs(diff)))
            if s > STASH_DIFF_THRESH:
                if self.inv_locked[c][r]:
                    continue
                if large_item_need_not_click[c][r]:
                    continue
                check_right_border_index = c
                check_lower_border_index = r
                while check_right_border_index + 1 < inv_cell_info.n_c:
                    i = check_right_border_index * inv_cell_info.n_r + r
                    if not self.check_right_border(split_image[i][2]):
                        break
                    # print("item extends right")
                    # large_item_need_not_click[check_right_border_index][r] = True
                    check_right_border_index += 1
                while check_lower_border_index + 1 < inv_cell_info.n_r:
                    i = c * inv_cell_info.n_r + check_lower_border_index
                    if not self.check_lower_border(split_image[i][2]):
                        break

                    # print("item extends down")
                    # large_item_need_not_click[c][check_lower_border_index] = True
                    check_lower_border_index += 1
                for c_i in range(c, check_right_border_index + 1):
                    for r_i in range(r, check_lower_border_index + 1):
                        if c_i == c and r_i == r:
                            continue
                        large_item_need_not_click[c_i][r_i] = True
                print(c, r, s)

                self.ctrl_click_cell(c, r)

    @staticmethod
    def check_lower_border(cell: np.array, n: int = 2) -> bool:
        """
        look at the last n rows of cells, ignoring the lowest 2 rows of cells (border)
        :param cell:
        :return:
        """
        slice = cell[-(n + 2):-2, :]
        print("lower_border:", np.sum(np.sqrt(slice)))
        return np.sum(np.sqrt(slice)) > (1200 / n)

    @staticmethod
    def check_right_border(cell: np.array, n: int = 2) -> bool:
        """
        look at the last n columns of cells, ignoring the lowest 2 columns of cells (border)
        :param cell:
        :return:
        """
        slice = cell[:, -(n + 2):-2]
        print("right_border:", np.sum(np.sqrt(slice)))
        return np.sum(np.sqrt(slice)) > (1200 / n)

    def ctrl_click_cell(self, c: int, r: int):
        ahkpy.mouse_move(inv_cell_info.start_x + (0.5 + c) * inv_cell_info.width_c, inv_cell_info.start_y + (0.5 + r) * inv_cell_info.height_r,
                         relative_to="screen", speed=self.MOUSE_SPEED)
        ahkpy.send("{Ctrl down}")
        ahkpy.mouse_press("left")
        ahkpy.mouse_release("left")
        ahkpy.send("{Ctrl up}")
