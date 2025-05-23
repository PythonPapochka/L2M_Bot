import threading
import time
import random
import os

from datetime import datetime, timedelta
from clogger import log

from methods.base_methods import SettingsManager, parseCBT, check_pixel, click_mouse, load_config

from manager import PvpManager, BackToSpotManager, DeathManager, HpBankManager, PerevesManager, \
    FarmManager, MailClaimerManager, RewardsManager, ShopStashSellManager

from methods.game_utils import teleportToTown, energo_mode, navigateToNPC, \
    teleportToRandomSpot, respawn, buyLootAfterRIP, checkRIP, checkEnergoMode, \
    checkAutoHunt

from methods.game_utils import claim_clan, claim_mail, claim_achiv, claim_daily, \
    claim_battle_pass, claim_donate_shop

from tgbot.tg import TgBotus

cfg = load_config('config.ini')
SLEEP_AFTER_PVP_DODGE = cfg.timers.SLEEP_AFTER_PVP_DODGE
SLEEP_AFTER_RIP = cfg.timers.SLEEP_AFTER_RIP
SPOT_OT = cfg.spots.SPOT_OT
SPOT_DO = cfg.spots.SPOT_DO
settingsm = SettingsManager()

class Scenary:
    def __init__(self):
        self.bot = TgBotus()
        self.filename = os.path.splitext(os.path.basename(__file__))[0]
        self.settings = settingsm.loadSettings()
        self.bot.send_message("admin", f"✅ <b>Успешно запустили сценарий!</b>\n<code>{self.filename}</code>")

        self.hpBankManager = HpBankManager()
        self.pvpManager = PvpManager()
        self.spotManager = BackToSpotManager()
        self.deathManager = DeathManager()
        self.perevesManager = PerevesManager()
        self.farmManager = FarmManager()
        self.mailClaimerManager = MailClaimerManager()
        self.rewardsManager = RewardsManager()
        self.shopStashManager = ShopStashSellManager()

        threading.Thread(target=self.hpBankManager.start).start()
        threading.Thread(target=self.spotManager.start).start()
        threading.Thread(target=self.pvpManager.start).start()
        threading.Thread(target=self.deathManager.start).start()
        threading.Thread(target=self.perevesManager.start).start()
        threading.Thread(target=self.farmManager.start).start()
        threading.Thread(target=self.mailClaimerManager.start).start()
        threading.Thread(target=self.rewardsManager.start).start()
        threading.Thread(target=self.shopStashManager.start).start()

        self.spot_in_progress = False
        self.death_in_progress = False
        self.banka_in_progress = False
        self.pereves_in_progress = False
        self.farm_backer_in_progress = False
        self.rewards_in_progress = False
        self.mail_in_progress = False
        self.shop_stash_in_progress = False

    def process_pvp(self):
        queue = self.pvpManager.get_queue()
        #log(self.settings)
        if queue:
            while queue:
                window_id = queue.popleft()
                if str(window_id) in self.settings:
                    log(f"Начал обрабатывать очередь пвп", window_id)
                    windowname = str(window_id)
                    data = self.settings[windowname]
                    log(f"Сдетектил пвп, возможно нам пизда {window_id}", window_id)
                    result = teleportToTown({window_id: data}, True)
                    log(f"Попытка тп в город: {result}", window_id)
                    if result:
                        log(f"ez dodge sasai lalka {window_id}", window_id)
                        min_sleep, max_sleep = map(int, SLEEP_AFTER_PVP_DODGE.split("-"))
                        sleep_minutes = random.randint(min_sleep, max_sleep)
                        self.bot.send_message("admin", f"<b>Доджнул пвп, сплю {sleep_minutes} мин.</b>", charid=window_id)
                        time.sleep(0.5)
                        energo_mode({window_id: data}, "on")
                        log(f"Поставил энергомод вкл", window_id)
                        log(f"sleep {sleep_minutes}", window_id)
                        nexttime = datetime.now() + timedelta(minutes=sleep_minutes)
                        data["InHome"] = nexttime.strftime('%Y-%m-%d %H:%M:%S')
                        data["State"] = "afk"
                        log(f"Поставил афк стейт на время сна", window_id)
                        settingsm.editSettingsByHWND(window_id, data)
                        self.pvpManager.remove_from_queue(window_id)
                    else:
                        log(f"Ошибка при телепорте, возможно мы уже дохлые: {result}", window_id)
                        result = respawn({window_id: data})
                        log(f"Попробовал реснуться, результ: {result}", window_id)
                        if result:
                            min_sleep, max_sleep = map(int, SLEEP_AFTER_PVP_DODGE.split("-"))
                            sleep_minutes = random.randint(min_sleep, max_sleep)
                            nexttime = datetime.now() + timedelta(minutes=sleep_minutes)
                            data["InHome"] = nexttime.strftime('%Y-%m-%d %H:%M:%S')
                            data["State"] = "afk"
                            log(f"Реснулся, пробую поставить афк стейт и инхом на {sleep_minutes} мин.", window_id)
                            settingsm.editSettingsByHWND(window_id, data)
                            log(f"Реснулся, установил афк стейт, не буду выкупать шмотки", window_id)
                            state = settingsm.loadSettingsByHWND(window_id)
                            log(state, window_id)
                            energo_mode({window_id: data}, "on")
                            self.bot.send_message("admin", f"<b>Шото произошло, сначала сдохли но не сдохли\nНо потом точно сдохли и реснулись\n\n{result}</b>", charid=window_id)
                            self.pvpManager.remove_from_queue(window_id)
                        else:
                            log(f"Были не дохлые, попробовал возродиться тщетно {result}, чета случилось не обработанное, попробую поставить ему афк стейт", window_id)
                            self.bot.send_message("admin", f"<b>Ошибка при телепорте от пвп, чет случилось очень злое и не обработанное {result}</b>", charid=window_id)
                            min_sleep, max_sleep = map(int, SLEEP_AFTER_PVP_DODGE.split("-"))
                            sleep_minutes = random.randint(min_sleep, max_sleep)
                            nexttime = datetime.now() + timedelta(minutes=sleep_minutes)
                            data["InHome"] = nexttime.strftime('%Y-%m-%d %H:%M:%S')
                            data["State"] = "afk"
                            settingsm.editSettingsByHWND(window_id, data)
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
                    settingsm.editSettingsByHWND(window_id, data)
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
           # print(f"DEATH {death_queue}")
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
                        settingsm.editSettingsByHWND(window_id, data)
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
                                settingsm.editSettingsByHWND(window_id, data)
                                self.bot.send_message("admin", f"<b>Реснул перса, выкупил опыт и шмотки</b>", charid=window_id)
                                self.deathManager.remove_from_queue(window_id)

                    if self.pvpManager.get_queue() or self.spotManager.get_queue():
                        self.death_in_progress = False
                        break

                self.death_in_progress = False

    def process_hp_banks(self):
         if not self.banka_in_progress and not self.pvpManager.get_queue() and not self.spotManager.get_queue() and not self.deathManager.get_queue():
            bankaqueue = self.hpBankManager.get_queue()
            #print(f"banka {bankaqueue}")
            if bankaqueue:
                xy_to_check, rgb_to_check = parseCBT("hp_bank_in_energo")
                self.banka_in_progress = True
                while bankaqueue:
                    window_id = bankaqueue.popleft()
                    windowname = str(window_id)
                    data = self.settings[windowname]
                    is_true = check_pixel({window_id: data}, xy_to_check, rgb_to_check, 3)
                    if not is_true:
                        log(f"Ложное срабатывание банки, мб были в стане", window_id)
                        self.banka_in_progress = False
                        self.hpBankManager.remove_from_queue(window_id)
                        break

                    if data["State"] not in ["combat", "afk"]:
                        log(f"Ложное срабатывание банки, скорее всего стоим в стане {data['State']}", window_id)
                        self.banka_in_progress = False
                        self.hpBankManager.remove_from_queue(window_id)
                        if data["State"] == "death":
                            log(f"Вероятно багнулся, был в {data['State']} - переставил на афк, верну через пару минут на спот", window_id)
                            data["State"] = "afk"
                            nexttime = datetime.now() + timedelta(minutes=SLEEP_AFTER_RIP)
                            data["InHome"] = nexttime.strftime('%Y-%m-%d %H:%M:%S')
                            settingsm.editSettingsByHWND(window_id, data)

                        break

                    log(f"Пробую тпнуться в город, кончились баночки", window_id)
                    sdoh = checkRIP({window_id: data})
                    if sdoh:
                        res = respawn({window_id: data})
                        if res:
                            energo_mode({window_id: data}, "on")
                            log(f"Хотел купить баночки, но сдох, ресаюсь и чиллю", window_id)
                            data["State"] = "afk"
                            nexttime = datetime.now() + timedelta(minutes=SLEEP_AFTER_RIP)
                            data["InHome"] = nexttime.strftime('%Y-%m-%d %H:%M:%S')
                            settingsm.editSettingsByHWND(window_id, data)
                            self.hpBankManager.remove_from_queue(window_id)
                            self.banka_in_progress = False
                            break

                    teleport = teleportToTown({window_id: data}, True)
                    if teleport:
                        log(f"Тпнулся в город успешно", window_id)
                        data["State"] = "shopping"
                        settingsm.editSettingsByHWND(window_id, data)
                        log(f"Пробую пойти к магазу", window_id)
                        result = navigateToNPC({window_id: data}, "shop")
                        log(f"Результат закупочки - {result}", window_id)
                        log(f"Пробую тп на рандом спот", window_id)
                        result2 = teleportToRandomSpot({window_id: data}, SPOT_OT, SPOT_DO)
                        log(f"Результат тп на рандом спот - {result2}", window_id)
                        if result or result2:
                            log(f"После закупки и тп - {result}, {result2}", window_id)
                            data["InHome"] = "null"
                            data["State"] = "combat"
                            settingsm.editSettingsByHWND(window_id, data)
                            self.bot.send_message("admin",
                                              f"<b>Купил банки и вернул на спот</b>", charid=window_id)
                            log(f"Купил банки и вернул на спот", window_id)

                        else:
                            log(f"Чет пошло не так, не закупился и не тпнулся, ставлю окну афк + нулл", window_id)
                            nexttime = datetime.now() + timedelta(minutes=SLEEP_AFTER_RIP)
                            data["InHome"] = nexttime.strftime('%Y-%m-%d %H:%M:%S')
                            data["State"] = "afk"
                            settingsm.editSettingsByHWND(window_id, data)
                            self.hpBankManager.remove_from_queue(window_id)

                        self.hpBankManager.remove_from_queue(window_id)

                    else:
                        log(f"teleport to buy banks - {teleport}", window_id)
                        nexttime = datetime.now() + timedelta(minutes=SLEEP_AFTER_RIP)
                        data["InHome"] = nexttime.strftime('%Y-%m-%d %H:%M:%S')
                        data["State"] = "afk"
                        settingsm.editSettingsByHWND(window_id, data)
                        self.hpBankManager.remove_from_queue(window_id)

                    if self.pvpManager.get_queue() or self.spotManager.get_queue() or self.deathManager.get_queue():
                        self.banka_in_progress = False
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
                                settingsm.editSettingsByHWND(window_id, data)
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
                        settingsm.editSettingsByHWND(window_id, data)
                        self.farmManager.remove_from_queue(window_id)
                        self.farm_backer_in_progress = False
                        break
                    else:
                        rip = checkRIP({window_id: data})
                        if rip:
                            self.farmManager.remove_from_queue(window_id)
                            self.farm_backer_in_progress = False
                        else:
                            print(autohunt)
                            print("monkey")

                    energo = checkEnergoMode({window_id: data})
                    if energo:
                        energo_mode({window_id: data}, "off")

                    teleport = teleportToRandomSpot({window_id: data}, SPOT_OT, SPOT_DO)
                    if teleport:
                        hunt = checkAutoHunt({window_id: data})
                        if hunt:
                            data["State"] = "combat"
                            settingsm.editSettingsByHWND(window_id, data)
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
                                    settingsm.editSettingsByHWND(window_id, data)
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

    def process_mail(self):
        if not self.mail_in_progress and not self.farm_backer_in_progress and not self.pereves_in_progress and not self.banka_in_progress and not self.pvpManager.get_queue() and not self.spotManager.get_queue() and not self.deathManager.get_queue() and not self.perevesManager.get_queue():
            mailqueue = self.mailClaimerManager.get_queue()
            if mailqueue:
                self.mail_in_progress = True
                while mailqueue:

                    window_id = mailqueue.popleft()
                    windowname = str(window_id)
                    data = self.settings[windowname]
                    log(f"По графику пытаюсь собрать почту", window_id)
                    if data["State"] not in ["death", "stashing", "shopping"]:
                        energo = checkEnergoMode({window_id: data})
                        before = False
                        if energo:
                            before = True
                            energo_mode({window_id: data}, "off")

                        suc = False

                        if claim_mail({window_id: data}):
                            log("Почта собрана!", window_id)
                            suc = True
                        else:
                            log("Не удалось собрать почту...", window_id)

                        if suc:
                            self.mail_in_progress = False
                            self.mailClaimerManager.remove_from_queue(window_id)
                        else:
                            #todo
                            log("чет пошло не так при сборе почты по расписанию, возможно галочки не стоят?", window_id)
                            self.mail_in_progress = False
                            self.mailClaimerManager.remove_from_queue(window_id)

                        if before:
                            time.sleep(0.5)
                            energo_mode({window_id: data}, "on")

                    if self.pvpManager.get_queue() or self.spotManager.get_queue() or self.deathManager.get_queue() or self.hpBankManager.get_queue():
                        break

    def process_rewards(self):
        if not self.rewards_in_progress and not self.mail_in_progress and not self.farm_backer_in_progress and not self.pereves_in_progress and not self.banka_in_progress and not self.pvpManager.get_queue() and not self.spotManager.get_queue() and not self.deathManager.get_queue() and not self.perevesManager.get_queue():
            rewardsqueue = self.rewardsManager.get_queue()
            if rewardsqueue:
                self.rewards_in_progress = True
                while rewardsqueue:
                    before = False
                    window_id = rewardsqueue.popleft()
                    windowname = str(window_id)
                    data = self.settings[windowname]
                    log(f"По графику пытаюсь собрать все награды кроме почты", window_id)
                    if data["State"] not in ["death", "stashing", "shopping"]:
                        energo = checkEnergoMode({window_id: data})
                        if energo:
                            before = True
                            energo_mode({window_id: data}, "off")

                        if claim_clan({window_id: data}):
                            log("Клан собран!", window_id)
                        else:
                            log("Не удалось собрать клан...", window_id)

                        if claim_achiv({window_id: data}):
                            log("Ачивки собраны!", window_id)
                        else:
                            log("Не удалось собрать ачивки...", window_id)

                        if claim_daily({window_id: data}):
                            log("Дейлик собран!", window_id)
                        else:
                            log("Не удалось собрать дейлик...", window_id)

                        if claim_donate_shop({window_id: data}):
                            log("Успешно выкупил донат-шоп!", window_id)
                        else:
                            log("Не удалось выкупить донат-шоп...", window_id)

                        if claim_battle_pass({window_id: data}):
                            log("Успешно собрал весь бп", window_id)
                        else:
                            log("Не удалось собрать бп...", window_id)

                        self.rewards_in_progress = False
                        self.rewardsManager.remove_from_queue(window_id)

                        if before:
                            time.sleep(1.5)
                            energo_mode({window_id: data}, "on")

                    if self.pvpManager.get_queue() or self.spotManager.get_queue() or self.deathManager.get_queue() or self.hpBankManager.get_queue():
                        break

    def process_zakup_po_time(self):
        if not self.shop_stash_in_progress and not self.rewards_in_progress and not self.mail_in_progress and not self.farm_backer_in_progress and not self.pereves_in_progress and not self.banka_in_progress and not self.pvpManager.get_queue() and not self.spotManager.get_queue() and not self.deathManager.get_queue() and not self.perevesManager.get_queue():
            shopstashqueue = self.shopStashManager.get_queue()
            if shopstashqueue:
                self.shop_stash_in_progress = True
                while shopstashqueue:
                    before = False
                    window_id = shopstashqueue.popleft()
                    windowname = str(window_id)
                    data = self.settings[windowname]
                    log(f"По графику пытаюсь закупиться, продаться, сложиться", window_id)
                    if data["State"] not in ["death", "stashing", "shopping"]:
                        if data["State"] == "combat":
                            tp = teleportToTown({window_id: data}, True)
                            if tp:
                                log(f"tped {tp}", window_id)
                                zakup1 = navigateToNPC({window_id: data}, "shop|stash|buyer")
                                if zakup1:
                                    log("шото наделал, хз вроде закупился", window_id)

                                time.sleep(0.1)
                                teleportToRandomSpot({window_id: data}, SPOT_OT, SPOT_DO)
                                self.shop_stash_in_progress = False
                                self.shopStashManager.remove_from_queue(window_id)
                                break

                            else:
                                log("чет пошло не так, чини =(", window_id)

                    if self.pvpManager.get_queue() or self.spotManager.get_queue() or self.deathManager.get_queue() or self.hpBankManager.get_queue():
                        break

    def run(self):
        log("started")
        while True:
            if cfg.misc.PVP_DODGER:
                self.process_pvp()
            self.process_spots()
            self.process_death()
            if cfg.misc.BANKA_CHECKER:
                self.process_hp_banks()
            self.process_pereves()
            self.process_farmbacker()
            self.process_mail()
            self.process_rewards()
            self.process_zakup_po_time()

def main():
    scenary = Scenary()
    scenary.run()