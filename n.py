#!/usr/bin/env python3
import os
import subprocess
import socket

class SystemChecker:
    def check_internet(self, host="8.8.8.8", port=53):
        """Проверка доступности интернета"""
        try:
            socket.create_connection((host, int(port)), timeout=3)
            return True, f"Соединение с {host}:{port} установлено"
        except Exception as e:
            return False, f"Ошибка: {str(e)}"

    def check_ping(self, host="google.com"):
        """Проверка доступности хоста через ping"""
        try:
            result = subprocess.run(
                ["ping", "-c", "1", host],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode == 0:
                return True, f"Успешный ping до {host}"
            return False, f"Не удалось выполнить ping до {host}"
        except Exception as e:
            return False, f"Ошибка: {str(e)}"

    def check_disk(self, path="/", min_gb=5):
        """Проверка свободного места на диске"""
        try:
            stat = os.statvfs(path)
            free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
            total_gb = (stat.f_blocks * stat.f_frsize) / (1024**3)
            status = free_gb >= min_gb
            msg = f"Свободно {free_gb:.1f}ГБ из {total_gb:.1f}ГБ"
            return status, msg
        except Exception as e:
            return False, f"Ошибка: {str(e)}"

    def check_resources(self):
        """Проверка загрузки системы"""
        try:
            load = os.getloadavg()
            mem = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / (1024**3)
            return True, f"Загрузка CPU: {load[0]:.2f}, Всего памяти: {mem:.1f}ГБ"
        except Exception as e:
            return False, f"Ошибка: {str(e)}"

def show_menu():
    """Отображение меню"""
    print("\nВыберите проверки (введите номера через запятую):")
    print("1. Проверка интернета")
    print("2. Проверка ping")
    print("3. Проверка диска")
    print("4. Проверка ресурсов")
    print("5. Все проверки")
    print("0. Выход")

def get_parameters(selected_checks):
    """Запрос параметров для выбранных проверок"""
    params = {}
    
    if 1 in selected_checks or 5 in selected_checks:
        params['host'] = input("Введите хост для проверки интернета [8.8.8.8]: ") or "8.8.8.8"
        params['port'] = input("Введите порт [53]: ") or 53

    if 2 in selected_checks or 5 in selected_checks:
        params['ping_host'] = input("Введите хост для ping [google.com]: ") or "google.com"

    if 3 in selected_checks or 5 in selected_checks:
        params['disk_path'] = input("Введите путь для проверки диска [/]: ") or "/"
        params['min_gb'] = input("Минимальный требуемый объем (ГБ) [5]: ") or 5

    return params

def main():
    """Основная функция программы"""
    checker = SystemChecker()
    
    while True:
        show_menu()
        choice = input("Ваш выбор: ").strip()
        
        if choice == '0':
            break
            
        try:
            selected_checks = list(map(int, choice.split(',')))
        except ValueError:
            print("Ошибка ввода. Попробуйте снова.")
            continue
            
        if 5 in selected_checks:
            selected_checks = [1, 2, 3, 4]

        params = get_parameters(selected_checks)
        
        print("\nРезультаты проверки:")
        if 1 in selected_checks:
            success, msg = checker.check_internet(params.get('host'), params.get('port'))
            print(f"Интернет: {'✓' if success else '✗'} {msg}")
            
        if 2 in selected_checks:
            success, msg = checker.check_ping(params.get('ping_host'))
            print(f"Ping: {'✓' if success else '✗'} {msg}")
            
        if 3 in selected_checks:
            success, msg = checker.check_disk(params.get('disk_path')), float(params.get('min_gb'))
            print(f"Диск: {'✓' if success else '✗'} {msg}")
            
        if 4 in selected_checks:
            success, msg = checker.check_resources()
            print(f"Ресурсы: {'✓' if success else '✗'} {msg}")

if __name__ == "__main__":
    main()