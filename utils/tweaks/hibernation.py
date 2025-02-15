import platform
import subprocess
import os
from utils.registry_handler import RegistryHandler
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata


class HibernationTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.registry_path = os.path.join(os.getenv('APPDATA', os.path.expanduser("~")), "ASX-Hub",
                                          "ParameterFunction")  # Пример пути
        self.value_name = "Hibernation"
        self.log_file = self.setup_log_file()

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Гибернация",
            description="Включает/отключает режим гибернации в системе",
            category="Оптимизация и настройки"
        )

    def check_status(self) -> bool:
        if platform.system() != "Windows":
            return False
        # Check registry key for custom override.  If it exists, hibernation is considered OFF.
        custom_setting = self.reg.get_registry_value(self.registry_path, self.value_name)
        if custom_setting is not None:
            return False  # Custom setting overrides, Hibernation considered OFF

        # If no custom setting, check actual powercfg setting.
        try:
            result = subprocess.run(['powercfg', '/a'], capture_output=True, text=True, check=True)
            # Check if hibernation is available.  The presence of "Гибернация" in the output indicates it's enabled.
            return "Гибернация" in result.stdout or "Hibernation" in result.stdout
        except subprocess.CalledProcessError:
            return False  # Assume off if powercfg /a fails.

    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if not current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        try:
            # Delete the registry override.
            self.reg.delete_registry_value(self.registry_path, self.value_name)
            subprocess.run(['powercfg', '/hibernate', 'on'], check=True)
            self.log_action("enable", "Enabled", True)
            return True
        except (subprocess.CalledProcessError, OSError) as e:
            self.log_action("enable", "Enabled", False)
            print(f"Error enabling hibernation: {e}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def disable(self) -> bool:
        try:
            #  Set a registry key to indicate hibernation is overridden.
            self.reg.set_registry_value(self.registry_path, self.value_name, 1, "REG_DWORD")
            subprocess.run(['powercfg', '/hibernate', 'off'], check=True)
            self.log_action("disable", "Disabled", True)
            return True
        except (subprocess.CalledProcessError, OSError) as e:
            self.log_action("disable", "Disabled", False)
            print(f"Error disabling hibernation: {e}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "hibernation_log.txt")
        return log_file

    def log_action(self, action, state, success):
        """Logs actions to the log file."""
        try:
            with open(self.log_file, "a") as f:
                timestamp = self.get_timestamp()
                log_message = f"[{timestamp}] Action: {action}, State: {state}, Success: {success}\n"
                f.write(log_message)
                print(log_message)
        except Exception as e:
            print(f"Error writing to log file: {e}")

    def get_timestamp(self):
        """Gets the current timestamp formatted for logging."""
        import datetime
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")