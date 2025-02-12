import sys
import subprocess
import psutil
import platform
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTextEdit, QTabWidget, QLabel, QProgressBar,
                             QMessageBox, QFileDialog)
from PyQt5.QtGui import QColor, QTextCursor
from PyQt5.QtCore import Qt, QTimer

class SystemCheckApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Комплексный мониторинг ОС РОСА")
        self.setGeometry(100, 100, 1024, 768)
        
        # Инициализация UI
        self.init_ui()
        self.init_timer()
        
        # Стили
        self.setStyleSheet("""
            QMainWindow { background-color: #f0f0f0; }
            QTabWidget::pane { border: 1px solid #cccccc; }
            QTextEdit { background-color: white; font-family: Courier; }
            QProgressBar { 
                text-align: center; 
                border: 1px solid grey;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)

    def init_ui(self):
        # Главный виджет
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Панель быстрого статуса
        self.status_bar = QHBoxLayout()
        self.cpu_label = QLabel("CPU: ")
        self.mem_label = QLabel("MEM: ")
        self.disk_label = QLabel("DISK: ")
        self.net_label = QLabel("NET: ")
        
        for widget in [self.cpu_label, self.mem_label, self.disk_label, self.net_label]:
            self.status_bar.addWidget(widget)
        
        layout.addLayout(self.status_bar)

        # Вкладки
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Создание вкладок
        self.create_dashboard_tab()
        self.create_detailed_checks_tab()
        self.create_report_tab()

    def create_dashboard_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Системная информация
        self.sys_info = QTextEdit()
        self.sys_info.setReadOnly(True)
        
        # Графические индикаторы
        self.cpu_progress = QProgressBar()
        self.mem_progress = QProgressBar()
        self.disk_progress = QProgressBar()

        # Кнопки
        self.btn_refresh = QPushButton("Обновить данные")
        self.btn_refresh.clicked.connect(self.update_dashboard)
        
        layout.addWidget(QLabel("Основные показатели:"))
        layout.addWidget(self.cpu_progress)
        layout.addWidget(self.mem_progress)
        layout.addWidget(self.disk_progress)
        layout.addWidget(QLabel("Системная информация:"))
        layout.addWidget(self.sys_info)
        layout.addWidget(self.btn_refresh)
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Дашборд")

    def create_detailed_checks_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Подвкладки для детальных проверок
        self.detailed_tabs = QTabWidget()
        
        # Создание подвкладок
        self.create_network_subtab()
        self.create_disk_subtab()
        self.create_services_subtab()
        self.create_processes_subtab()
        self.create_security_subtab()
        
        layout.addWidget(self.detailed_tabs)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Детальные проверки")

    def create_network_subtab(self):
        subtab = QWidget()
        layout = QVBoxLayout()
        
        self.network_info = QTextEdit()
        self.network_info.setReadOnly(True)
        btn_network = QPushButton("Проверить сеть")
        btn_network.clicked.connect(self.check_network)
        
        layout.addWidget(btn_network)
        layout.addWidget(self.network_info)
        subtab.setLayout(layout)
        self.detailed_tabs.addTab(subtab, "Сеть")

    def create_disk_subtab(self):
        subtab = QWidget()
        layout = QVBoxLayout()
        
        self.disk_info = QTextEdit()
        self.disk_info.setReadOnly(True)
        btn_disk = QPushButton("Проверить диски")
        btn_disk.clicked.connect(self.check_disks)
        
        layout.addWidget(btn_disk)
        layout.addWidget(self.disk_info)
        subtab.setLayout(layout)
        self.detailed_tabs.addTab(subtab, "Диски")

    def create_services_subtab(self):
        subtab = QWidget()
        layout = QVBoxLayout()
        
        self.services_info = QTextEdit()
        self.services_info.setReadOnly(True)
        btn_services = QPushButton("Проверить сервисы")
        btn_services.clicked.connect(self.check_services)
        
        layout.addWidget(btn_services)
        layout.addWidget(self.services_info)
        subtab.setLayout(layout)
        self.detailed_tabs.addTab(subtab, "Сервисы")

    def create_processes_subtab(self):
        subtab = QWidget()
        layout = QVBoxLayout()
        
        self.processes_info = QTextEdit()
        self.processes_info.setReadOnly(True)
        btn_processes = QPushButton("Проверить процессы")
        btn_processes.clicked.connect(self.check_processes)
        
        layout.addWidget(btn_processes)
        layout.addWidget(self.processes_info)
        subtab.setLayout(layout)
        self.detailed_tabs.addTab(subtab, "Процессы")

    def create_security_subtab(self):
        subtab = QWidget()
        layout = QVBoxLayout()
        
        self.security_info = QTextEdit()
        self.security_info.setReadOnly(True)
        btn_security = QPushButton("Проверить безопасность")
        btn_security.clicked.connect(self.check_security)
        
        layout.addWidget(btn_security)
        layout.addWidget(self.security_info)
        subtab.setLayout(layout)
        self.detailed_tabs.addTab(subtab, "Безопасность")

    def create_report_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.report_info = QTextEdit()
        self.report_info.setReadOnly(True)
        btn_save = QPushButton("Сохранить отчет")
        btn_save.clicked.connect(self.save_report)
        
        layout.addWidget(btn_save)
        layout.addWidget(self.report_info)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Отчеты")

    def init_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_dashboard)
        self.timer.start(5000)  # Обновление каждые 5 секунд

    def update_dashboard(self):
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            self.cpu_progress.setValue(int(cpu_percent))
            self.cpu_progress.setFormat(f"Загрузка CPU: {cpu_percent}%")
            self.set_progress_color(self.cpu_progress, cpu_percent)

            # Memory
            mem = psutil.virtual_memory()
            self.mem_progress.setValue(mem.percent)
            self.mem_progress.setFormat(f"Использование памяти: {mem.percent}%")
            self.set_progress_color(self.mem_progress, mem.percent)

            # Disk
            disk = psutil.disk_usage('/')
            self.disk_progress.setValue(disk.percent)
            self.disk_progress.setFormat(f"Использование корневого раздела: {disk.percent}%")
            self.set_progress_color(self.disk_progress, disk.percent)

            # System Info
            sys_info = f"""
            Системная информация:
            ОС: {platform.system()} {platform.release()}
            Версия: {platform.version()}
            Процессор: {platform.processor()}
            Время работы: {datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")}
            """
            self.sys_info.setPlainText(sys_info)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def set_progress_color(self, progress, value):
        if value > 90:
            color = "#ff4444"
        elif value > 70:
            color = "#ffbb33"
        else:
            color = "#4CAF50"
        
        progress.setStyleSheet(f"""
            QProgressBar::chunk {{ background-color: {color}; }}
        """)

    def check_network(self):
        try:
            self.network_info.clear()
            self.append_colored_text(self.network_info, "=== Расширенная проверка сети ===", "#000080")
            
            # Основные интерфейсы
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            io_counters = psutil.net_io_counters(pernic=True)
            
            for interface in interfaces:
                self.append_colored_text(self.network_info, f"\nИнтерфейс: {interface}", "#006600")
                
                # Адреса
                for addr in interfaces[interface]:
                    self.network_info.append(f"  {addr.family.name}: {addr.address}")
                
                # Статус
                if stats[interface].isup:
                    status = "UP"
                    color = "#008000"
                else:
                    status = "DOWN"
                    color = "#ff0000"
                self.append_colored_text(self.network_info, f"  Статус: {status}", color)
                
                # Статистика
                io = io_counters.get(interface)
                if io:
                    self.network_info.append(f"  Отправлено: {io.bytes_sent / 1024**2:.2f} MB")
                    self.network_info.append(f"  Получено: {io.bytes_recv / 1024**2:.2f} MB")
                    
            # Соединения
            self.append_colored_text(self.network_info, "\nАктивные соединения:", "#000080")
            connections = psutil.net_connections()
            for conn in connections:
                if conn.status == 'ESTABLISHED':
                    self.network_info.append(f"{conn.laddr.ip}:{conn.laddr.port} -> {conn.raddr.ip}:{conn.raddr.port} [{conn.pid}]")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def check_disks(self):
        try:
            self.disk_info.clear()
            self.append_colored_text(self.disk_info, "=== Расширенная проверка дисков ===", "#000080")
            
            # SMART-данные (требует прав)
            try:
                smart = subprocess.check_output(["smartctl", "--scan"], stderr=subprocess.STDOUT)
                self.disk_info.append("\nSMST-устройства:\n" + smart.decode())
            except Exception as e:
                self.append_colored_text(self.disk_info, "\nОшибка получения SMART-данных: " + str(e), "#ff0000")
            
            # RAID-статус
            try:
                mdstat = subprocess.check_output(["cat", "/proc/mdstat"])
                self.disk_info.append("\nRAID-статус:\n" + mdstat.decode())
            except Exception as e:
                self.append_colored_text(self.disk_info, "\nОшибка проверки RAID: " + str(e), "#ff0000")
            
            # Основная информация
            partitions = psutil.disk_partitions()
            for part in partitions:
                usage = psutil.disk_usage(part.mountpoint)
                self.disk_info.append(f"\nУстройство: {part.device}")
                self.disk_info.append(f"Точка монтирования: {part.mountpoint}")
                self.disk_info.append(f"Файловая система: {part.fstype}")
                self.disk_info.append(f"Всего: {usage.total / 1024**3:.2f} GB")
                self.disk_info.append(f"Использовано: {usage.percent}%")
                
                if usage.percent > 90:
                    self.append_colored_text(self.disk_info, "ВНИМАНИЕ: Мало свободного места!", "#ff0000")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def check_services(self):
        try:
            self.services_info.clear()
            self.append_colored_text(self.services_info, "=== Расширенная проверка сервисов ===", "#000080")
            
            # Неудачные сервисы
            try:
                failed = subprocess.check_output(["systemctl", "list-units", "--state=failed"])
                self.services_info.append("\nНеудачные сервисы:\n" + failed.decode())
            except Exception as e:
                self.append_colored_text(self.services_info, "\nОшибка проверки сервисов: " + str(e), "#ff0000")
            
            # Сервисы с автозагрузкой
            try:
                enabled = subprocess.check_output(["systemctl", "list-unit-files", "--state=enabled"])
                self.services_info.append("\nСервисы с автозагрузкой:\n" + enabled.decode())
            except Exception as e:
                self.append_colored_text(self.services_info, "\nОшибка проверки автозагрузки: " + str(e), "#ff0000")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def check_processes(self):
        try:
            self.processes_info.clear()
            self.append_colored_text(self.processes_info, "=== Анализ процессов ===", "#000080")
            
            # Топ процессов по CPU
            self.processes_info.append("\nТоп процессов по CPU:")
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                if proc.info['cpu_percent'] > 5.0:
                    self.processes_info.append(f"PID: {proc.info['pid']} | Имя: {proc.info['name']} | CPU: {proc.info['cpu_percent']}%")

            # Топ процессов по памяти
            self.processes_info.append("\nТоп процессов по памяти:")
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                if proc.info['memory_percent'] > 1.0:
                    self.processes_info.append(f"PID: {proc.info['pid']} | Имя: {proc.info['name']} | MEM: {proc.info['memory_percent']}%")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def check_security(self):
        try:
            self.security_info.clear()
            self.append_colored_text(self.security_info, "=== Проверка безопасности ===", "#000080")
            
            # Проверка обновлений
            try:
                updates = subprocess.check_output(["apt", "list", "--upgradable"])
                self.security_info.append("\nДоступные обновления:\n" + updates.decode())
            except Exception as e:
                self.append_colored_text(self.security_info, "\nОшибка проверки обновлений: " + str(e), "#ff0000")
            
            # Проверка брандмауэра
            try:
                firewall = subprocess.check_output(["ufw", "status"])
                self.security_info.append("\nСтатус брандмауэра:\n" + firewall.decode())
            except Exception as e:
                self.append_colored_text(self.security_info, "\nОшибка проверки брандмауэра: " + str(e), "#ff0000")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def save_report(self):
        try:
            filename, _ = QFileDialog.getSaveFileName(self, "Сохранить отчет", "", "Текстовые файлы (*.txt)")
            if filename:
                with open(filename, 'w') as f:
                    f.write(self.report_info.toPlainText())
                QMessageBox.information(self, "Успешно", "Отчет сохранен")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def append_colored_text(self, text_edit, text, color):
        text_edit.moveCursor(QTextCursor.End)
        text_edit.setTextColor(QColor(color))
        text_edit.insertPlainText(text + "\n")
        text_edit.setTextColor(QColor("black"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SystemCheckApp()
    window.show()
    sys.exit(app.exec_())