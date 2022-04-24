
from src.utils import CellInfo

#HOTKEYS






MOUSESPEED = 2

inv_cell_info = CellInfo(n_c=12,
                         n_r=5,
                         width_c=70,
                         height_r=70,
                         alt_width_c=71,
                         alt_height_r=71,
                         alt_c=[4,9],
                         alt_r=[2],
                         start_x= 1696,
                         start_y=784
                         )
EMPTY_CELL_FP = "data/empty_cells/empty70x70.png"
EMPTY_CELL_XY_ALT_FP = "data/empty_cells/empty71x71.png"
EMPTY_CELL_X_ALT_FP = "data/empty_cells/empty71x70.png"
EMPTY_CELL_Y_ALT_FP = "data/empty_cells/empty70x71.png"

inv_locked = [[0 for _ in range(inv_cell_info.n_r)] for _ in range(inv_cell_info.n_c)]
""" if locked inv cells on startup is desired, wont be shown in gui tho.
first element of each list is the most upper cell of that column
"""

inv_locked = [
    [0,0,0,0,0],
    #[1,1,1,1,1],
    [0,0,0,0,0],
    [0,0,0,0,0],
    [0,0,0,0,0],
    [0,0,0,0,0],
    [0,0,0,0,0],
    [0,0,0,0,0],
    [0,0,0,0,0],
    [0,0,0,0,0],
    [0,0,0,0,0],
    [0,0,0,0,0],
    [0,0,0,0,0],]

