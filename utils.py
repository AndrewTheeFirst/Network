from os import system, name as os_name
from threading import Thread
from typing import Callable, overload
from curses import window
from time import sleep

def clear():
    '''clears the console / terminal'''
    if os_name == "nt":
        system("cls")
    else:
        print("\x1b[2J\x1b[H", end="")

def background_process(func: Callable) -> Callable:
    '''aync function decorator'''
    def wrapper(*args):
        t = Thread(target = func, args = args)
        t.start()
    return wrapper

@overload
def wprint(self, window: window, message: str): ...

@overload
def wprint(window: window, y: int, x: int, message: str): ...

def wprint(window: window, arg_1: str | int, x: int = -1, message: str = ""):
    '''Adds string to window with automatic refresh'''
    if not message: # the first arg is message
        message = arg_1
    else: # the first two args are coords
        window.move(arg_1, x)
    window.addstr(message)
    window.refresh()

@overload
def wread(window: window, message: str, speed: int = 1): ...
@overload
def wread(window: window, y: int, x: int, message: str, speed: int = 1): ...

def wread(window: window, arg_1: str | int, arg_2: int = 1, message: str = "", speed = 1):
    '''Adds string to window with automatic refresh.
    Prints one char at a time to emulate a typed look'''
    if not message: # the first two args is message and speed respectively
        speed = arg_2
        message = arg_1
    else: # the first two args are coords
        window.move(arg_1, arg_2)
    rate = 0.1/speed
    for char in message:
        sleep(rate)
        window.addch(char)
        window.refresh()

def wclear(window: window):
    window.clear()
    window.refresh()