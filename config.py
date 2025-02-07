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

# Определение твиков
TWEAKS = [
    {
        'title': "План электропитания ASX Hub",
        'description': "Оптимизированный план электропитания для максимальной производительности.\nУменьшает задержки и увеличивает FPS в играх.",
        'toggle_command': None,
        'check_status_func': None,
        'switch_ref': None
    },
    {
        'title': "FSO и GameBar",
        'description': "Оптимизация игровых настроек Windows для лучшей производительности.\nОтключает ненужные визуальные эффекты и игровую панель Windows.",
        'toggle_command': None,
        'check_status_func': None,
        'switch_ref': None
    },
    {
        'title': "Spectre, Meltdown, DownFall Mitigations",
        'description': "Отключение аппаратных средств устранения уязвимостей Spectre, Meltdown и DownFall.\nМожет повысить производительность, но снижает безопасность.",
        'toggle_command': None,
        'check_status_func': None,
        'switch_ref': None
    },
    {
        'title': "Оптимизация настроек Nvidia",
        'description': "Применение рекомендуемых настроек Nvidia для повышения производительности и снижения задержек.",
        'toggle_command': None,
        'check_status_func': None,
        'switch_ref': None
    },
    {
        'title': "HDCP",
        'description': "HDCP (High-bandwidth Digital Content Protection).\nМожет решить проблемы совместимости с некоторыми мониторами и устройствами захвата.",
        'toggle_command': None,
        'check_status_func': None,
        'switch_ref': None
    },
    {
        'title': "Отключить Power Throttling",
        'description': "Отключает Power Throttling, функцию Windows, снижающую производительность приложений в фоновом режиме.",
        'toggle_command': None,
        'check_status_func': None,
        'switch_ref': None
    },
    {
        'title': "Работа UWP программ в фоне",
        'description': "Запрещает UWP (Universal Windows Platform) приложениям работать в фоновом режиме.\nМожет снизить использование ресурсов системы.",
        'toggle_command': None,
        'check_status_func': None,
        'switch_ref': None
    },
    {
        'title': "Уведомления",
        'description': "Отключает уведомления Windows.\nУменьшает отвлекающие факторы и повышает концентрацию.",
        'toggle_command': None,
        'check_status_func': None,
        'switch_ref': None
    },
    {
        'title': "Cortana",
        'description': "Отключает Cortana, голосового ассистента Windows.\nОсвобождает системные ресурсы и повышает конфиденциальность.",
        'toggle_command': None,
        'check_status_func': None,
        'switch_ref': None
    },
    # Добавьте другие твики сюда в виде словарей
]
