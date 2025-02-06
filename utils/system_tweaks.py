import os
import platform
import subprocess
import requests  # Добавляем импорт библиотеки requests для скачивания файлов
from utils.registry_handler import RegistryHandler

# Импортируем winreg только на Windows
if platform.system() == "Windows":
    import winreg

class SystemTweaks:
    # GUID для плана электропитания ASX Hub
    ASX_POWER_PLAN_GUID = "44444444-4444-4444-4444-444444444449"

    # Список GUID стандартных планов электропитания
    DEFAULT_POWER_PLANS = [
        "381b4222-f694-41f0-9685-ff5bb260df2e",  # Сбалансированный
        "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",  # Высокая производительность
        "a1841308-3541-4fab-bc81-f71556f20b4a",  # Экономия энергии
        "a9758bf0-cfc6-439c-a392-7783990ff716"   # Максимальная производительность
    ]

    @staticmethod
    def is_windows():
        return platform.system() == "Windows"

    @staticmethod
    def check_power_plan_status():
        """Check if ASX power plan is active"""
        if not SystemTweaks.is_windows():
            return False

        try:
            # Get current power plan using powercfg
            result = subprocess.run(['powercfg', '/getactivescheme'], capture_output=True, text=True)
            return "ASX" in result.stdout
        except Exception:
            return False

    @staticmethod
    def check_game_bar_status():
        """Check if Game Bar is enabled"""
        if not SystemTweaks.is_windows():
            return False

        try:
            if not hasattr(SystemTweaks, '_winreg'):
                return False
            # Open the registry key
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"System\GameConfigStore", 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, "GameDVR_Enabled")
            winreg.CloseKey(key)
            return value == 1
        except Exception:
            return False

    @staticmethod
    def optimize_power_plan():
        """Set ASX Hub power plan"""
        if not SystemTweaks.is_windows():
            print("Power plan optimization is only available on Windows")
            return False

        try:
            # Restore default schemes first
            subprocess.run(['powercfg', '-restoredefaultschemes'], check=True)

            # Remove existing ASX plan if it exists
            subprocess.run(['powercfg', '/d', SystemTweaks.ASX_POWER_PLAN_GUID],
                         capture_output=True)  # Ignore errors if plan doesn't exist

            # Скачиваем файл .pow
            download_url = "https://github.com/ALFiX01/ASX-Hub/releases/download/File/ASX.Hub-Power.pow"
            temp_pow_file = os.path.join(os.environ['TEMP'], "ASX Hub-Power.pow")

            try:
                response = requests.get(download_url, stream=True)
                response.raise_for_status()  # Проверка на ошибки HTTP
                with open(temp_pow_file, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                print(f"Файл power plan успешно скачан в: {temp_pow_file}")
            except requests.exceptions.RequestException as e:
                print(f"Ошибка при скачивании файла power plan: {e}")
                return False

            # Import ASX power plan из скачанного файла
            if os.path.exists(temp_pow_file):
                subprocess.run(['powercfg', '-import', temp_pow_file,
                              SystemTweaks.ASX_POWER_PLAN_GUID], check=True)

                # Set ASX plan as active
                subprocess.run(['powercfg', '-SETACTIVE',
                              SystemTweaks.ASX_POWER_PLAN_GUID], check=True)

                # Set plan name and description
                subprocess.run(['powercfg', '/changename', SystemTweaks.ASX_POWER_PLAN_GUID,
                              "ASX Hub-Power", "Больше FPS и меньше задержки."], check=True)

                # Remove other power plans
                for guid in SystemTweaks.DEFAULT_POWER_PLANS:
                    subprocess.run(['powercfg', '/d', guid], capture_output=True)

                return True
            else:
                print(f"Файл power plan не найден после скачивания: {temp_pow_file}")
                return False

        except Exception as e:
            print(f"Error optimizing power plan: {str(e)}")
            return False

    @staticmethod
    def restore_default_power_plan():
        """Restore default power plans"""
        if not SystemTweaks.is_windows():
            return False

        try:
            # Restore default schemes
            subprocess.run(['powercfg', '-restoredefaultschemes'], check=True)
            return True
        except Exception:
            return False

    @staticmethod
    def optimize_visual_effects():
        """Optimize visual effects for performance"""
        if not SystemTweaks.is_windows():
            print("Visual effects optimization is only available on Windows")
            return False

        reg = RegistryHandler()
        success = reg.set_registry_value(
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects",
            "VisualFXSetting",
            2
        )

        # Set GameDVR_Enabled
        try:
            if SystemTweaks.is_windows():
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"System\GameConfigStore", 0,
                                    winreg.KEY_WRITE)
                winreg.SetValueEx(key, "GameDVR_Enabled", 0, winreg.REG_DWORD, 1)
                winreg.CloseKey(key)
            return success
        except Exception:
            return False

    @staticmethod
    def disable_services(service_name):
        """Disable a Windows service"""
        if not SystemTweaks.is_windows():
            print("Service control is only available on Windows")
            return False

        try:
            subprocess.run(['sc', 'config', service_name, 'start=disabled'])
            subprocess.run(['sc', 'stop', service_name])
            return True
        except Exception:
            return False