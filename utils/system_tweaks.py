import os
import platform
import subprocess
import zipfile
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

    # === Spectre, Meltdown, DownFall Mitigations ===
    @staticmethod
    def check_spectre_meltdown_status():
        """Check status of Spectre/Meltdown mitigations using Registry"""
        if not SystemTweaks.is_windows():
            return False
        reg = RegistryHandler()
        # Check "FeatureSettings" value - if it contains "0x1", mitigations are likely enabled
        feature_settings = reg.get_registry_value(
            r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management",
            "FeatureSettings"
        )
        return feature_settings == 1  # If FeatureSettings == 1 (0x1), assume mitigations are enabled (ВКЛ)

    @staticmethod
    def optimize_spectre_meltdown():
        """Disable Spectre/Meltdown/Downfall mitigations using Registry"""
        if not SystemTweaks.is_windows():
            return False
        reg = RegistryHandler()
        success = True  # Assume success unless any registry operation fails

        # Batch code suggests setting FeatureSettingsOverride and FeatureSettingsOverrideMask to specific values to DISABLE mitigations
        success &= reg.set_registry_value(  # Use &= to track success across multiple operations
            r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management",
            "FeatureSettingsOverride",
            33554432,  # 0x2000000 - Value from batch code for disabling mitigations
            winreg.REG_DWORD
        )
        success &= reg.set_registry_value(
            r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management",
            "FeatureSettingsOverrideMask",
            3,  # 0x3 - Value from batch code for disabling mitigations
            winreg.REG_DWORD
        )
        # Batch code also suggests deleting "FeatureSettingsOverride" and "FeatureSettingsOverrideMask" - we are setting Override, not deleting, based on batch logic
        # success &= reg.delete_registry_value( # No delete operation based on batch code logic
        #     r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management",
        #     "FeatureSettingsOverride"
        # )
        # success &= reg.delete_registry_value(
        #     r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management",
        #     "FeatureSettingsOverrideMask"
        # )

        if success:
            print(
                "Spectre, Meltdown, Downfall mitigations DISABLED (попытка). Требуется перезагрузка системы для полного применения.")  # User info - Reboot required
        else:
            print("Error disabling Spectre, Meltdown, Downfall mitigations.")  # Error message
        return success

    @staticmethod
    def restore_default_spectre_meltdown():
        """Restore default Spectre/Meltdown mitigations using Registry"""
        if not SystemTweaks.is_windows():
            return False
        reg = RegistryHandler()
        success = True  # Assume success unless delete operation fails

        # Batch code suggests deleting FeatureSettingsOverride and FeatureSettingsOverrideMask to RESTORE default mitigations
        success &= reg.delete_registry_value(  # Use &= to track success across multiple operations
            r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management",
            "FeatureSettingsOverride"
        )
        success &= reg.delete_registry_value(
            r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management",
            "FeatureSettingsOverrideMask"
        )

        if success:
            print(
                "Spectre, Meltdown, Downfall mitigations RESTORED to default (попытка). Требуется перезагрузка системы для полного применения.")  # User info - Reboot required
        else:
            print("Error restoring default Spectre, Meltdown, Downfall mitigations.")  # Error message
        return success


    # === Оптимизация настроек Nvidia ===
    @staticmethod
    def check_nvidia_optimization_status():
        """Check Nvidia optimization status using Registry"""
        if not SystemTweaks.is_windows():
            return False
        reg = RegistryHandler()
        # Check if "NvidiaPanelOptimization" value exists in registry - if yes, optimization is likely enabled
        nvidia_optimized = reg.get_registry_value(
            r"HKEY_CURRENT_USER\Software\ALFiX inc.\ASX\Data\ParameterFunction", # Registry path from batch code
            "NvidiaPanelOptimization" # Registry value name from batch code
        )
        return nvidia_optimized is not None # If value exists, assume optimization is enabled (ВКЛ)


    @staticmethod
    def optimize_nvidia_optimization():
        """Apply Nvidia optimization using Nvidia Profile Inspector"""
        if not SystemTweaks.is_windows():
            print("Nvidia optimization is only available on Windows")
            return False

        # === Define paths and URLs ===
        base_dir = "downloads" # Base download directory
        nvidia_inspector_zip_filename = "nvidiaProfileInspector.zip"
        nvidia_inspector_zip_filepath = os.path.join(base_dir, nvidia_inspector_zip_filename)
        nvidia_inspector_extract_dir = os.path.join("resources", "nvidiaProfileInspector") # Папка для распаковки
        nvidia_inspector_exe_path = os.path.join(nvidia_inspector_extract_dir, "nvidiaProfileInspector.exe")
        asx_profile_nip_filename = "ASX_Profile.nip"
        asx_profile_nip_filepath = os.path.join(nvidia_inspector_extract_dir, asx_profile_nip_filename)
        base_profile_nip_filename = "Base_Profile.nip"
        base_profile_nip_filepath = os.path.join(nvidia_inspector_extract_dir, base_profile_nip_filename)

        nvidia_inspector_zip_url = "https://github.com/Orbmu2k/nvidiaProfileInspector/releases/latest/download/nvidiaProfileInspector.zip" # Example - Replace with correct URL if needed
        asx_profile_nip_url = "https://raw.githubusercontent.com/ALFiX01/ASX-Hub/refs/heads/main/Files/Resources/NvidiaProfileInspector/ASX_Profile.nip" # URL from batch code
        base_profile_nip_url = "https://raw.githubusercontent.com/ALFiX01/ASX-Hub/refs/heads/main/Files/Resources/NvidiaProfileInspector/Base_Profile.nip" # URL from batch code


        reg = RegistryHandler()
        success = True # Assume success unless any operation fails

        try:
            # === Ensure directories exist ===
            os.makedirs(base_dir, exist_ok=True)
            os.makedirs(nvidia_inspector_extract_dir, exist_ok=True)


            # === Download Nvidia Profile Inspector ZIP ===
            print(f"Downloading Nvidia Profile Inspector ZIP from: {nvidia_inspector_zip_url} to {nvidia_inspector_zip_filepath}") # User info
            response = requests.get(nvidia_inspector_zip_url, stream=True, allow_redirects=True)
            response.raise_for_status()
            with open(nvidia_inspector_zip_filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"Nvidia Profile Inspector ZIP downloaded successfully to: {nvidia_inspector_zip_filepath}") # User info


            # === Extract Nvidia Profile Inspector ZIP ===
            print(f"Extracting Nvidia Profile Inspector ZIP to: {nvidia_inspector_extract_dir}") # User info
            with zipfile.ZipFile(nvidia_inspector_zip_filepath, 'r') as zip_ref:
                zip_ref.extractall(nvidia_inspector_extract_dir)
            print(f"Nvidia Profile Inspector ZIP extracted successfully to: {nvidia_inspector_extract_dir}") # User info
            os.remove(nvidia_inspector_zip_filepath) # Clean up ZIP file


            # === Download ASX Profile .nip ===
            print(f"Downloading ASX Profile .nip from: {asx_profile_nip_url} to {asx_profile_nip_filepath}") # User info
            response = requests.get(asx_profile_nip_url, stream=True, allow_redirects=True)
            response.raise_for_status()
            with open(asx_profile_nip_filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"ASX Profile .nip downloaded successfully to: {asx_profile_nip_filepath}") # User info


            # === Import ASX Profile using Nvidia Profile Inspector ===
            print(f"Importing ASX Profile using Nvidia Profile Inspector: {asx_profile_nip_filepath}") # User info
            subprocess.run([nvidia_inspector_exe_path, asx_profile_nip_filepath], check=True)
            print("ASX Profile imported successfully.") # User info


            # === Set Registry Value to mark optimization as enabled ===
            success &= reg.set_registry_value( # Track success
                r"HKEY_CURRENT_USER\Software\ALFiX inc.\ASX\Data\ParameterFunction", # Registry path from batch code
                "NvidiaPanelOptimization", # Registry value name from batch code
                1, # Mark as optimized (ВКЛ)
                winreg.REG_DWORD
            )


        except Exception as e:
            print(f"Error optimizing Nvidia settings: {e}") # Error message
            success = False # Mark operation as failed

        if success:
            print("Nvidia settings optimized successfully.") # Success message
        return success


    @staticmethod
    def restore_default_nvidia_optimization():
        """Restore default Nvidia settings using Nvidia Profile Inspector"""
        if not SystemTweaks.is_windows():
            print("Nvidia optimization is only available on Windows")
            return False

        # === Define paths and URLs (same as in optimize_nvidia_optimization) ===
        base_dir = "downloads" # Base download directory
        nvidia_inspector_zip_filename = "nvidiaProfileInspector.zip"
        nvidia_inspector_zip_filepath = os.path.join(base_dir, nvidia_inspector_zip_filename)
        nvidia_inspector_extract_dir = os.path.join("resources", "nvidiaProfileInspector") # Папка для распаковки
        nvidia_inspector_exe_path = os.path.join(nvidia_inspector_extract_dir, "nvidiaProfileInspector.exe")
        base_profile_nip_filename = "Base_Profile.nip"
        base_profile_nip_filepath = os.path.join(nvidia_inspector_extract_dir, base_profile_nip_filename)

        nvidia_inspector_zip_url = "https://github.com/Orbmu2k/nvidiaProfileInspector/releases/latest/download/nvidiaProfileInspector.zip" # Example - Replace with correct URL if needed
        base_profile_nip_url = "https://raw.githubusercontent.com/ALFiX01/ASX-Hub/refs/heads/main/Files/Resources/NvidiaProfileInspector/Base_Profile.nip" # URL from batch code


        reg = RegistryHandler()
        success = True # Assume success unless any operation fails


        try:
             # === Ensure directories exist ===
            os.makedirs(base_dir, exist_ok=True)
            os.makedirs(nvidia_inspector_extract_dir, exist_ok=True)

            # === Download Nvidia Profile Inspector ZIP (if not already downloaded) ===
            if not os.path.exists(nvidia_inspector_exe_path): # Check if inspector EXE exists to avoid redundant download
                print(f"Downloading Nvidia Profile Inspector ZIP from: {nvidia_inspector_zip_url} to {nvidia_inspector_zip_filepath}") # User info
                response = requests.get(nvidia_inspector_zip_url, stream=True, allow_redirects=True)
                response.raise_for_status()
                with open(nvidia_inspector_zip_filepath, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                print(f"Nvidia Profile Inspector ZIP downloaded successfully to: {nvidia_inspector_zip_filepath}") # User info

                # === Extract Nvidia Profile Inspector ZIP ===
                print(f"Extracting Nvidia Profile Inspector ZIP to: {nvidia_inspector_extract_dir}") # User info
                with zipfile.ZipFile(nvidia_inspector_zip_filepath, 'r') as zip_ref:
                    zip_ref.extractall(nvidia_inspector_extract_dir)
                print(f"Nvidia Profile Inspector ZIP extracted successfully to: {nvidia_inspector_extract_dir}") # User info
                os.remove(nvidia_inspector_zip_filepath) # Clean up ZIP file


            # === Download Base Profile .nip ===
            print(f"Downloading Base Profile .nip from: {base_profile_nip_url} to {base_profile_nip_filepath}") # User info
            response = requests.get(base_profile_nip_url, stream=True, allow_redirects=True)
            response.raise_for_status()
            with open(base_profile_nip_filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"Base Profile .nip downloaded successfully to: {base_profile_nip_filepath}") # User info


            # === Import Base Profile using Nvidia Profile Inspector ===
            print(f"Importing Base Profile using Nvidia Profile Inspector: {base_profile_nip_filepath}") # User info
            subprocess.run([nvidia_inspector_exe_path, base_profile_nip_filepath], check=True)
            print("Base Profile imported successfully (Nvidia settings restored to default).") # User info


            # === Delete Registry Value to mark optimization as disabled ===
            success &= reg.delete_registry_value( # Track success
                r"HKEY_CURRENT_USER\Software\ALFiX inc.\ASX\Data\ParameterFunction", # Registry path from batch code
                "NvidiaPanelOptimization" # Registry value name from batch code
            )


        except Exception as e:
            print(f"Error restoring default Nvidia settings: {e}") # Error message
            success = False # Mark operation as failed

        if success:
            print("Nvidia settings restored to default successfully.") # Success message
        return success


    # === Отключить HDCP ===
    @staticmethod
    def check_hdcp_status():
        """Check HDCP status using Registry"""
        if not SystemTweaks.is_windows():
            return False
        reg = RegistryHandler()
        hdcp_value = reg.get_registry_value(
            r"HKLM\System\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}", # Registry path from batch code
            "RMHdcpKeyglobZero" # Registry value name from batch code
        )
        return hdcp_value == 1 # If RMHdcpKeyglobZero == 1 (0x1), assume HDCP is DISABLED (ВЫКЛ)

    @staticmethod
    def toggle_hdcp():
        """Toggle HDCP using Registry"""
        if not SystemTweaks.is_windows():
            return False
        reg = RegistryHandler()
        current_status = SystemTweaks.check_hdcp_status() # Get current status from check_hdcp_status (реестр)
        new_hdcp_value = 0 if current_status else 1 # Toggle value: if disabled (True/1), enable (0), and vice versa
        success = reg.set_registry_value(
            r"HKLM\System\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}", # Registry path from batch code
            "RMHdcpKeyglobZero",
            new_hdcp_value,
            winreg.REG_DWORD # Specify REG_DWORD type explicitly
        )
        if success:
            print(f"HDCP toggled to: {'Enabled' if new_hdcp_value == 0 else 'Disabled'}") # Corrected message - Enabled/Disabled
        else:
            print("Error toggling HDCP")
        return success


    # === Отключить Power Throttling ===
    @staticmethod
    def check_power_throttling_status():
        """Check Power Throttling status using Registry"""
        if not SystemTweaks.is_windows():
            return False
        reg = RegistryHandler()
        power_throttling_value = reg.get_registry_value(
            r"ControlSet001\Control\Power\PowerThrottling",
            "PowerThrottlingOff"
        )
        return power_throttling_value == 1

    @staticmethod
    def toggle_power_throttling():
        """Toggle Power Throttling using Registry"""
        if not SystemTweaks.is_windows():
            return False
        reg = RegistryHandler()
        current_status = SystemTweaks.check_power_throttling_status()
        new_power_throttling_value = 0 if current_status else 1
        success = reg.set_registry_value(
            r"ControlSet001\Control\Power\PowerThrottling",
            "PowerThrottlingOff",
            new_power_throttling_value,
            winreg.REG_DWORD
        )
        if success:
            print(f"Power Throttling toggled to: {'Disabled' if new_power_throttling_value == 1 else 'Enabled'}")
        else:
            print("Error toggling Power Throttling")
        return success


    # === Работа UWP программ в фоне ===
    @staticmethod
    def check_uwp_background_status():
        """Check UWP background apps status using Registry"""
        if not SystemTweaks.is_windows():
            return False
        reg = RegistryHandler()
        uwp_background_value = reg.get_registry_value(
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\BackgroundActivity",
            "DisableActivity"
        )
        return uwp_background_value == 1

    @staticmethod
    def toggle_uwp_background():
        """Toggle UWP background apps using Registry"""
        if not SystemTweaks.is_windows():
            return False
        reg = RegistryHandler()
        current_status = SystemTweaks.check_uwp_background_status()
        new_uwp_background_value = 0 if current_status else 1
        success = reg.set_registry_value(
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\BackgroundActivity",
            "DisableActivity",
            new_uwp_background_value,
            winreg.REG_DWORD
        )
        if success:
            print(f"UWP Background Apps toggled to: {'Disabled' if new_uwp_background_value == 1 else 'Enabled'}")
        else:
            print("Error toggling UWP Background Apps")
        return success


    # === Уведомления ===
    @staticmethod
    def check_notifications_status():
        """Check Notifications status using Registry"""
        if not SystemTweaks.is_windows():
            return False
        reg = RegistryHandler()
        notifications_value = reg.get_registry_value(
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\PushNotifications",
            "ToastEnabled"
        )
        return notifications_value == 0

    @staticmethod
    def toggle_notifications():
        """Toggle Notifications using Registry"""
        if not SystemTweaks.is_windows():
            return False
        reg = RegistryHandler()
        current_status = SystemTweaks.check_notifications_status()
        new_notifications_value = 1 if current_status else 0
        success = reg.set_registry_value(
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\PushNotifications",
            "ToastEnabled",
            new_notifications_value,
            winreg.REG_DWORD
        )
        if success:
            print(f"Notifications toggled to: {'Disabled' if new_notifications_value == 0 else 'Enabled'}")
        else:
            print("Error toggling Notifications")
        return success


    # === Cortana ===
    @staticmethod
    def check_cortana_status():
        """Check Cortana status using Registry (example - placeholder)"""
        # ... (check_cortana_status заглушка - БЕЗ ИЗМЕНЕНИЙ) ...
        return False

    @staticmethod
    def toggle_cortana():
        """Toggle Cortana using Registry (example - placeholder)"""
        # ... (toggle_cortana заглушка - БЕЗ ИЗМЕНЕНИЙ) ...
        return True