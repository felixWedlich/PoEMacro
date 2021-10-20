#Features:

Flask macro:
 - configurable duration per flask / hotkey => adaptable for periodic spell use (guards/blood rage)
 - alternating flask (2 quicksilvers in leveling)
 - (optionally) automatically enable/disable macro in towns => no macro spam when pricing in stash
 - (optionally) automatically enable/disable macro while using chat (cltr-enter/enter) => no  macro spam when chatting
    - this may interfere with existing logout/hideout macros, for this logout/hideout hotkeys are configurable
    
Auto stash:
 - auto (cltr) click every occupied inventory cell => saves time compared to clicking every cell
 - (optionally) lock inventory cells which are to be ignoreed when auto clickng (e.g scrolls / transmutes)

Gem-Leveling:
 - configurable Hotkey to move mouse and level gem, then return mouse to old position
# Installation:

- requirements: Python3 installation

`pip install -r requirements.txt`


# Usage:
If PoE is running:

`python3 -m ahkpy macro.py`

(need to restart macro if PoE is restarted, is on todo)

#Config:

necessary: adapt the PoE.exe name that is running in Flask.py 

optional: adapt the hotkeys in config.py and the X/Y offsets depending on resolution