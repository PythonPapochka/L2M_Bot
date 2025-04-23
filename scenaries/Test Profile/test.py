import time
import os
from clogger import log

from methods.base_methods import loadSettings

from methods.game_utils import energo_mode, checkEnergoMode, \
    claim_battle_pass

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
            log("Пробую чекнуть кол-во вкладок бп", nickname)
            windowdata = data["State"] #todo допилить чтоб не собирало бп у... у кого?
            if windowdata not in ["death", "stashing", "shopping", "claiming"]:
                energomode = checkEnergoMode(windowInfo)
                if energomode:
                    before = True
                    energo_mode(windowInfo, "off")

                ress = claim_battle_pass(windowInfo)

                if before:
                    time.sleep(2)
                    energo_mode(windowInfo, "on")
                    time.sleep(2)

        return

    def run(self):
        self.process_rewards()
        time.sleep(0.05)

def main():
    scenary = Scenary()
    scenary.run()