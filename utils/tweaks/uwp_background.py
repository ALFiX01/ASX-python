import platform
import winreg
from utils.registry_handler import RegistryHandler
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata

class UWPBackgroundTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.registry_path = r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications"
        self.value_name = "GlobalUserDisabled"
    
    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Работа UWP программ в фоне",
            description="Запрещает UWP (Universal Windows Platform) приложениям работать в фоновом режиме.\nМожет снизить использование ресурсов системы.",
            category="Оптимизация и настройки"
        )
    
    def check_status(self) -> bool:
        if platform.system() != "Windows":
            return False
        value = self.reg.get_registry_value(self.registry_path, self.value_name)
        return value != 1  # Not disabled = enabled
        
    def toggle(self) -> bool:
        current_status = self.check_status()
        return self.disable() if current_status else self.enable()
        
    def enable(self) -> bool:
        return self.reg.set_registry_value(
            self.registry_path,
            self.value_name,
            0,
            winreg.REG_DWORD
        )
        
    def disable(self) -> bool:
        return self.reg.set_registry_value(
            self.registry_path,
            self.value_name,
            1,
            winreg.REG_DWORD
        )
