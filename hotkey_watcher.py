from typing import Callable

import keyboard

from scan_code_to_name import scan_code_to_name


class HotKeyWatcher:
    _hotkey: str = ''
    callback: Callable

    def __init__(self):
        self._keys_down = {}
        self.callback = lambda x: None
        self.d = keyboard.hook(self._on_press)

    def on_key_down(self):
        pass

    def _on_pressR(self, event: keyboard.KeyboardEvent):
        print(event.event_type)

    def _on_press(self, event: keyboard.KeyboardEvent):
        key = scan_code_to_name(event.scan_code)
        if key is None: return

        self._keys_down[event.scan_code] = {
            "scan": event.scan_code,
            "name": key,
            "is_press": event.event_type == 'down'
        }

        keys = []
        scans = []
        for key_name, info in self._keys_down.items():
            if not info["is_press"]: continue
            keys.append(info["name"])
            scans.append(info["scan"])

        next_keys = sum(scans)
        if event.event_type == 'down' and self._hotkey != next_keys:
            self._hotkey = next_keys
            self.callback(keyboard.get_hotkey_name(keys))

    def get_hotkey_pressed(self):
        return self._hotkey
