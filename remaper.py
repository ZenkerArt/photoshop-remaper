from dataclasses import dataclass

import keyboard
import win32gui
from loguru import logger

from hotkey_remap import HotkeyRemap
from hotkey_watcher import Hotkey


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

    def remap_result(self, key_src: Hotkey, key_dst: Hotkey) -> bool:
        if self.get_has_src(key_src.name): return True
        try:
            keyboard.add_hotkey(key_src.scan, self._hotkey_handler, (key_src, key_dst), suppress=True,
                                trigger_on_release=False)
            logger.info(f'Add remap hotkey "{self._program_class}": {key_src} -> {key_dst}')
            self._keys.append(HotkeyRemap(
                src=key_src.name,
                dst=key_dst.name,
                scan_src=key_src.scan,
                scan_dst=key_dst.scan,
                index=len(self._keys)
            ))
            return True
        except ValueError:
            logger.warning(f'Invalid hotkey "{self._program_class}": {key_src} -> {key_dst}')
            return False

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
        hotkey = self.get_by_index(index)

        try:
            keyboard.remove_hotkey(src)
        except KeyError:
            pass
        keyboard.add_hotkey(src, self._hotkey_handler, (src, dst), suppress=True, trigger_on_release=False)

        logger.info(f'Change remap hotkey "{self._program_class}": from "{hotkey.src} -> {hotkey.dst}" to "{src} -> {dst}"')

        hotkey.src = src
        hotkey.dst = dst

    def get_keys(self) -> list[HotkeyRemap]:
        return self._keys
