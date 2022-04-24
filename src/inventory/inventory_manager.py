import ahkpy
import numpy as np
from tkinter import Tk, Canvas

from src.config import inv_cell_info, EMPTY_CELL_FP, EMPTY_CELL_XY_ALT_FP, EMPTY_CELL_Y_ALT_FP, EMPTY_CELL_X_ALT_FP, inv_locked
from src.utils import images_to_cells

from PIL import Image, ImageGrab

class InventoryManager:

    def __init__(self):
        self.spam_click_timer = ahkpy.set_timer(0.1,self._ctrl_click)
        self.spam_click_timer.stop()
        self.FAST_CLICKING = False


        # gui and hooks for locking stash cells to not be autodumped
        self.inv_locked = inv_locked

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
        self.empty_cell_ref = {(70,70):  np.array(Image.open(EMPTY_CELL_FP).convert("L")).astype(int),
                               (71,70):  np.array(Image.open(EMPTY_CELL_Y_ALT_FP).convert("L")).astype(int),
                               (70,71):  np.array(Image.open(EMPTY_CELL_X_ALT_FP).convert("L")).astype(int),
                               (71,71):  np.array(Image.open(EMPTY_CELL_XY_ALT_FP).convert("L")).astype(int)}

    @staticmethod
    def _ctrl_click():
        ahkpy.mouse_press()
        ahkpy.mouse_release()
    @staticmethod
    def _get_row_col_from_x_y(x: int, y: int) -> (int, int):
        assert x >= 0
        assert y >= 0

        return x // inv_cell_info.width_c, y // inv_cell_info.height_r


    def mark_locked_cell(self,event):
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

    def toggle_open_lock_gui(self,):
        if self.LOCK_GUI_SHOWN:
            self.root.withdraw()
        else:
            self.root.deiconify()
        self.LOCK_GUI_SHOWN = not self.LOCK_GUI_SHOWN

    def stash_all_non_empty_cells(self,):
        STASH_DIFF_THRESH = 100
        print("="*40)
        ahkpy.sleep(0.2)
        MOUSESPEED = 2

        # playsound.playsound(r"C:\Users\Felix\IdeaProjects\Macro\dump_it.mp3",block=False)
        # with ahkpy.block_input():
        im = ImageGrab.grab(bbox=inv_cell_info.get_bbox()).convert("L")
        split_image = images_to_cells(np.array(im),inv_cell_info)
        large_item_need_not_click = [[0 for _ in range(inv_cell_info.n_r)] for _ in range(inv_cell_info.n_c)]
        for c, r, cell in split_image:
            cell = cell.astype(int)

            diff = np.subtract(cell, self.empty_cell_ref[cell.shape])
            # if c in inv_cell_info.alt_c and r in inv_cell_info.alt_r:
            #     diff = np.subtract(cell, EMPTY_CELL_XY_SCUFFED)
            # elif c in inv_cell_info.alt_c:
            #     diff = np.subtract(cell, EMPTY_CELL_X_SCUFFED)
            # elif r in inv_cell_info.alt_r:
            #     diff = np.subtract(cell, EMPTY_CELL_Y_SCUFFED)
            # else:
            #     diff = np.subtract(cell, EMPTY_CELL)
            # Image.fromarray(diff).save(f"pics/diff_c{c}_r{r}.png")
            s = np.sqrt(np.sum(np.abs(diff)))
            if s > STASH_DIFF_THRESH:
                if self.inv_locked[c][r]:
                    continue
                # if large_item_need_not_click [c][r]:
                #     #print("skipped click")
                #     continue
                # check_right_border_index = c
                # check_lower_border_index = r
                # while check_right_border_index + 1 < inv_cell_info.n_c:
                #     i = check_right_border_index * inv_cell_info.n_r + r
                #     if not check_right_border(split_image[i][2]):
                #         break
                #     #print("item extends right")
                #     #large_item_need_not_click[check_right_border_index][r] = True
                #     check_right_border_index += 1
                # while check_lower_border_index + 1 < inv_cell_info.n_r:
                #     i = c*inv_cell_info.n_r + check_lower_border_index
                #     if not check_lower_border(split_image[i][2]):
                #         break
                #
                #     #print("item extends down")
                #     #large_item_need_not_click[c][check_lower_border_index] = True
                #     check_lower_border_index += 1
                # for c_i in range(c,check_right_border_index+1):
                #     for r_i in range(r,check_lower_border_index+1):
                #         if c_i == c and r_i == r:
                #             continue
                #         large_item_need_not_click[c_i][r_i] = True
                print(c, r, s)

                self.ctrl_click_cell(c,r)
        MOUSESPEED = 1
    @staticmethod
    def ctrl_click_cell(c: int , r:int):
        ahkpy.mouse_move(inv_cell_info.start_x + (0.5 + c) * inv_cell_info.width_c, inv_cell_info.start_y + (0.5 + r) * inv_cell_info.height_r,
                         relative_to="screen", speed=2)
        ahkpy.send("{Ctrl down}")
        ahkpy.mouse_press("left")
        ahkpy.mouse_release("left")
        ahkpy.send("{Ctrl up}")