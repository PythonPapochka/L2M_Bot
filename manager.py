from clogger import log
import numpy as np
import mss
from methods.base_methods import loadSettings, parseCBT
from datetime import datetime
import threading
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed


def pixel_checkManager(window, rgb, xy, timeout=0.02):
    if rgb == "no":
        return None

    left, top = window['Position']
    adjusted_x = xy[0] + left
    adjusted_y = xy[1] + top

    with mss.mss() as sct:
        monitor = {"left": adjusted_x, "top": adjusted_y, "width": 1, "height": 1}
        start_time = time.time()

        while time.time() - start_time < timeout:
            screenshot = np.array(sct.grab(monitor))
            pixel_color = screenshot[0, 0][:3][::-1]

            if np.all(np.abs(pixel_color - rgb) <= 2):
                return window['Nickname']

            time.sleep(0.005)

    return None


_settings_cache = None
_settings_timestamp = 0
_settings_lock = threading.Lock()

def get_cached_settings():
    global _settings_cache, _settings_timestamp
    with _settings_lock:
        now = time.time()
        if now - _settings_timestamp > 1.2 or _settings_cache is None: #todo сделать норм одни настройки для всех, багует если дрочить быстро
            _settings_cache = loadSettings()
            _settings_timestamp = now
        return _settings_cache

# базовый класс с которого все наследуем
class Manager:
    log("BaseManager loaded")
    def __init__(self):
        self.settings = loadSettings()
        self.q = deque()
        self.processed_windows = set()
        self.lock = threading.Lock()

    def get_settings(self):
        with self.lock:
            return get_cached_settings()

    def upd(self, window_nickname):
        with self.lock:
            if window_nickname not in self.processed_windows:
                self.q.append(window_nickname)
                self.processed_windows.add(window_nickname)

    def checker(self, windows_info, rgb, xy, recheck=1, delay=2):
        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = []
            for window_nickname, window in windows_info.items():

                futures.append(executor.submit(
                    self._recheck_window,
                    window, rgb, xy, recheck, delay
                ))

            for future in as_completed(futures):
                final_nickname = future.result()
                if final_nickname and final_nickname not in self.processed_windows:
                    with self.lock:
                        self.q.append(final_nickname)
                        self.processed_windows.add(final_nickname)

    def _recheck_window(self, window, rgb, xy, recheck, delay):
        results = set()
        for i in range(recheck):
            #print("речек", i)
            nickname = pixel_checkManager(window, rgb, xy)
            results.add(nickname)
            if len(results) > 1:
                return None
            time.sleep(delay)
        return results.pop() if len(results) == 1 else None

    def start(self):
        t = threading.Thread(target=self.add_to_queue)
        t.daemon = True
        t.start()

    def get_queue(self):
        with self.lock:
            return self.q

    def remove_from_queue(self, item):
        with self.lock:
            if item in self.processed_windows:
                self.processed_windows.remove(item)
            temp_queue = deque()
            while self.q:
                current_item = self.q.popleft()
                if current_item != item:
                    temp_queue.append(current_item)
            self.q = temp_queue

    def _is_in_queue(self, item):
        with self.lock:
            return item in self.processed_windows

    def add_to_queue(self):
        raise Exception("to implement or abstract method")

# менеджер смертей, проверяет все окна на то умерли ли они
class DeathManager(Manager):
    log("DeathManager loaded")
    def add_to_queue(self):
        cbts = ["you_were_killed_energomode", "check_death_penalty", "respawn_village"]
        while True:
            for cbt in cbts:
                xy_to_check, rgb_to_check = parseCBT(cbt)
                self.checker(self.get_settings(), rgb_to_check, xy_to_check)
                time.sleep(0.5)

# менеджер пвп, проверяет все окна на то бьют ли их
class PvpManager(Manager):
    log("PvpManager loaded")
    def add_to_queue(self):
        xy_to_check, rgb_to_check = parseCBT("pvp_energo_trigger")
        while True:
            #print("начал чекать чет пвп менеджером")
            self.checker(self.get_settings(), rgb_to_check, xy_to_check, recheck=1)
            time.sleep(0.5)

# менеджер возвращения из города, проверяет настройки всех окон
# на наличие InHome != null, если там есть время то после наступления этого времени должны вернуться на спот
class BackToSpotManager(Manager):
    log("BackToSpotManager loaded")
    def check(self, windows_info):
        current_time = datetime.now()

        for window_id, window in windows_info.items():
            state = window.get("State")
            in_home = window.get("InHome")

            if state == "afk" and in_home and in_home != "null":
                try:
                    in_home_time = datetime.strptime(in_home, "%Y-%m-%d %H:%M:%S")
                    if in_home_time <= current_time:
                        if window_id not in self.processed_windows:
                            with self.lock:
                                self.q.append(window_id)
                                self.processed_windows.add(window_id)
                except ValueError:
                    continue

    def add_to_queue(self):
        while True:
            self.check(self.get_settings())
            time.sleep(1)

#todo отловить вылет с сервера и закрывать либо логинить персонажа
class ReloggerManager(Manager):
    log("ReloggerManager not loaded, empty")
    #def add_to_queue(self):
        #cbts = ["confirm_orange_center"] #todo добавить кнопки закрытия рекламы
        #while True:
            #for cbt in cbts:
                #xy_to_check, rgb_to_check = parseCBT(cbt)
                #self.checker(self.get_settings(), rgb_to_check, xy_to_check)
                #time.sleep(1)

# менеджер проверки хп банок на всех окнах, если банок 0 = тпаемся в город закупаться и ставим окну InHome на 5 минут чтоб подхилился
class HpBankManager(Manager):
    log("HpBankManager loaded")
    def add_to_queue(self):
        xy_to_check, rgb_to_check = parseCBT("hp_bank_in_energo")
        while True:
            settings2 = self.get_settings()
            for window_id, window in settings2.items():
                state = window.get("State")
                in_home = window.get("InHome")
                if state == "combat" and in_home == "null":
                    #print("хп банка чет чекает 4 раза")
                    self.checker(settings2, rgb_to_check, xy_to_check, recheck=4)
                    time.sleep(0.5)

# менеджер проверки сумки, уведет окно если будет 50% или 80% перевеса
class PerevesManager(Manager):
    log("PerevesManager loaded")
    def add_to_queue(self):
        while True:
            settings2 = self.get_settings()
            cbts = ["pereves1", "pereves2"]
            for cbt in cbts:
                xy_to_check, rgb_to_check = parseCBT(cbt)
                for window_id, window in settings2.items():
                    state = window.get("State")
                    stashing = window.get("Stashing")

                    if state == "combat" and stashing == 0:
                        self.checker(settings2, rgb_to_check, xy_to_check)
                        time.sleep(1)

# проверяем все окна и бекаем на рандом спот если нет стейта
class FarmManager(Manager):
    log("FarmManager loaded")
    def check(self, windows_info):
        for window_id, window in windows_info.items():
            state = window.get("State")

            if state == "null":
                try:
                    if window_id not in self.processed_windows:
                        with self.lock:
                            self.q.append(window_id)
                            self.processed_windows.add(window_id)
                except ValueError:
                    continue

    def add_to_queue(self):
        while True:
            self.check(self.get_settings())
            time.sleep(1)

# todo ждем наступления времени сборов и собираем во всех окнах почту
class RewardsManager(Manager):
    log("RewardsManager loaded")
    def check(self, windows_info):
        for window_id, window in windows_info.items():
            state = window.get("State")
            time.sleep(555555555)
            pass

    def add_to_queue(self):
        while True:
            self.check(self.get_settings())
            time.sleep(1)