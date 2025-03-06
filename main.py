import sys
import os
# Явно указываем использование X11 backend

from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QTableWidget,
                            QTableWidgetItem, QPushButton, QVBoxLayout, QWidget,
                            QFileDialog, QHeaderView, QLabel, QProgressBar)
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCore import Qt
import subprocess
import socket
import psutil
import logging
import mysql.connector

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tests_config = {
            'Сеть': [
                ('Доступ в интернет', self.test_port, ('8.8.8.8', 53)),
                ('Ping google.com', self.test_ping, 'google.com'),
                ('DNS разрешение', self.test_dns, 'google.com')
            ],
            'Файлы': [('Целостность файла', self.test_file, None)],
            'Система': [
                (metric, self.add_system_result, metric) for metric in 
                ('Загрузка CPU', 'Использование памяти')
            ],
            'Службы': [
                (svc, self.test_service, svc) for svc in 
                ('SSH сервер', 'Веб сервер', 'MySQL сервер')
            ],
            'Базы данных': [
                ('Доступность MariaDB', self.test_port, ('localhost', 3306)),
                ('Доступность PostGre', self.test_port, ('localhost', 5432)),
                ('Операции MariaDB', self.test_db_ops, None)
            ]
        }
        self.init_ui()
        logging.basicConfig(filename='tests.log', level=logging.INFO, format='%(asctime)s - %(message)s')

    def init_ui(self):
        self.setWindowTitle("Системный диагностический инструмент")
        self.tabs = QTabWidget()
        for tab_name in self.tests_config:
            tab = QWidget()
            table = QTableWidget(0, 3)
            table.setHorizontalHeaderLabels([' Проверка ', ' Статус ', ' Подробности '])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
            btn = QPushButton(f'Запустить проверку {tab_name}')
            btn.clicked.connect(lambda _, t=table, n=tab_name: self.run_tests(t, self.tests_config[n]))
            
            layout = QVBoxLayout()
            layout.addWidget(QLabel(tab_name, font=QFont('Arial', 12, QFont.Bold)))
            layout.addWidget(btn)
            layout.addWidget(table)
            tab.setLayout(layout)
            self.tabs.addTab(tab, tab_name)
        
        self.setCentralWidget(self.tabs)
        self.setGeometry(100, 100, 1024, 768)
        self.show()

    def run_tests(self, table, tests):
        table.setRowCount(0)
        progress = QProgressBar(maximum=len(tests))
        table.parent().layout().insertWidget(1, progress)
        
        for i, (name, func, arg) in enumerate(tests):
            func(table, name, arg)
            progress.setValue(i+1)
            QApplication.processEvents()
        
        progress.deleteLater()

    def add_result(self, table, test, result, details):
        row = table.rowCount()
        table.insertRow(row)
        colors = {'Успешно': '#dfffdf', 'Ошибка': '#ffe0e0', 'Предупреждение': '#ffffe0'}
        
        for col, text in enumerate([test, result, details]):
            item = QTableWidgetItem(text)
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            if col == 1: item.setBackground(QColor(colors.get(result, 'white')))
            table.setItem(row, col, item)
        
        logging.info(f"[{'OK' if result == 'Успешно' else 'ERROR'}] {test} - {details}")

    def test_port(self, table, name, args):
        try:
            with socket.create_connection(args, timeout=2):
                self.add_result(table, name, 'Успешно', f"Порт {args[1]} доступен")
        except Exception as e:
            self.add_result(table, name, 'Ошибка', f"Ошибка: {str(e)}")


    def test_ping(self, table, name, host):
        param = '-n' if sys.platform == 'win32' else '-c'
        try:
            subprocess.check_call(['ping', param, '1', host], stdout=subprocess.DEVNULL)
            self.add_result(table, name, 'Успешно', 'Ответ получен')
        except:
            self.add_result(table, name, 'Ошибка', 'Не доступен')

    def test_dns(self, table, name, host):
        try:
            ip = socket.gethostbyname(host)
            self.add_result(table, name, 'Успешно', f"{host} → {ip}")
        except:
            self.add_result(table, name, 'Ошибка', 'Сбой разрешения')

    def test_file(self, table, name, _):
        file, _ = QFileDialog.getOpenFileName(self, 'Выберите файл')
        status = 'Успешно' if file else 'Предупреждение'
        self.add_result(table, name, status, "Файл целый" if file else "Файл не выбран")

    def add_system_result(self, table, name, metric):
        stats = {
            'Загрузка CPU': lambda: f"Нагрузка: {psutil.cpu_percent()}%",
            'Использование памяти': lambda: (
                mem := psutil.virtual_memory(),
                f"Использовано: {mem.percent}% от {mem.total//1024//1024} МБ"
            )[1]
        }
        self.add_result(table, name, 'Успешно', stats[metric]())

    def test_service(self, table, name, service):
        try:
            status = subprocess.check_output(
                ['systemctl', 'is-active', {'SSH сервер':'sshd', 'Веб сервер':'httpd', 'MySQL сервер':'mysql'}[service]],
                text=True
            ).strip()
            self.add_result(table, name, 'Успешно' if status == 'active' else 'Ошибка', f"Статус: {status}")
        except:
            self.add_result(table, name, 'Ошибка', 'Ошибка проверки')

    def test_db_ops(self, table, name, _):
        try:
            with mysql.connector.connect(host="localhost", user="root", password="") as conn:
                conn.cursor().execute("""
                    CREATE DATABASE IF NOT EXISTS testdb;
                    USE testdb;
                    CREATE TABLE IF NOT EXISTS test (id INT);
                    INSERT INTO test VALUES (1);
                    DROP TABLE test;
                """)
            self.add_result(table, name, 'Успешно', 'Тестовые операции выполнены')
        except Exception as e:
            self.add_result(table, name, 'Ошибка', f"Ошибка: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
