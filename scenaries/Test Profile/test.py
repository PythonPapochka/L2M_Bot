import time
import os
from clogger import log

from methods.base_methods import SettingsManager

from methods.game_utils import energo_mode, checkEnergoMode, \
    claim_battle_pass, teleportToTown, teleportToRandomSpot, navigateToNPC

from tgbot.tg import TgBotus

settingsm = SettingsManager()

class Scenary:
    def __init__(self):
        self.bot = TgBotus()
        self.filename = os.path.splitext(os.path.basename(__file__))[0]
        self.bot.send_message("admin", f"✅ <b>Успешно запустили сценарий!</b>\n<code>{self.filename}</code>")

        self.settings = settingsm.loadSettings()

    def process_rewards(self):
        for nickname, data in self.settings.items():
            before = False
            windowInfo = {nickname: data}
            windowdata = data["State"] #todo допилить чтоб не собирало бп у... у кого?
            if windowdata not in ["death", "stashing", "shopping", "claiming"]:

                tp = teleportToTown({nickname: data}, True)
                if tp:
                    zakup1 = navigateToNPC({nickname: data}, "shop|stash|buyer")
                    if zakup1:
                        log("yes", nickname)

                    time.sleep(0.1)
                    teleportToRandomSpot({nickname: data}, 1, 1)

        return

    def run(self):
        self.process_rewards()
        time.sleep(0.05)

def main():
    scenary = Scenary()
    scenary.run()