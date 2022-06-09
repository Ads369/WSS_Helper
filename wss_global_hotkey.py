from typing import Callable
from pynput import keyboard
import pyperclip
import sys
from loguru import logger
import wss_main_support_service as mss
import wss_main_helper


class HotKeylistener(object):
    """
    This simple class for heandling global HotKeys powered by pynput

    1) init class:
        hkl = HotKeylistener()

    2) init hotkey:
            hotkey1 = keyboard.HotKey(
                keyboard.HotKey.parse('<cmd>+h'),
                on_activate)
            -or-
            hotkey3 = HotKey(
                [Key.alt, Key.ctrl, KeyCode(char='y')],
                function_2)

    3) add hotkey to hotkeys(array)

    4) Run listener
            listener = hkl.get_keyboard()
            with listener as l:
                l.join()
            -or-
            listener = hkl.get_keyboard()
            listener.start()

    # Bind HotKeys ------- (<cmd>, <alt>, <cntl>, <shift>, <shift>+c)
    # On mac don't work <alt> and <cntl>
    # Work but need activate debug mode and copy special keys

    hotkeys = [hotkey1,
            hotkey2,
            hotkey3,
            hotkey4,]

    """

    def __init__(self) -> None:
        super().__init__()
        self.hotkeys = []
        self.listener = keyboard.Listener(
            on_press=self.signal_press_to_hotkeys,
            on_release=self.signal_release_to_hotkeys,
        )

    def add_hotkeys(self, hotkey):
        self.hotkeys.append(hotkey)

    def generate_add_hotkeys(self, hot_key_str: str, func: Callable) -> None:
        hotkey_new = keyboard.HotKey(keyboard.HotKey.parse(hot_key_str), func)
        self.add_hotkeys(hotkey_new)

    def show_hotKeys(self):
        print(self.hotkeys)

    def for_canonical(self, f):
        return lambda k: f(self.listener.canonical(k))

    def signal_press_to_hotkeys(self, key):
        # logger.debug('> {} ({})'.format(str(key), self.listener.canonical(key)))
        for hotkey in self.hotkeys:
            hotkey.press(self.listener.canonical(key))

    def signal_release_to_hotkeys(self, key):
        # logger.debug('< {} ({})'.format(str(key), self.listener.canonical(key)))
        for hotkey in self.hotkeys:
            hotkey.release(self.listener.canonical(key))

    def get_keyboard(self) -> keyboard.Listener:
        """
        Return listenerKyborad
        -!- After need to run it: 'listener.start()'
        """
        return self.listener


if __name__ == "__main__":
    # logger.remove()
    # logger.add(sys.stdout, level="INFO")
    # logger.add(sys.stdout, level="DEBUG")
    # logger.add(sys.stdout, format="<g>{time:YYYY-MM-DD HH:mm:ss}</g> | <lvl>{level}</lvl> | <c>{name}</c>:<c>{function}</c>:<c>{line}</c> - <lvl>{message}</lvl>", level="DEBUG")

    # with keyboard.Listener(on_press=signal_press_to_hotkeys, on_release=signal_release_to_hotkeys) as l:
    #     l.join()

    hkl = HotKeylistener()
    listener = hkl.get_keyboard()

    def on_activate():
        print("qwe123")

    def on_activate_2():
        print("234zxc")

    hkl.generate_add_hotkeys("<ctrl>+i", on_activate)
    hkl.generate_add_hotkeys("<ctrl>+\x0c", on_activate_2)

    listener = hkl.get_keyboard()
    with listener as l:
        l.join()
