import time
import os
from datetime import datetime, timedelta
from clogger import log
from constans import SLEEP_AFTER_PVP_DODGE, SLEEP_AFTER_RIP, SPOT_OT, SPOT_DO

from methods.base_methods import loadSettings, editSettingsByHWND, parseCBT, check_pixel, click_mouse
from manager import PvpManager, BackToSpotManager, DeathManager, HpBankManager, PerevesManager, \
    FarmManager
from methods.game_utils import teleportToTown, energo_mode, navigateToNPC, \
    teleportToRandomSpot, respawn, buyLootAfterRIP, checkRIP, checkEnergoMode, \
    checkAutoHunt

from tgbot.tg import TgBotus

class Scenary:
    def __init__(self):
        self.bot = TgBotus()
        self.filename = os.path.splitext(os.path.basename(__file__))[0]
        self.bot.send_message("admin", f"✅ <b>Успешно запустили сценарий!</b>\n<code>{self.filename}</code>")

        self.hpBankManager = HpBankManager()
        self.pvpManager = PvpManager()
        self.spotManager = BackToSpotManager()
        self.deathManager = DeathManager()
        self.perevesManager = PerevesManager()
        self.farmManager = FarmManager()

        self.hpBankManager.start()
        self.spotManager.start()
        self.pvpManager.start()
        self.deathManager.start()
        self.perevesManager.start()
        self.farmManager.start()

        self.settings = loadSettings()

        self.spot_in_progress = False
        self.death_in_progress = False
        self.banka_in_progress = False
        self.pereves_in_progress = False
        self.farm_backer_in_progress = False


    def process_pvp(self):
        queue = self.pvpManager.get_queue()
        #print(f"pvp {queue}")
        if queue:
            while queue:
                window_id = queue.popleft()
                if str(window_id) in self.settings:
                    windowname = str(window_id)
                    data = self.settings[windowname]
                    log(f"Сдетектил пвп, возможно нам пизда {window_id}", window_id)
                    result = teleportToTown({window_id: data}, True)
                    if result:
                        log(f"ez dodge sasai lalka {window_id}", window_id)
                        self.bot.send_message("admin", f"<b>Доджнул пвп, сплю {SLEEP_AFTER_PVP_DODGE} минут</b>", charid=window_id)
                        time.sleep(1.5)
                        energo_mode({window_id: data}, "on")
                        log(f"sleep {SLEEP_AFTER_PVP_DODGE}", window_id)
                        nexttime = datetime.now() + timedelta(minutes=SLEEP_AFTER_PVP_DODGE)
                        data["InHome"] = nexttime.strftime('%Y-%m-%d %H:%M:%S')
                        data["State"] = "afk"
                        editSettingsByHWND(window_id, data)
                        self.pvpManager.remove_from_queue(window_id)
                    else:
                        log(f"Ошибка при телепорте, возможно мы уже дохлые: {result}", window_id)
                        result = respawn({window_id: data})
                        if result:
                            nexttime = datetime.now() + timedelta(minutes=SLEEP_AFTER_PVP_DODGE)
                            data["InHome"] = nexttime.strftime('%Y-%m-%d %H:%M:%S')
                            data["State"] = "afk"
                            editSettingsByHWND(window_id, data)
                            energo_mode({window_id: data}, "on")
                            self.bot.send_message("admin", f"<b>Ошибка при телепорте, возможно мы уже дохлые {result}</b>")
                            self.pvpManager.remove_from_queue(window_id)
                        else:
                            log(f"Были не дохлые, попробовал возродиться тщетно {result}", window_id)
                            self.bot.send_message("admin", f"<b>Ошибка при телепорте от пвп, чет случилось очень злое {result}</b>")
                            self.pvpManager.remove_from_queue(window_id)
                            

    def process_spots(self):
        if not self.spot_in_progress and not self.pvpManager.get_queue() and not self.deathManager.get_queue():
            spot_queue = self.spotManager.get_queue()
            if spot_queue:
                self.spot_in_progress = True

                while spot_queue:
                    window_id = spot_queue.popleft()
                    windowname = str(window_id)
                    data = self.settings[windowname]
                    energo_mode({window_id: data}, "off")
                    navigateToNPC({window_id: data}, "shop")
                    teleportToRandomSpot({window_id: data}, SPOT_OT, SPOT_DO)
                    data["InHome"] = "null"
                    data["State"] = "combat"
                    editSettingsByHWND(window_id, data)
                    self.bot.send_message("admin", f"<b>Вернул на спот после сна</b>", charid=window_id)
                    log(f"Вернул на спот после сна", window_id)
                    self.spotManager.remove_from_queue(window_id)

                    if self.pvpManager.get_queue() or self.spotManager.get_queue() or self.deathManager.get_queue():
                        self.spot_in_progress = False
                        break

                self.spot_in_progress = False

    def process_death(self):
        if not self.death_in_progress and not self.pvpManager.get_queue() and not self.spotManager.get_queue():
            death_queue = self.deathManager.get_queue()

            if death_queue:
                self.death_in_progress = True

                while death_queue:
                    window_id = death_queue.popleft()
                    windowname = str(window_id)
                    data = self.settings[windowname]

                    revive_result = checkRIP({window_id: data})

                    if revive_result:
                        log(f"Чар {window_id} помер, пытаюсь воскресить", window_id)
                        data["State"] = "death"
                        editSettingsByHWND(window_id, data)
                        result = respawn({window_id: data})
                        if result:
                            log(f"Успешно воскрес", window_id)
                            result = buyLootAfterRIP({window_id: data})
                            if result:
                                log(f"Куплен лут после рипа", window_id)
                                time.sleep(1)
                                energo_mode({window_id: data}, "on")
                                nexttime = datetime.now() + timedelta(minutes=SLEEP_AFTER_RIP)
                                data["InHome"] = nexttime.strftime('%Y-%m-%d %H:%M:%S')
                                data["State"] = "afk"
                                editSettingsByHWND(window_id, data)
                                self.bot.send_message("admin", f"<b>Реснул перса, выкупил опыт и шмотки</b>", charid=window_id)
                                self.deathManager.remove_from_queue(window_id)

                    if self.pvpManager.get_queue() or self.spotManager.get_queue():
                        self.death_in_progress = False
                        break

                self.death_in_progress = False

    def process_hp_banks(self):
         if not self.banka_in_progress and not self.pvpManager.get_queue() and not self.spotManager.get_queue() and not self.deathManager.get_queue():
            bankaqueue = self.hpBankManager.get_queue()

            if bankaqueue:
                xy_to_check, rgb_to_check = parseCBT("hp_bank_in_energo")
                self.banka_in_progress = True
                while bankaqueue:
                    window_id = bankaqueue.popleft()
                    windowname = str(window_id)
                    data = self.settings[windowname]
                    is_true = check_pixel({window_id: data}, xy_to_check, rgb_to_check, 3)
                    if not is_true:
                        log(f"Ложное срабатывание банки", window_id)
                        self.banka_in_progress = False
                        self.hpBankManager.remove_from_queue(window_id)
                        break

                    log(f"Пробую тпнуться в город, кончились баночки", window_id)
                    teleport = teleportToTown({window_id: data}, True)
                    if teleport:
                        log(f"Тпнулся в город успешно", window_id)
                        data["State"] = "shopping"
                        editSettingsByHWND(window_id, data)
                        time.sleep(0.3)
                        log(f"Пробую пойти к магазу", window_id)
                        result = navigateToNPC({window_id: data}, "shop")
                        time.sleep(0.2)
                        log(f"Результат закупочки - {result}", window_id)
                        log(f"Пробую тп на рандом спот", window_id)
                        result2 = teleportToRandomSpot({window_id: data}, SPOT_OT, SPOT_DO)
                        log(f"Результат тп на рандом спот - {result2}", window_id)
                        if result or result2:
                            log(f"После закупки и тп - {result}, {result2}", window_id)
                            data["InHome"] = "null"
                            data["State"] = "combat"
                            editSettingsByHWND(window_id, data)
                            self.bot.send_message("admin",
                                              f"<b>Купил банки и вернул на спот</b>", charid=window_id)
                            log(f"Купил банки и вернул на спот", window_id)

                        else:
                            log(f"Чет пошло не так, не закупился и не тпнулся, ставлю окну афк + нулл", window_id)
                            data["InHome"] = "null"
                            data["State"] = "afk"
                            editSettingsByHWND(window_id, data)
                            self.hpBankManager.remove_from_queue(window_id)

                        self.hpBankManager.remove_from_queue(window_id)

                    else:
                        log(f"teleport to buy banks - {teleport}", window_id)
                        data["InHome"] = "null"
                        data["State"] = "afk"
                        editSettingsByHWND(window_id, data)
                        self.hpBankManager.remove_from_queue(window_id)

                    if self.pvpManager.get_queue() or self.spotManager.get_queue() or self.deathManager.get_queue():
                        break

                self.banka_in_progress = False

    def process_pereves(self):
         if not self.pereves_in_progress and not self.banka_in_progress and not self.pvpManager.get_queue() and not self.spotManager.get_queue() and not self.deathManager.get_queue():
            perevesqueue = self.perevesManager.get_queue()
            if perevesqueue:
                self.pereves_in_progress = True
                while perevesqueue:
                    window_id = perevesqueue.popleft()
                    windowname = str(window_id)
                    data = self.settings[windowname]
                    teleport = teleportToTown({window_id: data}, True)
                    if teleport:
                        data["State"] = "stashing"
                        result = navigateToNPC({window_id: data}, "stash")
                        if result:
                            tp = teleportToRandomSpot({window_id: data}, SPOT_OT, SPOT_DO)
                            if tp:
                                data["InHome"] = "null"
                                data["State"] = "combat"
                                data["Stashing"] = 1
                                editSettingsByHWND(window_id, data)
                                self.bot.send_message("admin",
                                                      f"<b>Скинул шмот на склад, у нас был перевес, задумайся...</b>", charid=window_id)
                                log(f"Скинул шмот на склад, у нас был перевес", window_id)
                                self.perevesManager.remove_from_queue(window_id)

                            if self.pvpManager.get_queue() or self.spotManager.get_queue() or self.deathManager.get_queue() or self.hpBankManager.get_queue():
                                break

                self.pereves_in_progress = False

    def process_farmbacker(self): #todo refactor как будет время
        if not self.farm_backer_in_progress and not self.pereves_in_progress and not self.banka_in_progress and not self.pvpManager.get_queue() and not self.spotManager.get_queue() and not self.deathManager.get_queue() or self.perevesManager.get_queue():
            farmqueue = self.farmManager.get_queue()
            if farmqueue:
                self.farm_backer_in_progress = True
                while farmqueue:
                    window_id = farmqueue.popleft()
                    windowname = str(window_id)
                    data = self.settings[windowname]
                    autohunt = checkAutoHunt({window_id: data})
                    if autohunt:
                        log(f"Персонаж уже в бою, не возвращаем", window_id)
                        data["State"] = "combat"
                        editSettingsByHWND(window_id, data)
                        self.farmManager.remove_from_queue(window_id)
                        self.farm_backer_in_progress = False
                        break

                    energo = checkEnergoMode({window_id: data})
                    if energo:
                        energo_mode({window_id: data}, "off")

                    teleport = teleportToRandomSpot({window_id: data}, SPOT_OT, SPOT_DO)
                    if teleport:
                        time.sleep(3)
                        hunt = checkAutoHunt({window_id: data})
                        if hunt:
                            data["State"] = "combat"
                            editSettingsByHWND(window_id, data)
                            self.bot.send_message("admin",
                                                  f"<b>Перс был не в бою, поставил на рандом спот</b>",
                                                  charid=window_id)
                            log(f"Перс был не в бою, поставил на рандом спот", window_id)
                            self.farmManager.remove_from_queue(window_id)
                        else:
                            time.sleep(2)
                            energo = checkEnergoMode({window_id: data})
                            if energo:
                                energo_mode({window_id: data}, "off")

                            xy, rgb = parseCBT("zalupka_gui")
                            teleported = check_pixel({window_id: data}, xy, rgb, 10)
                            if teleported:
                                xy, rgb = parseCBT("auto_combat_mode_gui")
                                time.sleep(0.5)
                                x, y = xy
                                result = click_mouse({window_id: data}, x, y)
                                if result:
                                    time.sleep(0.5)
                                    energo_mode({window_id: data}, "on")
                                    time.sleep(0.05)
                                    data["State"] = "combat"
                                    editSettingsByHWND(window_id, data)
                                    self.bot.send_message("admin",
                                                          f"<b>Перс был не в бою, поставил на рандом спот</b>",
                                                          charid=window_id)
                                    log(f"Перс был не в бою, поставил на рандом спот", window_id)
                                    self.farmManager.remove_from_queue(window_id)
                    else:
                        self.bot.send_message("admin",
                                              f"<b>Чет сломалось в бек ту спот, зырь логи перса\nмы вроде тпнулись но автобоя нет</b>",
                                              charid=window_id)
                        log(f"Чет сломалось в бек ту спот, зырь логи выше", window_id)

                    if self.pvpManager.get_queue() or self.spotManager.get_queue() or self.deathManager.get_queue() or self.hpBankManager.get_queue():
                        break

                self.farm_backer_in_progress = False

    def run(self):
        while True:
            self.process_pvp()
            self.process_spots()
            self.process_death()
            self.process_hp_banks()
            self.process_pereves()
            self.process_farmbacker()

def main():
    scenary = Scenary()
    scenary.run()