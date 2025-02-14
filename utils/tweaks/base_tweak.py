from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class TweakMetadata:
    title: str
    description: str
    category: str
    russian_name: str = ""  # Russian name for status bar

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
