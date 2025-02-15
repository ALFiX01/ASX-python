from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class TweakMetadata:
    def __init__(self, title, description, category, warning=None):  # Добавили warning=None
        self.title = title
        self.description = description
        self.category = category
        self.warning = warning  # Добавили атрибут warning

class BaseTweak(ABC):
    @property
    @abstractmethod
    def metadata(self) -> TweakMetadata:
        """Get tweak metadata"""
        pass

    @abstractmethod
    def check_status(self) -> bool:
        """Check current status of the tweak"""
        pass

    @abstractmethod
    def toggle(self) -> bool:
        """Toggle the tweak state"""
        pass

    @abstractmethod
    def enable(self) -> bool:
        """Enable the tweak"""
        pass

    @abstractmethod
    def disable(self) -> bool:
        """Disable the tweak"""
        pass
