
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

    def set_registry_value(self, key_path: str, value_name: str, value_data: Any, value_type: int = winreg.REG_DWORD) -> bool:
        """Set registry value with better error handling"""
        if platform.system() != "Windows":
            return False

        try:
            hkey, subpath = self._parse_key_path(key_path)
            
            try:
                key = winreg.CreateKeyEx(hkey, subpath, 0, winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY)
            except Exception as e:
                print(f"Failed to create/open key {key_path}: {str(e)}")
                return False

            try:
                winreg.SetValueEx(key, value_name, 0, value_type, value_data)
                return True
            except Exception as e:
                print(f"Failed to set value {value_name}: {str(e)}")
                return False
            finally:
                winreg.CloseKey(key)
                
        except Exception as e:
            print(f"Registry operation failed: {str(e)}")
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
            except Exception as e:
                print(f"Failed to open key {key_path}: {str(e)}")
                return None

            try:
                value, _ = winreg.QueryValueEx(key, value_name)
                return value
            except FileNotFoundError:
                return None
            except Exception as e:
                print(f"Failed to query value {value_name}: {str(e)}")
                return None
            finally:
                winreg.CloseKey(key)
                
        except Exception as e:
            print(f"Registry operation failed: {str(e)}")
            return None

    def delete_registry_value(self, key_path: str, value_name: str) -> bool:
        """Delete registry value with better error handling"""
        if platform.system() != "Windows":
            return False

        try:
            hkey, subpath = self._parse_key_path(key_path)
            
            try:
                key = winreg.OpenKey(hkey, subpath, 0, winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY)
            except Exception as e:
                print(f"Failed to open key {key_path}: {str(e)}")
                return False

            try:
                winreg.DeleteValue(key, value_name)
                return True
            except FileNotFoundError:
                return True  # Consider it success if value doesn't exist
            except Exception as e:
                print(f"Failed to delete value {value_name}: {str(e)}")
                return False
            finally:
                winreg.CloseKey(key)
                
        except Exception as e:
            print(f"Registry operation failed: {str(e)}")
            return False
