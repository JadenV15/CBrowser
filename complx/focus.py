# Source - https://stackoverflow.com/a/47161643
# Adapted from multiple answers

import ctypes
from threading import Thread

set_to_foreground = ctypes.windll.user32.SetForegroundWindow
keybd_event = ctypes.windll.user32.keybd_event

alt_key = 0x12
extended_key = 0x0001
key_up = 0x0002

def _steal(root, child):
    keybd_event(alt_key, 0, extended_key | 0, 0)
    set_to_foreground(root.winfo_id())
    keybd_event(alt_key, 0, extended_key | key_up, 0)

    child.focus_set()

def steal_focus(root, child):
    root.after(5, lambda: Thread(target=lambda:_steal(root, child), daemon=True).start())