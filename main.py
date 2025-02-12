#!/usr/bin/env python3
import os
import socket
import shutil
import subprocess


def check_internet():
    try:
        # Пытаемся установить соединение с DNS-сервером Google (8.8.8.8) на порту 53
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True, "Интернет-соединение установлено"
    except Exception as e:
        return False, f"Проверка интернет-соединения провалена: {e}"


def check_dns():
    try:
        ip = socket.gethostbyname("www.google.com")
        return True, f"DNS разрешение успешно, www.google.com -> {ip}"
    except Exception as e:
        return False, f"Проверка DNS разрешения провалена: {e}"


def check_disk_space():
    try:
        total, used, free = shutil.disk_usage("/")
        # Выводим свободное место в гигабайтах
        return True, f"Свободное место на диске: {free // (2 ** 30)} ГБ"
    except Exception as e:
        return False, f"Проверка свободного места на диске провалена: {e}"


def check_filesystem_integrity():
    # Симулированная проверка целостности файловой системы
    return True, "Проверка целостности файловой системы пройдена (симуляция)"


def check_cpu_load():
    try:
        load1, load5, load15 = os.getloadavg()
        return True, f"Загрузка процессора (1,5,15 мин): {load1}, {load5}, {load15}"
    except Exception as e:
        return False, f"Проверка загрузки процессора провалена: {e}"


def check_memory_usage():
    try:
        with open('/proc/meminfo', 'r') as meminfo:
            lines = meminfo.readlines()
            mem_total = None
            mem_free = None
            for line in lines:
                if "MemTotal:" in line:
                    mem_total = int(line.split()[1])
                if "MemAvailable:" in line:
                    mem_free = int(line.split()[1])
            if mem_total and mem_free:
                usage = 100 - (mem_free / mem_total * 100)
                return True, f"Использование памяти: {usage:.2f}%"
            else:
                return False, "Информация о памяти не найдена"
    except Exception as e:
        return False, f"Проверка памяти провалена: {e}"


def check_system_service(service_name):
    try:
        result = subprocess.run(["systemctl", "is-active", service_name],
                                capture_output=True, text=True)
        if result.stdout.strip() == "active":
            return True, f"Служба {service_name} активна"
        else:
            return False, f"Служба {service_name} не активна"
    except Exception as e:
        return False, f"Проверка службы {service_name} провалена: {e}"


def check_database():
    # Симулируем проверку базы данных (MySQL) по попытке подключения к порту 3306
    try:
        sock = socket.create_connection(("127.0.0.1", 3306), timeout=3)
        sock.close()
        return True, "Сервер базы данных (MySQL) доступен на порту 3306"
    except Exception as e:
        return False, f"Проверка базы данных провалена: {e}"


def run_all_checks():
    tests = [
        ("Интернет-соединение", check_internet),
        ("DNS разрешение", check_dns),
        ("Свободное место на диске", check_disk_space),
        ("Целостность файловой системы", check_filesystem_integrity),
        ("Загрузка процессора", check_cpu_load),
        ("Использование памяти", check_memory_usage),
        ("Служба SSH", lambda: check_system_service("ssh")),
        ("Служба HTTPD", lambda: check_system_service("httpd")),
        ("Служба MySQL", lambda: check_system_service("mysql")),
        ("База данных", check_database)
    ]

    for test_name, test_func in tests:
        status, message = test_func()
        print(f"[{'PASS' if status else 'FAIL'}] {test_name}: {message}")


if __name__ == "__main__":
    run_all_checks()
