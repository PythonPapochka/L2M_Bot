import threading
import telebot
import telebot.types
import psutil
import os
import time
import pyautogui
from io import BytesIO
from clogger import log
from datetime import datetime
from methods.base_methods import load_config
from methods.base_methods import SettingsManager

settingsm = SettingsManager()
_settings_cache = None
_settings_timestamp = 0
_settings_lock = threading.Lock()

def get_cached_settings():
    global _settings_cache, _settings_timestamp
    with _settings_lock:
        now = time.time()
        if now - _settings_timestamp > 0.05 or _settings_cache is None: #todo сделать норм одни настройки для всех, багует если дрочить быстро
            _settings_cache = settingsm.loadSettings()
            _settings_timestamp = now
            #print(_settings_cache)
        return _settings_cache

cfg = load_config('config.ini')
TG_TOKEN = cfg.telegram.TG_TOKEN
TG_IDS = cfg.telegram.TG_IDS
BOT_ACTIVE = cfg.telegram.TG_BOT

class TgBotus:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TgBotus, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, "bot"):
            return

        self.starttime = time.time()
        self.bot = telebot.TeleBot(TG_TOKEN)
        self._polling_started = False
        self.current_scenario_name = None
        self.scenaries = []
        self.settings = get_cached_settings()

        #todo fix govnocode
        @self.bot.callback_query_handler(func=lambda call: call.data == "l2m:back")
        def handle_back(call):
            buttons = [
                [("📷 Скриншотер", "l2m:screener")],
                [("🔥 Нагрузка", "l2m:nagruz")],
                [("ℹ️ Информация о сценариях", "l2m:scenaries")],
                [("👤 Информация про все окна", "l2m:chars")],
                [("⚰️ Закрыть все окна", "l2m:killer")],
            ]
            markup = self.create_inline_keyboard(buttons)

            try:
                if call.message.text:
                    self.bot.edit_message_text(
                        f"😎 Всего аккаунтов храним: {len(get_cached_settings())}\n🕹 Выбирай нужную кнопочку снизу",
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=markup
                    )
                else:
                    self.bot.send_message(
                        call.message.chat.id,
                        f"😎 Всего аккаунтов храним: {len(get_cached_settings())}\n🕹 Выбирай нужную кнопочку снизу",
                        reply_markup=markup
                    )
            except telebot.apihelper.ApiTelegramException as e:
                self.bot.send_message(
                    call.message.chat.id,
                    f"😎 Всего аккаунтов храним: {len(get_cached_settings())}\n🕹 Выбирай нужную кнопочку снизу",
                    reply_markup=markup
                )

        @self.bot.message_handler(commands=["menu"])
        def handle_menu_command(message):
            if self._is_admin(message.chat.id):
                self.send_menu(message.chat.id)

        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("l2m:"))
        def handle_callback(call):
            if not self._is_admin(call.message.chat.id):
                return

            self.bot.answer_callback_query(call.id)
            key = call.data.split(":")[1]

            if key == "screener":
                self.show_nicknames(call.message.chat.id)
            elif key == "nagruz":
                self.send_system_info(call.message.chat.id)
            elif key == "killer":
                self.bot.send_message(call.message.chat.id, "❌ Когда-то появится...")
            elif key == "chars":
                self.send_char_info(call.message.chat.id)
            elif key == "scenaries":
                self.send_scenary_info(call.message.chat.id)

        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("select:"))
        def handle_screener(call):
            nickname = call.data.split(":")[1]
            markup = self.back()

            settings = self.settings.get(nickname, {})
            if settings:
                position = settings.get("Position", [0, 0])
                width = settings.get("Width", 400)
                height = settings.get("Height", 225)

                screenshot = self.capture_window(position[0], position[1], width, height)
                self.bot.send_photo(call.message.chat.id, screenshot, caption=f"Скриншот для {nickname}",
                                    reply_markup=markup)


    def back(self):
        buttons = [
            [("◀️ Назад", "l2m:back")],
        ]
        markup = self.create_inline_keyboard(buttons)
        return markup

    def capture_window(self, x, y, width, height):
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        img_byte_arr = BytesIO()
        screenshot.save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)
        return img_byte_arr

    def _is_admin(self, chat_id):
        return chat_id in TG_IDS

    def set_current_scenario(self, name):
        self.current_scenario_name = name

    def set_scenaries(self, scenaries):
        self.scenaries = scenaries  # [(dir_path, main_file, display), ...]

    def configure_bot(self):
        try:
            target_desc = (
                "🚀 Бесплатный бот для Lineage 2M (japan)\n\n"
                "✅ Автоматизация фарма, сбора наград, аукциона\n"
                "🛠 Открытый исходный код (GitHub)\n"
                "🧠 Настраиваемые действия, сценарии\n"
                "👥 Полная чистота, никаких запросов налево\n\n"
                "🔗 https://github.com/PythonPapochka/L2M_Bot"
            )

            target_short = "🎮 L2M Bot (JP edition) — сборщик, фармер.\n✅ Бесплатно и с исходниками\n🔗 https://github.com/PythonPapochka/L2M_Bot"
            target_commands = [
                telebot.types.BotCommand("menu", "Открыть меню"),
            ]

            current_desc = self.bot.get_my_description().description or ""
            current_short = self.bot.get_my_short_description().short_description or ""
            current_cmds = self.bot.get_my_commands()

            if current_desc != target_desc:
                self.bot.set_my_description(description=target_desc)

            if current_short != target_short:
                self.bot.set_my_short_description(short_description=target_short)

            if current_cmds != target_commands:
                self.bot.set_my_commands(target_commands)

        except Exception as e:
            log(f"pzdccc {e}")

    def start_polling(self):
        if not self._polling_started:
            if BOT_ACTIVE:
                log("tg bot started epta")
                self.configure_bot()
                self.polling_thread = threading.Thread(target=self.bot.infinity_polling, daemon=True)
                self.polling_thread.start()
                self._polling_started = True
            else:
                log("tg bot not active")
                return

    def split_send_message(self, chat_id, msg, max_length=4096, reply_markup=None):
        if len(msg) > max_length:
            parts = [msg[i:i + max_length] for i in range(0, len(msg), max_length)]

            for part in parts:
                self.bot.send_message(chat_id, part, parse_mode='HTML', reply_markup=reply_markup)
        else:
            self.bot.send_message(chat_id, msg, parse_mode='HTML', reply_markup=reply_markup)

    def send_message(self, chat_id, text, reply_markup=None, charid=None):
        if not BOT_ACTIVE:
            return

        if chat_id == "admin":
            chat_ids = TG_IDS
        else:
            chat_ids = [chat_id]

        for chat_id in chat_ids:
            if self._is_admin(chat_id):
                settings = settingsm.loadSettingsByHWND(charid)
                nickname = f"<code>{settings.get('Nickname')}</code>" if settings and charid else ""
                final_text = f"{nickname}\n{text}" if nickname else text
                self.bot.send_message(chat_id, final_text, reply_markup=reply_markup, parse_mode='HTML')


    def create_inline_keyboard(self, buttons):
        markup = telebot.types.InlineKeyboardMarkup()
        for row in buttons:
            markup.add(*[telebot.types.InlineKeyboardButton(text=btn[0], callback_data=btn[1]) for btn in row])
        return markup

    def send_menu(self, chat_id):
        buttons = [
            [("📷 Скриншотер", "l2m:screener")],
            [("🔥 Нагрузка", "l2m:nagruz")],
            [("ℹ️ Информация о сценариях", "l2m:scenaries")],
            [("👤 Информация про все окна", "l2m:chars")],
            [("⚰️ Закрыть все окна", "l2m:killer")],
        ]
        markup = self.create_inline_keyboard(buttons)
        self.send_message(chat_id, f"😎 Всего аккаунтов храним: {len(get_cached_settings())}\n🕹 Выбирай нужную кнопочку снизу", reply_markup=markup)

    def show_nicknames(self, chat_id):
        buttons = []
        for i, (nickname, data) in enumerate(self.settings.items()):
            if i % 2 == 0:
                row = [(nickname, f"select:{nickname}")]
                if i + 1 < len(self.settings):
                    next_nickname, _ = list(self.settings.items())[i + 1]
                    row.append((next_nickname, f"select:{next_nickname}"))
                buttons.append(row)

        markup = self.create_inline_keyboard(buttons)
        self.send_message(chat_id, "Выберите никнейм для скриншота:", reply_markup=markup)

    def send_scenary_info(self, chat_id):
        if not self.scenaries:
            self.send_message(chat_id, "❌ Сценарии ещё не загружены.")
            return

        active = self.current_scenario_name
        total = len(self.scenaries)

        active_line = "⚠️ <i>Нет активного сценария</i>"
        other_lines = []

        for dir_path, main_file, display in self.scenaries:
            folder = os.path.basename(dir_path)
            if folder == active:
                active_line = f"🔥 <b>Активный:</b>\n👉 <code>{display}</code>"
            else:
                other_lines.append(f"▫️ <code>{display}</code>")

        list_title = "<b>Доступные:</b>" if active else "<b>Сценарии:</b>"
        msg = f"🎮 <b>Сценарии (всего: {total})</b>\n\n{active_line}\n\n📄 {list_title}\n" + "\n".join(other_lines)
        self.send_message(chat_id, msg, reply_markup=self.back())

    def send_char_info(self, chat_id):
        settings = get_cached_settings()
        if not settings:
            self.send_message(chat_id, "❌ Нет информации о персонажах либо настры пустые")
            return

        char_lines = []

        for char, data in settings.items():
            nickname = data.get("Nickname")
            char_id = data.get("ID")
            state = data.get("State")
            in_home = data.get("InHome")

            char_line = f"👤 <b>{nickname}</b>\n"
            char_line += f"   📌 <i>Состояние:</i> <code>{state}</code>\n"
            char_line += f"   🏠 <i>Инхом:</i> <code>{in_home}</code>\n"
            char_line += f"   🔒 <i>HWND:</i> <tg-spoiler>{char_id}</tg-spoiler>"

            char_lines.append(char_line)

        msg = f"🎮 <b>Информация о персонажах (всего: {len(settings)})</b>\n\n" + "\n\n".join(char_lines)
        self.split_send_message(chat_id, msg, reply_markup=self.back())

    def send_system_info(self, chat_id):
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_partitions()
        uptime = psutil.boot_time()
        boot_time = datetime.fromtimestamp(uptime)
        now = datetime.now()
        uptime_duration = str(now - boot_time).split('.')[0]
        days, remainder = uptime_duration.split(' days, ')
        hours, minutes, seconds = remainder.split(':')
        days = int(days)
        hours = int(hours)
        minutes = int(minutes)
        seconds = int(seconds)
        bot_uptime = time.time() - self.starttime
        bot_uptime_hours = int(bot_uptime // 3600)
        bot_uptime_minutes = int((bot_uptime % 3600) // 60)
        bot_uptime_seconds = int(bot_uptime % 60)
        formatted_bot_uptime = f"{bot_uptime_hours} ч. {bot_uptime_minutes} мин. {bot_uptime_seconds} сек."
        formatted_uptime = f"{days} дн. {hours} ч. {minutes} мин. {seconds} сек."
        active = self.current_scenario_name

        msg = f"⚙️ <b>Системинфо:</b>\n\n"
        msg += f"🖥 <b>Процессор:</b> <code>{cpu_percent}%</code> загрузки\n"
        msg += f"💾 <b>Память:</b> <code>{memory.percent}%</code> использовано из <code>{memory.total / (1024 ** 3):.2f} GB</code>\n"

        msg += f"\n🗄 <b>Диски:</b>\n"
        for p in disk:
            disk_usage = psutil.disk_usage(p.mountpoint)
            msg += f"🔹 <b>{p.device}</b>: <code>{disk_usage.percent}%</code> использовано из <code>{disk_usage.total / (1024 ** 3):.2f} GB</code>\n"

        msg += f"\n⏳ <b>Комп вкл уже:</b> <code>{formatted_uptime}</code>\n"

        net_io = psutil.net_io_counters()
        msg += f"\n🌐 <b>Интернет:</b>\n"
        msg += f"🔹 <b>Отправлено:</b> <code>{net_io.bytes_sent / (1024 ** 2):.2f} MB</code>\n"
        msg += f"🔹 <b>Получено:</b> <code>{net_io.bytes_recv / (1024 ** 2):.2f} MB</code>\n"

        msg += f"\n🧠 <b>Загрузка ядер</b>\n"
        for i, core in enumerate(psutil.cpu_percent(interval=1, percpu=True), 1):
            msg += f"🔹 <b>Ядро {i}:</b> <code>{core}%</code>\n"

        msg += f"\n⏱ <b>Время работы бота:</b> <code>{formatted_bot_uptime}</code>\n"
        msg += f"💬 <code>{chat_id}</code>\n"
        msg += f"🎥 <code>{active}</code>" if active else ""

        self.split_send_message(chat_id, msg, reply_markup=self.back())