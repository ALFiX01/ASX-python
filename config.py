# Application configuration
from utils.tweaks.fso_gamebar import FsoGameBarTweak
from utils.tweaks.hdcp import HdcpTweak
from utils.tweaks.nvidia_optimization import NvidiaOptimizationTweak
from utils.tweaks.power_throttling import PowerThrottlingTweak
from utils.tweaks.powerplan import PowerPlanTweak
from utils.tweaks.spectre_meltdown import SpectreMeltdownTweak

# GitHub API configuration
GITHUB_API_URL = "https://api.github.com"
GITHUB_DOWNLOAD_FOLDER = "downloads"

# App Ver
APP_VERSION = "0.0.05"

# Registry paths
REGISTRY_PATHS = {
    "services": r"SYSTEM\CurrentControlSet\Services",
    "context_menu": r"SOFTWARE\Classes\*\shell",
    "startup": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
}

# Tweak categories
TWEAK_CATEGORIES = [
    "Оптимизация и настройки",
    "Конфиденциальность",
    "Контекстное меню",
    "Кастомизация",
    "Службы",
    "Экспериментальные",
    "Исправление проблем"
]

# Program sources
PROGRAM_SOURCES = {
    "browsers": {
        "Chrome": "https://github.com/...",
        "Firefox": "https://github.com/..."
    },
    "utilities": {
        "7-Zip": "https://github.com/...",
        "VLC": "https://github.com/..."
    }
}

# --- Tweak Definitions (Refactored) ---
#  - Use 'class_name' to specify the class (as a string).
#  - Use 'module' to specify the module (optional, for brevity).
TWEAKS = [
    {
        'key': 'power_plan',
        'class_name': 'PowerPlanTweak',  # No specific class
        'module':'powerplan',
        'category': "Оптимизация и настройки",
    },
    {
        'key': 'FsoGameBar',
        'class_name': 'FsoGameBarTweak',
        'module':'fso_gamebar',
        'category': "Оптимизация и настройки",
    },
    {
        'key': 'spectre_meltdown',
        'class_name': 'SpectreMeltdownTweak',
        'module': 'spectre_meltdown',
        'category': "Оптимизация и настройки",
    },
    {
        'key': 'nvidia_optimization',
        'class_name': 'NvidiaOptimizationTweak',
        'module': 'nvidia_optimization',
        'category': "Оптимизация и настройки",
    },
    {
        'key': 'hdcp',
        'class_name': 'HdcpTweak',
        'module': 'hdcp',
        'category': "Оптимизация и настройки",
    },
    {
        'key': 'power_throttling',
        'class_name': 'PowerThrottlingTweak',
        'module': 'power_throttling',
        'category': "Оптимизация и настройки",
    },
    {
        'key': 'uwp_background',
        'class_name': 'UWPBackgroundTweak',
        'module': 'uwp_background',
        'category': "Оптимизация и настройки",
    },
    {
        'key': 'notifications',
        'class_name': 'NotificationsTweak',  # Class name as a string
        'module': 'notifications',  # Module name (optional, for brevity)
        'category': "Оптимизация и настройки",
    },
    {
        'key': 'cortana',
        'class_name': 'CortanaTweak',
        'module': 'cortana',
        'category': "Оптимизация и настройки",
    },
    {
        'key': 'fastboot',
        'class_name': 'FastBootTweak',
        'module': 'fastboot',
        'category': "Оптимизация и настройки",
    },
]