import os
import sys
from dataclasses import asdict
from json import dumps, loads

import dearpygui.dearpygui as dpg

from hotkey_remap_window import HotKeyRemapWindow
from hotkey_watcher import HotKeyWatcher
from remaper import Remaper

application_path = os.path.dirname(__file__)
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)

FILE_KEYS_PATH = os.path.join(application_path, './keys.json')
FONT_PATH = os.path.join(application_path, './assets/fonts/arial.ttf')
photoshop = Remaper('Photoshop')

if os.path.exists(FILE_KEYS_PATH):
    with open(FILE_KEYS_PATH, mode='r') as fs:
        data = loads(fs.read())['data']
        for i in data:
            photoshop.remap(i['src'], i['dst'])

is_open = False
class HotkeyList:
    _listbox: int = 0
    _remaper: Remaper
    _items: list[str]

    def __init__(self, remaper: Remaper):
        self._items = []
        self._remaper = remaper
        self._listbox = dpg.add_listbox(label='##Keys', num_items=10)

        self.update_list()

    def update_list(self):
        self._items = []
        for key in self._remaper.get_keys():
            self._items.append(f'{key.src} -> {key.dst}')
        dpg.configure_item(self._listbox, items=self._items)

    def add_hotkey(self, key_src: str, key_dst: str):
        self._remaper.remap(key_src, key_dst)
        self.update_list()

    def remove_hotkey(self, index: int):
        key = self._remaper.get_by_index(index)
        self._remaper.unremap(key.src)
        self.update_list()

    def edit_hotkey(self, index: int, key_src: str, key_dst: str):
        self._remaper.change(index, key_src, key_dst)
        self.update_list()

    def get_index(self):
        return self._items.index(dpg.get_value(self._listbox))

    def get_hotkey(self):
        return self._remaper.get_by_index(self.get_index())


def start_app():
    global is_open

    if is_open:
        return

    is_open = True
    dpg.create_context()
    dpg.create_viewport()
    dpg.setup_dearpygui()
    dpg.set_viewport_title("PhotoshopRemaper")

    with dpg.font_registry():
        with dpg.font(FONT_PATH, 18, default_font=True, tag="Default font") as f:
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)

    hot = HotKeyWatcher()
    dpg.bind_font("Default font")
    with dpg.window(label="Example Window") as wnd:
        window = HotKeyRemapWindow(hot, "Добавить")
        window_edit = HotKeyRemapWindow(hot, "Изменить")

        hotkey_list = HotkeyList(photoshop)

        def save_remap():
            data = []
            for key in photoshop.get_keys():
                data.append(asdict(key))

            with open(FILE_KEYS_PATH, mode='w') as fs:
                fs.write(dumps({
                    "data": data
                }, indent=2))

        def start_edit():
            key = hotkey_list.get_hotkey()
            window_edit.set_key_src(key.src)
            window_edit.set_key_dst(key.dst)
            window_edit.show()

        def edit_hotkey(key_src: str, key_dst: str):
            hotkey_list.edit_hotkey(hotkey_list.get_index(), key_src, key_dst)
            save_remap()

        def add_button(x, y):
            hotkey_list.add_hotkey(x, y)
            save_remap()

        window.apply_callback = add_button
        window_edit.apply_callback = edit_hotkey

        with dpg.group(horizontal=True):
            dpg.add_button(label="Добавить", callback=window.show)
            dpg.add_button(label="Изменить", callback=start_edit)
            dpg.add_button(label="Удалить",
                           callback=lambda: (hotkey_list.remove_hotkey(hotkey_list.get_index()), save_remap()))

        dpg.set_primary_window(wnd, True)
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
    is_open = False


def stop_app():
    dpg.stop_dearpygui()