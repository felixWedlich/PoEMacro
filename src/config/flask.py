MANUAL_TOGGLE_FLASK_KEY = "^+!F5"

# FLASK CONFIG
AUTO_TOGGLE = True
DISABLE_MACRO_WHILE_CHAT = False
CLIENT_TXT_LOCATION = r"C:\Program Files (x86)\Steam\steamapps\common\Path of Exile\logs\Client.txt"


CLIENT_TXT_REFRESH_DURATION = 2
# FLASKS = [Flask(0, "1"),
#           Flask(0, "2"),
#           Flask(5, "3"),
#           Flask(6, "4"),
#           Flask(7.2, "5"),
#           Flask(20,"f")
#           #Flask(0, "f"),
#           #Flask(0, "m"),
#           ]
FLASKS = [("F",0, "1"),
          # ("F", (7.2,), ("2",)),
          ("A",(6,6),("4","5")),
          # ("F",7, "4"),
          ("M",0.1,"3"),
          ("L",0.1,"1"),
          ]
# FLASKS = [#
#           # Flask(7.2, "2"),
#           Flask(7, "3"),
#           # Flask(6, "4"),
#           # Flask(9.2, "5"),
#           # AlternatingFlask((6,6),("4","5")),
#           #Flask(0, "m"),
#           ]


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
                             "Karui Shores"
                             ]


SIMULACRUM_PLACES = ["Lunacy's Watch", "The Bridge Enraptured", "The Syndrome Encampment",
                     "Hysteriagate", "Oriath Delusion"]
FLASK_TIMEOUT = 5.000
