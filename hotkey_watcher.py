from dataclasses import dataclass
from typing import Callable

import keyboard

from scan_code_to_name import scan_code_to_name


@dataclass
class KeyInfo:
    scan: int
    name: str
    is_press: bool


@dataclass
class Hotkey:
    keys: list[str]
    scan: list[int]

    @property
    def name(self):
        return keyboard.get_hotkey_name(self.keys)


class HotKeyWatcher:
    _hotkey: int = 0
    callback: Callable
    _keys_down: dict[str, KeyInfo]

    def __init__(self):
        self._keys_down = {}
        self.callback = lambda x: None
        self.d = keyboard.hook(self._on_press)

    def _on_press(self, event: keyboard.KeyboardEvent):
        key = scan_code_to_name(event.scan_code)
        if key is None: return

        self._keys_down[event.scan_code] = KeyInfo(
            scan=event.scan_code,
            name=key,
            is_press=event.event_type == 'down'
        )

        keys = []
        scans = []
        for key_name, info in self._keys_down.items():
            if not info.is_press: continue
            keys.append(info.name)
            scans.append(info.scan)

        next_keys = sum(scans)
        if event.event_type == 'down':
            self._hotkey = next_keys
            # self.callback(keyboard.get_hotkey_name(keys))
            self.callback(Hotkey(
                keys=keys,
                scan=scans
            ))

    def get_hotkey_pressed(self):
        return self._hotkey
