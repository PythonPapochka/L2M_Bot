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
    xy, rgb = parseCBT("auto_combat_ON")
    result = check_pixel(windowInfo, xy, rgb, 8)
    if result:
        return True
    else:
        return False

def teleportToTown(windowInfo, energo):
    windowid = next(iter(windowInfo))

    if not energo:
        if checkEnergoMode(windowInfo):
            xy, rgb = parseCBT("home_scroll_button_energomode")
        else:
            xy, rgb = parseCBT("home_scroll_button_no_energomode")
    else:
        xy, rgb = parseCBT("home_scroll_button_energomode")

    if xy and rgb and check_pixel(windowInfo, xy, rgb, 0.5):
        x, y = xy
        gui_xy, gui_rgb = parseCBT("zalupka_gui")
        start_time = time.time()
        timeout = 10

        while time.time() - start_time < timeout:
            if check_pixel(windowInfo, gui_xy, gui_rgb, 0.5):
                break
            else:
                log("еще тпаюсь", windowid)

            if check_pixel(windowInfo, xy, rgb, 0.5):
                click_mouse(windowInfo, x, y)
            else:
                break

            time.sleep(0.05)

        if check_pixel(windowInfo, gui_xy, gui_rgb, 0.5):
            log("тпнулся", windowid)
            time.sleep(2)
            return True

    return False


def teleportToRandomSpot(windowInfo, from_=1, to_=4):
    windowid = next(iter(windowInfo))
    random_spot = random.randint(from_, to_)
    cbt_choices = [
        "spot_teleport_call_button",
        f"spot_choice_{random_spot}",
        f"spot_acept_choice_{random_spot}"
    ]

    if checkEnergoMode(windowInfo):
        # todo забить на это болт и вызывать функцию исключительно после выхода
        energo_mode(windowInfo, "off")
        time.sleep(2)

    for cbt_choice in cbt_choices:
        xy, rgb = parseCBT(cbt_choice)
        if not check_pixel(windowInfo, xy, rgb, 3):
            return False

        x, y = xy
        result = click_mouse(windowInfo, x, y)
        if not result:
            return False
        time.sleep(0.1)

    time.sleep(3.5)
    xy, rgb = parseCBT("zalupka_gui")
    teleported = check_pixel(windowInfo, xy, rgb, 10)
    if teleported:
        xy, rgb = parseCBT("auto_combat_mode_gui")
        time.sleep(2)
        x, y = xy
        result = click_mouse(windowInfo, x, y)
        if result:
            time.sleep(0.5)
            energo_mode(windowInfo, "on")
            time.sleep(0.05)
            return True

    return False


def buyLootAfterRIP(windowInfo):
    windowid = next(iter(windowInfo))

    if not checkEnergoMode(windowInfo):
        xy, rgb = parseCBT("krest_after_respawn")
        if check_pixel(windowInfo, xy, rgb, 1):
            x, y = xy
            result = click_mouse(windowInfo, x, y)

            xy, rgb = parseCBT("respawn_icon_in_gui")
            result = check_pixel(windowInfo, xy, rgb, 2)
            if result:
                xy, rgb = parseCBT("monetka_respawn")
                while True:
                    result = check_pixel(windowInfo, xy, rgb, 3)
                    if not result:
                        x, y = xy
                        click = click_mouse(windowInfo, x, y)
                        time.sleep(0.05)
                    if result:
                        break

                time.sleep(0.3)
                value = []
                for x in range(1, 5):
                    time.sleep(0.3)
                    cbt = f"respawn_monetka_exp_{x}"
                    xy, rgb = parseCBT(cbt)
                    result = check_pixel(windowInfo, xy, rgb)
                    if result:
                        value.append(cbt)
                        x, y = xy
                        click_mouse(windowInfo, x, y)
                    if x == 2 and not result:
                        break

                if value:
                    xy, rgb = parseCBT("respawn_buy_gui_button")
                    result = check_pixel(windowInfo, xy, rgb, 2)
                    if result:
                        x, y = xy
                        click = click_mouse(windowInfo, x, y)
                        time.sleep(0.05)
                        xy, rgb = parseCBT("respawn_accept_buy_gui_button")
                        result = check_pixel(windowInfo, xy, rgb, 3)
                        if result:
                            x, y = xy
                            click = click_mouse(windowInfo, x, y)
                            time.sleep(4)
                            xy, rgb = parseCBT("respawn_exit_gui_button")
                            x, y = xy
                            result = click_mouse(windowInfo, x, y)
                            log(f"Успешно выкупил {len(value)} шт опыта!", windowid)
                            lvlup = checkLvlUp(windowInfo)
                            if lvlup:
                                log(f"сломался лвл ап чек", windowid)
                            return True
            else:
                log("Не нужно выкупать предметы", windowid)
                return True

def checkRIP(windowInfo):
    cbts = ["you_were_killed_energomode", "check_death_penalty", "respawn_village"]

    for cbt in cbts:
        xy, rgb = parseCBT(cbt)
        if check_pixel(windowInfo, xy, rgb, 0.5):
            return True

    return False

def checkLvlUp(windowInfo):
    windowid = next(iter(windowInfo))
    xy, rgb = parseCBT("lvl_up_black")
    teleported = check_pixel(windowInfo, xy, rgb, 2)
    if teleported:
        xy, rgb = parseCBT("lvl_up_close")
        x, y = xy
        click_mouse(windowInfo, x, y)
        time.sleep(1)
        return True
    else:
        #log(f"??? {teleported}", windowid)
        return False

def checkEnergoMode(windowInfo):
    windowid = next(iter(windowInfo))

    cbts = ["energomode_center_gui"]

    for cbt in cbts:
        xy, rgb = parseCBT(cbt)
        if not check_pixel(windowInfo, xy, rgb):
            return False

    log(f"Находимся в энергорежиме", windowid)
    return True


def navigateToNPC(windowInfo, NPC):
    windowid = next(iter(windowInfo))
    NPC_list = NPC.split("|") if "|" in NPC else [NPC]

    for npc in NPC_list:
        if npc not in NPCS:
            log(f"{npc} не существует", windowid)
            return False

    energo = checkEnergoMode(windowInfo)
    if energo:
        energo_mode(windowInfo, "off")
        time.sleep(0.2)

    lvlup = checkLvlUp(windowInfo)
    if lvlup:
        log(f"сломался лвл ап чек", windowid)

    town, allNPC = checkINtown(windowInfo)
    if not town:
        return False

    npcPositions = allNPC
    if not npcPositions:
        log("? error in navigate", windowid)
        return False

    json_pos = json.loads(npcPositions)

    for current_npc in NPC_list:
        if current_npc not in json_pos:
            continue

        data = json_pos[current_npc]
        xy, rgb = parseCBT(data)
        x, y = xy
        click_mouse(windowInfo, x, y)

        if current_npc in NPC_CHECK_BUTTONS:
            xy, rgb = parseCBT(NPC_CHECK_BUTTONS[current_npc])
            attempts = 0
            while not check_pixel(windowInfo, xy, rgb, 2):
                time.sleep(0.02)
                attempts += 1
                if attempts >= 1000:
                    return False

            def click_button(button_name):
                if button_name in ["npc_shop_button_1", "npc_stash_button_1", "npc_buyer_button_1"]:
                    time.sleep(0.15)
                xy, rgb = parseCBT(button_name)
                x, y = xy
                result = check_pixel(windowInfo, xy, rgb, 1)
                if result:
                    time.sleep(0.1)
                    return click_mouse(windowInfo, x, y)
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
                        time.sleep(0.05)
                        continue
                else:
                    result = click_button("npc_global_quit_button")
                    if not result:
                        time.sleep(0.05)
                        return False

            if current_npc == "stash":
                if waitAndClick(["npc_stash_button_1", "npc_stash_button_2"]):
                    result = click_button("npc_global_quit_button")
                    if result:
                        time.sleep(0.05)
                        continue
                else:
                    result = click_button("npc_global_quit_button")
                    if not result:
                        time.sleep(0.05)
                        return False

            elif current_npc == "buyer":
                if waitAndClick(["npc_buyer_button_1", "npc_buyer_button_2", "npc_buyer_button_3"]):
                    result = click_button("npc_global_quit_button")
                    if result:
                        time.sleep(0.05)
                        continue
                else:
                    result = click_button("npc_global_quit_button")
                    if not result:
                        time.sleep(0.05)
                        return False

    return True

def checkINtown(windowInfo, timeout=20):
    windowid = next(iter(windowInfo))
    start_time = time.time()

    lvlup = checkLvlUp(windowInfo)
    if lvlup:
        log(f"сломался лвл ап чек", windowid)

    while time.time() - start_time < timeout:
        xy, rgb = parseCBT("white_cube_in_minimap")
        result = check_pixel(windowInfo, xy, rgb, 2)
        if result:
            xy, rgb = parseCBT("npc_list_in_town")
            x, y = xy
            result = click_mouse(windowInfo, x, y)
            if result:
                time.sleep(0.03)
                allNPC = getNPCposition(windowInfo)
                if allNPC:
                    log("Нахожусь в городе, список нпс открыт", windowid)
                    return True, allNPC
        else:
            if checkEnergoMode(windowInfo):
                log("Не нашел карту, мы в энергомоде", windowid)
                return False, None
            else:
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

        time.sleep(0.05)

    log("Не удалось определить, в городе ли мы =(", windowid)
    return False, None

def getNPCposition(windowInfo):
    npc_mapping = {}
    time.sleep(2)
    for j in range(3, 5):
        xy, rgb = parseCBT(f"npc_list_{j}")
        result = check_pixel(windowInfo, xy, rgb, 0.2)

        if result:
            if j == 3:
                npc_mapping = {
                    "stash": f"npc_list_{j}",
                    "shop": "npc_list_1",
                    "buyer": "npc_list_5"
                }
            elif j == 4:
                npc_mapping = {
                    "stash": f"npc_list_{j}",
                    "shop": "npc_list_2",
                    "buyer": "npc_list_6"
                }
            break
    if npc_mapping:
        return json.dumps(npc_mapping, indent=4)
    else:
        return None

def respawn(windowInfo): #todo refactor govnocode
    windowid = next(iter(windowInfo))
    if checkEnergoMode(windowInfo):
        r = energo_mode(windowInfo, "off")

    cbts = ["check_death_penalty", "respawn_village"]
    max_attempts = 200
    result = False

    for _ in range(max_attempts):
        for cbt in cbts:
            xy, rgb = parseCBT(cbt)
            if check_pixel(windowInfo, xy, rgb, 0.04):
                #print("кнопка реса есть")
                result = True
                break
        if result:
            break
        time.sleep(0.02)

    if result:
        x, y = xy
        result = click_mouse(windowInfo, x, y)
        if result:
            lvlup = checkLvlUp(windowInfo)
            if lvlup:
                log(f"сломался лвл ап чек", windowid)

            xy, rgb = parseCBT("zalupka_gui")
            time.sleep(1)
            teleported = check_pixel(windowInfo, xy, rgb, 5)
            if teleported:
                log("Успешно восстал из мертвых", windowid)
                return True

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
            time.sleep(0.2)

            width = window["Width"]
            height = window["Height"]
            center_x = width // 2
            center_y = height // 2

            click_mouse(windowInfo, center_x, center_y)

            return True

    return False
