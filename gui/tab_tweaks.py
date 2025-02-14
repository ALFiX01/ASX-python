import os
import json
import sys
import threading
import tkinter as tk
import asyncio

try:
    import customtkinter as ctk
except ImportError:
    print("Error: CustomTkinter not found. Please install it using: pip install customtkinter")
    sys.exit(1)

from config import TWEAK_CATEGORIES, TWEAKS
from utils.system_tweaks import SystemTweaks

def load_settings(settings_file="settings.json"):
    """
    Загружает настройки из JSON-файла.
    При ошибке загрузки возвращает настройки по умолчанию.
    """
    try:
        with open(settings_file, "r") as f:
            settings = json.load(f)
            return settings
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading settings: {e}. Using default settings.")
        return {
            "appearance_mode": "System",
            "theme": "blue",
            "language": "Russian",
            "accent_color": "#1f6aa5"  # Default accent color
        }

# Глобальная настройка темы и стиля из настроек
settings = load_settings()
ctk.set_appearance_mode(settings.get("appearance_mode", "System"))
ctk.set_default_color_theme(settings.get("theme", "blue"))

def start_asyncio_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

# Создайте новый цикл событий и запустите его в отдельном потоке
loop = asyncio.new_event_loop()
threading.Thread(target=start_asyncio_loop, args=(loop,), daemon=True).start()

class TweaksTab:
    """
    Класс для создания вкладки «Твики».
    Здесь формируется боковая панель с категориями, область поиска и список твиков.
    Также реализована проверка и обновление состояния твиков в отдельном потоке.
    """

    def __init__(self, parent):
        self.parent = parent
        self.system_tweaks = SystemTweaks()
        self._update_id = None
        self.current_category = None
        self.search_cache = {}
        self.is_searching = False
        self.selected_category = None  # Текущая выбранная категория
        self.category_buttons = {}     # Словарь кнопок по категориям
        self.update_lock = threading.Lock()  # Lock для потокобезопасности

        # Определяем акцентный цвет из настроек
        self.accent_color = settings.get("accent_color", "#FF5733")

        # Настройка основного контейнера
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Создание боковой панели (сайдбар)
        self.sidebar = ctk.CTkFrame(
            self.main_frame,
            width=200,
            corner_radius=10,
            fg_color=("gray85", "gray17")
        )
        self.sidebar.grid(row=0, column=0, sticky="ns", padx=(0, 10), pady=5)
        self._create_sidebar()

        # Создание области поиска и контента
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_rowconfigure(1, weight=1)
        self._create_search_area()
        self._create_content_area()

        # Создание экземпляров твиков
        self.tweaks = {}
        for tweak_config in TWEAKS:
            self.tweaks[tweak_config['key']] = self._create_tweak_data(tweak_config)

        # Установка категории по умолчанию
        default_category = "Оптимизация и настройки"
        if default_category in self.category_buttons:
            self.select_category(default_category, self.category_buttons[default_category])
        else:
            self.show_category(default_category)

    def _create_sidebar(self):
        """Создаёт боковую панель с заголовком, разделителем и кнопками категорий."""
        header_label = ctk.CTkLabel(
            self.sidebar,
            text="Категории",
            font=("Roboto", 18, "bold"),
            fg_color="transparent",
            text_color=("gray10", "gray90")
        )
        header_label.pack(pady=(10, 5), padx=10)

        # Имитация разделителя с помощью CTkFrame
        separator = ctk.CTkFrame(
            self.sidebar,
            height=2,
            fg_color=("gray70", "gray30"),
            corner_radius=1
        )
        separator.pack(fill="x", padx=10, pady=(0, 10))

        for category in TWEAK_CATEGORIES:
            btn = ctk.CTkButton(
                self.sidebar,
                text=category,
                corner_radius=7,
                fg_color="transparent",
                hover_color=("gray70", "gray30"),
                text_color=("gray10", "gray90"),
                font=("Roboto", 14),
                command=lambda c=category, b=None: None  # временная заглушка
            )
            btn.pack(pady=8, padx=10, fill="x")
            btn.configure(command=lambda c=category, b=btn: self.select_category(c, b))
            self.category_buttons[category] = btn

    def select_category(self, category, button):
        """
        Обновляет состояние выбранной категории:
         – изменяет цвета кнопок,
         – сохраняет выбранную категорию,
         – отображает соответствующий контент.
        """
        self.selected_category = category
        for cat, btn in self.category_buttons.items():
            if cat == category:
                btn.configure(fg_color=self.accent_color, text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=("gray10", "gray90"))
        self.show_category(category)

    def _create_search_area(self):
        """Создаёт область поиска с полем ввода и кнопкой очистки."""
        self.search_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(6, 7))
        self.search_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="Поиск твиков...",
            height=38,
            corner_radius=8,
            border_width=2,
            border_color="gray25",
            fg_color=("gray85", "gray17"),
            font=("Roboto", 14)
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.search_entry.bind("<KeyRelease>", self.search_tweaks)
        self.search_entry.bind("<FocusIn>", self.start_search)
        self.search_entry.bind("<FocusOut>", self.end_search)

        button_width = 38
        clear_btn = ctk.CTkButton(
            self.search_frame,
            text="✕",
            width=button_width,
            height=38,
            corner_radius=8,
            fg_color=("gray85", "gray17"),
            hover_color=("gray70", "gray30"),
            border_width=2,
            border_color="gray25",
            command=self.clear_search,
            font=("Open Sans", 25),
            text_color=self.accent_color
        )
        clear_btn.grid(row=0, column=1)

    def _create_content_area(self):
        """Создаёт область для отображения списка твиков."""
        self.scrollable_content = ctk.CTkScrollableFrame(
            self.content_frame,
            corner_radius=10,
            fg_color=("gray85", "gray17")
        )
        self.scrollable_content.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=1)

    def clear_search(self):
        """Очищает поле поиска и возвращает отображение твиков для текущей категории."""
        self.search_entry.delete(0, tk.END)
        self.is_searching = False
        if self.current_category:
            self.setup_tweaks_page(self.current_category)
        else:
            self.setup_tweaks_page("Оптимизация и настройки")

    def _create_tweak_data(self, tweak_config):
        """
        Создаёт словарь с данными для твика.
        Если указан класс твика, создаётся его экземпляр, иначе используется метод из SystemTweaks.
        """
        tweak_data = {
            'category': tweak_config['category'],
            'instance': None,
            'switch_ref': None,
        }
        if tweak_config['class_name']:
            module_name = tweak_config.get('module', tweak_config['key'])
            module = __import__(f"utils.tweaks.{module_name}", fromlist=[tweak_config['class_name']])
            tweak_class = getattr(module, tweak_config['class_name'])
            tweak_data['instance'] = tweak_class()
            tweak_data['check_status_func'] = tweak_data['instance'].check_status
        else:
            tweak_data['check_status_func'] = getattr(
                self.system_tweaks, f"check_{tweak_config['key']}_status", None
            )

        tweak_data['toggle_command'] = getattr(self, f"toggle_{tweak_config['key']}", None)
        if tweak_data['toggle_command'] is None:
            print(f"Warning: toggle_{tweak_config['key']} method not found in TweaksTab.")

        return tweak_data

    def start_search(self, _=None):
        """Обрабатывает начало поиска, обновляя состояние рамки поля ввода."""
        self.is_searching = True
        self.update_search_entry_border_color()

    def end_search(self, _=None):
        """Обрабатывает окончание поиска, возвращая стандартный цвет рамки поля ввода."""
        self.is_searching = False
        self.update_search_entry_border_color()

    def update_search_entry_border_color(self, _=None):
        """
        Обновляет цвет рамки поля поиска в зависимости от режима и состояния поиска.
        Если ведётся поиск, цвет рамки равен акцентному.
        В противном случае для темной темы используется 'gray70', для светлой – 'gray25'.
        """
        mode = ctk.get_appearance_mode()  # Возвращает строку: "Dark" или "Light"
        if self.is_searching:
            border = self.accent_color
        else:
            border = "gray70" if mode.lower() == "dark" else "gray25"
        self.search_entry.configure(border_color=border)

    # --- Методы переключения твиков ---
    def toggle_spectre_meltdown(self):
        self._generic_toggle("spectre_meltdown",
                             self.system_tweaks.toggle_spectre_meltdown,
                             self.system_tweaks.toggle_spectre_meltdown)

    def toggle_nvidia_optimization(self):
        self._generic_toggle("nvidia_optimization",
                             self.system_tweaks.toggle_nvidia_optimization,
                             self.system_tweaks.toggle_nvidia_optimization)

    def toggle_hdcp(self):
        self._generic_toggle("hdcp",
                             self.system_tweaks.toggle_hdcp,
                             self.system_tweaks.toggle_hdcp)

    def toggle_power_throttling(self):
        self._generic_toggle("power_throttling",
                             self.system_tweaks.toggle_power_throttling,
                             self.system_tweaks.toggle_power_throttling)

    def toggle_uwp_background(self):
        self._generic_toggle("uwp_background",
                             self.system_tweaks.toggle_uwp_background,
                             self.system_tweaks.toggle_uwp_background)

    def toggle_FsoGameBar(self):
        self._generic_toggle("FsoGameBar",
                             self.system_tweaks.toggle_FsoGameBar,
                             self.system_tweaks.toggle_FsoGameBar)

    def toggle_power_plan(self):
        self._generic_toggle("power_plan",
                             self.system_tweaks.toggle_powerplan,
                             self.system_tweaks.toggle_powerplan)

    def toggle_fastboot(self):
        self._generic_toggle("fastboot",
                             self.system_tweaks.toggle_fastboot,
                             self.system_tweaks.toggle_fastboot)

    def toggle_notifications(self):
        tweak_instance = self.tweaks["notifications"]['instance']
        if self.tweaks["notifications"]['switch_ref'].get():
            success = tweak_instance.disable()
            if not success:
                self.tweaks["notifications"]['switch_ref'].deselect()
        else:
            success = tweak_instance.enable()
            if not success:
                self.tweaks["notifications"]['switch_ref'].select()

    def toggle_cortana(self):
        tweak_instance = self.tweaks["cortana"]['instance']
        if self.tweaks["cortana"]['switch_ref'].get():
            success = tweak_instance.disable()
            if not success:
                self.tweaks["cortana"]['switch_ref'].deselect()
        else:
            success = tweak_instance.enable()
            if not success:
                self.tweaks["cortana"]['switch_ref'].select()

    def _generic_toggle(self, tweak_key, enable_func, disable_func):
        """
        Универсальная функция для переключения твика:
         – обновляет состояние переключателя,
         – выводит сообщение в статус-бар.
        """
        switch_ref = self.tweaks[tweak_key]['switch_ref']
        status_bar = self.parent.winfo_toplevel().dynamic_status

        # Используем русское название, если доступно
        tweak_instance = self.tweaks[tweak_key].get('instance')
        tweak_name = getattr(tweak_instance.metadata, 'title', None) or tweak_key

        if switch_ref.get():
            success = enable_func()
            if success:
                status_bar.update_text(f"Твик '{tweak_name}' успешно включен", duration=2000)
            else:
                switch_ref.deselect()
                status_bar.update_text(f"Ошибка при включении твика '{tweak_name}'", duration=3000)
        else:
            success = disable_func()
            if success:
                status_bar.update_text(f"Твик '{tweak_name}' успешно выключен", duration=2000)
            else:
                switch_ref.select()
                status_bar.update_text(f"Ошибка при выключении твика '{tweak_name}'", duration=3000)

    def setup_tweaks_page(self, category, search_term=""):
        """
        Очищает текущее содержимое и заполняет область новыми твиками,
        отфильтрованными по категории или поисковому запросу.
        """
        for widget in self.scrollable_content.winfo_children():
            widget.destroy()

        container = ctk.CTkFrame(self.scrollable_content, corner_radius=8, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=5, pady=5)

        if search_term:
            if search_term in self.search_cache:
                filtered_tweaks = self.search_cache[search_term]
            else:
                filtered_tweaks = {}
                for key, data in self.tweaks.items():
                    title = data['instance'].metadata.title if data['instance'] else key.replace("_", " ").title()
                    desc = data['instance'].metadata.description if data['instance'] else "Нет описания."
                    if search_term.lower() in title.lower() or search_term.lower() in desc.lower():
                        filtered_tweaks[key] = data
                self.search_cache[search_term] = filtered_tweaks
        else:
            filtered_tweaks = {k: v for k, v in self.tweaks.items() if v['category'] == category}

        for tweak_key, tweak_data in filtered_tweaks.items():
            card = ctk.CTkFrame(
                container,
                corner_radius=10,
                fg_color=("gray90", "gray20"),
                border_width=1,
                border_color=("gray80", "gray30")
            )
            card.pack(fill="x", expand=True, padx=10, pady=8)

            text_frame = ctk.CTkFrame(card, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            text_frame.grid_rowconfigure(0, weight=1)
            text_frame.grid_columnconfigure(0, weight=1)

            if tweak_data['instance']:
                title = tweak_data['instance'].metadata.title
                description = tweak_data['instance'].metadata.description
            else:
                title = tweak_key.replace("_", " ").title()
                description = "Нет описания."

            title_label = ctk.CTkLabel(text_frame, text=title, font=("Roboto", 14, "bold"))
            title_label.grid(row=0, column=0, sticky="w")
            desc_label = ctk.CTkLabel(
                text_frame,
                text=description,
                font=("Roboto", 12),
                justify="left",
                text_color="#7E7E7E",
                wraplength=500
            )
            desc_label.grid(row=1, column=0, sticky="w", pady=(2, 0))

            tweak_switch = ctk.CTkSwitch(
                card,
                text="",
                command=tweak_data['toggle_command'],
                onvalue=1,
                offvalue=0,
                font=("Roboto", 12),
                # При включении используется акцентный цвет
                progress_color=self.accent_color,
                # Опционально: цвет кнопки переключателя (можно оставить по умолчанию)
                button_color=("white", "white")
            )

            tweak_switch.pack(side="right", padx=10, pady=10)
            tweak_switch.tweak_key = tweak_key
            tweak_data['switch_ref'] = tweak_switch

            # Обновление состояния переключателя после фильтрации
            self._update_switch_status(tweak_key)

        if not self.is_searching:
            if self._update_id is not None:
                self.parent.after_cancel(self._update_id)
            self.update_status()

    def _update_switch_status(self, tweak_key):
        """Обновляет состояние переключателя после фильтрации."""
        tweak_data = self.tweaks.get(tweak_key)
        if tweak_data and tweak_data.get('check_status_func'):
            is_enabled = tweak_data['check_status_func']()
            switch = tweak_data['switch_ref']
            if switch and switch.winfo_exists():
                if is_enabled:
                    switch.select()
                else:
                    switch.deselect()

    def show_category(self, category):
        """Запоминает выбранную категорию и отображает соответствующую страницу твиков."""
        self.current_category = category
        self.setup_tweaks_page(category)

    def search_tweaks(self, event):
        """Обрабатывает поиск твиков по введенному тексту асинхронно."""
        search_term = self.search_entry.get()
        self.update_search_entry_border_color()
        if search_term:
            self.is_searching = True
            asyncio.run_coroutine_threadsafe(self.setup_tweaks_page_async(search_term=search_term), loop)
        else:
            self.is_searching = False
            if self.current_category:
                self.setup_tweaks_page(self.current_category)
            else:
                self.setup_tweaks_page("Оптимизация и настройки")

    async def setup_tweaks_page_async(self, search_term=""):
        """Асинхронно обновляет страницу твиков."""
        await asyncio.sleep(0.1)  # Имитация асинхронной задержки
        self.parent.after(0, self.setup_tweaks_page, None, search_term)

    def update_status_manual(self):
        """Обновляет статусы твиков вручную (например, по нажатию кнопки)."""
        self.update_status(manual=True)

    def update_status(self, manual=False):
        """
        Проверяет и обновляет состояние всех твиков в отдельном потоке.
        Используется блокировка для предотвращения одновременных обновлений.
        """
        if self._update_id:
            self.parent.after_cancel(self._update_id)
            self._update_id = None

        if not self.update_lock.acquire(blocking=False):
            if not manual:
                self._update_id = self.parent.after(100, self.update_status)
            return

        try:
            def update_in_thread():
                try:
                    for tweak_key, tweak_data in self.tweaks.items():
                        switch = tweak_data.get('switch_ref')
                        check_status_func = tweak_data.get('check_status_func')
                        if switch is not None and check_status_func and switch.winfo_exists():
                            try:
                                is_enabled = check_status_func()
                                self.parent.after(0, self._update_switch, switch, is_enabled)
                            except Exception as e:
                                print(f"Error updating status for {tweak_key}: {e}")
                finally:
                    if not self.is_searching:
                        self.parent.after(5000, self.update_status)
                    self.update_lock.release()

                if manual:
                    print("Statuses updated manually by 'R' button.")

            threading.Thread(target=update_in_thread, daemon=True).start()

        except Exception as e:
            print(f"An unexpected error occurred during the update: {e}")
            self.update_lock.release()

    def _update_switch(self, switch, is_enabled):
        """Обновляет состояние переключателя на главном потоке."""
        try:
            if switch.winfo_exists():
                if is_enabled:
                    switch.select()
                else:
                    switch.deselect()
        except tk.TclError as e:
            print(f"TclError updating switch: {e}")

if __name__ == "__main__":
    app = ctk.CTk()
    app.title("ASX Hub Tweaks")
    app.geometry("1050x800")
    # Для корректной работы status_bar предполагается, что основной класс приложения создаёт динамический статус-бар.
    # Если его нет, можно создать его здесь для теста:
    # app.dynamic_status = DynamicStatusBar(app, default_text="Статус приложения", height=25)
    tweaks_tab = TweaksTab(app)
    app.mainloop()
