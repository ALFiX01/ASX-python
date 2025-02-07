import os
import platform
import win32api

# Import winreg only on Windows
if platform.system() == "Windows":
    import winreg
    from win32api import GetLastError, FormatMessage

class RegistryHandler:
    @staticmethod
    def is_windows():
        return platform.system() == "Windows"

    @staticmethod
    def set_registry_value(key_path, value_name, value_data, value_type=None):
        """Set a registry value"""
        if not RegistryHandler.is_windows():
            print(f"Registry operation not supported on {platform.system()}")
            return False

        try:
            if platform.system() == "Windows":
                reg_key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
                winreg.SetValueEx(reg_key, value_name, 0, value_type or winreg.REG_DWORD, value_data)
                winreg.CloseKey(reg_key)
            return True
        except Exception as e:
            print(f"Error setting registry value: {str(e)}")
            return False

    @staticmethod
    def get_registry_value(key_path, value_name):
        """Get a registry value"""
        if not RegistryHandler.is_windows():
            print(f"Registry operation not supported on {platform.system()}")
            return None

        try:
            # Handle HKEY_LOCAL_MACHINE and HKEY_CURRENT_USER paths
            if key_path.startswith("HKLM\\"):
                hkey = winreg.HKEY_LOCAL_MACHINE
                key_path = key_path[5:]
            elif key_path.startswith("HKEY_LOCAL_MACHINE\\"):
                hkey = winreg.HKEY_LOCAL_MACHINE
                key_path = key_path[19:]
            elif key_path.startswith("HKEY_CURRENT_USER\\"):
                hkey = winreg.HKEY_CURRENT_USER
                key_path = key_path[18:]
            else:
                hkey = winreg.HKEY_LOCAL_MACHINE

            key = winreg.OpenKey(hkey, key_path, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            return value
        except WindowsError as e:
            print(f"Error reading registry value {key_path}\\{value_name}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error reading registry: {e}")
            return None

    @staticmethod
    def delete_registry_value(key_path, value_name):
        """Delete a registry value"""
        if not RegistryHandler.is_windows():
            print(f"Registry operation not supported on {platform.system()}")
            return False

        try:
            if platform.system() == "Windows":
                reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
                winreg.DeleteValue(reg_key, value_name)
                winreg.CloseKey(reg_key)
            return True
        except Exception as e:
            print(f"Error deleting registry value: {str(e)}")
            return False