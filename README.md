# ⚔️ Lineage 2M Japan Bot 🤖🐉

![Lineage II](https://img.shields.io/badge/Lineage2-Mobile_JP-red?style=for-the-badge&logo=android)
![Status](https://img.shields.io/badge/status-Active-green?style=for-the-badge)
![Language](https://img.shields.io/badge/language-Python-blue?style=for-the-badge&logo=python)

> 🧠 *Анти-интеллектуальный* бот для **Lineage 2M Japan**. Фарм, автоматизация и немного боли. 😵‍💫⚙️

---

## 🚀 Возможности бота 🌟

### 🧠 Гибкость и сценарии  
🔹 **Сценарии под любые задачи** — (почти) каждый сможет написать сценарий для бота под себя. Для большинства игровых механик уже есть удобные методы. Пиши свой сценрарий — и в бой!

### 💬 Telegram-интеграция  
📬 Все важные события (и не только) сразу в Telegram. Получай уведомления, получай информацию и скриншоты окон прямо из чата. Удобно? Еще как!

### 🔒 Безопасность превыше всего  
🧪 Никаких подозрительных запросов. Всё локально, всё чисто. Спокойствие и прозрачность.

---

### 🎛️ Интерфейс и удобство  
- 💥 **Красивый GUI** — понятный, современный интерфейс для лёгкого управления ботом  
- ⚙️ **Минимум настроек** — всё работает из коробки. Подключил и кайфанул

---

### ⚔️ Что бот умеет  

- 📦 **Сбор наград**: БП, дейлики, достижения, клановые награды
- 💰 **Автозакуп**: бот сам выкупает нужные вам вкладки в донат магазине, донатит в клан и собирает его награду
- 🧪 **Следит за банками**: бот знает, когда заканчиваются банки хила и сам телепортируется в город за пополнением  
- ⚖️ **Контроль перевеса**: при перевесе возвращается в город, сбрасывает все в стеш, если не помогает — сообщает в Telegram  
- 🏃‍♂️ **Авто-уход от PvP**: нападают?, бьют ногами?, обссыкают? Бот улетает в город, закупается и возвращается на рандомный спот  
- 💀 **Авто-воскрешение**: все же помер? Воскреснет, выкупит опыт, закупится — и снова в бой!

---



## 🛠 Установка 🧰

### 1. Установка Interception драйвера 🔌
📥 [Скачать с GitHub →](https://github.com/oblitum/Interception)  
- Следуй инструкциям в репозитории 📖  
- После установки **обязательно перезагрузи компьютер** 🔁💻

### 2. Установка Python 3.11.5 🐍
🔗 [Скачать →](https://www.python.org/downloads/release/python-3115/)  
- Не забудь поставить галочку ✅ `Add Python to PATH` во время установки

### 3. Установка зависимостей 📦

Открой терминал в папке с ботом и выполни:

```bash
pip install -r requirements.txt
```

### 4. Запуск 🚀

Запусти бота командой:

```bash
python3.11 gui.py
```

---

## ⚙️ Настройка 🧩

***Перед запуском не забудь***:

1. 🗂️ **`config.ini`**  
   - 🤖 Вставь Telegram-токен от `@BotFather` (`/newbot`), после создания бота перейди в него и пропиши /start
   - 🆔 Укажи свой Telegram ID (чтобы узнать пропиши `/start` в бота `@getmyid_bot`)
   - ⏱️ Настрой задержки (по умолчанию норм, меньше 1 — не надо)  
   - 📍 Диапазон спотов — например, `1 1` если нужен только один спот (не больше `1 4`)
   - 🖥️ Проверь разрешение окна игры — **обязательно 400x225**, иначе ниче не заведется

---

## 💡 Часто задаваемые вопросы & Решение проблем 💡

### 🚫 Проблема: GUI не запускается
**❓ Вопрос:**  
"Не запускается gui.py либо тупит бот, что делать?"  

**✅ Решение:**  
1. Создай issue в репозитории, описав проблему и приложив видео/cкриншоты/текст ошибок
2. Если это баг - я починю в следующем обновлении  
3. Проверь, что ты установил все зависимости из requirements.txt

---

### 🚫️ Проблема: Ошибка при запуске gui.py
**❓ Вопрос:**  
"При запуске gui.py выдает ошибку" (не помню че там за ошибка но чет с ру буквами)

**✅ Решение:**  
🔹 **Основная причина:** Русские символы в имени пользователя  
🔹 **Как исправить:**  
1. Создайте нового пользователя с именем на латинице  
2. Перенесите проект в папку с путем, не содержащим кириллицу  
3. Либо измените имя текущего пользователя

✨ **Совет:** Всегда используйте английские имена для системных папок и пользователей! 

---

❌ Если что-то пошло не так — не паникуй. Просто начни с шага 1.  
🧘 Или шагни на улицу — возможно, Lineage не для тебя 😄🌳