import platform
import os
import subprocess
import requests
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata


class PowerPlanTweak(BaseTweak):
    ASX_POWER_PLAN_GUID = "44444444-4444-4444-4444-444444444449"  # Replace with YOUR GUID
    DEFAULT_POWER_PLANS = [
        "381b4222-f694-41f0-9685-ff5bb260df2e",  # Balanced
        "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",  # High performance
        "a1841308-3541-4fab-bc81-f71556f20b4a",  # Power saver
    ]

    def __init__(self):
        self.log_file = self.setup_log_file()

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="План электропитания ASX Hub",
            description="Оптимизированный план электропитания",
            category="Оптимизация и настройки"
        )

    def check_status(self) -> bool:
        """Checks if the ASX power plan is active."""
        if platform.system() != "Windows":
            return False
        try:
            result = subprocess.run(['powercfg', '/getactivescheme'], capture_output=True, text=True, shell=True)
            result.check_returncode()
            # Extract GUID from the output string.  More robust.
            output = result.stdout
            guid_start = output.find(":") + 2  # Find the colon and add 2 (space and start of GUID)
            guid_end = guid_start + 36       # GUIDs are 36 characters long
            active_guid = output[guid_start:guid_end].lower()
            return active_guid == self.ASX_POWER_PLAN_GUID.lower()

        except (subprocess.CalledProcessError, FileNotFoundError, IndexError) as e:
            print(f"Error checking power plan status: {e}")
            self.log_action("check_status", "N/A", False)
            return False

    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if not current_status else "Enabled", result)
        return result


    def enable(self) -> bool:
        if platform.system() != "Windows":
            print("Power plan optimization is only available on Windows")
            return False

        try:
            subprocess.run(['powercfg', '-restoredefaultschemes'], check=True)
            subprocess.run(['powercfg', '/d', self.ASX_POWER_PLAN_GUID], capture_output=True)

            download_url = "https://github.com/ALFiX01/ASX-Hub/releases/download/File/ASX.Hub-Power.pow"
            temp_pow_file = os.path.join(os.environ['TEMP'], "ASX.Hub-Power.pow")

            try:
                response = requests.get(download_url, stream=True)
                response.raise_for_status()
                with open(temp_pow_file, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
            except requests.exceptions.RequestException as e:
                print(f"Error downloading power plan file: {e}")
                self.log_action("enable", "N/A", False)
                return False

            if os.path.exists(temp_pow_file):
                subprocess.run(['powercfg', '-import', temp_pow_file, self.ASX_POWER_PLAN_GUID], check=True)
                subprocess.run(['powercfg', '-SETACTIVE', self.ASX_POWER_PLAN_GUID], check=True)
                subprocess.run(['powercfg', '/changename', self.ASX_POWER_PLAN_GUID,
                              "ASX Hub-Power", "Больше FPS и меньше задержки."], check=True)
                for guid in self.DEFAULT_POWER_PLANS:
                    subprocess.run(['powercfg', '/d', guid], capture_output=True)

                self.log_action("enable", "Enabled", True)
                return True
            else:
                print(f"Power plan file not found after download: {temp_pow_file}")
                self.log_action("enable", "N/A", False)
                return False

        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error optimizing power plan: {e}")
            self.log_action("enable", "N/A", False)
            return False

    def disable(self) -> bool:
        if platform.system() != "Windows":
            return False

        try:
            subprocess.run(['powercfg', '-restoredefaultschemes'], check=True)
            self.log_action("disable", "Disabled", True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error restoring default power plans: {e}")
            self.log_action("disable", "N/A", False)
            return False

    def setup_log_file(self):
        """Sets up the log file."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "power_plan_log.txt")
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