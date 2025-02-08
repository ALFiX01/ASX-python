import os
import platform
import subprocess
import zipfile
import requests  # Добавляем импорт библиотеки requests для скачивания файлов
from utils.registry_handler import RegistryHandler

# Import winreg only on Windows
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

    # === Power Plan ===
    @staticmethod
    def check_powerplan():
        from utils.tweaks.powerplan import PowerPlanTweak
        tweak = PowerPlanTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_powerplan():
        from utils.tweaks.powerplan import PowerPlanTweak
        tweak = PowerPlanTweak()
        return tweak.toggle()


    # === Fso и GameBar ===
    @staticmethod
    def check_FsoGameBar():
        from utils.tweaks.fso_gamebar import FsoGameBarTweak
        tweak = FsoGameBarTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_FsoGameBar():
        from utils.tweaks.fso_gamebar import FsoGameBarTweak
        tweak = FsoGameBarTweak()
        return tweak.toggle()


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

    # === Spectre, Meltdown, DownFall Mitigations ===
    @staticmethod
    def check_spectre_meltdown_status():
        from utils.tweaks.spectre_meltdown import SpectreMeltdownTweak
        tweak = SpectreMeltdownTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_spectre_meltdown():
        from utils.tweaks.spectre_meltdown import SpectreMeltdownTweak
        tweak = SpectreMeltdownTweak()
        return tweak.toggle()


    # === Оптимизация настроек Nvidia ===
    @staticmethod
    def check_nvidia_optimization_status():
        from utils.tweaks.nvidia_optimization import NvidiaOptimizationTweak
        tweak = NvidiaOptimizationTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_nvidia_optimization():
        from utils.tweaks.nvidia_optimization import NvidiaOptimizationTweak
        tweak = NvidiaOptimizationTweak()
        return tweak.toggle()


    # === HDCP ===
    @staticmethod
    def check_hdcp_status():
        from utils.tweaks.hdcp import HdcpTweak
        tweak = HdcpTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_hdcp():
        from utils.tweaks.hdcp import HdcpTweak
        tweak = HdcpTweak()
        return tweak.toggle()


    # === Power Throttling ===
    @staticmethod
    def check_power_throttling_status():
        from utils.tweaks.power_throttling import PowerThrottlingTweak
        tweak = PowerThrottlingTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_power_throttling():
        from utils.tweaks.power_throttling import PowerThrottlingTweak
        tweak = PowerThrottlingTweak()
        return tweak.toggle()


    @staticmethod
    def check_uwp_background_status():
        from utils.tweaks.uwp_background import UWPBackgroundTweak
        tweak = UWPBackgroundTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_uwp_background():
        from utils.tweaks.uwp_background import UWPBackgroundTweak
        tweak = UWPBackgroundTweak()
        return tweak.toggle()


    # === Уведомления ===
    @staticmethod
    def check_notifications_status():
        from utils.tweaks.notifications import NotificationsTweak
        tweak = NotificationsTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_notifications():
        from utils.tweaks.notifications import NotificationsTweak
        tweak = NotificationsTweak()
        return tweak.toggle()


    # === Cortana ===
    @staticmethod
    def check_cortana_status():
        from utils.tweaks.cortana import CortanaTweak
        tweak = CortanaTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_cortana():
        from utils.tweaks.cortana import CortanaTweak
        tweak = CortanaTweak()
        return tweak.toggle()