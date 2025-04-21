import os
import threading
import subprocess
import psutil
from functools import partial
from PyQt5 import QtWidgets, QtGui, QtCore
from methods.base_methods import loadSettings
from constans import SCENARIES_DIR
from clogger import log
from tgbot.tg import TgBotus
import json

class gui(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Telegram - @BotLinеage2M")
        self.setFixedSize(350, 600)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.old_pos = None
        self.current_process = None
        self.is_paused = False
        self.selected_button = None

        self.settings = loadSettings()
        self.bot = TgBotus()
        self.bot_thread = threading.Thread(target=self.bot.start_polling, daemon=True)
        self.bot_thread.start()
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        container = QtWidgets.QFrame()
        container.setObjectName("container")
        container.setStyleSheet("""
            QFrame#container {
                background-color: rgba(25, 25, 25, 200);
                border-radius: 20px;
                border: 5px solid transparent;
                background-image: linear-gradient(45deg, #CC0000, #CC7A00, #CCCC00, #29CC29, #0066CC, #6600B2, #CC0055);
            }
        """)

        container_layout = QtWidgets.QVBoxLayout(container)
        container_layout.setContentsMargins(15, 15, 15, 15)

        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("✨ Сценарии")
        title.setStyleSheet("color: white; font: bold 16pt 'Segoe UI';")
        header.addWidget(title)
        header.addStretch()

        minimize_btn = QtWidgets.QPushButton("")
        minimize_btn.setFixedSize(30, 30)
        minimize_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffaa00;
                color: white;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #ffbb33;
            }
        """)
        minimize_btn.clicked.connect(self.showMinimized)
        header.addWidget(minimize_btn)

        close_btn = QtWidgets.QPushButton("")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff5555;
                color: white;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #ff7777;
            }
        """)
        close_btn.clicked.connect(self.close_app)
        header.addWidget(close_btn)
        container_layout.addLayout(header)

        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск... (для даунов)")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 40);
                border-radius: 10px;
                padding: 6px;
                color: white;
                font: 10pt 'Segoe UI';
            }
            QLineEdit:hover {
                background-color: rgba(255, 255, 255, 60);
            }
        """)
        self.search_input.textChanged.connect(self.filter_scenaries)
        container_layout.addWidget(self.search_input)

        self.buttons = []
        self.scenary_map = {}

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background-color: transparent; border: none;")
        self.scroll_content = QtWidgets.QWidget()
        self.scroll_layout = QtWidgets.QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(QtCore.Qt.AlignTop)

        self.scroll_content.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_content)
        container_layout.addWidget(self.scroll_area)

        self.load_scenaries()
        self.bot.set_scenaries(self.get_scenaries())

        self.status_label = QtWidgets.QLabel("Слакаю...")
        self.status_label.setStyleSheet("color: #A9A9A9; font: 11pt 'Segoe UI'; text-align: center;")
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        container_layout.addWidget(self.status_label)

        self.run_button = QtWidgets.QPushButton("🚀 Запустить")
        self.pause_button = QtWidgets.QPushButton("⏸ Пауза")
        self.stop_button = QtWidgets.QPushButton("🛑 Стопнуть")

        for btn in [self.run_button, self.pause_button, self.stop_button]:
            btn.setEnabled(False)
            btn.setStyleSheet(self.get_control_style())
            btn.setGraphicsEffect(self.create_button_shadow())
            container_layout.addWidget(btn)

        self.pause_button.clicked.connect(self.pause_resume_scenary)
        self.stop_button.clicked.connect(self.stop_scenary)

        self.wmark = QtWidgets.QLabel("tg - @BotLineage2M")
        self.wmark.setStyleSheet("""
            color: rgba(255, 255, 255, 0.5); 
            font: 9pt 'Segoe UI'; 
            text-align: center; 
            background-color: rgba(51, 51, 51, 0.5); 
            padding: 2px 6px; 
            border-radius: 5px;
            font-weight: normal;
            opacity: 0.7;
        """)
        self.wmark.setAlignment(QtCore.Qt.AlignCenter)
        self.wmark.setFixedWidth(self.wmark.sizeHint().width())
        spacer = QtWidgets.QSpacerItem(1, 20)
        container_layout.addItem(spacer)
        container_layout.addWidget(self.wmark, alignment=QtCore.Qt.AlignCenter)

        layout.addWidget(container)

    def get_button_style(self):
        return """
            QPushButton {
                background-color: #333333;
                color: #D1D3D4;
                border-radius: 15px;
                padding: 12px;
                font: 11pt 'Segoe UI';
                text-align: center;
                border: 2px solid #555555;
            }
            QPushButton:hover {
                background-color: #3A3F42;
                color: white;
                border-color: #00FF99;
            }
            QPushButton:pressed {
                background-color: #444D56;
            }
        """

    def get_control_style(self):
        return """
            QPushButton {
                background-color: #3C3F41;
                color: white;
                font: bold 10pt 'Segoe UI';
                padding: 8px 16px;
                border-radius: 8px; 
                border: 2px solid #4CAF50;
            }

            QPushButton:enabled {
                background-color: #4CAF50;
                color: white;
                border: 2px solid #388E3C;
            }

            QPushButton:enabled:hover {
                background-color: #36A436;
            }

            QPushButton:disabled {
                background-color: rgba(100, 100, 100, 0.5);
                color: rgba(200, 200, 200, 0.7);
                border: 2px solid rgba(150, 150, 150, 0.5);
            }

            QPushButton:disabled:hover {
                background-color: #A0A0A0;
            }
        """

    def create_button_shadow(self):
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(4)
        shadow.setColor(QtGui.QColor(0, 255, 153, 120))
        shadow.setOffset(3, 3)
        return shadow

    def get_scenaries(self):
        result = []
        for entry in os.listdir(SCENARIES_DIR):
            dir_path = os.path.join(SCENARIES_DIR, entry)
            manifest_path = os.path.join(dir_path, "manifest.json")
            if os.path.isdir(dir_path) and os.path.isfile(manifest_path):
                try:
                    data = json.load(open(manifest_path, encoding="utf-8"))
                    name = data["profile_name"]
                    version = data["version"]
                    main_file = data["main_file"]
                    source = data["source"]
                    display = f"{name} v{version}"
                    result.append((dir_path, main_file, display))
                except Exception as e:
                    log(f"Ошибка чтения {manifest_path}: {e}")
        return result

    def load_scenaries(self):
        for dir_path, main_file, display in self.get_scenaries():
            btn = QtWidgets.QPushButton(f"▶ {display}")
            btn.setStyleSheet(self.get_button_style())
            btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            btn.setGraphicsEffect(self.create_button_shadow())
            btn.clicked.connect(partial(self.on_scenary_click, dir_path, main_file, btn))
            self.scroll_layout.addWidget(btn)
            self.buttons.append(btn)
            self.scenary_map[dir_path] = (main_file, btn)

    def filter_scenaries(self, text):
        for dir_path, (main_file, btn) in self.scenary_map.items():
            profile = os.path.basename(dir_path)
            btn.setVisible(text.lower() in profile.lower())

    def on_scenary_click(self, dir_path, main_file, button):
        if self.selected_button:
            self.selected_button.setStyleSheet(self.get_button_style())

        self.selected_button = button
        button.setStyleSheet("""
            QPushButton {
                background-color: #5A6365;
                color: white;
                border: 2px solid cyan;
                border-radius: 10px;
                padding: 10px;
                font: bold 10pt 'Segoe UI';
            }
        """)
        try:
            self.run_button.clicked.disconnect()
        except TypeError:
            pass

        self.run_button.clicked.connect(partial(self.run_scenary, dir_path, main_file))
        self.run_button.setText(f"🚀 Запустить")

        if self.current_process:
            self.run_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.stop_button.setEnabled(True)
        else:
            self.run_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.stop_button.setEnabled(False)

        self.update_status(f"Готов: {os.path.basename(dir_path)}")

    def run_scenary(self, dir_path=None, main_file=None):
        if self.current_process:
            self.update_status("Сначала останови текущий сценарий")
            return

        if dir_path is None:
            return  # защита от ДАУНА

        script = os.path.join(dir_path, main_file)
        # командная строка: импорт и вызов main()
        cmd = [
            "python", "-c",
            (
                "import runpy; m = runpy.run_path(r'%s'); "
                "m.get('main', lambda:None)()"
            ) % script.replace("\\", "\\\\")
        ]

        def target():
            try:
                self.current_process = subprocess.Popen(
                    cmd,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
                self.update_status(f"{os.path.basename(dir_path)} — запущен")
                self.toggle_controls(running=True)
                self.run_button.setEnabled(False)
                self.bot.set_current_scenario(os.path.basename(dir_path))
                self.current_process.wait()
                self.update_status(f"{os.path.basename(dir_path)} — завершён")
            except Exception as e:
                self.update_status(f"Ошибка запуска: {e}")
            finally:
                self.current_process = None
                self.is_paused = False
                self.pause_button.setText("⏸ Пауза")
                self.toggle_controls(running=False)

        threading.Thread(target=target, daemon=True).start()

    def stop_scenary(self):
        if not self.current_process:
            return
        try:
            proc = psutil.Process(self.current_process.pid)
            for child in proc.children(recursive=True):
                child.kill()
            proc.kill()
            self.update_status("Остановлен")
            self.bot.set_current_scenario(None)
        except Exception as e:
            self.update_status(f"Ошибка остановки: {e}")
        finally:
            self.current_process = None
            self.is_paused = False
            self.pause_button.setText("⏸ Пауза")
            self.toggle_controls(running=False)
            if self.selected_button:
                self.run_button.setEnabled(True)

    def pause_resume_scenary(self):
        if not self.current_process:
            return
        try:
            proc = psutil.Process(self.current_process.pid)
            if not self.is_paused:
                proc.suspend()
                self.pause_button.setText("▶️ Продолжить")
                self.update_status("Приостановлен")
            else:
                proc.resume()
                self.pause_button.setText("⏸ Пауза")
                self.update_status("Возобновлён")
            self.is_paused = not self.is_paused
        except Exception as e:
            self.update_status(f"Ошибка паузы: {e}")

    def update_status(self, text):
        self.status_label.setText(text)

    def toggle_controls(self, running):
        self.pause_button.setEnabled(running)
        self.stop_button.setEnabled(running)

    def close_app(self):
        self.stop_scenary()
        self.close()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = QtCore.QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    win = gui()
    win.show()
    sys.exit(app.exec_())
