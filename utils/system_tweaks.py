import os
import platform
import subprocess
from utils.registry_handler import RegistryHandler

class SystemTweaks:
    @staticmethod
    def is_windows():
        return platform.system() == "Windows"

    @staticmethod
    def optimize_power_plan():
        """Set high performance power plan"""
        if not SystemTweaks.is_windows():
            print("Power plan optimization is only available on Windows")
            return False

        try:
            subprocess.run(['powercfg', '/setactive', '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'])
            return True
        except Exception:
            return False

    @staticmethod
    def disable_telemetry():
        """Disable Windows telemetry"""
        if not SystemTweaks.is_windows():
            print("Telemetry control is only available on Windows")
            return False

        reg = RegistryHandler()
        return reg.set_registry_value(
            r"SOFTWARE\Policies\Microsoft\Windows\DataCollection",
            "AllowTelemetry",
            0
        )

    @staticmethod
    def optimize_visual_effects():
        """Optimize visual effects for performance"""
        if not SystemTweaks.is_windows():
            print("Visual effects optimization is only available on Windows")
            return False

        reg = RegistryHandler()
        return reg.set_registry_value(
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects",
            "VisualFXSetting",
            2
        )

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