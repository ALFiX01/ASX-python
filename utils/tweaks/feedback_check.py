import os
import winreg
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata
from utils.registry_handler import RegistryHandler


class FeedbackCheckTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.log_file = self.setup_log_file()

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Проверка обратной связи",
            description="Включает/отключает проверку обращений через Центр обратной связи Windows",
            category="Конфиденциальность"
        )

    def check_status(self) -> bool:
        """
        Проверяет, *отключена* ли проверка обратной связи.
        Считаем, что проверка отключена, если DoNotShowFeedbackNotifications равен 1.
        Если значение равно 0 или ключ отсутствует, считаем, что проверка включена (по умолчанию).
        """
        try:
            do_not_show = self.reg.get_registry_value(
                r"HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection",
                "DoNotShowFeedbackNotifications"
            )
            # Если значение 1 - проверка отключена, если 0 - включена.
            status = (do_not_show == 0)
            self.log_action("check_status", f"Feedback Check {'Disabled' if status else 'Enabled'}", True)
            return status  # True, если проверка *отключена*
        except FileNotFoundError:
            # Если ключ отсутствует, считаем, что проверка включена по умолчанию.
            self.log_action("check_status", "DoNotShowFeedbackNotifications key not found, assuming enabled", True)
            return False  # Проверка включена (False)
        except Exception as e:
            self.log_action("check_status", f"Error checking status: {e}", False)
            print(f"Error checking Feedback Check status: {e}")
            return False

    def toggle(self) -> bool:
        """
        Переключает состояние проверки обратной связи:
        если она отключена (DoNotShowFeedbackNotifications = 1), то включает (установив 0),
        если включена (0), то отключает (установив 1).
        """
        current_status = self.check_status()
        # Если текущий статус True (отключена), то включаем; если False (включена) - отключаем.
        result = self.enable() if current_status else self.disable()
        self.log_action("toggle", "Enabled" if current_status else "Disabled", result)
        return result

    def enable(self) -> bool:
        """Включает проверку обращений (разрешает показ уведомлений)."""
        try:
            self._set_registry_values(enabled=False)
            self.log_action("enable", "Enabled", True)
            return True
        except Exception as e:
            self.log_action("enable", "Failed to enable", False)
            print(f"Error enabling Feedback Check: {e}")
            return False

    def disable(self) -> bool:
        """Отключает проверку обращений (запрещает показ уведомлений)."""
        try:
            self._set_registry_values(enabled=True)
            self.log_action("disable", "Disabled", True)
            return True
        except Exception as e:
            self.log_action("disable", "Failed to disable", False)
            print(f"Error disabling Feedback Check: {e}")
            return False

    def _set_registry_values(self, enabled: bool):
        """Устанавливает необходимые значения реестра.

        Параметры:
            enabled (bool): Если True, включаем проверку (DoNotShowFeedbackNotifications = 0);
                            если False, отключаем (DoNotShowFeedbackNotifications = 1).
        """
        # Для NumberOfSIUFInPeriod и PeriodInNanoSeconds всегда устанавливаем 0.
        self.reg.set_registry_value(
            r"HKCU\Software\Microsoft\Siuf\Rules",
            "NumberOfSIUFInPeriod",
            0,
            winreg.REG_DWORD
        )
        self.reg.set_registry_value(
            r"HKCU\Software\Microsoft\Siuf\Rules",
            "PeriodInNanoSeconds",
            0,
            winreg.REG_DWORD
        )

        # DoNotShowFeedbackNotifications: 0 - проверка включена, 1 - проверка отключена.
        do_not_show_value = 0 if enabled else 1
        self.reg.set_registry_value(
            r"HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection",
            "DoNotShowFeedbackNotifications",
            do_not_show_value,
            winreg.REG_DWORD
        )

    def setup_log_file(self):
        """Настраивает путь к лог-файлу, создавая необходимые директории."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "feedback_check_log.txt")
        return log_file

    def log_action(self, action, state, success):
        """Логирует действия в лог-файл."""
        try:
            with open(self.log_file, "a") as f:
                timestamp = self.get_timestamp()
                log_message = f"[{timestamp}] Action: {action}, State: {state}, Success: {success}\n"
                f.write(log_message)
                print(log_message)
        except Exception as e:
            print(f"Error writing to log file: {e}")

    def get_timestamp(self):
        """Возвращает текущую метку времени для логирования."""
        import datetime
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")
