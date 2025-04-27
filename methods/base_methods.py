from interception import inputs
import time
import pygetwindow as gw
from constans import CBT_JP, BATTLE_PASS
import win32gui
import win32process
import win32api
import win32con
import numpy as np
import mss
import configparser
import ast
import threading
import copy
from typing import Dict, Any

class ConfigSection:
    def __init__(self, section_data):
        for key, value in section_data.items():
            try:
                parsed_value = ast.literal_eval(value)
            except (ValueError, SyntaxError):
                parsed_value = value  # если не питоновская фигня — оставляем строкой
            setattr(self, key, parsed_value)

class Config:
    def __init__(self, config_file='config.ini'):
        parser = configparser.ConfigParser()
        parser.optionxform = str
        parser.read(config_file)

        for section in parser.sections():
            section_obj = ConfigSection(parser[section])
            setattr(self, section, section_obj)

def load_config(config_file='config.ini'):
    return Config(config_file)

def parseCBT(trigger_name):
    if trigger_name in CBT_JP:
        coordinates = CBT_JP[trigger_name]

        if len(coordinates) == 2:
            xy = tuple(map(int, coordinates[0].split(", ")))
            if coordinates[1] == "no":
                rgb = "no"
            else:
                rgb = tuple(map(int, coordinates[1].split(", ")))

            return xy, rgb
    return None, None

def find_BP_1(window_info, t=5, step=5, distance=30):
    window_id, window = next(iter(window_info.items()))
    left, top = window["Position"]
    width = window["Width"]

    y_search = BATTLE_PASS["y_vkladki"]
    red_rgb = tuple(map(int, BATTLE_PASS["red_dot_clr_vkladka"][0].split(', ')))

    hits = []

    with mss.mss() as sct:
        for x in range(0, width, step):
            adjusted_x = left + x
            adjusted_y = top + y_search

            monitor = {"left": adjusted_x, "top": adjusted_y, "width": 1, "height": 1}
            screenshot = np.array(sct.grab(monitor))
            pixel_rgb = screenshot[0, 0][:3][::-1]  # BGR to RGB

            if all(abs(int(pixel_rgb[i]) - red_rgb[i]) <= t for i in range(3)):
                hits.append(x)

    buttons = []
    if hits:
        group = [hits[0]]
        for x in hits[1:]:
            if x - group[-1] <= distance:
                group.append(x)
            else:
                buttons.append(int(sum(group) / len(group)))  # центр
                group = [x]
        buttons.append(int(sum(group) / len(group))) # финалочка

    return [[f"{x}, {y_search}", "no"] for x in buttons]

def find_BP_2(window_info, t=5, step=3, distance=20):
    window_id, window = next(iter(window_info.items()))
    left, top = window["Position"]
    height = window["Height"]

    x_search = BATTLE_PASS["x_podvkladki"]
    red_rgb = tuple(map(int, BATTLE_PASS["red_dot_clr_podvkladka"][0].split(', ')))

    hits = []

    with mss.mss() as sct:
        for y in range(0, height, step):
            adjusted_x = left + x_search
            adjusted_y = top + y

            monitor = {"left": adjusted_x, "top": adjusted_y, "width": 1, "height": 1}
            screenshot = np.array(sct.grab(monitor))
            pixel_rgb = screenshot[0, 0][:3][::-1]  # BGR to RGB

            if all(abs(int(pixel_rgb[i]) - red_rgb[i]) <= t for i in range(3)):
                hits.append(y)

    buttons = []
    if hits:
        group = [hits[0]]
        for y in hits[1:]:
            if y - group[-1] <= distance:
                group.append(y)
            else:
                buttons.append(int(sum(group) / len(group)))  # центр
                group = [y]
        buttons.append(int(sum(group) / len(group))) # финалочка

    return [[f"{x_search}, {y}", "no"] for y in buttons]

def check_pixel(window_info, xy, rgb, timeout=0.2):
    wait_time = 0.01
    if rgb == "no":
        return True

    window_id, window = next(iter(window_info.items()))
    left, top = window['Position']

    adjusted_x = xy[0] + left
    adjusted_y = xy[1] + top

    start_time = time.time()
    last_diffs = []

    with mss.mss() as sct:
        while time.time() - start_time < timeout:
            monitor = {"left": adjusted_x, "top": adjusted_y, "width": 2, "height": 2}
            screenshot = np.array(sct.grab(monitor))

            for y in range(2):
                for x in range(2):

                    pixel_color = screenshot[y, x][:3][::-1]  # BGR to RGB
                    diff = np.abs(pixel_color - rgb)
                    last_diffs.append(diff)
                    if np.all(diff <= 5):
                        return True

            time.sleep(wait_time)
    return False

def move_mouse(windowInfo, x_offset, y_offset):
    inputs.auto_capture_devices(keyboard=True, mouse=True)
    window_id, window = next(iter(windowInfo.items()))
    position_x, position_y = window["Position"]
    width = window["Width"]
    height = window["Height"]

    absolute_x = position_x + x_offset
    absolute_y = position_y + y_offset

    inputs.move_to(absolute_x, absolute_y)
    time.sleep(0.1)
    return True

def click_mouse(windowInfo, x_offset, y_offset, button="left"):
    inputs.auto_capture_devices(keyboard=True, mouse=True)
    window_id, window = next(iter(windowInfo.items()))
    position_x, position_y = window["Position"]
    width = window["Width"]
    height = window["Height"]

    absolute_x = position_x + x_offset
    absolute_y = position_y + y_offset

    inputs.move_to(absolute_x, absolute_y)
    inputs.mouse_down(button)
    inputs.mouse_up(button)
    return True

class SettingsManager:
    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SettingsManager, cls).__new__(cls)
                    cls._instance._settings = {}
                    cls._instance._settings_lock = threading.RLock()
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            with self._settings_lock:
                if not self._initialized:
                    self._initializeSettings()
                    self._initialized = True

    def _initializeSettings(self):
        current_windows = findAllWindows()

        with self._settings_lock:
            self._settings.clear()
            for hwnd, new_info in current_windows.items():
                nickname = new_info.get("Nickname", str(hwnd))
                self._settings[nickname] = copy.deepcopy(new_info)

    def loadSettings(self) -> Dict[str, Any]:
        with self._settings_lock:
            return self._settings

    def editSettingsByHWND(self, hwnd: int, new_settings: Dict[str, Any]) -> bool:
        hwnd_str = str(hwnd)
        with self._settings_lock:
            if hwnd_str in self._settings:
                self._settings[hwnd_str].update(copy.deepcopy(new_settings))
                return True
            return False

    def loadSettingsByHWND(self, hwnd: int) -> Dict[str, Any]:
        hwnd_str = str(hwnd)
        with self._settings_lock:
            return copy.deepcopy(self._settings.get(hwnd_str))

def findAllWindows():
    all_windows = gw.getWindowsWithTitle("Lineage2M")
    window_info = {}
    for window in all_windows:
        nick = window.title.split("l ")[1] if "l " in window.title else "No"
        info = {
            "Nickname": nick, # ник
            "Title": window.title,  # название окна фулл
            "ID": window._hWnd,  # айди окна
            "Position": window.topleft,  # позиция (верхний левый угол)
            "Width": window.width,  # ширина окна
            "Height": window.height,  # высота окна
            "Size": f"{window.width}x{window.height}",  # размер окна (ширина x высота)
            "Active": window.isActive,  # активно ли (булево)
            "Stashing": 0,
            "State": "null",
            "Energo": "null",
            "InHome": "null",
        }
        if nick != "No":
            window_info[nick] = info

    return window_info

def activate_window(windowInfo):
    try:
        if windowInfo:
            window_id, window = next(iter(windowInfo.items()))
            hwnd = window.get("ID")

            if hwnd:
                fg_window = win32gui.GetForegroundWindow()
                current_thread = win32api.GetCurrentThreadId()
                fg_thread, _ = win32process.GetWindowThreadProcessId(fg_window)
                target_thread, _ = win32process.GetWindowThreadProcessId(hwnd)
                win32process.AttachThreadInput(current_thread, fg_thread, True)
                win32process.AttachThreadInput(current_thread, target_thread, True)
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                win32process.AttachThreadInput(current_thread, fg_thread, False)
                win32process.AttachThreadInput(current_thread, target_thread, False)

                return True
                
    except Exception as e:
        return True
        
    return True