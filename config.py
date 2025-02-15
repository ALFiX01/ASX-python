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
APP_VERSION = "0.0.10"

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
    {
        'key': 'hibernation',
        'class_name': 'HibernationTweak',
        'module': 'hibernation',
        'category': "Оптимизация и настройки",
    },
    {
        'key': 'indexing',
        'class_name': 'IndexingTweak',
        'module': 'indexing',
        'category': "Оптимизация и настройки",
    },
    {
        'key': 'windows_defender',
        'class_name': 'WindowsDefenderTweak',
        'module': 'windows_defender',
        'category': "Оптимизация и настройки",
    },
    {
        'key': 'onedrive',
        'class_name': 'OneDriveTweak',
        'module': 'onedrive',
        'category': "Оптимизация и настройки",
    },
    {
        'key': 'wallpaper_compression',
        'class_name': 'WallpaperCompressionTweak',
        'module': 'wallpaper_compression',
        'category': "Кастомизация",
    },
    {
        'key': 'sticky_keys',
        'class_name': 'StickyKeysTweak',
        'module': 'sticky_keys',
        'category': "Оптимизация и настройки",
    },
    {
        'key': 'mouse_acceleration',
        'class_name': 'MouseAccelerationTweak',
        'module': 'mouse_acceleration',
        'category': "Оптимизация и настройки",
    },
    {
        'key': 'security_center_notifications',
        'class_name': 'SecurityCenterNotificationsTweak',
        'module': 'security_center_notifications',
        'category': "Оптимизация и настройки",
    },
    {
        'key': 'app_start_notify',
        'class_name': 'AppStartNotifyTweak',
        'module': 'app_start_notify',
        'category': "Оптимизация и настройки",  # Или "Безопасность"
    },
    {
        'key': 'prioritize_gaming_tasks',
        'class_name': 'PrioritizeGamingTasksTweak',
        'module': 'prioritize_gaming_tasks',
        'category': "Оптимизация и настройки",
    },
    {
        'key': 'uac',
        'class_name': 'UACTweak',
        'module': 'uac',
        'category': "Оптимизация и настройки",
    },
    {
        'key': 'hw_sch_mode',
        'class_name': 'HwSchModeTweak',
        'module': 'hw_sch_mode',
        'category': "Оптимизация и настройки",
    },
    {
        'key': 'widgets_uninstall',
        'class_name': 'WidgetsUninstallTweak',
        'module': 'widgets_uninstall',
        'category': "Оптимизация и настройки",
    },
    {
        'key': 'clipboard_history',
        'class_name': 'ClipboardHistoryTweak',
        'module': 'clipboard_history',
        'category': "Оптимизация и настройки",
    },
    {
        'key': 'core_isolation',
        'class_name': 'CoreIsolationTweak',
        'module': 'core_isolation',
        'category': "Оптимизация и настройки",
    },
    {
        'key': 'auto_update_maps',
        'class_name': 'AutoUpdateMapsTweak',
        'module': 'auto_update_maps',
        'category': "Оптимизация и настройки",
    },
    {
        'key': 'auto_store_apps',
        'class_name': 'AutoStoreAppsTweak',
        'module': 'auto_store_apps',
        'category': "Оптимизация и настройки",
    },
    {
        'key': 'background_task_edge_browser',
        'class_name': 'BackgroundTaskEdgeBrowserTweak',
        'module': 'background_task_edge_browser',
        'category': "Оптимизация и настройки",
    },
    {
        'key': 'win_ad',
        'class_name': 'WinAdTweak',
        'module': 'win_ad',
        'category': "Конфиденциальность",
    },
    {
        'key': 'windows_sync',
        'class_name': 'WindowsSyncTweak',
        'module': 'windows_sync',
        'category': "Конфиденциальность",
    },
    {
        'key': 'windows_telemetry',
        'class_name': 'WindowsTelemetryTweak',
        'module': 'windows_telemetry',
        'category': "Конфиденциальность",
    },
    {
        'key': 'nvidia_telemetry',
        'class_name': 'NvidiaTelemetryTweak',
        'module': 'nvidia_telemetry',
        'category': "Конфиденциальность",
    },
    {
        'key': 'installed_app_data',
        'class_name': 'InstalledAppDataTweak',
        'module': 'installed_app_data',
        'category': "Конфиденциальность",
    },
    {
        'key': 'app_usage_stats',
        'class_name': 'AppUsageStatsTweak',
        'module': 'app_usage_stats',
        'category': "Конфиденциальность",
    },
    {
        'key': 'handwriting_data',
        'class_name': 'HandwritingDataTweak',
        'module': 'handwriting_data',
        'category': "Конфиденциальность",
    },
    {
        'key': 'data_domains',
        'class_name': 'DataDomainsTweak',
        'module': 'data_domains',
        'category': "Конфиденциальность",  # Или "Безопасность"
    },
    {
        'key': 'user_behavior_logging',
        'class_name': 'UserBehaviorLoggingTweak',
        'module': 'user_behavior_logging',
        'category': "Конфиденциальность",
    },
    {
        'key': 'location_tracking',
        'class_name': 'LocationTrackingTweak',
        'module': 'location_tracking',
        'category': "Конфиденциальность",
    },
    {
        'key': 'feedback_check',
        'class_name': 'FeedbackCheckTweak',
        'module': 'feedback_check',
        'category': "Конфиденциальность",
    },
    {
        'key': 'background_speech_synthesis',
        'class_name': 'BackgroundSpeechSynthesisTweak',
        'module': 'background_speech_synthesis',
        'category': "Конфиденциальность",
    },
    {
        'key': 'system_monitoring',
        'class_name': 'SystemMonitoringTweak',
        'module': 'system_monitoring',
        'category': "Конфиденциальность",  # Или "Конфиденциальность"
    },
    {
        'key': 'remote_pc_experiments',
        'class_name': 'RemotePCExperimentsTweak',
        'module': 'remote_pc_experiments',
        'category': "Конфиденциальность",
    },
    {
        'key': 'microsoft_spy_modules',
        'class_name': 'MicrosoftSpyModulesTweak',
        'module': 'microsoft_spy_modules',
        'category': "Конфиденциальность",
    },
    {
        'key': 'windows_event_logging',
        'class_name': 'WindowsEventLoggingTweak',
        'module': 'windows_event_logging',
        'category': "Оптимизация и настройки",  # Или "Конфиденциальность"
    },
    {
        'key': 'app_start_tracking',
        'class_name': 'AppStartTrackingTweak',
        'module': 'app_start_tracking',
        'category': "Конфиденциальность",
    },
    {
        'key': 'app_settings_sync',
        'class_name': 'AppSettingsSyncTweak',
        'module': 'app_settings_sync',
        'category': "Конфиденциальность",
    },
    {
        'key': 'explorer_blur',
        'class_name': 'ExplorerBlurTweak',
        'module': 'explorer_blur',
        'category': "Кастомизация",  # Или другая категория
    },
    {
        'key': 'show_file_extensions',
        'class_name': 'ShowFileExtensionsTweak',
        'module': 'show_file_extensions',
        'category': "Кастомизация",
    },
    {
        'key': 'gallery_explorer',
        'class_name': 'GalleryExplorerTweak',
        'module': 'gallery_explorer',
        'category': "Кастомизация",
    },
    {
        'key': 'home_explorer',
        'class_name': 'HomeExplorerTweak',
        'module': 'home_explorer',
        'category': "Кастомизация",
    },
    {
        'key': 'network_explorer',
        'class_name': 'NetworkExplorerTweak',
        'module': 'network_explorer',
        'category': "Кастомизация",
    },
    {
        'key': 'taskbar_date',
        'class_name': 'TaskbarDateTweak',
        'module': 'taskbar_date',
        'category': "Кастомизация",
    },
    {
        'key': 'icon_arrow_on_shortcut',
        'class_name': 'IconArrowOnShortcutTweak',
        'module': 'icon_arrow_on_shortcut',
        'category': "Кастомизация",
    },
    {
        'key': 'service_pcasvc',
        'class_name': 'PcaSvcServiceTweak',
        'module': 'services_pcasvc',
        'category': "Службы",
    },
    {
        'key': 'service_wecsvc',
        'class_name': 'WecsvcServiceTweak',
        'module': 'services_wecsvc',
        'category': "Службы",
    },
    {
        'key': 'service_wbiosrvc',
        'class_name': 'WbioSrvcServiceTweak',
        'module': 'services_wbiosrvc',
        'category': "Службы",
    },
    {
        'key': 'service_stisvc',
        'class_name': 'StisvcServiceTweak',
        'module': 'services_stisvc',
        'category': "Службы",
    },
    {
        'key': 'service_wsearch',
        'class_name': 'WSearchServiceTweak',
        'module': 'services_wsearch',
        'category': "Службы",
    },
    {
        'key': 'service_mapsbroker',
        'class_name': 'MapsBrokerServiceTweak',
        'module': 'services_mapsbroker',
        'category': "Службы",
    },
    {
        'key': 'service_sensorservice',
        'class_name': 'SensorServicesTweak',
        'module': 'services_sensorservice',
        'category': "Службы",
    },
    {
        'key': 'service_hyperv',
        'class_name': 'HyperVServicesTweak',
        'module': 'services_hyperv',
        'category': "Службы",
    },
    {
        'key': 'service_xblgamesave',
        'class_name': 'XblGameSaveServicesTweak',
        'module': 'services_xblgamesave',
        'category': "Службы",
    },
{
        'key': 'services_printer',
        'class_name': 'PrinterServicesTweak',
        'module': 'services_printer',
        'category': "Службы",
    },
{
        'key': 'service_sysmain',
        'class_name': 'SysMainServiceTweak',
        'module': 'service_sysmain',  # Изменен module
        'category': "Службы",
    },
{
        'key': 'service_wisvc',
        'class_name': 'WisvcServiceTweak',
        'module': 'service_wisvc',
        'category': "Службы",
    },
{
        'key': 'service_diagnostics',
        'class_name': 'DiagnosticsServicesTweak',
        'module': 'service_diagnostics',
        'category': "Службы",
    },
]