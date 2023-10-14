from dataclasses import dataclass

import keyboard
import win32gui
from loguru import logger


@dataclass()
class HotkeyRemap:
    src: str
    dst: str
    scan_src: list[int]
    scan_dst: list[int]
    index: int


class Remaper:
    _program_class = ''
    _keys: list[HotkeyRemap]

    def __init__(self, program_class: str):
        self._program_class = program_class
        self._keys = []

    def _hotkey_handler(self, key_src: str, key_dst: str):
        app_name = win32gui.GetClassName(win32gui.GetForegroundWindow())
        if app_name != self._program_class:
            return True

        logger.info(f'Remap hotkey "{self._program_class}": {key_src} -> {key_dst}')

        active_modifiers = sorted(
            modifier for modifier, state in keyboard._listener.modifier_states.items() if state == 'allowed')

        for modifier in active_modifiers:
            keyboard.release(modifier)

        keyboard.send(key_dst)

        for modifier in active_modifiers:
            keyboard.press(modifier)

        return False

    def get_has_src(self, src: str):
        for i in self._keys:
            if i.src == src:
                return i.src == src

        return False

    def get_hotkey(self, src: str) -> HotkeyRemap:
        for i in self._keys:
            if i.src == src:
                return i

        raise FileNotFoundError()

    def get_by_index(self, index: int) -> HotkeyRemap:
        return self._keys[index]

    def remap(self, key_src: str, key_dst: str) -> bool:
        if self.get_has_src(key_src): return True
        try:
            keyboard.add_hotkey(key_src, self._hotkey_handler, (key_src, key_dst), suppress=True,
                                trigger_on_release=False)
            logger.info(f'Add remap hotkey "{self._program_class}": {key_src} -> {key_dst}')
            self._keys.append(HotkeyRemap(
                src=key_src,
                dst=key_dst,
                index=len(self._keys)
            ))
            return True
        except ValueError:
            logger.warning(f'Invalid hotkey "{self._program_class}": {key_src} -> {key_dst}')
            return False

    def unremap(self, key_src: str):
        try:
            self._keys.pop(self.get_hotkey(key_src).index)
            keyboard.remove_hotkey(key_src)
            logger.info(f'Remove remap hotkey "{self._program_class}": {key_src}')

            for index, i in enumerate(self._keys):
                i.index = index - 1

        except KeyError:
            pass

    def change(self, index: int, src: str, dst: str):
        self._keys[index].src = src
        self._keys[index].dst = dst

    def get_keys(self) -> list[HotkeyRemap]:
        return self._keys
