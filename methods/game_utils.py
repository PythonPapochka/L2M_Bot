from interception import inputs
import time
from clogger import log
from constans import NPCS, NPC_CHECK_BUTTONS
from methods.base_methods import click_mouse, parseCBT, check_pixel, load_config, activate_window, find_BP_1, find_BP_2, \
    move_mouse
import json
import random
import math

def claim_achiv(windowInfo):
    claimed = False
    def wait_and_click(tag, timeout=5):
        xy, rgb = parseCBT(tag)
        if check_pixel(windowInfo, xy, rgb, timeout):
            x, y = xy
            click_mouse(windowInfo, x, y)
            return True
        return False

    windowid = next(iter(windowInfo))

    if checkEnergoMode(windowInfo):
        before = True
        energo_mode(windowInfo, "off")

    if not wait_and_click("red_dot_achiv", 5):
        return False

    if not wait_and_click("red_dot_achiv2", 3):
        close = wait_and_click("npc_global_quit_button", 5)
        return False

    while True:
        found_clan_3 = wait_and_click("achiv_claim_1", 2)
        found_clan_4 = wait_and_click("achiv_claim_accept", 2)

        if not found_clan_3:
            claimed = True
            close = wait_and_click("npc_global_quit_button", 5)
            time.sleep(2)
            break

    if not claimed:
        return False

    return True

def claim_mail(windowInfo):
    claimed = False
    def wait_and_click(tag, timeout=5):
        xy, rgb = parseCBT(tag)
        if check_pixel(windowInfo, xy, rgb, timeout):
            x, y = xy
            click_mouse(windowInfo, x, y)
            return True
        return False

    windowid = next(iter(windowInfo))

    if checkEnergoMode(windowInfo):
        before = True
        energo_mode(windowInfo, "off")

    if not wait_and_click("main_menu_gui", 5):
        return False

    if not wait_and_click("red_dot_mail", 3):
        close = wait_and_click("npc_global_quit_button", 5)
        return False

    if not wait_and_click("claim_all_mail", 5):
        close = wait_and_click("npc_global_quit_button", 5)
        return False

    time.sleep(5)
    claimed = True
    close = wait_and_click("npc_global_quit_button", 5)
    time.sleep(2)

    if not claimed:
        return False

    return True


def claim_battle_pass(windowInfo):

    def wait_and_click(tag, timeout=5):
        xy, rgb = parseCBT(tag)
        if check_pixel(windowInfo, xy, rgb, timeout):
            x, y = xy
            click_mouse(windowInfo, x, y)
            return True
        return False

    windowid = next(iter(windowInfo))
    xy_sbor1, rgb_sbor1 = parseCBT("battle_pass_sbor_1")
    xy_sbor2, rgb_sbor2 = parseCBT("battle_pass_sbor_2")
    xy_sbor22, rgb_sbor22 = parseCBT("battle_pass_sbor_2_2")
    xy_empty, rgb_empty = parseCBT("battle_pass_empty")
    xe, ye = xy_empty


    if checkEnergoMode(windowInfo):
        energo_mode(windowInfo, "off")
        time.sleep(0.2)

    if not wait_and_click("main_menu_gui", 5):
        return False

    if not wait_and_click("battle_pass_red_dot_gui", 3):
        log("Батлпасса нет, собирать не будем", windowid)
        close = wait_and_click("npc_global_quit_button", 5)
        return False
    
    time.sleep(3)
    tabs = find_BP_1(windowInfo)
    log(f"Обнаружил вкладок бп: {len(tabs)}, начинаю чекать...", windowid)

    for i, tab in enumerate(tabs, 1):
        if len(tab) >= 2:
            x, y = map(int, tab[0].split(", "))
            xy = (x, y)

            if tab[1] == "no":
                rgb = "no"
            else:
                r, g, b = map(int, tab[1].split(", "))
                rgb = (r, g, b)

        x, y = xy
        click_mouse(windowInfo, x, y)

        podtabs = find_BP_2(windowInfo)
        for q, podtab in enumerate(podtabs, 1):
            if len(podtab) >= 2:
                x, y = map(int, podtab[0].split(", "))
                xy = (x, y)

                if podtab[1] == "no":
                    rgb = "no"
                else:
                    r, g, b = map(int, podtab[1].split(", "))
                    rgb = (r, g, b)

            x, y = xy
            click_mouse(windowInfo, x, y)

            while True:
                if check_pixel(windowInfo, xy_sbor1, rgb_sbor1, 2):
                    log(f"Вижу цель во вкладке {i} и подвкладке {q}, собираю!", windowid)
                    x, y = xy_sbor1
                    click_mouse(windowInfo, x, y)
                    time.sleep(0.05)
                    move_mouse(windowInfo, xe, ye)
                    time.sleep(1.2)
                else:
                    log(f"Награды во вкладке {i} и подвкладке {q} кончились либюо их не было", windowid)
                    break
            
        time.sleep(1)
            
        found_1 = check_pixel(windowInfo, xy_sbor2, rgb_sbor2, 2)
        found_2 = check_pixel(windowInfo, xy_sbor22, rgb_sbor22, 2)

        if found_1:
            x, y = xy_sbor2
            click_mouse(windowInfo, x, y)
            time.sleep(5)
        elif found_2:
            x, y = xy_sbor22
            click_mouse(windowInfo, x, y)
            time.sleep(5)
        else:
            log("Собирать нечего, иду чекать некст вкладку если она есть", windowid)

        log("Походу собрал фулл бп, ливаю?", windowid)

    close = wait_and_click("npc_global_quit_button", 5)
    if tabs:
        return True

    return False


def claim_daily(windowInfo):
    def wait_and_click(tag, timeout=5):
        xy, rgb = parseCBT(tag)
        if check_pixel(windowInfo, xy, rgb, timeout):
            x, y = xy
            click_mouse(windowInfo, x, y)
            return True
        return False

    windowid = next(iter(windowInfo))

    if checkEnergoMode(windowInfo):
        before = True
        energo_mode(windowInfo, "off")

    if not wait_and_click("main_menu_gui", 5):
        return False

    if not wait_and_click("red_dot_daily_rewards", 3):
        log("Дейликов нет, собирать не будем", windowid)
        close = wait_and_click("npc_global_quit_button", 5)
        return False

    xy, rgb = parseCBT("red_dot_daily_2")
    dot2 = check_pixel(windowInfo, xy, rgb, 5)
    if not dot2:
        close = wait_and_click("npc_global_quit_button", 5)
        return False

    if wait_and_click("daily_rewards_claim", 3):
        close = wait_and_click("npc_global_quit_button", 5)
        return True

    return False

def claim_clan(windowInfo):
    before = False
    def wait_and_click(tag, timeout=5):
        xy, rgb = parseCBT(tag)
        if check_pixel(windowInfo, xy, rgb, timeout):
            x, y = xy
            click_mouse(windowInfo, x, y)
            return True
        return False

    windowid = next(iter(windowInfo))

    if checkEnergoMode(windowInfo):
        energo_mode(windowInfo, "off")
        time.sleep(1)

    if not wait_and_click("main_menu_gui", 5):
        return False

    if not wait_and_click("red_dot_clan", 2):
        close = wait_and_click("npc_global_quit_button", 5)
        return False

    if not wait_and_click("clan_1", 3):
        close = wait_and_click("npc_global_quit_button", 5)
        return False

    if not wait_and_click("clan_2", 3):
        close = wait_and_click("npc_global_quit_button", 5)
        return False

    while True:
        found_clan_3 = wait_and_click("clan_3", 2)
        found_clan_4 = wait_and_click("clan_4", 2)

        if found_clan_3:
            if found_clan_4:
                time.sleep(0.5)
                wait_and_click("clan_4", 1)
            continue
        else:
            break

    if wait_and_click("clan_5", 5):
        if wait_and_click("clan_6", 5):
            time.sleep(0.3)
            wait_and_click("npc_global_quit_button", 5)
            time.sleep(2)
            return True
        else:
            close = wait_and_click("npc_global_quit_button", 5)
            return False

    return False

def claim_aliance(windowInfo):
    #не делать, его нет на японии
    pass

def claim_donate_shop(windowInfo):
    cfg = load_config()
    vkladki = [int(x.strip()) for x in cfg.other.MAGAZ_PAGES.split(",")]

    def wait_and_click(tag, timeout=5):
        xy, rgb = parseCBT(tag)
        if check_pixel(windowInfo, xy, rgb, timeout):
            x, y = xy
            click_mouse(windowInfo, x, y)
            return True
        return False

    def go_to_tab(tab_num):
        tag = f"magaz_str_{tab_num}"
        result = wait_and_click(tag, 5)
        time.sleep(1)
        return result

    windowid = next(iter(windowInfo))

    if checkEnergoMode(windowInfo):
        energo_mode(windowInfo, "off")
        time.sleep(2)

    if not wait_and_click("magaz_gui_open", 5):
        return False

    if wait_and_click("magaz_reklama_trigger", 5):
        if wait_and_click("magaz_reklama_close", 2):
            log("Вылезла реклама, закрыл гадость", windowid)

    if not wait_and_click("red_dot_magaz", 4):
        wait_and_click("npc_global_quit_button", 5)
        return False

    for tab in vkladki:
        if not go_to_tab(tab):
            continue

        time.sleep(1)

        if not wait_and_click("purc_all_magaz", 10):
            wait_and_click("npc_global_quit_button", 5)
            return False

        if not wait_and_click("buy_all_magaz", 5):
            wait_and_click("close_buy_magaz", 5)
            time.sleep(1)
            wait_and_click("npc_global_quit_button", 5)
            log("чет пошло не так, бабахед", windowid)
            return False

        xy, rgb = parseCBT("purc_all_magaz")
        if check_pixel(windowInfo, xy, rgb, timeout=10):
            time.sleep(0.1)
        else:
            log("чет пошло не так, не трогаю окно, зырь в него", windowid)
            return False

    if not wait_and_click("close_magaz", 20):
        wait_and_click("npc_global_quit_button", 5)
        return False

    time.sleep(1)
    return True

def checkAutoHunt(windowInfo):
    windowid = next(iter(windowInfo))
    xy, rgb = parseCBT("auto_combat_ON")
    result = check_pixel(windowInfo, xy, rgb, 12, 10, "4x4")
    if result:
        log("Автобой включен" ,windowid)
        return True
    else:
        log("Автобой выключен", windowid)
        return False

def teleportToTown(windowInfo, energo):
    windowid = next(iter(windowInfo))
    log("Начало тп в город", windowid)
    emode = False
    if not energo:
        if checkEnergoMode(windowInfo):
            log("Энергомод включен, продолжаю тпаться", windowid)
            emode = True
            xy, rgb = parseCBT("home_scroll_button_energomode")
        else:
            log("Энергомод выключен, продолжаю тпаться", windowid)
            emode = False
            xy, rgb = parseCBT("home_scroll_button_no_energomode")
    else:
        emode = True
        xy, rgb = parseCBT("home_scroll_button_energomode")

    log("Ищу свиток тп", windowid)
    if xy and rgb and check_pixel(windowInfo, xy, rgb, 1.5, 8):
        x, y = xy
        log(f"Свиток тк найден, {xy}", windowid)
        gui_xy, gui_rgb = parseCBT("zalupka_gui")
        start_time = time.time()
        timeout = 60
        click_mouse(windowInfo, x, y)
        log(f"Начал ждать телепорта", windowid)
        founds = 0
        while time.time() - start_time < timeout:
            log(f"Тпаюсь", windowid)
            lvlup = checkLvlUp(windowInfo)
            if lvlup:
                log(f"Вероятно был лвл ап?", windowid)
            if not checkEnergoMode(windowInfo) and emode:
                log("Не в энерго")
                founds += 1
                if founds >= 6:
                    log("брикед, не в энерго 100%", windowid)
                    time.sleep(5)
            else:
                log("залупки гуи нет, не брикаю, буду спать 10 сек", windowid)
                time.sleep(10)

            if check_pixel(windowInfo, xy, rgb, 0.5):
                log(f"Кликнул по свитку", windowid)
                click_mouse(windowInfo, x, y)

            time.sleep(0.05)

            if check_pixel(windowInfo, gui_xy, gui_rgb, 0.5):
                log("Залупка гуи 100% есть, вернусь через 2 сек", windowid)
                time.sleep(2)
                return True

    log(f"Фолс при тп в город, хз", windowid)
    return False


def teleportToRandomSpot(windowInfo, from_=1, to_=4):
    time.sleep(2)
    windowid = next(iter(windowInfo))
    random_spot = random.randint(from_, to_)
    cbt_choices = [
        "spot_teleport_call_button",
        f"spot_choice_{random_spot}",
        f"spot_acept_choice_{random_spot}"
    ]
    log(f"Пробую тпнуться на спот №{random_spot}", windowid)
    if checkEnergoMode(windowInfo):
        log(f"При тп на спот был в энерго, вырубил", windowid)
        # todo забить на это болт и вызывать функцию исключительно после выхода
        energo_mode(windowInfo, "off")
        time.sleep(2)

    for cbt_choice in cbt_choices:
        xy, rgb = parseCBT(cbt_choice)
        if not check_pixel(windowInfo, xy, rgb, 3):
            log(f"Не нашел кнопку за 3 сек, фолс {cbt_choice}", windowid)
            return False

        x, y = xy
        result = click_mouse(windowInfo, x, y)
        if not result:
            return False
        time.sleep(0.1)

    time.sleep(2)
    xy, rgb = parseCBT("zalupka_gui")
    log(f"Начал ждать залупку гуи 10 сек", windowid)
    teleported = check_pixel(windowInfo, xy, rgb, 10)
    if teleported:
        log(f"Залупка гуи детектед, врубаю автобой и энрго", windowid)
        xy, rgb = parseCBT("auto_combat_mode_gui")
        time.sleep(2)
        x, y = xy
        log(f"Автобой включен епта", windowid)
        result = click_mouse(windowInfo, x, y)
        if result:
            time.sleep(0.2)
            energo_mode(windowInfo, "on")
            time.sleep(0.05)
            return True

    log(f"Фолс при тп на спот, ъх", windowid)
    return False


def buyLootAfterRIP(windowInfo):
    windowid = next(iter(windowInfo))
    log(f"Начало выполнения закупки опыта после рипа", windowid)
    if not checkEnergoMode(windowInfo):
        log(f"Не нахожусь в энерго при закупке опыта", windowid)
        xy, rgb = parseCBT("krest_after_respawn")
        log(f"Начинаю искать krest_after_respawn", windowid)
        if check_pixel(windowInfo, xy, rgb, 3):
            log(f"Нашел krest_after_respawn, кликаю", windowid)
            x, y = xy
            result = click_mouse(windowInfo, x, y)
            log(f"Начинаю ждать respawn_icon_in_gui", windowid)
            xy, rgb = parseCBT("respawn_icon_in_gui")
            result = check_pixel(windowInfo, xy, rgb, 2)
            if result:
                log(f"Охуенно, нашел респавн иконку, жду монетку", windowid)
                xy, rgb = parseCBT("monetka_respawn")
                while True:
                    log(f"Начал чекать монетку гуи", windowid)
                    result = check_pixel(windowInfo, xy, rgb, 3)
                    log(f"Результат монетки - {result}", windowid)
                    if not result:
                        x, y = xy
                        click = click_mouse(windowInfo, x, y)
                        time.sleep(0.05)
                    if result:
                        log(f"Монетка стоит, брикаю", windowid)
                        break

                time.sleep(0.3)
                value = []
                log(f"Начинаю чекать кол-во экспы на выкуп", windowid)
                for h in range(1, 5):
                    time.sleep(0.3)
                    cbt = f"respawn_monetka_exp_{h}"
                    xy, rgb = parseCBT(cbt)
                    result = check_pixel(windowInfo, xy, rgb)
                    log(f"Пробую выкупить respawn_monetka_exp_{h}", windowid)
                    if result:
                        value.append(cbt)
                        x, y = xy
                        click_mouse(windowInfo, x, y)
                        log(f"Кликнул по respawn_monetka_exp_{h}", windowid)
                    if h == 2 and not result:
                        log(f"Видимо была только один опыт на выкуп respawn_monetka_exp_{h} не нашел и результ фалс", windowid)
                        break

                log(f"Валью: {value}", windowid)
                if value:
                    log(f"Суммарно выкупил: {value}", windowid)
                    xy, rgb = parseCBT("respawn_buy_gui_button")
                    result = check_pixel(windowInfo, xy, rgb, 2)
                    log(f"Проверка респавн_бай_гуи_бутон: {result}", windowid)
                    if result:
                        x, y = xy
                        click = click_mouse(windowInfo, x, y)
                        log(f"Кликнул по respawn_buy_gui_button", windowid)
                        time.sleep(0.05)
                        xy, rgb = parseCBT("respawn_accept_buy_gui_button")
                        result = check_pixel(windowInfo, xy, rgb, 3)
                        log(f"Проверка respawn_accept_buy_gui_button: {result}", windowid)
                        if result:
                            x, y = xy
                            click = click_mouse(windowInfo, x, y)
                            time.sleep(4)
                            lvlup = checkLvlUp(windowInfo)
                            if lvlup:
                                log(f"Вероятно был лвл ап?", windowid)
                            xy, rgb = parseCBT("respawn_exit_gui_button")
                            x, y = xy
                            result = click_mouse(windowInfo, x, y)
                            log(f"Успешно выкупил {len(value)} шт опыта!", windowid)
                            time.sleep(1)
                            lvlup = checkLvlUp(windowInfo)
                            if lvlup:
                                log(f"сломался лвл ап чек", windowid)
                            return True
                else:
                    xy, rgb = parseCBT("respawn_exit_gui_button")
                    x, y = xy
                    result = click_mouse(windowInfo, x, y)
                    log("Шось жоско поломалось да и пох", windowid)
                    return False

            else:
                log("Не нужно выкупать предметы", windowid)
                return True

def checkRIP(windowInfo):
    windowid = next(iter(windowInfo))
    cbts = ["you_were_killed_energomode", "check_death_penalty", "respawn_village"]
    log(f"Начал чекать смерть, ща насру логами...", windowid)
    for cbt in cbts:
        log(f"Чекаю {cbt}", windowid)
        xy, rgb = parseCBT(cbt)
        if check_pixel(windowInfo, xy, rgb, 0.5):
            log(f"Детектнул {cbt}", windowid)
            return True

    return False

def checkLvlUp(windowInfo):
    windowid = next(iter(windowInfo))
    xy, rgb = parseCBT("lvl_up_black")
    log(f"Чекаю лвл ап залупу", windowid)
    teleported = check_pixel(windowInfo, xy, rgb, 3)
    if teleported:
        log(f"Лвл ап вылез, закрываю", windowid)
        xy, rgb = parseCBT("lvl_up_close")
        x, y = xy
        click_mouse(windowInfo, x, y)
        return True
    else:
        log(f"Вероятно лвл апа не было {teleported}", windowid)
        return False

def checkEnergoMode(windowInfo):
    windowid = next(iter(windowInfo))

    cbts = ["energomode_center_gui"]

    for cbt in cbts:
        xy, rgb = parseCBT(cbt)
        if not check_pixel(windowInfo, xy, rgb, 0.5):
            log(f"Не находимся в энерго", windowid)
            return False

    log(f"Находимся в энергорежиме", windowid)
    return True


def navigateToNPC(windowInfo, NPC):
    windowid = next(iter(windowInfo))
    NPC_list = NPC.split("|") if "|" in NPC else [NPC]
    log(f"Пробую бежать по списочку {NPC}", windowid)
    energo = checkEnergoMode(windowInfo)
    if energo:
        log(f"Во время навигейта был в энерго, оффаю", windowid)
        energo_mode(windowInfo, "off")
        time.sleep(0.2)

    lvlup = checkLvlUp(windowInfo)
    if lvlup:
        log(f"Закрыл лвл ап", windowid)

    town, allNPC = checkINtown(windowInfo)
    if not town:
        log(f"Вроде не нахожусь в городе, или шо", windowid)
        return False
    else:
        log(f"Вроде нахожусь в городе, или шо", windowid)

    npcPositions = allNPC
    if not npcPositions:
        log("? error in navigate", windowid)
        return False

    json_pos = json.loads(npcPositions)
    log(f"Списка жсон: {json_pos}", windowid)
    for current_npc in NPC_list:
        if current_npc not in json_pos:
            continue

        log(f"Кликнул по нпс: {current_npc}", windowid)

        data = json_pos[current_npc]
        xy, rgb = parseCBT(data)
        x, y = xy
        click_mouse(windowInfo, x, y)

        if current_npc in NPC_CHECK_BUTTONS:
            log(f"{current_npc} находится в {NPC_CHECK_BUTTONS}, жду появления гуи", windowid)
            xy, rgb = parseCBT(NPC_CHECK_BUTTONS[current_npc])
            attempts = 0
            while not check_pixel(windowInfo, xy, rgb, 1):
                log(f"Все еще бегу к {current_npc}", windowid)
                time.sleep(0.005)
                attempts += 1
                if attempts >= 200:
                    log(f"Лимит попыток беготни к {current_npc}", windowid)
                    return False

            def click_button(button_name):
                if button_name in ["npc_shop_button_1", "npc_stash_button_1", "npc_buyer_button_1"]:
                    time.sleep(0.1)

                xy, rgb = parseCBT(button_name)
                x, y = xy
                result = check_pixel(windowInfo, xy, rgb, 3)
                if result:
                    log(f"Кликнул по {button_name}", windowid)
                    click_mouse(windowInfo, x, y)
                    return True
                elif not result and button_name in ["npc_shop_button_2", "npc_stash_button_2", "npc_buyer_button_2"]:
                    return True
                return False

            def waitAndClick(buttons):
                for button in buttons:
                    if not click_button(button):
                        if button in ["npc_shop_button_2", "npc_stash_button_2", "npc_buyer_button_2"]:
                            return False
                        return False
                return True

            if current_npc == "shop":
                if waitAndClick(["npc_shop_button_1", "npc_shop_button_2", "npc_shop_button_3"]):
                    result = click_button("npc_global_quit_button")
                    if result:
                        time.sleep(0.01)
                        continue
                else:
                    result = click_button("npc_global_quit_button")
                    if not result:
                        time.sleep(0.01)
                        return False

            if current_npc == "stash":
                if waitAndClick(["npc_stash_button_1", "npc_stash_button_2"]):
                    result = click_button("npc_global_quit_button")
                    if result:
                        time.sleep(0.01)
                        continue
                else:
                    result = click_button("npc_global_quit_button")
                    if not result:
                        time.sleep(0.01)
                        return False

            elif current_npc == "buyer":
                if waitAndClick(["npc_buyer_button_1", "npc_buyer_button_2", "npc_buyer_button_3"]):
                    result = click_button("npc_global_quit_button")
                    if result:
                        time.sleep(0.01)
                        continue
                else:
                    result = click_button("npc_global_quit_button")
                    if not result:
                        time.sleep(0.01)
                        return False

    return True

def checkINtown(windowInfo, timeout=10):
    windowid = next(iter(windowInfo))
    start_time = time.time()
    log(f"Начал проверять в городе ли я, таймаут: {timeout}", windowid)
    while time.time() - start_time < timeout:
        xy, rgb = parseCBT("white_cube_in_minimap")
        log(f"Чекаю белый кубик на мапе", windowid)
        result = check_pixel(windowInfo, xy, rgb, 1)
        if result:
            log(f"Белый кубик найден, открываю список нпс", windowid)
            xy, rgb = parseCBT("npc_list_in_town")
            x, y = xy
            result = click_mouse(windowInfo, x, y)
            if result:
                log(f"Открыл список нпс, получаю позиции", windowid)
                time.sleep(0.03)
                allNPC = getNPCposition(windowInfo)
                if allNPC:
                    log("Нахожусь в городе, список нпс открыт", windowid)
                    return True, allNPC
        else:
            if 1==2:
            #if checkEnergoMode(windowInfo): #kostyl
                log("Не нашел карту, мы в энергомоде", windowid)
                return False, None
            else:
                log(f"Белого кубика не было, чекаю позиции в тупую", windowid)
                allNPC = getNPCposition(windowInfo)
                if allNPC:
                    log("Список нпс уже открыт, мы в городе", windowid)

                    return True, allNPC

                elif checkRIP(windowInfo):
                    log("Умер прямо в момент тпшки в город, ресаюсь", windowid)
                    res = respawn(windowInfo)
                    if res:
                        log("Встал, верну фолс", windowid)
                        return False, None

                else:
                    log("Все условия не пройдены, жесть", windowid)

    log("Не удалось определить, в городе ли мы =( (ТАЙМАУТ ТИПО ИСТЕК)", windowid)
    return False, None

def getNPCposition(windowInfo):
    npc_mapping = {}
    windowid = next(iter(windowInfo))
    log(f"Пробую получить позиции нпс ( вроде сломана навигация )", windowid)
    for j in [4, 3]:
        xy, rgb = parseCBT(f"npc_list_{j}")
        log(f"Пробую чекнуть npc_list_{j} ({xy}, {rgb})", windowid)
        result = check_pixel(windowInfo, xy, rgb, 1.5, 2, "1x1")
        log(f"npc_list_{j} ({xy}, {rgb}) | {result}", windowid)
        if result:
            log(f"Детектнул позиции, возможно бабах ноо {j}", windowid)
            if j == 4:
                npc_mapping = {
                    "stash": f"npc_list_{j}",
                    "shop": "npc_list_2",
                    "buyer": "npc_list_6"
                }
            if j == 3:
                npc_mapping = {
                    "stash": f"npc_list_{j}",
                    "shop": "npc_list_1",
                    "buyer": "npc_list_5"
                }
            break
    if npc_mapping:
        log(json.dumps(npc_mapping, indent=4), windowid)
        return json.dumps(npc_mapping, indent=4)
    else:
        log("getnpc false, и 3 и 4 не прошли", windowid)
        return None

def respawn(windowInfo): #todo refactor govnocode
    windowid = next(iter(windowInfo))
    log(f"Начало респавн функи, чекаю энергомод", windowid)
    if checkEnergoMode(windowInfo):
        log(f"Был в энерго при респавне, выключил", windowid)
        r = energo_mode(windowInfo, "off")

    cbts = ["check_death_penalty", "respawn_village"]
    max_attempts = 200
    result = False
    log(f"Начинаю чекать {cbts}", windowid)
    for _ in range(max_attempts):
        for cbt in cbts:
            #print(cbt)
            log(f"Проверяю {cbt}", windowid)
            xy, rgb = parseCBT(cbt)
            if check_pixel(windowInfo, xy, rgb, 0.5):
                log(f"Нашел кнопку, завершаюсь {cbt}", windowid)
                result = True
                break
            else:
                log(f"Пока все еще не нашел {cbt}", windowid)

        if result:
            break

        time.sleep(0.02)

    if result:
        x, y = xy
        result = click_mouse(windowInfo, x, y)
        log(f"Кликнул по кнопке реса, сплю 2 сек и чекаю лвл ап", windowid)
        if result:
            time.sleep(2)
            lvlup = checkLvlUp(windowInfo)
            if lvlup:
                log(f"сломался лвл ап чек", windowid)

            xy, rgb = parseCBT("zalupka_gui")
            log(f"Начинаю ждать залупку_гуи в респавн функе", windowid)
            teleported = check_pixel(windowInfo, xy, rgb, 5)
            if 1==1: #todo
                log("Успешно восстал из мертвых (залупка гуи на месте)", windowid)
                return True
            else:
                log(f"Залупки гуи не было, верну фолс", windowid)

    return False

def energo_mode(windowInfo, state):
    inputs.auto_capture_devices(keyboard=True, mouse=True)
    if windowInfo:
        window_id, window = next(iter(windowInfo.items()))
        button_xy, button_rgb = parseCBT("energo_mode_gui")
        button_x, button_y = button_xy

        if state == "off":
            activate_window(windowInfo)
            width = window["Width"]
            height = window["Height"]
            position_x, position_y = window["Position"]
            center_x = position_x + width // 2
            center_y = position_y + height // 2
            radius = 15

            inputs.move_to(center_x, center_y)
            time.sleep(0.05)
            inputs.mouse_down("left")

            points = []
            for i in range(5):
                angle = math.pi / 2 + 2 * math.pi * i / 5
                x = center_x + radius * math.cos(angle)
                y = center_y - radius * math.sin(angle)
                points.append((x, y))

            zv = [points[0], points[2], points[4], points[1], points[3], points[0]]

            for x, y in zv:
                inputs.move_to(x, y)
                time.sleep(0.01)

            inputs.mouse_up("left")
            xy1, rgb1 = parseCBT("zalupka_gui")
            teleported = check_pixel(windowInfo, xy1, rgb1, 10)
            if teleported:
                lvlup = checkLvlUp(windowInfo)
                if lvlup:
                    log(f"сломался лвл ап чек", window_id)
                    
                return True
            else:
                if checkEnergoMode(windowInfo):
                    log("Шось пошло не так при снятии с энерго", window_id)
                    inputs.move_to(center_x, center_y)
                    inputs.mouse_down("left")
                    time.sleep(0.05)
                    inputs.move_to(center_x - 75, center_y - 50)
                    time.sleep(0.05)
                    inputs.mouse_up("left")
                    time.sleep(0.2)
                    
                time.sleep(1)
                lvlup = checkLvlUp(windowInfo)
                if lvlup:
                    log(f"сломался лвл ап чек", window_id)

                teleported = check_pixel(windowInfo, xy1, rgb1, 3)
                if teleported:
                    return True

            return False

        elif state == "on":
            click_mouse(windowInfo, button_x, button_y)
            time.sleep(0.4)
            width = window["Width"]
            height = window["Height"]
            center_x = width // 2
            center_y = height // 2

            click_mouse(windowInfo, center_x, center_y)

            return True

    return False
