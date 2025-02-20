import os
import json
import sys
import threading
import tkinter as tk
import asyncio
import time

try:
    import customtkinter as ctk
except ImportError:
    print("Error: CustomTkinter not found. Install: pip install customtkinter")
    sys.exit(1)

from config import TWEAK_CATEGORIES, TWEAKS
from utils.system_tweaks import SystemTweaks


def load_settings(settings_file="settings.json"):
    """Loads settings from a JSON file or returns default settings."""
    try:
        with open(settings_file, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error loading settings. Using defaults.")
        return {
            "appearance_mode": "System",
            "theme": "blue",
            "language": "Russian",
            "accent_color": "#1f6aa5"
        }


settings = load_settings()
ctk.set_appearance_mode(settings.get("appearance_mode", "System"))
ctk.set_default_color_theme(settings.get("theme", "blue"))


def start_asyncio_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


# Asyncio loop in a separate thread
loop = asyncio.new_event_loop()
threading.Thread(target=start_asyncio_loop, args=(loop,), daemon=True).start()


class TweaksTab:
    def __init__(self, parent):
        # Add lazy initialization
        self.parent = parent
        self.initialized = False
        self._initialize_basic_components()
        # Defer full initialization
        self.parent.after(100, self._initialize_full)
        # Add cleanup binding
        self.parent.bind("<Destroy>", self._cleanup)

    def _initialize_basic_components(self):
        """Initialize only essential components for initial display"""
        # Basic cache and state variables
        self.tweak_cards = {}
        self.status_cache = {}
        self.search_cache = {}
        self.category_buttons = {}
        self.update_lock = threading.Lock()
        self.visible = True
        self.current_category = None
        self.selected_category = None
        self.is_searching = False

        # UI update settings
        self.ui_update_interval = 5000
        self.accent_color = settings.get("accent_color", "#FF5733")

        # Basic UI setup
        self._setup_grid()
        self._create_main_frames()

    def _setup_grid(self):
        """Setup initial grid configuration"""
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)

    def _create_main_frames(self):
        """Create and setup main UI frames"""
        # Main frame
        self.main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self.main_frame, width=200, corner_radius=10,
                                    fg_color=("gray85", "gray17"))
        self.sidebar.grid(row=0, column=0, sticky="ns", padx=(0, 10), pady=5)

        # Content frame
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_rowconfigure(1, weight=1)

    def _initialize_full(self):
        """Initialize remaining components after basic UI is shown"""
        if self.initialized:
            return

        try:
            # Initialize system components with progress tracking
            self._init_progress = 0
            self._update_init_status("Инициализация системных компонентов...")

            # Initialize system tweaks
            self.system_tweaks = SystemTweaks()
            self._init_progress = 20

            # Initialize analyzer with optimized settings
            from utils.tweak_analyzer import TweakAnalyzer
            self.analyzer = TweakAnalyzer()
            # Предварительная загрузка кэша анализатора в фоновом режиме
            self.parent.after(100, self._preload_analyzer_cache)
            self._init_progress = 30

            # Create UI components in specific order for better performance
            self._update_init_status("Создание интерфейса...")
            self._create_sidebar()
            self._init_progress = 40
            self._create_search_area()
            self._init_progress = 50
            self._create_content_area()
            self._init_progress = 60

            # Initialize tweaks with batching
            self._update_init_status("Инициализация твиков...")
            self.tweaks = {}
            self._initialize_tweaks_in_batches()
            self._init_progress = 80

            # Setup event bindings
            self._setup_bindings()
            self._init_progress = 90

            # Set default category
            default_category = "Оптимизация и настройки"
            if default_category in self.category_buttons:
                # Отложенный выбор категории
                self.parent.after(100, lambda: self.select_category(default_category,
                                                                    self.category_buttons[default_category]))
            else:
                self.parent.after(100, lambda: self.show_category(default_category))

            # Start UI updates in background
            self.parent.after(200, self._schedule_ui_update)

            self._init_progress = 100
            self._update_init_status("Инициализация завершена")
            self.initialized = True

        except Exception as e:
            print(f"Error during initialization: {e}")
            self._update_init_status(f"Ошибка инициализации: {str(e)}", error=True)

    def _preload_analyzer_cache(self):
        """Предварительная загрузка кэша анализатора в фоновом режиме"""
        try:
            threading.Thread(
                target=self.analyzer.load_latest_analysis,
                daemon=True
            ).start()
        except Exception as e:
            print(f"Error preloading analyzer cache: {e}")

    def _initialize_tweaks_in_batches(self, batch_size=10):
        """Initialize tweaks in batches for better responsiveness"""
        from config import TWEAKS

        total_tweaks = len(TWEAKS)
        processed = 0

        for i in range(0, total_tweaks, batch_size):
            batch = TWEAKS[i:i + batch_size]
            batch_tweaks = {
                config["key"]: self._create_tweak_data(config)
                for config in batch
            }
            self.tweaks.update(batch_tweaks)

            processed += len(batch)
            progress = (processed / total_tweaks) * 100
            self._update_init_status(f"Загрузка твиков... {int(progress)}%")

            # Даем интерфейсу время на обновление
            if i + batch_size < total_tweaks:
                self.parent.update_idletasks()

    def _update_init_status(self, message, error=False):
        """Update initialization status"""
        if hasattr(self.parent, 'dynamic_status'):
            self.parent.dynamic_status.update_text(
                message,
                message_type="error" if error else "info"
            )
        print(f"Init ({self._init_progress}%): {message}")

    def _setup_bindings(self):
        """Setup event bindings"""
        self.parent.bind("<Visibility>", self.on_visibility_change)
        self.parent.bind("<KeyPress-r>", self.on_key_press_r)
        self.parent.bind("<KeyPress-R>", self.on_key_press_r)

    def _cleanup(self, event=None):
        """Clean up resources when tab is destroyed"""
        # Clear caches
        self.search_cache.clear()
        self.status_cache.clear()

        # Clear UI elements
        for card in self.tweak_cards.values():
            if card.winfo_exists():
                card.destroy()
        self.tweak_cards.clear()

        # Remove references to large objects
        self.system_tweaks = None
        self.analyzer = None
        self.tweaks = None

        # Cancel any pending updates
        if hasattr(self, 'search_debounce_timer'):
            self.parent.after_cancel(self.search_debounce_timer)

        # Stop UI updates
        self.visible = False

    def on_key_press_r(self, event):
        if self.visible:
            self.update_status_manual()

    def _create_sidebar(self):
        header_label = ctk.CTkLabel(self.sidebar, text="Категории", font=("Roboto", 18, "bold"),
                                    fg_color="transparent", text_color=("gray10", "gray90"))
        header_label.pack(pady=(10, 5), padx=10)
        separator = ctk.CTkFrame(self.sidebar, height=2, fg_color=("gray70", "gray30"), corner_radius=1)
        separator.pack(fill="x", padx=10, pady=(0, 10))
        for category in TWEAK_CATEGORIES:
            btn = ctk.CTkButton(self.sidebar, text=category, corner_radius=7, fg_color="transparent",
                                hover_color=("gray70", "gray30"), text_color=("gray10", "gray90"), font=("Roboto", 14),
                                command=lambda c=category, b=None: None)  # Dummy command
            btn.pack(pady=6, padx=10, fill="x")
            btn.configure(command=lambda c=category, b=btn: self.select_category(c, b))  # Real command
            self.category_buttons[category] = btn

    def select_category(self, category, button):
        self.selected_category = category
        for cat, btn in self.category_buttons.items():
            if cat == category:
                btn.configure(fg_color=self.accent_color, text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=("gray10", "gray90"))
        self.show_category(category)

    def _create_search_area(self):
        self.search_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(6, 7))
        self.search_frame.grid_columnconfigure(0, weight=1)
        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Поиск твиков...", height=38,
                                         corner_radius=8, border_width=2, border_color="gray25",
                                         fg_color=("gray85", "gray17"), font=("Roboto", 14))
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.search_entry.bind("<KeyRelease>", self.search_tweaks)
        self.search_entry.bind("<FocusIn>", lambda e: self.update_search_entry_border_color(searching=True))
        self.search_entry.bind("<FocusOut>", lambda e: self.update_search_entry_border_color(searching=False))

        button_width = 38
        self.refresh_button = ctk.CTkButton(self.search_frame, text="R", width=button_width, height=38,
                                            corner_radius=8, fg_color=("gray85", "gray17"),
                                            hover_color=("gray70", "gray30"), border_width=2, border_color="gray25",
                                            command=self.update_status_manual, font=("Open Sans", 16),
                                            text_color=self.accent_color)
        self.refresh_button.grid(row=0, column=1, padx=(0, 5))
        clear_btn = ctk.CTkButton(self.search_frame, text="✕", width=button_width, height=38, corner_radius=8,
                                  fg_color=("gray85", "gray17"), hover_color=("gray70", "gray30"), border_width=2,
                                  border_color="gray25", command=self.clear_search, font=("Open Sans", 25),
                                  text_color=self.accent_color)
        clear_btn.grid(row=0, column=2)

        analyze_btn = ctk.CTkButton(self.search_frame, text="📊", width=button_width, height=38,
                                    corner_radius=8, fg_color=("gray85", "gray17"),
                                    hover_color=("gray70", "gray30"), border_width=2,
                                    border_color="gray25", command=self.analyze_tweaks,
                                    font=("Segoe UI Emoji", 16), text_color=self.accent_color)
        analyze_btn.grid(row=0, column=3, padx=(5, 0))

    def _create_content_area(self):
        self.scrollable_content = ctk.CTkScrollableFrame(self.content_frame, corner_radius=10,
                                                         fg_color=("gray85", "gray17"))
        self.scrollable_content.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=1)

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.is_searching = False
        self.show_category(self.current_category or "Оптимизация и настройки")

    def _create_tweak_data(self, tweak_config):
        tweak_data = {"category": tweak_config["category"], "instance": None, "switch_ref": None}
        if tweak_config["class_name"]:
            module_name = tweak_config.get("module", tweak_config["key"])
            module = __import__(f"utils.tweaks.{module_name}", fromlist=[tweak_config["class_name"]])
            tweak_class = getattr(module, tweak_config["class_name"])
            tweak_data["instance"] = tweak_class()
            tweak_data["check_status_func"] = tweak_data["instance"].check_status
        else:
            tweak_data["check_status_func"] = getattr(self.system_tweaks, f"check_{tweak_config['key']}_status", None)
        tweak_data["toggle_command"] = getattr(self, f"toggle_{tweak_config['key']}", None)
        if tweak_data["toggle_command"] is None:
            print(f"Warning: toggle_{tweak_config['key']} not found in TweaksTab.")
        return tweak_data

    def update_search_entry_border_color(self, searching=False):
        mode = ctk.get_appearance_mode()
        border_color = self.accent_color if searching else ("gray70" if mode.lower() == "dark" else "gray25")
        self.search_entry.configure(border_color=border_color)

    # --- Tweak toggle methods ---

    def toggle_spectre_meltdown(self):
        self._generic_toggle("spectre_meltdown", self.system_tweaks.toggle_spectre_meltdown,
                             self.system_tweaks.toggle_spectre_meltdown)

    def toggle_nvidia_optimization(self):
        self._generic_toggle("nvidia_optimization", self.system_tweaks.toggle_nvidia_optimization,
                             self.system_tweaks.toggle_nvidia_optimization)

    def toggle_hdcp(self):
        self._generic_toggle("hdcp", self.system_tweaks.toggle_hdcp, self.system_tweaks.toggle_hdcp)

    def toggle_power_throttling(self):
        self._generic_toggle("power_throttling", self.system_tweaks.toggle_power_throttling,
                             self.system_tweaks.toggle_power_throttling)

    def toggle_uwp_background(self):
        self._generic_toggle("uwp_background", self.system_tweaks.toggle_uwp_background,
                             self.system_tweaks.toggle_uwp_background)

    def toggle_FsoGameBar(self):
        self._generic_toggle("FsoGameBar", self.system_tweaks.toggle_FsoGameBar, self.system_tweaks.toggle_FsoGameBar)

    def toggle_power_plan(self):
        self._generic_toggle("power_plan", self.system_tweaks.toggle_powerplan, self.system_tweaks.toggle_powerplan)

    def toggle_fastboot(self):
        self._generic_toggle("fastboot", self.system_tweaks.toggle_fastboot, self.system_tweaks.toggle_fastboot)

    def toggle_notifications(self):
        self._generic_toggle("notifications", self.system_tweaks.toggle_notifications,
                             self.system_tweaks.toggle_notifications)

    def toggle_cortana(self):
        self._generic_toggle("notifications", self.system_tweaks.toggle_cortana, self.system_tweaks.toggle_cortana)

    def toggle_hibernation(self):
        self._generic_toggle("hibernation", self.system_tweaks.toggle_hibernation,
                             self.system_tweaks.toggle_hibernation)

    def toggle_indexing(self):
        self._generic_toggle("indexing", self.system_tweaks.toggle_indexing, self.system_tweaks.toggle_indexing)

    def toggle_windows_defender(self):
        self._generic_toggle("windows_defender", self.system_tweaks.toggle_windows_defender,
                             self.system_tweaks.toggle_windows_defender)

    def remove_onedrive(self):
        self._generic_toggle("onedrive", self.system_tweaks.remove_onedrive, self.system_tweaks.remove_onedrive)

    def toggle_wallpaper_compression(self):
        self._generic_toggle("wallpaper_compression", self.system_tweaks.toggle_wallpaper_compression,
                             self.system_tweaks.toggle_wallpaper_compression)

    def toggle_sticky_keys(self):
        self._generic_toggle("sticky_keys", self.system_tweaks.toggle_sticky_keys,
                             self.system_tweaks.toggle_sticky_keys)

    def toggle_mouse_acceleration(self):
        self._generic_toggle("mouse_acceleration", self.system_tweaks.toggle_mouse_acceleration,
                             self.system_tweaks.toggle_mouse_acceleration)

    def toggle_security_center_notifications(self):
        self._generic_toggle("security_center_notifications", self.system_tweaks.toggle_security_center_notifications,
                             self.system_tweaks.toggle_security_center_notifications)

    def toggle_app_start_notify(self):
        self._generic_toggle("app_start_notify", self.system_tweaks.toggle_app_start_notify,
                             self.system_tweaks.toggle_app_start_notify)

    def toggle_prioritize_gaming_tasks(self):
        self._generic_toggle("prioritize_gaming_tasks", self.system_tweaks.toggle_prioritize_gaming_tasks,
                             self.system_tweaks.toggle_prioritize_gaming_tasks)

    def toggle_uac(self):
        self._generic_toggle("uac", self.system_tweaks.toggle_uac, self.system_tweaks.toggle_uac)

    def toggle_hw_sch_mode(self):
        self._generic_toggle("hw_sch_mode", self.system_tweaks.toggle_hw_sch_mode,
                             self.system_tweaks.toggle_hw_sch_mode)

    def uninstall_widgets(self):
        self._generic_toggle("widgets_uninstall", self.system_tweaks.uninstall_widgets,
                             self.system_tweaks.uninstall_widgets)

    def toggle_clipboard_history(self):
        self._generic_toggle("clipboard_history", self.system_tweaks.toggle_clipboard_history,
                             self.system_tweaks.toggle_clipboard_history)

    def toggle_core_isolation(self):
        self._generic_toggle("core_isolation", self.system_tweaks.toggle_core_isolation,
                             self.system_tweaks.toggle_core_isolation)  # security_tweaks

    def toggle_auto_update_maps(self):
        self._generic_toggle("auto_update_maps", self.system_tweaks.toggle_auto_update_maps,
                             self.system_tweaks.toggle_auto_update_maps)

    def toggle_auto_store_apps(self):
        self._generic_toggle("auto_store_apps", self.system_tweaks.toggle_auto_store_apps,
                             self.system_tweaks.toggle_auto_store_apps)

    def toggle_background_task_edge_browser(self):
        self._generic_toggle("background_task_edge_browser", self.system_tweaks.toggle_background_task_edge_browser,
                             self.system_tweaks.toggle_background_task_edge_browser)

    def toggle_win_ad(self):
        self._generic_toggle("win_ad", self.system_tweaks.toggle_win_ad,
                             self.system_tweaks.toggle_win_ad)  # privacy_tweaks

    def toggle_windows_sync(self):
        self._generic_toggle("windows_sync", self.system_tweaks.toggle_windows_sync,
                             self.system_tweaks.toggle_windows_sync)  # privacy_tweaks

    def toggle_windows_telemetry(self):
        self._generic_toggle("windows_telemetry", self.system_tweaks.toggle_windows_telemetry,
                             self.system_tweaks.toggle_windows_telemetry)

    def toggle_nvidia_telemetry(self):
        self._generic_toggle("nvidia_telemetry", self.system_tweaks.toggle_nvidia_telemetry,
                             self.system_tweaks.toggle_nvidia_telemetry)

    def toggle_installed_app_data(self):
        self._generic_toggle("installed_app_data", self.system_tweaks.toggle_installed_app_data,
                             self.system_tweaks.toggle_installed_app_data)  # privacy_tweaks

    def toggle_app_usage_stats(self):
        self._generic_toggle("app_usage_stats", self.system_tweaks.toggle_app_usage_stats,
                             self.system_tweaks.toggle_app_usage_stats)  # privacy_tweaks

    def toggle_handwriting_data(self):
        self._generic_toggle("handwriting_data", self.system_tweaks.toggle_handwriting_data,
                             self.system_tweaks.toggle_handwriting_data)  # privacy_tweaks

    def modify_hosts_file(self):  # Более описательное название
        self._generic_toggle("data_domains", self.system_tweaks.modify_hosts_file,
                             self.system_tweaks.modify_hosts_file)  # system_tweaks

    def toggle_user_behavior_logging(self):
        self._generic_toggle("user_behavior_logging", self.system_tweaks.toggle_user_behavior_logging,
                             self.system_tweaks.toggle_user_behavior_logging)  # privacy_tweaks

    def toggle_location_tracking(self):
        self._generic_toggle("location_tracking", self.system_tweaks.toggle_location_tracking,
                             self.system_tweaks.toggle_location_tracking)  # privacy_tweaks

    def toggle_feedback_check(self):
        self._generic_toggle("feedback_check", self.system_tweaks.toggle_feedback_check,
                             self.system_tweaks.toggle_feedback_check)  # privacy_tweaks

    def toggle_background_speech_synthesis(self):
        self._generic_toggle("background_speech_synthesis", self.system_tweaks.toggle_background_speech_synthesis,
                             self.system_tweaks.toggle_background_speech_synthesis)  # privacy_tweaks

    def toggle_system_monitoring(self):
        self._generic_toggle("system_monitoring", self.system_tweaks.toggle_system_monitoring,
                             self.system_tweaks.toggle_system_monitoring)

    def toggle_remote_pc_experiments(self):
        self._generic_toggle("remote_pc_experiments", self.system_tweaks.toggle_remote_pc_experiments,
                             self.system_tweaks.toggle_remote_pc_experiments)  # privacy_tweaks

    def toggle_microsoft_spy_modules(self):
        self._generic_toggle("microsoft_spy_modules", self.system_tweaks.toggle_microsoft_spy_modules,
                             self.system_tweaks.toggle_microsoft_spy_modules)  # privacy_tweaks

    def toggle_windows_event_logging(self):
        self._generic_toggle("windows_event_logging", self.system_tweaks.toggle_windows_event_logging,
                             self.system_tweaks.toggle_windows_event_logging)

    def toggle_app_start_tracking(self):
        self._generic_toggle("app_start_tracking", self.system_tweaks.toggle_app_start_tracking,
                             self.system_tweaks.toggle_app_start_tracking)  # privacy_tweaks

    def toggle_app_settings_sync(self):
        self._generic_toggle("app_settings_sync", self.system_tweaks.toggle_app_settings_sync,
                             self.system_tweaks.toggle_app_settings_sync)  # privacy_tweaks

    def toggle_explorer_blur(self):
        self._generic_toggle("explorer_blur", self.system_tweaks.toggle_explorer_blur,
                             self.system_tweaks.toggle_explorer_blur)

    def toggle_show_file_extensions(self):
        self._generic_toggle("show_file_extensions", self.system_tweaks.toggle_show_file_extensions,
                             self.system_tweaks.toggle_show_file_extensions)

    def toggle_gallery_explorer(self):
        self._generic_toggle("gallery_explorer", self.system_tweaks.toggle_gallery_explorer,
                             self.system_tweaks.toggle_gallery_explorer)

    def toggle_home_explorer(self):
        self._generic_toggle("home_explorer", self.system_tweaks.toggle_home_explorer,
                             self.system_tweaks.toggle_home_explorer)

    def toggle_network_explorer(self):
        self._generic_toggle("network_explorer", self.system_tweaks.toggle_network_explorer,
                             self.system_tweaks.toggle_network_explorer)

    def toggle_taskbar_date(self):
        self._generic_toggle("taskbar_date", self.system_tweaks.toggle_taskbar_date,
                             self.system_tweaks.toggle_taskbar_date)

    def toggle_icon_arrow_on_shortcut(self):
        self._generic_toggle("icon_arrow_on_shortcut", self.system_tweaks.toggle_icon_arrow_on_shortcut,
                             self.system_tweaks.toggle_icon_arrow_on_shortcut)

    # Службы
    def toggle_service_pcasvc(self):
        self._generic_toggle("service_pcasvc", self.system_tweaks.toggle_service_pcasvc,
                             self.system_tweaks.toggle_service_pcasvc)

    def toggle_service_wecsvc(self):
        self._generic_toggle("service_wecsvc", self.system_tweaks.toggle_service_wecsvc,
                             self.system_tweaks.toggle_service_wecsvc)

    def toggle_service_wbiosrvc(self):
        self._generic_toggle("service_wbiosrvc", self.system_tweaks.toggle_service_wbiosrvc,
                             self.system_tweaks.toggle_service_wbiosrvc)

    def toggle_service_stisvc(self):
        self._generic_toggle("service_stisvc", self.system_tweaks.toggle_service_stisvc,
                             self.system_tweaks.toggle_service_stisvc)

    def toggle_service_wsearch(self):
        self._generic_toggle("service_wsearch", self.system_tweaks.toggle_service_wsearch,
                             self.system_tweaks.toggle_service_wsearch)

    def toggle_service_mapsbroker(self):
        self._generic_toggle("service_mapsbroker", self.system_tweaks.toggle_service_mapsbroker,
                             self.system_tweaks.toggle_service_mapsbroker)

    def toggle_service_sensorservice(self):
        self._generic_toggle("service_sensorservice", self.system_tweaks.toggle_service_sensorservice,
                             self.system_tweaks.toggle_service_sensorservice)

    def toggle_service_hyperv(self):
        self._generic_toggle("service_hyperv", self.system_tweaks.toggle_service_hyperv,
                             self.system_tweaks.toggle_service_hyperv)

    def toggle_service_xblgamesave(self):
        self._generic_toggle("service_xblgamesave", self.system_tweaks.toggle_service_xblgamesave,
                             self.system_tweaks.toggle_service_xblgamesave)

    def toggle_services_printer(self):
        self._generic_toggle("printer_services", self.system_tweaks.toggle_service_printer,
                             self.system_tweaks.toggle_service_printer)

    def toggle_service_sysmain(self):
        self._generic_toggle("service_sysmain", self.system_tweaks.toggle_service_sysmain,
                             self.system_tweaks.toggle_service_sysmain)

    def toggle_service_wisvc(self):
        self._generic_toggle("service_wisvc", self.system_tweaks.toggle_service_wisvc,
                             self.system_tweaks.toggle_service_wisvc)

    def toggle_service_diagnostics(self):
        self._generic_toggle("service_diagnostics", self.system_tweaks.toggle_service_diagnostics,
                             self.system_tweaks.toggle_service_diagnostics)

    def _generic_toggle(self, tweak_key, enable_func, disable_func):
        """Handles toggling a tweak with separate enable/disable functions."""
        switch_ref = self.tweaks[tweak_key]["switch_ref"]
        status_bar = self.parent.winfo_toplevel().dynamic_status
        tweak_instance = self.tweaks[tweak_key].get("instance")

        # Safely access the title, providing a default if metadata or title is missing
        tweak_name = tweak_instance.metadata.title if tweak_instance and hasattr(tweak_instance,
                                                                                 'metadata') and hasattr(
            tweak_instance.metadata, 'title') else tweak_key

        # Determine the *intended* action based on the switch's *initial* state.
        initial_state = bool(switch_ref.get())  # True if switch is ON, False if OFF

        # Call the appropriate function (enable or disable) based on the *initial* state.
        if initial_state:
            # Switch was initially ON, so the user intends to *disable*.
            success = disable_func()
            action = "включен"  # User intended to *disable*.
        else:
            # Switch was initially OFF, so the user intends to *enable*.
            success = enable_func()
            action = "выключен"  # User intended to *enable*.

        if success:
            status_bar.update_text(f"Твик '{tweak_name}' успешно {action}", duration=3000)
            self.status_cache.pop(tweak_key, None)  # Invalidate cache
            self._update_switch_status(tweak_key)  # Update UI from cache
        else:
            status_bar.update_text(
                f"Ошибка при {'включении' if action == 'включен' else 'выключении'} твика '{tweak_name}'",
                duration=4000)
            # Correctly revert the switch based on the *initial* state.
            self.parent.after(0, switch_ref.select if not initial_state else switch_ref.deselect)

    def setup_tweaks_page(self, category, search_term=""):
        # Add batch processing for better performance
        BATCH_SIZE = 10
        visible_tweaks = []

        # Get filtered tweaks
        if search_term:
            filtered_tweaks = self._get_filtered_tweaks(search_term)
        else:
            filtered_tweaks = {k: v for k, v in self.tweaks.items() if v["category"] == category}

        # Hide all cards first
        for card in self.tweak_cards.values():
            card.pack_forget()

        # Process tweaks in batches
        tweaks_items = list(filtered_tweaks.items())
        for i in range(0, len(tweaks_items), BATCH_SIZE):
            batch = tweaks_items[i:i + BATCH_SIZE]
            for tweak_key, tweak_data in batch:
                if tweak_key not in self.tweak_cards:
                    self.tweak_cards[tweak_key] = self._create_card(tweak_key, tweak_data)
                card = self.tweak_cards[tweak_key]
                card.pack(fill="x", expand=True, padx=10, pady=8)
                visible_tweaks.append(tweak_key)
                # Update in next event loop iteration
                self.parent.after(10, lambda k=tweak_key: self._update_switch_status(k))

    def _create_card(self, tweak_key, tweak_data):
        card = ctk.CTkFrame(self.scrollable_content, corner_radius=10, fg_color=("gray90", "gray20"),
                            border_width=1, border_color=("gray80", "gray30"))
        text_frame = ctk.CTkFrame(card, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        title = tweak_data["instance"].metadata.title if tweak_data["instance"] else tweak_key.replace("_", " ").title()
        description = tweak_data["instance"].metadata.description if tweak_data["instance"] else "Нет описания."

        title_label = ctk.CTkLabel(text_frame, text=title, font=("Roboto", 14, "bold"))
        title_label.grid(row=0, column=0, sticky="w")
        desc_label = ctk.CTkLabel(text_frame, text=description, font=("Roboto", 12), justify="left",
                                  text_color="#7E7E7E", wraplength=500)
        desc_label.grid(row=1, column=0, sticky="w", pady=(2, 0))

        tweak_switch = ctk.CTkSwitch(card, text="", command=tweak_data["toggle_command"], onvalue=1, offvalue=0,
                                     font=("Roboto", 12), progress_color=self.accent_color,
                                     button_color=("white", "white"))
        tweak_switch.pack(side="right", padx=10, pady=10)
        tweak_switch.tweak_key = tweak_key
        tweak_data["switch_ref"] = tweak_switch
        return card

    def _update_card(self, card, tweak_key, tweak_data):
        title = tweak_data["instance"].metadata.title if tweak_data["instance"] else tweak_key.replace("_", " ").title()
        description = tweak_data["instance"].metadata.description if tweak_data["instance"] else "Нет описания."
        title_label = card.winfo_children()[0].winfo_children()[0]
        desc_label = card.winfo_children()[0].winfo_children()[1]
        title_label.configure(text=title)
        desc_label.configure(text=description)
        tweak_switch = card.winfo_children()[1]
        tweak_switch.tweak_key = tweak_key  # Keep key updated
        tweak_data["switch_ref"] = tweak_switch

    def _update_switch_status(self, tweak_key):
        tweak_data = self.tweaks.get(tweak_key)
        if tweak_data and tweak_data.get("check_status_func"):
            switch = tweak_data["switch_ref"]
            if switch and switch.winfo_exists():
                try:
                    is_enabled = self._check_status_cached(tweak_key, tweak_data["check_status_func"])
                    if is_enabled:
                        switch.select()
                    else:
                        switch.deselect()
                except Exception as e:
                    print(f"Error during check_status_func for {tweak_key}: {e}")

    def _check_status_cached(self, tweak_key, check_status_func):
        now = time.time()
        if tweak_key in self.status_cache:
            is_enabled, timestamp = self.status_cache[tweak_key]
            if now - timestamp < 300:  # 5-minute cache
                return is_enabled
        try:
            is_enabled = check_status_func()
            self.status_cache[tweak_key] = (is_enabled, now)
            return is_enabled
        except Exception as e:
            print(f"Error checking status for {tweak_key}: {e}")
            return False

    def show_category(self, category):
        self.current_category = category
        self.setup_tweaks_page(category)

        self.search_debounce_timer = None

    def search_tweaks(self, event):
        search_term = self.search_entry.get().lower()  # Convert to lowercase once
        self.update_search_entry_border_color(searching=bool(search_term))

        # Cancel previous timer
        if self.search_debounce_timer:
            self.parent.after_cancel(self.search_debounce_timer)

        # Increase debounce time for better performance
        DEBOUNCE_TIME = 500  # ms
        self.search_debounce_timer = self.parent.after(DEBOUNCE_TIME, self._perform_search, search_term)

    def _get_filtered_tweaks(self, search_term):
        # Cache search results
        if search_term not in self.search_cache:
            filtered_tweaks = {}
            search_term_lower = search_term.lower()

            for key, data in self.tweaks.items():
                if data["instance"]:
                    title = data["instance"].metadata.title.lower()
                    description = data["instance"].metadata.description.lower()
                    if search_term_lower in title or search_term_lower in description:
                        filtered_tweaks[key] = data
                else:
                    if search_term_lower in key.replace("_", " ").lower():
                        filtered_tweaks[key] = data

            self.search_cache[search_term] = filtered_tweaks
        return self.search_cache[search_term]

    def _perform_search(self, search_term):
        self.search_debounce_timer = None # Сбрасываем таймер

        if search_term:
            self.is_searching = True
            asyncio.run_coroutine_threadsafe(self.setup_tweaks_page_async(search_term=search_term), loop)
        else:
            self.is_searching = False
            self.show_category(self.current_category or "Оптимизация и настройки")

    async def setup_tweaks_page_async(self, search_term=""):
        await asyncio.sleep(0.01)  # Small delay
        self.parent.after(0, self.setup_tweaks_page, None, search_term)

    def update_status_manual(self):
        self.update_status(manual=True)

    def analyze_tweaks(self):
        """Analyze and save current tweak statuses"""
        analysis = self.analyzer.collect_tweak_statuses(self.tweaks)
        window = self.parent.winfo_toplevel()

        if self.analyzer.save_analysis(analysis):
            # Successfully saved without showing a message
            pass
        else:
            if hasattr(window, 'dynamic_status'):
                window.dynamic_status.update_text(
                    "Ошибка при сохранении анализа твиков",
                    message_type="error"
                )

    def update_status(self, manual=False):
        if not self.update_lock.acquire(blocking=False):
            if not manual:
                self.parent.after(100, self.update_status)
            return

        def update_in_thread():
            try:
                for tweak_key, tweak_data in self.tweaks.items():
                    if tweak_data.get("check_status_func"):
                        try:
                            self._check_status_cached(tweak_key, tweak_data["check_status_func"])  # Update cache
                        except Exception:
                            print(f"Error updating cache for {tweak_key}")
            finally:
                self.update_lock.release()
                if manual:
                    print("Statuses updated manually.")

        threading.Thread(target=update_in_thread, daemon=True).start()

    def on_visibility_change(self, event):
        if event.widget == self.parent:
            if event.state == 0:
                self.visible = False
            elif not self.visible:
                self.visible = True
                self._schedule_ui_update()  # Restart UI updates
                self.update_status_manual()

    def _schedule_ui_update(self):
        if not self.visible:
            return

        UPDATE_INTERVAL = 10000  # Increase from 5000 to 10000ms

        async def batch_update():
            if not self.visible:
                return

            BATCH_SIZE = 5
            tweak_keys = list(self.tweaks.keys())

            for i in range(0, len(tweak_keys), BATCH_SIZE):
                if not self.visible:
                    break
                batch = tweak_keys[i:i + BATCH_SIZE]
                for tweak_key in batch:
                    self._update_switch_status(tweak_key)
                await asyncio.sleep(0.1)  # Small delay between batches

        asyncio.run_coroutine_threadsafe(batch_update(), loop)
        self.parent.after(UPDATE_INTERVAL, self._schedule_ui_update)


if __name__ == "__main__":
    app = ctk.CTk()
    app.title("ASX Hub Tweaks")
    app.geometry("1050x800")
    tweaks_tab = TweaksTab(app)
    app.mainloop()
