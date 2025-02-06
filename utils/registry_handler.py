import os
import platform

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
            import winreg
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
            import winreg
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ)
            value, value_type = winreg.QueryValueEx(reg_key, value_name)
            winreg.CloseKey(reg_key)
            return value
        except Exception as e:
            print(f"Error getting registry value: {str(e)}")
            return None

    @staticmethod
    def delete_registry_value(key_path, value_name):
        """Delete a registry value"""
        if not RegistryHandler.is_windows():
            print(f"Registry operation not supported on {platform.system()}")
            return False

        try:
            import winreg
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
            winreg.DeleteValue(reg_key, value_name)
            winreg.CloseKey(reg_key)
            return True
        except Exception as e:
            print(f"Error deleting registry value: {str(e)}")
            return False