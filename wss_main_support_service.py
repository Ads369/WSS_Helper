import os
from sys import platform as _platform
import pyperclip
from loguru import logger


def check_os() -> None:
    """Function check OS information
    """
    if _platform == "linux" or _platform == "linux2":
        logger.debug('# linux')
    elif _platform == "darwin":
        logger.debug('# MAC OS X')
    elif _platform == "win32":
        logger.debug('# Windows')
    elif _platform == "win64":
        logger.debug('# Windows 64-bit')


def to_clipboard(in_str:str) -> None:
    """Paste to Clipboard"""
    pyperclip.copy(in_str)


def change_clipboard() -> str:
    """Simple replace substring in Clipboard"""

    str_befor = 'Criteria="e"'
    str_after = 'Criteria="contains"'

    text_cb = pyperclip.paste()

    new_text = text_cb.replace(str_befor, str_after)
    pyperclip.copy(new_text)
    return new_text


def send_notify(title:str, text:str):
    """Display notification"""
    # on MAC
    if _platform == "darwin":
        os.system(f"osascript -e 'display notification \"{text}\" with title \"{title}\"'")
