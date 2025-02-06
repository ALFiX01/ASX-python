import os
import platform
import subprocess
import winreg
from utils.registry_handler import RegistryHandler

class SystemTweaks:
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
            # Open the registry key
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"System\GameConfigStore", 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, "GameDVR_Enabled")
            winreg.CloseKey(key)
            return value == 1
        except Exception:
            return False

    @staticmethod
    def optimize_power_plan():
        """Set high performance power plan"""
        if not SystemTweaks.is_windows():
            print("Power plan optimization is only available on Windows")
            return False

        try:
            subprocess.run(['powercfg', '/setactive', '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'])
            # Rename the plan to include ASX
            subprocess.run(['powercfg', '/changename', '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c', 
                          'ASX High Performance', 'Оптимизированный план электропитания ASX Hub'])
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