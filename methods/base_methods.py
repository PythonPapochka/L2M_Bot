from interception import inputs
import time
import pygetwindow as gw
from constans import SETTINGS_DIR, CBT
import win32gui
import win32con
import numpy as np
import mss
import json
import os
import copy
from clogger import log
import configparser
import ast

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
        parser.read(config_file)

        for section in parser.sections():
            section_obj = ConfigSection(parser[section])
            setattr(self, section, section_obj)

def load_config(config_file='config.ini'):
    return Config(config_file)

def parseCBT(trigger_name):
    if trigger_name in CBT:
        coordinates = CBT[trigger_name]

        if len(coordinates) == 2:
            xy = tuple(map(int, coordinates[0].split(", ")))
            if coordinates[1] == "no":
                rgb = "no"
            else:
                rgb = tuple(map(int, coordinates[1].split(", ")))

            return xy, rgb
    return None, None

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
                    if np.all(diff <= 3):
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
    time.sleep(0.1)
    return True

def loadSettings(): #todo переписать говнокод
    if os.path.exists(SETTINGS_DIR):
        try:
            with open(SETTINGS_DIR, 'r') as file:
                settings = json.load(file)

                if not settings:
                    log("Настройки пустые, обновляю файл")
                    current_windows = findAllWindows()
                    saveSettings(current_windows)
                    return current_windows

        except json.JSONDecodeError as e:
            log(f"Файл настроек повреждён, пересоздаю =( {e}")
            current_windows = findAllWindows()
            saveSettings(current_windows)
            return current_windows
    else:
        log("Файл настроек не найден. Создаю новый.")
        current_windows = findAllWindows()
        saveSettings(current_windows)
        return current_windows

    current_windows = findAllWindows()
    updated = False

    for hwnd, new_info in current_windows.items():
        nickname = new_info.get("Nickname", str(hwnd))

        if nickname in settings:
            saved_info = settings[nickname]
            updated_info = copy.deepcopy(saved_info)

            updated_info["ID"] = new_info["ID"]
            updated_info["Position"] = new_info["Position"]
            updated_info["Width"] = new_info["Width"]
            updated_info["Height"] = new_info["Height"]
            updated_info["Size"] = new_info["Size"]

            if updated_info != saved_info:
                settings[nickname] = updated_info
                updated = True
        else:
            settings[nickname] = new_info
            updated = True

    current_hwnds = set(str(hwnd) for hwnd in current_windows.keys())
    saved_hwnds = set(settings.keys())

    to_remove = saved_hwnds - current_hwnds
    for nickname in to_remove:
        del settings[nickname]
        updated = True

    if updated and settings:
        saveSettings(settings)

    return settings

def editSettingsByHWND(hwnd, new_settings):
    settings = loadSettings()

    if str(hwnd) in settings:
        current_settings = settings[str(hwnd)]
        if current_settings != new_settings:
            settings[str(hwnd)].update(new_settings)
            saveSettings(settings)
    else:
        log(f"pzdc {hwnd}")

def loadSettingsByHWND(hwnd):
    settings = loadSettings()
    return settings.get(str(hwnd), None)

def saveSettings(settings):
    with open(SETTINGS_DIR, 'w') as file:
        json.dump(settings, file, indent=4)

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

def activate_window(windowInfo): # юзлес не юзается ноо хули нет
    if windowInfo:
        window_id, window = next(iter(windowInfo.items()))
        hwnd = window.get("ID")

        if hwnd:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            return True

    return False
