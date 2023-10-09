from typing import Callable

import dearpygui.dearpygui as dpg

from hotkey_watcher import HotKeyWatcher


class HotKeyRemapWindow:
    _texts: int
    _text1: int = 0
    _text2: int = 0
    _wnd: int = 0
    _key_src = ''
    _key_dst = ''
    _hotkey_watcher: HotKeyWatcher
    apply_callback: Callable[[str, str], None]
    cancel_callback: Callable[[None], None]

    def __init__(self, hot: HotKeyWatcher, name: str):
        self._hotkey_watcher = hot
        self._texts = []
        self.apply_callback = lambda x, y: None
        self.cancel_callback = lambda: None

        with dpg.window(label=name, autosize=True, show=False, no_close=True) as self._wnd:
            with dpg.group(horizontal=True, horizontal_spacing=100):
                self._text1 = dpg.add_text(default_value="Не задано")
                self._texts.append(self._text1)

                def on_button_click():
                    for i in self._texts:
                        dpg.configure_item(i, color=None)

                    dpg.configure_item(self._text1, color=[0, 255, 0])
                    self._hotkey_watcher.callback = self.set_key_src

                dpg.add_button(label="Поменять сочетание", callback=on_button_click)

            with dpg.group(horizontal=True, horizontal_spacing=100):
                self._text2 = dpg.add_text(default_value="Не задано")
                self._texts.append(self._text2)

                def on_button_click():
                    for i in self._texts:
                        dpg.configure_item(i, color=None)

                    dpg.configure_item(self._text2, color=[0, 255, 0])
                    self._hotkey_watcher.callback = self.set_key_dst

                dpg.add_button(label="Поменять сочетание", callback=on_button_click)

            dpg.add_spacer(height=25)
            with dpg.group(horizontal=True, horizontal_spacing=10):
                dpg.add_button(label="Применить", callback=self._apply)
                dpg.add_button(label="Отмена", callback=self._cancel)

    def hide(self):
        self.set_key_dst('')
        self.set_key_src('')
        dpg.hide_item(self._wnd)

    def show(self):
        dpg.show_item(self._wnd)

    def _cancel(self):
        self.cancel_callback()
        self.hide()

    def _apply(self):
        if not self._key_dst or not self._key_src:
            return
        self.apply_callback(self._key_src, self._key_dst)
        self.hide()

    def set_key_src(self, text: str):
        dpg.configure_item(self._text1, default_value=text or "Не задано")
        self._key_src = text

    def set_key_dst(self, text: str):
        dpg.configure_item(self._text2, default_value=text or "Не задано")
        self._key_dst = text
