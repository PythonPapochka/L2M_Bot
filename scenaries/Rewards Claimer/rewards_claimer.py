import time
import os
from datetime import datetime, timedelta
from clogger import log

from methods.base_methods import loadSettings, editSettingsByHWND

from methods.game_utils import energo_mode, checkEnergoMode, \
    claim_clan, claim_mail, claim_achiv, claim_daily, \
    claim_battle_pass, claim_donate_shop

from tgbot.tg import TgBotus

class Scenary:
    def __init__(self):
        self.bot = TgBotus()
        self.filename = os.path.splitext(os.path.basename(__file__))[0]
        self.bot.send_message("admin", f"✅ <b>Успешно запустили сценарий!</b>\n<code>{self.filename}</code>")

        self.settings = loadSettings()

    def process_rewards(self):
        for nickname, data in self.settings.items():
            before = False
            windowInfo = {nickname: data}
            log("Пробую забрать награды", nickname)
            windowdata = data["State"] #todo допилить чтоб не собирало награды у... у кого?
            if windowdata not in ["death", "stashing", "shopping", "claiming"]:
                energomode = checkEnergoMode(windowInfo)
                if energomode:
                    before = True
                    energo_mode(windowInfo, "off")

                if claim_clan(windowInfo):
                    log("Клан собран!", nickname)
                else:
                    log("Не удалось собрать клан...", nickname)

                if claim_achiv(windowInfo):
                    log("Ачивки собраны!", nickname)
                else:
                    log("Не удалось собрать ачивки...", nickname)

                if claim_mail(windowInfo):
                    log("Почта собрана!", nickname)
                else:
                    log("Не удалось собрать почту...", nickname)

                if claim_daily(windowInfo):
                    log("Дейлик собран!", nickname)
                else:
                    log("Не удалось собрать дейлик...", nickname)

                if claim_donate_shop(windowInfo):
                    log("Успешно выкупил донат-шоп!", nickname)
                else:
                    log("Не удалось выкупить донат-шоп...", nickname)

                if claim_battle_pass(windowInfo):
                    log("Собрал фулл бп", nickname)
                else:
                    log("Не смог собрать бп...", nickname)

                if before:
                    time.sleep(2)
                    energo_mode(windowInfo, "on")

        return

    def run(self):
        self.process_rewards()
        time.sleep(0.05)

def main():
    scenary = Scenary()
    scenary.run()