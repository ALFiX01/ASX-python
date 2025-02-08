import platform
import winreg
import os
import subprocess
import requests
import zipfile
from utils.registry_handler import RegistryHandler
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata


class NvidiaOptimizationTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.registry_path = r"HKEY_CURRENT_USER\Software\ALFiX inc.\ASX\Data\ParameterFunction"
        self.value_name = "NvidiaPanelOptimization"
        self.log_file = self.setup_log_file()

        self.base_dir = "downloads"
        self.nvidia_inspector_zip_filename = "nvidiaProfileInspector.zip"
        self.nvidia_inspector_zip_filepath = os.path.join(self.base_dir, self.nvidia_inspector_zip_filename)
        self.nvidia_inspector_extract_dir = os.path.join("resources", "nvidiaProfileInspector")
        self.nvidia_inspector_exe_path = os.path.join(self.nvidia_inspector_extract_dir, "nvidiaProfileInspector.exe")
        self.asx_profile_nip_filename = "ASX_Profile.nip"
        self.asx_profile_nip_filepath = os.path.join(self.nvidia_inspector_extract_dir, self.asx_profile_nip_filename)
        self.base_profile_nip_filename = "Base_Profile.nip"
        self.base_profile_nip_filepath = os.path.join(self.nvidia_inspector_extract_dir, self.base_profile_nip_filename)

        self.nvidia_inspector_zip_url = "https://github.com/Orbmu2k/nvidiaProfileInspector/releases/latest/download/nvidiaProfileInspector.zip"
        self.asx_profile_nip_url = "https://raw.githubusercontent.com/ALFiX01/ASX-Hub/refs/heads/main/Files/Resources/NvidiaProfileInspector/ASX_Profile.nip"
        self.base_profile_nip_url = "https://raw.githubusercontent.com/ALFiX01/ASX-Hub/refs/heads/main/Files/Resources/NvidiaProfileInspector/Base_Profile.nip"

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Оптимизация настроек Nvidia",
            description="Отключает/Включает оптимизированные настройки Nvidia",
            category="Оптимизация и настройки"
        )

    def check_status(self) -> bool:
        if platform.system() != "Windows":
            return False
        # Check if the value exists.  If it exists, we consider the optimization ENABLED.
        value = self.reg.get_registry_value(self.registry_path, self.value_name)
        return value is not None

    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if not current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        """Apply Nvidia optimization."""
        success = True
        try:
            os.makedirs(self.base_dir, exist_ok=True)
            os.makedirs(self.nvidia_inspector_extract_dir, exist_ok=True)

            if not os.path.exists(self.nvidia_inspector_exe_path):
                self._download_and_extract_inspector()

            self._download_file(self.asx_profile_nip_url, self.asx_profile_nip_filepath)
            subprocess.run([self.nvidia_inspector_exe_path, self.asx_profile_nip_filepath], check=True)

            # Use REG_SZ and set a string value (e.g., "1")
            success = self.reg.set_registry_value(self.registry_path, self.value_name, "1", winreg.REG_SZ)
            self.log_action("enable", "Enabled", success)

        except Exception as e:
            print(f"Error enabling Nvidia optimization: {e}")
            success = False
            self.log_action("enable", "Enabled", success)

        return success

    def disable(self) -> bool:
        """Restore default Nvidia settings."""
        success = True
        try:
            os.makedirs(self.base_dir, exist_ok=True)
            os.makedirs(self.nvidia_inspector_extract_dir, exist_ok=True)

            if not os.path.exists(self.nvidia_inspector_exe_path):
                self._download_and_extract_inspector()

            self._download_file(self.base_profile_nip_url, self.base_profile_nip_filepath)
            subprocess.run([self.nvidia_inspector_exe_path, self.base_profile_nip_filepath], check=True)

            # Delete the registry value
            success = self.reg.delete_value(self.registry_path, self.value_name)
            self.log_action("disable", "Disabled", success)

        except Exception as e:
            print(f"Error disabling Nvidia optimization: {e}")
            success = False
            self.log_action("disable", "Disabled", success)

        return success

    def _download_and_extract_inspector(self):
        """Downloads and extracts Nvidia Profile Inspector."""
        self._download_file(self.nvidia_inspector_zip_url, self.nvidia_inspector_zip_filepath)
        with zipfile.ZipFile(self.nvidia_inspector_zip_filepath, 'r') as zip_ref:
            zip_ref.extractall(self.nvidia_inspector_extract_dir)
        os.remove(self.nvidia_inspector_zip_filepath)

    def _download_file(self, url, filepath):
        """Downloads a file."""
        print(f"Downloading {os.path.basename(filepath)} from: {url}")
        response = requests.get(url, stream=True, allow_redirects=True)
        response.raise_for_status()
        with open(filepath, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"{os.path.basename(filepath)} downloaded successfully.")

    def setup_log_file(self):
        """Sets up the log file."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "nvidia_optimization_log.txt")
        return log_file

    def log_action(self, action, state, success):
        """Logs actions."""
        try:
            with open(self.log_file, "a") as f:
                timestamp = self.get_timestamp()
                log_message = f"[{timestamp}] Action: {action}, State: {state}, Success: {success}\n"
                f.write(log_message)
                print(log_message)
        except Exception as e:
            print(f"Error writing to log file: {e}")

    def get_timestamp(self):
        """Gets the current timestamp."""
        import datetime
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")