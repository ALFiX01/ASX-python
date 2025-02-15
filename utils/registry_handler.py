import os
import platform
import winreg
from typing import Optional, Any, Tuple

class RegistryHandler:
    def __init__(self):
        self.hkey_map = {
            'HKEY_LOCAL_MACHINE': winreg.HKEY_LOCAL_MACHINE,
            'HKLM': winreg.HKEY_LOCAL_MACHINE,
            'HKEY_CURRENT_USER': winreg.HKEY_CURRENT_USER,
            'HKCU': winreg.HKEY_CURRENT_USER
        }

    def _parse_key_path(self, key_path: str) -> Tuple[Any, str]:
        """Parse registry path and return hkey and subpath"""
        parts = key_path.split('\\', 1)

        if len(parts) == 1:
            return winreg.HKEY_LOCAL_MACHINE, key_path

        hkey_str = parts[0].upper()
        hkey = self.hkey_map.get(hkey_str, winreg.HKEY_LOCAL_MACHINE)

        return hkey, parts[1] if len(parts) > 1 else ""

    def set_registry_value(self, key_path: str, value_name: str, value_data: Any,
                           value_type: int = winreg.REG_DWORD) -> bool:
        """Set registry value with better error handling"""
        if platform.system() != "Windows":
            return False

        try:
            hkey, subpath = self._parse_key_path(key_path)

            try:
                key = winreg.CreateKeyEx(hkey, subpath, 0, winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY)
            except Exception:
                return False

            try:
                winreg.SetValueEx(key, value_name, 0, value_type, value_data)
                return True
            except Exception:
                return False
            finally:
                winreg.CloseKey(key)

        except Exception:
            return False

    def get_registry_value(self, key_path: str, value_name: str) -> Optional[Any]:
        """Get registry value with better error handling"""
        if platform.system() != "Windows":
            return None

        try:
            hkey, subpath = self._parse_key_path(key_path)

            try:
                key = winreg.OpenKey(hkey, subpath, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
            except FileNotFoundError:
                return None
            except Exception:
                return None

            try:
                value, _ = winreg.QueryValueEx(key, value_name)
                return value
            except FileNotFoundError:
                return None
            except Exception:
                return None
            finally:
                winreg.CloseKey(key)

        except Exception:
            return None

    def delete_registry_value(self, key_path: str, value_name: str, ignore_not_found: bool = False) -> bool:
        """Delete registry value with better error handling and ignore_not_found option."""
        if platform.system() != "Windows":
            return False

        try:
            hkey, subpath = self._parse_key_path(key_path)

            try:
                key = winreg.OpenKey(hkey, subpath, 0, winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY)
            except FileNotFoundError:
                if ignore_not_found:
                    return True  # Ключ не найден, но мы игнорируем
                else:
                    return False
            except Exception:
                return False

            try:
                winreg.DeleteValue(key, value_name)
                return True
            except FileNotFoundError:
                if ignore_not_found:
                    return True  # Значение не найдено, но мы игнорируем
                else:
                    return False
            except Exception:
                return False
            finally:
                winreg.CloseKey(key)

        except Exception:
            return False

    def delete_registry_key(self, key_path: str, ignore_not_found: bool = False) -> bool:
        """
        Удаляет ключ реестра.

        Args:
            key_path: Полный путь к удаляемому ключу.
            ignore_not_found: Если True, не вызывает исключение, если ключ не найден.
        """
        if platform.system() != "Windows":
            return False

        try:
            hkey, subpath = self._parse_key_path(key_path)
            # Разделяем подключ на родительский ключ и имя подключа
            parent_path, subkey_name = os.path.split(subpath)

            try:
                # Открываем родительский ключ с правами KEY_ALL_ACCESS (запись + чтение)
                parent_key = winreg.OpenKey(hkey, parent_path, 0, winreg.KEY_ALL_ACCESS | winreg.KEY_WOW64_64KEY)
            except FileNotFoundError:
                if ignore_not_found:
                    return True  # Родительский ключ не найден, но мы игнорируем
                else:
                    return False
            except Exception:
                return False

            try:
                winreg.DeleteKey(parent_key, subkey_name)
                return True  # Успешно удалили
            except FileNotFoundError:
                if ignore_not_found:
                    return True  # Подключ не найден, но мы игнорируем
                else:
                    return False
            except Exception:
                return False  # Другая ошибка при удалении
            finally:
                winreg.CloseKey(parent_key)  # Закрываем родительский ключ

        except Exception:
            return False
