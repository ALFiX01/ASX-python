# Application configuration

# GitHub API configuration
GITHUB_API_URL = "https://api.github.com"
GITHUB_DOWNLOAD_FOLDER = "downloads"

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
