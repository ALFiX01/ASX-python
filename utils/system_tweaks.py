import os
import platform
import subprocess
import zipfile
import requests  # Добавляем импорт библиотеки requests для скачивания файлов
from utils.registry_handler import RegistryHandler

# Import winreg only on Windows
if platform.system() == "Windows":
    import winreg

class SystemTweaks:
    # GUID для плана электропитания ASX Hub
    ASX_POWER_PLAN_GUID = "44444444-4444-4444-4444-444444444449"

    # Список GUID стандартных планов электропитания
    DEFAULT_POWER_PLANS = [
        "381b4222-f694-41f0-9685-ff5bb260df2e",  # Сбалансированный
        "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",  # Высокая производительность
        "a1841308-3541-4fab-bc81-f71556f20b4a",  # Экономия энергии
        "a9758bf0-cfc6-439c-a392-7783990ff716"   # Максимальная производительность
    ]

    @staticmethod
    def is_windows():
        return platform.system() == "Windows"

    # === Power Plan ===
    @staticmethod
    def check_powerplan():
        from utils.tweaks.powerplan import PowerPlanTweak
        tweak = PowerPlanTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_powerplan():
        from utils.tweaks.powerplan import PowerPlanTweak
        tweak = PowerPlanTweak()
        return tweak.toggle()


    # === Fso и GameBar ===
    @staticmethod
    def check_FsoGameBar():
        from utils.tweaks.fso_gamebar import FsoGameBarTweak
        tweak = FsoGameBarTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_FsoGameBar():
        from utils.tweaks.fso_gamebar import FsoGameBarTweak
        tweak = FsoGameBarTweak()
        return tweak.toggle()


    @staticmethod
    def disable_services(service_name):
        """Disable a Windows service"""
        if not SystemTweaks.is_windows():
            print("Service control is only available on Windows")
            return False

        try:
            subprocess.run(['sc', 'config', service_name, 'start=disabled'])
            subprocess.run(['sc', 'stop', service_name])
            return True
        except Exception:
            return False

    # === Spectre, Meltdown, DownFall Mitigations ===
    @staticmethod
    def check_spectre_meltdown_status():
        from utils.tweaks.spectre_meltdown import SpectreMeltdownTweak
        tweak = SpectreMeltdownTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_spectre_meltdown():
        from utils.tweaks.spectre_meltdown import SpectreMeltdownTweak
        tweak = SpectreMeltdownTweak()
        return tweak.toggle()


    # === Оптимизация настроек Nvidia ===
    @staticmethod
    def check_nvidia_optimization_status():
        from utils.tweaks.nvidia_optimization import NvidiaOptimizationTweak
        tweak = NvidiaOptimizationTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_nvidia_optimization():
        from utils.tweaks.nvidia_optimization import NvidiaOptimizationTweak
        tweak = NvidiaOptimizationTweak()
        return tweak.toggle()


    # === HDCP ===
    @staticmethod
    def check_hdcp_status():
        from utils.tweaks.hdcp import HdcpTweak
        tweak = HdcpTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_hdcp():
        from utils.tweaks.hdcp import HdcpTweak
        tweak = HdcpTweak()
        return tweak.toggle()


    # === Power Throttling ===
    @staticmethod
    def check_power_throttling_status():
        from utils.tweaks.power_throttling import PowerThrottlingTweak
        tweak = PowerThrottlingTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_power_throttling():
        from utils.tweaks.power_throttling import PowerThrottlingTweak
        tweak = PowerThrottlingTweak()
        return tweak.toggle()


    @staticmethod
    def check_uwp_background_status():
        from utils.tweaks.uwp_background import UWPBackgroundTweak
        tweak = UWPBackgroundTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_uwp_background():
        from utils.tweaks.uwp_background import UWPBackgroundTweak
        tweak = UWPBackgroundTweak()
        return tweak.toggle()


    # === Уведомления ===
    @staticmethod
    def check_notifications_status():
        from utils.tweaks.notifications import NotificationsTweak
        tweak = NotificationsTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_notifications():
        from utils.tweaks.notifications import NotificationsTweak
        tweak = NotificationsTweak()
        return tweak.toggle()


    # === Cortana ===
    @staticmethod
    def check_cortana_status():
        from utils.tweaks.cortana import CortanaTweak
        tweak = CortanaTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_cortana():
        from utils.tweaks.cortana import CortanaTweak
        tweak = CortanaTweak()
        return tweak.toggle()

    # === FastBoot ===
    @staticmethod
    def check_fastboot_status():
        from utils.tweaks.fastboot import FastBootTweak
        tweak = FastBootTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_fastboot():
        from utils.tweaks.fastboot import FastBootTweak
        tweak = FastBootTweak()
        return tweak.toggle()

    # === Hibernation ===
    @staticmethod
    def check_hibernation_status():
        from utils.tweaks.hibernation import HibernationTweak
        tweak = HibernationTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_hibernation():
        from utils.tweaks.hibernation import HibernationTweak
        tweak = HibernationTweak()
        return tweak.toggle()

    # === Indexing ===
    @staticmethod
    def check_indexing_status():
        from utils.tweaks.indexing import IndexingTweak
        tweak = IndexingTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_indexing():
        from utils.tweaks.indexing import IndexingTweak
        tweak = IndexingTweak()
        return tweak.toggle()

    # === Windows Defender ===
    @staticmethod
    def check_windows_defender_status():
        from utils.tweaks.windows_defender import WindowsDefenderTweak
        tweak = WindowsDefenderTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_windows_defender():
        from utils.tweaks.windows_defender import WindowsDefenderTweak
        tweak = WindowsDefenderTweak()
        return tweak.toggle()

    # === OneDrive ===
    @staticmethod
    def check_onedrive_status():
        from utils.tweaks.onedrive import OneDriveTweak
        tweak = OneDriveTweak()
        return tweak.check_status()

    @staticmethod
    def remove_onedrive():  # Изменено на remove
        from utils.tweaks.onedrive import OneDriveTweak
        tweak = OneDriveTweak()
        return tweak.remove()  # Изменено на remove

    # === Wallpaper Compression ===
    @staticmethod
    def check_wallpaper_compression_status():
        from utils.tweaks.wallpaper_compression import WallpaperCompressionTweak
        tweak = WallpaperCompressionTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_wallpaper_compression():
        from utils.tweaks.wallpaper_compression import WallpaperCompressionTweak
        tweak = WallpaperCompressionTweak()
        return tweak.toggle()

    # === Sticky Keys ===
    @staticmethod
    def check_sticky_keys_status():
        from utils.tweaks.sticky_keys import StickyKeysTweak
        tweak = StickyKeysTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_sticky_keys():
        from utils.tweaks.sticky_keys import StickyKeysTweak
        tweak = StickyKeysTweak()
        return tweak.toggle()

    # === Mouse Acceleration ===
    @staticmethod
    def check_mouse_acceleration_status():
        from utils.tweaks.mouse_acceleration import MouseAccelerationTweak
        tweak = MouseAccelerationTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_mouse_acceleration():
        from utils.tweaks.mouse_acceleration import MouseAccelerationTweak
        tweak = MouseAccelerationTweak()
        return tweak.toggle()

    # === Security Center Notifications ===
    @staticmethod
    def check_security_center_notifications_status():
        from utils.tweaks.security_center_notifications import SecurityCenterNotificationsTweak
        tweak = SecurityCenterNotificationsTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_security_center_notifications():
        from utils.tweaks.security_center_notifications import SecurityCenterNotificationsTweak
        tweak = SecurityCenterNotificationsTweak()
        return tweak.toggle()

    # === App Start Notify ===
    @staticmethod
    def check_app_start_notify_status():
        from utils.tweaks.app_start_notify import AppStartNotifyTweak
        tweak = AppStartNotifyTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_app_start_notify():
        from utils.tweaks.app_start_notify import AppStartNotifyTweak
        tweak = AppStartNotifyTweak()
        return tweak.toggle()

    # === Prioritize Gaming Tasks ===
    @staticmethod
    def check_prioritize_gaming_tasks_status():
        from utils.tweaks.prioritize_gaming_tasks import PrioritizeGamingTasksTweak
        tweak = PrioritizeGamingTasksTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_prioritize_gaming_tasks():
        from utils.tweaks.prioritize_gaming_tasks import PrioritizeGamingTasksTweak
        tweak = PrioritizeGamingTasksTweak()
        return tweak.toggle()

    # === User Account Control (UAC) ===
    @staticmethod
    def check_uac_status():
        from utils.tweaks.uac import UACTweak
        tweak = UACTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_uac():
        from utils.tweaks.uac import UACTweak
        tweak = UACTweak()
        return tweak.toggle()

    # === Hardware-accelerated GPU Scheduling ===
    @staticmethod
    def check_hw_sch_mode_status():
        from utils.tweaks.hw_sch_mode import HwSchModeTweak
        tweak = HwSchModeTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_hw_sch_mode():
        from utils.tweaks.hw_sch_mode import HwSchModeTweak
        tweak = HwSchModeTweak()
        return tweak.toggle()

    # === Widgets Uninstall ===
    @staticmethod
    def check_widgets_uninstalled_status():
        from utils.tweaks.widgets_uninstall import WidgetsUninstallTweak
        tweak = WidgetsUninstallTweak()
        return tweak.check_status()

    @staticmethod
    def uninstall_widgets():
        from utils.tweaks.widgets_uninstall import WidgetsUninstallTweak
        tweak = WidgetsUninstallTweak()
        return tweak.uninstall()

    # === Clipboard History ===
    @staticmethod
    def check_clipboard_history_status():
        from utils.tweaks.clipboard_history import ClipboardHistoryTweak
        tweak = ClipboardHistoryTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_clipboard_history():
        from utils.tweaks.clipboard_history import ClipboardHistoryTweak
        tweak = ClipboardHistoryTweak()
        return tweak.toggle()

    # === Core Isolation ===
    @staticmethod
    def check_core_isolation_status():
        from utils.tweaks.core_isolation import CoreIsolationTweak
        tweak = CoreIsolationTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_core_isolation():
        from utils.tweaks.core_isolation import CoreIsolationTweak
        tweak = CoreIsolationTweak()
        return tweak.toggle()

    # === Auto Update Maps ===
    @staticmethod
    def check_auto_update_maps_status():
        from utils.tweaks.auto_update_maps import AutoUpdateMapsTweak
        tweak = AutoUpdateMapsTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_auto_update_maps():
        from utils.tweaks.auto_update_maps import AutoUpdateMapsTweak
        tweak = AutoUpdateMapsTweak()
        return tweak.toggle()

    # === Auto Store Apps ===
    @staticmethod
    def check_auto_store_apps_status():
        from utils.tweaks.auto_store_apps import AutoStoreAppsTweak
        tweak = AutoStoreAppsTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_auto_store_apps():
        from utils.tweaks.auto_store_apps import AutoStoreAppsTweak
        tweak = AutoStoreAppsTweak()
        return tweak.toggle()

    # === Background Task Edge Browser ===
    @staticmethod
    def check_background_task_edge_browser_status():
        from utils.tweaks.background_task_edge_browser import BackgroundTaskEdgeBrowserTweak
        tweak = BackgroundTaskEdgeBrowserTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_background_task_edge_browser():
        from utils.tweaks.background_task_edge_browser import BackgroundTaskEdgeBrowserTweak
        tweak = BackgroundTaskEdgeBrowserTweak()
        return tweak.toggle()

    # === Windows Advertising ID ===
    @staticmethod
    def check_win_ad_status():
        from utils.tweaks.win_ad import WinAdTweak
        tweak = WinAdTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_win_ad():
        from utils.tweaks.win_ad import WinAdTweak
        tweak = WinAdTweak()
        return tweak.toggle()

    # === Windows Sync ===
    @staticmethod
    def check_windows_sync_status():
        from utils.tweaks.windows_sync import WindowsSyncTweak
        tweak = WindowsSyncTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_windows_sync():
        from utils.tweaks.windows_sync import WindowsSyncTweak
        tweak = WindowsSyncTweak()
        return tweak.toggle()

    # === Windows Telemetry ===
    @staticmethod
    def check_windows_telemetry_status():
        from utils.tweaks.windows_telemetry import WindowsTelemetryTweak
        tweak = WindowsTelemetryTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_windows_telemetry():
        from utils.tweaks.windows_telemetry import WindowsTelemetryTweak
        tweak = WindowsTelemetryTweak()
        return tweak.toggle()

    # === NVIDIA Telemetry ===
    @staticmethod
    def check_nvidia_telemetry_status():
        from utils.tweaks.nvidia_telemetry import NvidiaTelemetryTweak
        tweak = NvidiaTelemetryTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_nvidia_telemetry():
        from utils.tweaks.nvidia_telemetry import NvidiaTelemetryTweak
        tweak = NvidiaTelemetryTweak()
        return tweak.toggle()

    # === Installed App Data ===
    @staticmethod
    def check_installed_app_data_status():
        from utils.tweaks.installed_app_data import InstalledAppDataTweak
        tweak = InstalledAppDataTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_installed_app_data():
        from utils.tweaks.installed_app_data import InstalledAppDataTweak
        tweak = InstalledAppDataTweak()
        return tweak.toggle()

    # === App Usage Stats ===
    @staticmethod
    def check_app_usage_stats_status():
        from utils.tweaks.app_usage_stats import AppUsageStatsTweak
        tweak = AppUsageStatsTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_app_usage_stats():
        from utils.tweaks.app_usage_stats import AppUsageStatsTweak
        tweak = AppUsageStatsTweak()
        return tweak.toggle()

    # === Handwriting Data ===
    @staticmethod
    def check_handwriting_data_status():
        from utils.tweaks.handwriting_data import HandwritingDataTweak
        tweak = HandwritingDataTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_handwriting_data():
        from utils.tweaks.handwriting_data import HandwritingDataTweak
        tweak = HandwritingDataTweak()
        return tweak.toggle()

    # === Data Domains (hosts file modification) ===
    @staticmethod
    def check_data_domains_status():
        from utils.tweaks.data_domains import DataDomainsTweak
        tweak = DataDomainsTweak()
        return tweak.check_status()

    @staticmethod
    def modify_hosts_file():
        from utils.tweaks.data_domains import DataDomainsTweak
        tweak = DataDomainsTweak()
        return tweak.modify() #  Более подходящее название метода

    # === User Behavior Logging ===
    @staticmethod
    def check_user_behavior_logging_status():
        from utils.tweaks.user_behavior_logging import UserBehaviorLoggingTweak
        tweak = UserBehaviorLoggingTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_user_behavior_logging():
        from utils.tweaks.user_behavior_logging import UserBehaviorLoggingTweak
        tweak = UserBehaviorLoggingTweak()
        return tweak.toggle()

    # === Location Tracking ===
    @staticmethod
    def check_location_tracking_status():
        from utils.tweaks.location_tracking import LocationTrackingTweak
        tweak = LocationTrackingTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_location_tracking():
        from utils.tweaks.location_tracking import LocationTrackingTweak
        tweak = LocationTrackingTweak()
        return tweak.toggle()

    # === Feedback Check ===
    @staticmethod
    def check_feedback_check_status():
        from utils.tweaks.feedback_check import FeedbackCheckTweak
        tweak = FeedbackCheckTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_feedback_check():
        from utils.tweaks.feedback_check import FeedbackCheckTweak
        tweak = FeedbackCheckTweak()
        return tweak.toggle()

    # === Background Speech Synthesis ===
    @staticmethod
    def check_background_speech_synthesis_status():
        from utils.tweaks.background_speech_synthesis import BackgroundSpeechSynthesisTweak
        tweak = BackgroundSpeechSynthesisTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_background_speech_synthesis():
        from utils.tweaks.background_speech_synthesis import BackgroundSpeechSynthesisTweak
        tweak = BackgroundSpeechSynthesisTweak()
        return tweak.toggle()

    # === System Monitoring ===
    @staticmethod
    def check_system_monitoring_status():
        from utils.tweaks.system_monitoring import SystemMonitoringTweak
        tweak = SystemMonitoringTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_system_monitoring():
        from utils.tweaks.system_monitoring import SystemMonitoringTweak
        tweak = SystemMonitoringTweak()
        return tweak.toggle()

    # === Remote PC Experiments ===
    @staticmethod
    def check_remote_pc_experiments_status():
        from utils.tweaks.remote_pc_experiments import RemotePCExperimentsTweak
        tweak = RemotePCExperimentsTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_remote_pc_experiments():
        from utils.tweaks.remote_pc_experiments import RemotePCExperimentsTweak
        tweak = RemotePCExperimentsTweak()
        return tweak.toggle()

    # === Microsoft Spy Modules ===
    @staticmethod
    def check_microsoft_spy_modules_status():
        from utils.tweaks.microsoft_spy_modules import MicrosoftSpyModulesTweak
        tweak = MicrosoftSpyModulesTweak()
        return tweak.check_status()
    @staticmethod
    def toggle_microsoft_spy_modules():
        from utils.tweaks.microsoft_spy_modules import MicrosoftSpyModulesTweak
        tweak = MicrosoftSpyModulesTweak()
        return tweak.toggle()

    # === Windows Event Logging ===
    @staticmethod
    def check_windows_event_logging_status():
        from utils.tweaks.windows_event_logging import WindowsEventLoggingTweak
        tweak = WindowsEventLoggingTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_windows_event_logging():
        from utils.tweaks.windows_event_logging import WindowsEventLoggingTweak
        tweak = WindowsEventLoggingTweak()
        return tweak.toggle()

    # === App Start Tracking ===
    @staticmethod
    def check_app_start_tracking_status():
        from utils.tweaks.app_start_tracking import AppStartTrackingTweak
        tweak = AppStartTrackingTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_app_start_tracking():
        from utils.tweaks.app_start_tracking import AppStartTrackingTweak
        tweak = AppStartTrackingTweak()
        return tweak.toggle()

    # === App Settings Sync ===
    @staticmethod
    def check_app_settings_sync_status():
        from utils.tweaks.app_settings_sync import AppSettingsSyncTweak
        tweak = AppSettingsSyncTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_app_settings_sync():
        from utils.tweaks.app_settings_sync import AppSettingsSyncTweak
        tweak = AppSettingsSyncTweak()
        return tweak.toggle()

    # === Explorer Blur ===
    @staticmethod
    def check_explorer_blur_status():
        from utils.tweaks.explorer_blur import ExplorerBlurTweak
        tweak = ExplorerBlurTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_explorer_blur():
        from utils.tweaks.explorer_blur import ExplorerBlurTweak
        tweak = ExplorerBlurTweak()
        return tweak.toggle()

    # === Show File Extensions ===
    @staticmethod
    def check_show_file_extensions_status():
        from utils.tweaks.show_file_extensions import ShowFileExtensionsTweak
        tweak = ShowFileExtensionsTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_show_file_extensions():
        from utils.tweaks.show_file_extensions import ShowFileExtensionsTweak
        tweak = ShowFileExtensionsTweak()
        return tweak.toggle()

    # === Gallery Explorer ===
    @staticmethod
    def check_gallery_explorer_status():
        from utils.tweaks.gallery_explorer import GalleryExplorerTweak
        tweak = GalleryExplorerTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_gallery_explorer():
        from utils.tweaks.gallery_explorer import GalleryExplorerTweak
        tweak = GalleryExplorerTweak()
        return tweak.toggle()

    # === Home Explorer ===
    @staticmethod
    def check_home_explorer_status():
        from utils.tweaks.home_explorer import HomeExplorerTweak
        tweak = HomeExplorerTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_home_explorer():
        from utils.tweaks.home_explorer import HomeExplorerTweak
        tweak = HomeExplorerTweak()
        return tweak.toggle()

    # === Network Explorer ===
    @staticmethod
    def check_network_explorer_status():
        from utils.tweaks.network_explorer import NetworkExplorerTweak
        tweak = NetworkExplorerTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_network_explorer():
        from utils.tweaks.network_explorer import NetworkExplorerTweak
        tweak = NetworkExplorerTweak()
        return tweak.toggle()

    # === Taskbar Date ===
    @staticmethod
    def check_taskbar_date_status():
        from utils.tweaks.taskbar_date import TaskbarDateTweak
        tweak = TaskbarDateTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_taskbar_date():
        from utils.tweaks.taskbar_date import TaskbarDateTweak
        tweak = TaskbarDateTweak()
        return tweak.toggle()

    # === Icon Arrow On Shortcut ===
    @staticmethod
    def check_icon_arrow_on_shortcut_status():
        from utils.tweaks.icon_arrow_on_shortcut import IconArrowOnShortcutTweak
        tweak = IconArrowOnShortcutTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_icon_arrow_on_shortcut():
        from utils.tweaks.icon_arrow_on_shortcut import IconArrowOnShortcutTweak
        tweak = IconArrowOnShortcutTweak()
        return tweak.toggle()

    # === PcaSvc Service ===
    @staticmethod
    def check_service_pcasvc_status():
        from utils.tweaks.services_pcasvc import PcaSvcServiceTweak
        tweak = PcaSvcServiceTweak()
        return tweak.check_status()
    @staticmethod
    def toggle_service_pcasvc():
        from utils.tweaks.services_pcasvc import PcaSvcServiceTweak
        tweak = PcaSvcServiceTweak()
        return tweak.toggle()

    # === Wecsvc Service ===
    @staticmethod
    def check_service_wecsvc_status():
        from utils.tweaks.services_wecsvc import WecsvcServiceTweak
        tweak = WecsvcServiceTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_service_wecsvc():
        from utils.tweaks.services_wecsvc import WecsvcServiceTweak
        tweak = WecsvcServiceTweak()
        return tweak.toggle()

    # === WbioSrvc Service ===
    @staticmethod
    def check_service_wbiosrvc_status():
        from utils.tweaks.services_wbiosrvc import WbioSrvcServiceTweak
        tweak = WbioSrvcServiceTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_service_wbiosrvc():
        from utils.tweaks.services_wbiosrvc import WbioSrvcServiceTweak
        tweak = WbioSrvcServiceTweak()
        return tweak.toggle()

    # === stisvc Service ===
    @staticmethod
    def check_service_stisvc_status():
        from utils.tweaks.services_stisvc import StisvcServiceTweak
        tweak = StisvcServiceTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_service_stisvc():
        from utils.tweaks.services_stisvc import StisvcServiceTweak
        tweak = StisvcServiceTweak()
        return tweak.toggle()

    # === WSearch Service ===
    @staticmethod
    def check_service_wsearch_status():
        from utils.tweaks.services_wsearch import WSearchServiceTweak
        tweak = WSearchServiceTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_service_wsearch():
        from utils.tweaks.services_wsearch import WSearchServiceTweak
        tweak = WSearchServiceTweak()
        return tweak.toggle()

    # === MapsBroker Service ===
    @staticmethod
    def check_service_mapsbroker_status():
        from utils.tweaks.services_mapsbroker import MapsBrokerServiceTweak
        tweak = MapsBrokerServiceTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_service_mapsbroker():
        from utils.tweaks.services_mapsbroker import MapsBrokerServiceTweak
        tweak = MapsBrokerServiceTweak()
        return tweak.toggle()

    # === Sensor Services (SensorService, SensorDataService, SensrSvc) ===
    @staticmethod
    def check_service_sensorservice_status():
        from utils.tweaks.services_sensorservice import SensorServicesTweak
        tweak = SensorServicesTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_service_sensorservice():
        from utils.tweaks.services_sensorservice import SensorServicesTweak
        tweak = SensorServicesTweak()
        return tweak.toggle()

    # === Hyper-V Services ===
    @staticmethod
    def check_service_hyperv_status():
        from utils.tweaks.services_hyperv import HyperVServicesTweak
        tweak = HyperVServicesTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_service_hyperv():
        from utils.tweaks.services_hyperv import HyperVServicesTweak
        tweak = HyperVServicesTweak()
        return tweak.toggle()

    # === Xbox Services (XblGameSave, XboxNetApiSvc, XboxGipSvc, XblAuthManager) ===
    @staticmethod
    def check_service_xblgamesave_status():
        from utils.tweaks.services_xblgamesave import XblGameSaveServicesTweak
        tweak = XblGameSaveServicesTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_service_xblgamesave():
        from utils.tweaks.services_xblgamesave import XblGameSaveServicesTweak
        tweak = XblGameSaveServicesTweak()
        return tweak.toggle()

# === Printer Services ===
    @staticmethod
    def check_service_printer_status():
        from utils.tweaks.services_printer import PrinterServicesTweak
        tweak = PrinterServicesTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_service_printer():
        from utils.tweaks.services_printer import PrinterServicesTweak
        tweak = PrinterServicesTweak()
        return tweak.toggle()

# === SysMain Service ===
    @staticmethod
    def check_sysmain_service_status():
        from utils.tweaks.service_sysmain import SysMainServiceTweak  # Изменен путь импорта
        tweak = SysMainServiceTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_service_sysmain():
        from utils.tweaks.service_sysmain import SysMainServiceTweak  # Изменен путь импорта
        tweak = SysMainServiceTweak()
        return tweak.toggle()

# === wisvc Service ===
    @staticmethod
    def check_wisvc_service_status():
        from utils.tweaks.service_wisvc import WisvcServiceTweak
        tweak = WisvcServiceTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_service_wisvc():
        from utils.tweaks.service_wisvc import WisvcServiceTweak
        tweak = WisvcServiceTweak()
        return tweak.toggle()

# === Diagnostics Services ===
    @staticmethod
    def check_diagnostics_services_status():
        from utils.tweaks.service_diagnostics import DiagnosticsServicesTweak
        tweak = DiagnosticsServicesTweak()
        return tweak.check_status()

    @staticmethod
    def toggle_service_diagnostics():
        from utils.tweaks.service_diagnostics import DiagnosticsServicesTweak
        tweak = DiagnosticsServicesTweak()
        return tweak.toggle()