from Flask import Flask, AlternatingFlask
import numpy as np
from PIL import Image


# HOTKEYS
HIDEOUT_KEY = "F5"
LOGOUT_KEY = "F1"
STASH_KEY = "!+^F2"
INV_LOCK_TOGGLE_MENU_KEY = "!c"
MACRO_TRIGGER_KEY = "RButton"
MANUAL_TOGGLE_FLASK_KEY = "^+!F5"
RESTART_SCRIPT_KEY = "F8"
LEVEL_GEM_KEY = "!+^F6"
GET_POS_KEY = "!a"
GUILD_HIDEOUT_KEY = ""

# FLASK CONFIG
AUTO_TOGGLE = True
DISABLE_MACRO_WHILE_CHAT = True
CLIENT_TXT_LOCATION = r"C:\Program Files (x86)\Steam\steamapps\common\Path of Exile\logs\Client.txt"

CLIENT_TXT_REFRESH_DURATION = 2
FLASKS = [Flask(0, "1"),
          Flask(7.600, "2"),
          Flask(5.200, "3"),
          Flask(2.700, "4"),
          Flask(3.500, "5"),
          Flask(0, "f"),
          Flask(0, "m"),
          ]
"""FLASKS = [Flask(0, "1"),
          Flask(3, "2"),
          Flask(3, "3"),
          AlternatingFlask((4,4),("4","5")),
          #Flask(0, "m"),
          ]"""
AUTOFLASK_DISABLED_PLACES = ["Hideout",
                             "Rogue Harbour",
                             "Oriath",
                             "Lioneye's Watch",
                             "The Forest Encampment",
                             "The Sarn Encampment",
                             "Highgate",
                             "Overseer's Tower",
                             "The Bridge Encampment",
                             "Oriath Docks",
                             ]
FLASK_TIMEOUT = 5.000

# GEM-LEVEL (while leveling)
LEVEL_GEM_CLICK_OLD_MOUSE_POS = True
# if we expect for this sometimes to fail, clicking the gem position will issue a movement click
# which can be overwritten with a click to the old mouse pos.
# If X/Y are fixed (should be while leveling, outside of towns) then this should be set to False

GEM_LEVEL_X = 2475
GEM_LEVEL_Y = 280

# STASH / INV CONFIG
MOUSESPEED = 2
INV_CELL_WIDTH = 53
INV_CELL_HEIGHT = 53
INV_CELL_WIDTH_SCUFFED = 52
INV_CELL_HEIGHT_SCUFFED = 52
SCUFFED_ROWS = [1,4]
SCUFFED_COLUMNS = [0,3,6,9]
INV_WIDTH = (12-len(SCUFFED_COLUMNS))*INV_CELL_WIDTH + len(SCUFFED_COLUMNS)*INV_CELL_WIDTH_SCUFFED
INV_HEIGHT = (5-len(SCUFFED_ROWS))*INV_CELL_HEIGHT + len(SCUFFED_ROWS)*INV_CELL_HEIGHT_SCUFFED
INV_START_X = 1272 #1695.5
INV_START_Y = 588 #784.3
INV_ROWS = 5
INV_COLUMNS = 12
LOCK_GUI_SHOWN = False
IN_TOWN = True #to disable auto stash functions in maps, to avoid accidental usage
STASH_DIFF_THRESH = 100
EMPTY_CELL = np.array(Image.open("empty53x53.png").convert("L")).astype(int)
EMPTY_CELL_XY_SCUFFED = np.array(Image.open("empty52x52.png").convert("L")).astype(int)
EMPTY_CELL_X_SCUFFED = np.array(Image.open("empty52x53.png").convert("L")).astype(int)
EMPTY_CELL_Y_SCUFFED = np.array(Image.open("empty53x52.png").convert("L")).astype(int)
inv_locked = [[0 for _ in range(INV_ROWS)] for _ in range(INV_COLUMNS)]
""" if locked inv cells on startup is desired, wont be shown in gui tho.
first element of each list is the most upper cell of that column
"""
"""
inv_locked = [[1,0,0,0,0],
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
"""
inv_highlighted = [[0 for _ in range(INV_ROWS)] for _ in range(INV_COLUMNS)]
