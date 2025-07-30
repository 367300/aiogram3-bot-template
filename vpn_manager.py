#!/usr/bin/env python3
"""
Менеджер VPN для автоматического подключения только для запросов к OpenAI API
"""

import subprocess
import time
import os
import signal
import threading
from pathlib import Path

class VPNManager:
    def __init__(self, ovpn_config_path):
        self.ovpn_config_path = ovpn_config_path
        self.vpn_process = None
        self.vpn_active = False
        self.lock = threading.Lock()
        
    def start_vpn(self):
        """Запускает VPN подключение"""
        with self.lock:
            if self.vpn_active:
                print("🔒 VPN уже активен")
                return True
                
            try:
                print("🔒 Запуск VPN...")
                
                # Останавливаем существующие процессы OpenVPN
                subprocess.run(['sudo', 'pkill', 'openvpn'], 
                            capture_output=True, text=True)
                time.sleep(2)
                
                # Запускаем OpenVPN с правильными параметрами для маршрутизации
                self.vpn_process = subprocess.Popen([
                    'sudo', 'openvpn', 
                    '--config', self.ovpn_config_path,
                    '--daemon',
                    '--log', '/tmp/openvpn.log'  # Логи для отладки
                ])
                
                # Ждем подключения
                print("⏳ Ожидание подключения VPN...")
                time.sleep(20)
                
                # Проверяем статус процесса
                if self.vpn_process.poll() is None:
                    # Проверяем логи на успешное подключение
                    try:
                        result = subprocess.run(['sudo', 'cat', '/tmp/openvpn.log'], 
                                              capture_output=True, text=True)
                        if result.returncode == 0:
                            log_content = result.stdout
                            if 'Initialization Sequence Completed' in log_content:
                                print("✅ VPN подключился успешно!")
                                self.vpn_active = True
                                return True
                            else:
                                print("❌ VPN не завершил инициализацию")
                                return False
                        else:
                            print("❌ Не удалось прочитать логи VPN")
                            return False
                    except:
                        print("❌ Не удалось прочитать логи VPN")
                        return False
                else:
                    print("❌ Ошибка запуска VPN")
                    # Показываем логи для отладки
                    try:
                        with open('/tmp/openvpn.log', 'r') as f:
                            log_content = f.read()
                            print(f"📋 Логи OpenVPN:\n{log_content}")
                    except:
                        pass
                    return False
                    
            except Exception as e:
                print(f"❌ Ошибка запуска VPN: {e}")
                return False
    

    
    def _check_vpn_connection(self):
        """Проверяет, работает ли VPN подключение"""
        try:
            # Проверяем наличие tun интерфейса
            result = subprocess.run(['ip', 'link', 'show', 'tun0'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                return False
            
            # Проверяем маршрутизацию
            result = subprocess.run(['ip', 'route', 'show'], 
                                  capture_output=True, text=True)
            if 'tun0' not in result.stdout:
                return False
            
            # Проверяем, что трафик идет через VPN
            result = subprocess.run(['curl', '-s', '--connect-timeout', '10', 
                                   'https://ipinfo.io/ip'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                ip = result.stdout.strip()
                print(f"🌍 IP через VPN: {ip}")
                
                # Проверяем, что IP изменился (не локальный)
                if not ip.startswith('77.45.191.99'):  # Ваш текущий IP
                    return True
                else:
                    print("⚠️ IP не изменился - трафик не идет через VPN")
                    return False
            
            return False
            
        except:
            return False
    
    def stop_vpn(self):
        """Останавливает VPN подключение"""
        with self.lock:
            if not self.vpn_active:
                print("🌐 VPN не активен")
                return True
                
            try:
                print("🛑 Остановка VPN...")
                
                # Находим и убиваем процесс OpenVPN
                subprocess.run(['sudo', 'pkill', 'openvpn'], 
                            capture_output=True, text=True)
                
                if self.vpn_process:
                    self.vpn_process.terminate()
                    self.vpn_process.wait(timeout=10)
                
                # Ждем полной остановки
                time.sleep(3)
                
                # Очищаем маршрутизацию
                subprocess.run(['sudo', 'ip', 'route', 'flush', 'cache'], 
                            capture_output=True, text=True)
                
                self.vpn_active = False
                print("✅ VPN остановлен")
                return True
                
            except Exception as e:
                print(f"❌ Ошибка остановки VPN: {e}")
                return False
    
    def is_vpn_active(self):
        """Проверяет, активен ли VPN"""
        try:
            # Проверяем процесс
            result = subprocess.run(['pgrep', 'openvpn'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                return False
            
            # Проверяем подключение
            return self._check_vpn_connection()
        except:
            return False
    
    def get_vpn_ip(self):
        """Получает IP адрес через VPN"""
        try:
            result = subprocess.run(['curl', '-s', '--connect-timeout', '10', 
                                   'https://ipinfo.io/ip'], 
                                  capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return None
    
    def force_restart_vpn(self):
        """Принудительно перезапускает VPN"""
        print("🔄 Принудительный перезапуск VPN...")
        self.stop_vpn()
        time.sleep(3)
        return self.start_vpn()

# Глобальный экземпляр менеджера VPN
vpn_manager = None

def init_vpn_manager(ovpn_config_path):
    """Инициализирует менеджер VPN"""
    global vpn_manager
    vpn_manager = VPNManager(ovpn_config_path)
    return vpn_manager

def ensure_vpn_for_openai():
    """Обеспечивает VPN подключение для запросов к OpenAI"""
    global vpn_manager
    
    if not vpn_manager:
        print("⚠️ VPN менеджер не инициализирован")
        return False
    
    if not vpn_manager.is_vpn_active():
        print("🔒 Запуск VPN для OpenAI API...")
        if vpn_manager.start_vpn():
            # Ждем стабилизации подключения
            time.sleep(5)
            ip = vpn_manager.get_vpn_ip()
            if ip:
                print(f"🌍 VPN IP: {ip}")
            return True
        else:
            print("❌ Не удалось запустить VPN")
            return False
    else:
        print("🔒 VPN уже активен")
        return True

def cleanup_vpn():
    """Очищает VPN при завершении работы"""
    global vpn_manager
    if vpn_manager:
        vpn_manager.stop_vpn()

# Регистрируем обработчик сигналов для корректного завершения
def signal_handler(signum, frame):
    print("\n🛑 Получен сигнал завершения, останавливаем VPN...")
    cleanup_vpn()
    exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler) 