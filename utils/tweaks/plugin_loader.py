import os
import importlib
import inspect
from typing import Dict, Type, List
from utils.tweaks.base_tweak import BaseTweak

class TweakPluginLoader:
    @staticmethod
    def load_tweaks() -> Dict[str, Type[BaseTweak]]:
        tweaks = {}
        tweaks_dir = os.path.dirname(os.path.abspath(__file__))
        
        for filename in os.listdir(tweaks_dir):
            if filename.endswith('.py') and filename not in ['__init__.py', 'base_tweak.py', 'plugin_loader.py']:
                module_name = filename[:-3]
                module = importlib.import_module(f'utils.tweaks.{module_name}')
                
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and issubclass(obj, BaseTweak) 
                        and obj != BaseTweak):
                        tweaks[name] = obj
        
        return tweaks

    @staticmethod
    def get_categories(tweaks: Dict[str, Type[BaseTweak]]) -> List[str]:
        categories = set()
        for tweak_class in tweaks.values():
            categories.add(tweak_class().metadata.category)
        return sorted(list(categories))
