import platform
import winreg
import subprocess  # Import subprocess
from utils.registry_handler import RegistryHandler
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata

class CortanaTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        # Registry paths and value names are defined as instance variables
        self.policy_path = r"HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search"
        self.policy_value = "AllowCortana"
        self.search_path = r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Search"
        self.search_value_consent = "CortanaConsent"
        self.search_value_bing = "BingSearchEnabled"
        self.explorer_path = r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
        self.explorer_value = "ShowCortanaButton"
        # Add new registry keys here
        self.search_value_can_cortana = "CanCortanaBeEnabled" #HKCU
        self.speech_onecore_path = r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech_OneCore\Preferences" #HKLM
        self.speech_onecore_value = "ModelDownloadAllowed"
        self.windows_search_path = r"HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\Windows Search" # HKLM
        self.windows_search_value_cloud = "AllowCloudSearch"
        self.windows_search_value_location = "AllowSearchToUseLocation"
        self.windows_search_value_web = "ConnectedSearchUseWeb"
        self.windows_search_value_disableweb = "DisableWebSearch"
        self.input_personalization_path = r"HKEY_CURRENT_USER\Software\Microsoft\InputPersonalization" # HKCU
        self.input_personalization_value_ink = "RestrictImplicitInkCollection"
        self.input_personalization_value_text = "RestrictImplicitTextCollection"
        self.trained_data_path = r"HKEY_CURRENT_USER\Software\Microsoft\InputPersonalization\TrainedDataStore" #HKCU
        self.trained_data_value = "HarvestContacts"
        self.personalization_settings_path = r"HKEY_CURRENT_USER\Software\Microsoft\Personalization\Settings" #HKCU
        self.personalization_settings_value = "AcceptedPrivacyPolicy"
        self.windows_search_user_path = r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Windows Search" #HKCU
        self.windows_search_user_value = "CortanaConsent"
        self.search_value_cortana_enabled = "CortanaEnabled"
        self.search_value_searchbox = "SearchboxTaskbarMode"



    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Cortana",
            description="Включает или отключает ассистента Cortana в Windows",
            category="Оптимизация и настройки"
        )

    def check_status(self) -> bool:
        if platform.system() != "Windows":
            return False  # Cortana is only relevant on Windows

        # Check the primary policy setting
        value = self.reg.get_registry_value(self.policy_path, self.policy_value)
        return value != 0  # Enabled if not 0

    def toggle(self) -> bool:
        current_status = self.check_status()
        return self.disable() if current_status else self.enable()

    def enable(self) -> bool:
        """Enables Cortana using registry keys."""
        success = True

        # Set AllowCortana to 1
        success &= self.reg.set_registry_value(self.policy_path, self.policy_value, 1, winreg.REG_DWORD)
        # Restore other registry settings
        success &= self.reg.set_registry_value(self.search_path, self.search_value_consent, 1, winreg.REG_DWORD)
        success &= self.reg.set_registry_value(self.search_path, self.search_value_bing, 1, winreg.REG_DWORD)
        success &= self.reg.set_registry_value(self.explorer_path, self.explorer_value, 1, winreg.REG_DWORD)

        # New registry keys for enabling (setting to default/enabled state)
        success &= self.reg.set_registry_value(self.search_path, self.search_value_can_cortana, 1, winreg.REG_DWORD)  #HKCU
        success &= self.reg.set_registry_value(self.speech_onecore_path, self.speech_onecore_value, 1, winreg.REG_DWORD) # HKLM
        success &= self.reg.set_registry_value(self.windows_search_path, self.windows_search_value_cloud, 1, winreg.REG_DWORD)  # HKLM
        success &= self.reg.set_registry_value(self.windows_search_path, self.windows_search_value_location, 1, winreg.REG_DWORD)  # HKLM
        success &= self.reg.set_registry_value(self.windows_search_path, self.windows_search_value_web, 1, winreg.REG_DWORD)  # HKLM
        success &= self.reg.set_registry_value(self.windows_search_path, self.windows_search_value_disableweb, 0, winreg.REG_DWORD)  # HKLM
        success &= self.reg.set_registry_value(self.input_personalization_path, self.input_personalization_value_ink, 0, winreg.REG_DWORD) #HKCU
        success &= self.reg.set_registry_value(self.input_personalization_path, self.input_personalization_value_text, 0, winreg.REG_DWORD) #HKCU
        success &= self.reg.set_registry_value(self.trained_data_path, self.trained_data_value, 1, winreg.REG_DWORD)  #HKCU
        success &= self.reg.set_registry_value(self.personalization_settings_path, self.personalization_settings_value, 1, winreg.REG_DWORD) #HKCU
        success &= self.reg.set_registry_value(self.windows_search_user_path, self.windows_search_user_value, 1, winreg.REG_DWORD) #HKCU
        success &= self.reg.set_registry_value(self.search_path, self.search_value_cortana_enabled, 1, winreg.REG_DWORD)  #HKCU
        success &= self.reg.set_registry_value(self.search_path, self.search_value_searchbox, 1, winreg.REG_DWORD)  #HKCU

        # Restart explorer.exe to apply changes
        subprocess.run("taskkill /f /im explorer.exe", shell=True, capture_output=True)
        subprocess.run("start explorer.exe", shell=True, capture_output=True)

        return success

    def disable(self) -> bool:
        """Disables Cortana using registry keys and taskkill."""
        success = True

        # Set AllowCortana to 0 (the main policy setting)
        success &= self.reg.set_registry_value(self.policy_path, self.policy_value, 0, winreg.REG_DWORD)

        # Set additional registry keys to disable related features
        success &= self.reg.set_registry_value(self.search_path, self.search_value_consent, 0, winreg.REG_DWORD)
        success &= self.reg.set_registry_value(self.search_path, self.search_value_bing, 0, winreg.REG_DWORD)
        success &= self.reg.set_registry_value(self.explorer_path, self.explorer_value, 0, winreg.REG_DWORD)

        # Kill Cortana process (if running)
        subprocess.run("taskkill /f /im Cortana.exe", shell=True, capture_output=True)

        # New registry keys for disabling
        success &= self.reg.set_registry_value(self.search_path, self.search_value_can_cortana, 0, winreg.REG_DWORD)  #HKCU
        success &= self.reg.set_registry_value(self.speech_onecore_path, self.speech_onecore_value, 0, winreg.REG_DWORD) # HKLM
        success &= self.reg.set_registry_value(self.windows_search_path, self.windows_search_value_cloud, 0, winreg.REG_DWORD) # HKLM
        success &= self.reg.set_registry_value(self.windows_search_path, self.windows_search_value_location, 0, winreg.REG_DWORD) # HKLM
        success &= self.reg.set_registry_value(self.windows_search_path, self.windows_search_value_web, 0, winreg.REG_DWORD)  # HKLM
        success &= self.reg.set_registry_value(self.windows_search_path, self.windows_search_value_disableweb, 1, winreg.REG_DWORD)  # HKLM
        success &= self.reg.set_registry_value(self.input_personalization_path, self.input_personalization_value_ink, 1, winreg.REG_DWORD) #HKCU
        success &= self.reg.set_registry_value(self.input_personalization_path, self.input_personalization_value_text, 1, winreg.REG_DWORD) #HKCU
        success &= self.reg.set_registry_value(self.trained_data_path, self.trained_data_value, 0, winreg.REG_DWORD)  #HKCU
        success &= self.reg.set_registry_value(self.personalization_settings_path, self.personalization_settings_value, 0, winreg.REG_DWORD) #HKCU
        success &= self.reg.set_registry_value(self.windows_search_user_path, self.windows_search_user_value, 0, winreg.REG_DWORD)  #HKCU
        success &= self.reg.set_registry_value(self.search_path, self.search_value_cortana_enabled, 0, winreg.REG_DWORD)  #HKCU
        success &= self.reg.set_registry_value(self.search_path, self.search_value_searchbox, 0, winreg.REG_DWORD)  #HKCU


        # Restart explorer.exe to apply changes
        subprocess.run("taskkill /f /im explorer.exe", shell=True, capture_output=True)
        subprocess.run("start explorer.exe", shell=True, capture_output=True)

        return success