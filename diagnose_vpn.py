#!/usr/bin/env python3
"""
Скрипт для диагностики проблем с VPN
"""

import subprocess
import os
from decouple import config

def check_openvpn_installation():
    """Проверяет установку OpenVPN"""
    print("🔍 Проверка установки OpenVPN...")
    
    result = subprocess.run(['which', 'openvpn'], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ OpenVPN установлен: {result.stdout.strip()}")
        return True
    else:
        print("❌ OpenVPN не установлен")
        print("💡 Установите: sudo apt install openvpn")
        return False

def check_ovpn_file():
    """Проверяет файл конфигурации"""
    print("\n🔍 Проверка файла конфигурации...")
    
    ovpn_path = config('OVPN_CONFIG_PATH', default=False)
    if not ovpn_path:
        print("❌ OVPN_CONFIG_PATH не настроен в .env")
        return False
    
    if not os.path.exists(ovpn_path):
        print(f"❌ Файл не найден: {ovpn_path}")
        return False
    
    print(f"✅ Файл найден: {ovpn_path}")
    
    # Проверяем права доступа
    stat = os.stat(ovpn_path)
    print(f"📁 Права доступа: {oct(stat.st_mode)[-3:]}")
    
    return True

def check_sudo_permissions():
    """Проверяет права sudo"""
    print("\n🔍 Проверка прав sudo...")
    
    result = subprocess.run(['sudo', '-n', 'true'], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Sudo работает без пароля")
        return True
    else:
        print("⚠️ Требуется пароль для sudo")
        print("💡 Настройте sudoers для openvpn:")
        print("   sudo visudo")
        print("   Добавьте: username ALL=(ALL) NOPASSWD: /usr/sbin/openvpn")
        return False

def check_network_interfaces():
    """Проверяет сетевые интерфейсы"""
    print("\n🔍 Проверка сетевых интерфейсов...")
    
    result = subprocess.run(['ip', 'link', 'show'], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("📋 Доступные интерфейсы:")
        for line in result.stdout.split('\n'):
            if 'tun' in line or 'tap' in line:
                print(f"   🔒 {line.strip()}")
        return True
    else:
        print("❌ Не удалось получить список интерфейсов")
        return False

def test_manual_vpn():
    """Тестирует ручной запуск VPN"""
    print("\n🔍 Тестирование ручного запуска VPN...")
    
    ovpn_path = config('OVPN_CONFIG_PATH', default=False)
    if not ovpn_path:
        print("❌ OVPN_CONFIG_PATH не настроен")
        return False
    
    print("💡 Попробуйте запустить VPN вручную:")
    print(f"   sudo openvpn --config {ovpn_path}")
    print("💡 Если работает, проблема в автоматическом запуске")
    
    return True

def check_current_ip():
    """Проверяет текущий IP"""
    print("\n🔍 Проверка текущего IP...")
    
    try:
        result = subprocess.run(['curl', '-s', 'https://ipinfo.io/ip'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            ip = result.stdout.strip()
            print(f"🌍 Текущий IP: {ip}")
            return True
        else:
            print("❌ Не удалось получить IP")
            return False
    except Exception as e:
        print(f"❌ Ошибка получения IP: {e}")
        return False

def check_openai_connectivity():
    """Проверяет подключение к OpenAI"""
    print("\n🔍 Проверка подключения к OpenAI...")
    
    try:
        result = subprocess.run(['curl', '-s', '--connect-timeout', '10', 
                               'https://api.openai.com'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Подключение к OpenAI работает")
            return True
        else:
            print("❌ Подключение к OpenAI не работает")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения к OpenAI: {e}")
        return False

def main():
    """Главная функция диагностики"""
    print("🔒 Диагностика VPN для OpenAI API")
    print("=" * 50)
    
    checks = [
        check_openvpn_installation(),
        check_ovpn_file(),
        check_sudo_permissions(),
        check_network_interfaces(),
        check_current_ip(),
        check_openai_connectivity(),
        test_manual_vpn()
    ]
    
    print("\n" + "=" * 50)
    print("📊 Результаты диагностики:")
    
    if all(checks):
        print("🎉 Все проверки пройдены!")
        print("VPN должен работать корректно")
    else:
        print("⚠️ Обнаружены проблемы:")
        if not checks[0]:
            print("   - Установите OpenVPN")
        if not checks[1]:
            print("   - Проверьте путь к файлу конфигурации")
        if not checks[2]:
            print("   - Настройте права sudo")
        if not checks[4]:
            print("   - Проверьте интернет-соединение")
        if not checks[5]:
            print("   - OpenAI недоступен без VPN")
    
    print("\n💡 Рекомендации:")
    print("1. Убедитесь, что VPN работает вручную")
    print("2. Проверьте права sudo для openvpn")
    print("3. Убедитесь, что файл конфигурации валиден")

if __name__ == "__main__":
    main()