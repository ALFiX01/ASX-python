import os
import tkinter as tk
try:
    import customtkinter as ctk
except ImportError:
    print("Error: CustomTkinter not found. Please install it using: pip install customtkinter")
    import sys
    sys.exit(1)

from config import TWEAK_CATEGORIES, TWEAKS  # Импортируем TWEAKS из config.py
from utils.system_tweaks import SystemTweaks


class TweaksTab:
    def __init__(self, parent):
        self.parent = parent
        self.system_tweaks = SystemTweaks()

        # === Настройка темы и внешнего вида ===
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # === Левая боковая панель (категории) ===
        self.sidebar = ctk.CTkFrame(
            self.parent,
            width=150,
            corner_radius=10,
            fg_color=("gray85", "gray17")  # светло-серый фон для светлой темы
        )
        self.sidebar.pack(side="left", fill="y", padx=5, pady=5)

        # === Основная область контента ===
        self.content = ctk.CTkScrollableFrame(self.parent) # Используем ctk.CTkScrollableFrame вместо ctk.CTkFrame
        self.content.pack(side="left", fill="both", expand=True, padx=5, pady=5)  # Исправлено: fill="both"

        # === Передача функций-команд в TWEAKS ===
        TWEAKS[0]['toggle_command'] = self.toggle_power_plan
        TWEAKS[1]['toggle_command'] = self.toggle_visual_effects
        TWEAKS[0]['check_status_func'] = self.system_tweaks.check_power_plan_status
        TWEAKS[1]['check_status_func'] = self.system_tweaks.check_game_bar_status

        # === Связывание новых твиков с методами SystemTweaks ===
        TWEAKS[2]['toggle_command'] = self.toggle_spectre_meltdown
        TWEAKS[2]['check_status_func'] = self.system_tweaks.check_spectre_meltdown_status

        TWEAKS[3]['toggle_command'] = self.toggle_nvidia_optimization
        TWEAKS[3]['check_status_func'] = self.system_tweaks.check_nvidia_optimization_status

        TWEAKS[4]['toggle_command'] = self.toggle_hdcp
        TWEAKS[4]['check_status_func'] = self.system_tweaks.check_hdcp_status

        TWEAKS[5]['toggle_command'] = self.toggle_power_throttling
        TWEAKS[5]['check_status_func'] = self.system_tweaks.check_power_throttling_status

        TWEAKS[6]['toggle_command'] = self.toggle_uwp_background
        TWEAKS[6]['check_status_func'] = self.system_tweaks.check_uwp_background_status

        TWEAKS[7]['toggle_command'] = self.toggle_notifications
        TWEAKS[7]['check_status_func'] = self.system_tweaks.check_notifications_status

        TWEAKS[8]['toggle_command'] = self.toggle_cortana
        TWEAKS[8]['check_status_func'] = self.system_tweaks.check_cortana_status

        self.setup_categories()
        self.setup_optimization_page()

    # === Добавьте заглушки для новых toggle_command методов в TweaksTab ===
    def toggle_spectre_meltdown(self):
        """Toggle Spectre/Meltdown mitigations"""
        if TWEAKS[2]['switch_ref'].get():
            success = self.system_tweaks.optimize_spectre_meltdown()
            if not success:
                TWEAKS[2]['switch_ref'].deselect()
        else:
            success = self.system_tweaks.restore_default_spectre_meltdown()
            if not success:
                TWEAKS[2]['switch_ref'].select()

    def toggle_nvidia_optimization(self):
        """Toggle Nvidia optimization"""
        if TWEAKS[3]['switch_ref'].get():
            success = self.system_tweaks.optimize_nvidia_optimization()
            if not success:
                TWEAKS[3]['switch_ref'].deselect()
        else:
            success = self.system_tweaks.restore_default_nvidia_optimization()
            if not success:
                TWEAKS[3]['switch_ref'].select()

    def toggle_hdcp(self):
        """Toggle HDCP"""
        if TWEAKS[4]['switch_ref'].get():
            success = self.system_tweaks.toggle_hdcp()
            if not success:
                TWEAKS[4]['switch_ref'].deselect()
        else:
            success = self.system_tweaks.toggle_hdcp()  # Assuming toggle_hdcp toggles state
            if not success:
                TWEAKS[4]['switch_ref'].select()

    def toggle_power_throttling(self):
        """Toggle Power Throttling"""
        if TWEAKS[5]['switch_ref'].get():
            success = self.system_tweaks.toggle_power_throttling()
            if not success:
                TWEAKS[5]['switch_ref'].deselect()
        else:
            success = self.system_tweaks.toggle_power_throttling()  # Assuming toggle_power_throttling toggles state
            if not success:
                TWEAKS[5]['switch_ref'].select()

    def toggle_uwp_background(self):
        """Toggle UWP Background Apps"""
        if TWEAKS[6]['switch_ref'].get():
            success = self.system_tweaks.toggle_uwp_background()
            if not success:
                TWEAKS[6]['switch_ref'].deselect()
        else:
            success = self.system_tweaks.toggle_uwp_background()  # Assuming toggle_uwp_background toggles state
            if not success:
                TWEAKS[6]['switch_ref'].select()

    def toggle_notifications(self):
        """Toggle Notifications"""
        if TWEAKS[7]['switch_ref'].get():
            success = self.system_tweaks.toggle_notifications()
            if not success:
                TWEAKS[7]['switch_ref'].deselect()
        else:
            success = self.system_tweaks.toggle_notifications()  # Assuming toggle_notifications toggles state
            if not success:
                TWEAKS[7]['switch_ref'].select()

    def toggle_cortana(self):
        """Toggle Cortana"""
        if TWEAKS[8]['switch_ref'].get():
            success = self.system_tweaks.toggle_cortana()
            if not success:
                TWEAKS[8]['switch_ref'].deselect()
        else:
            success = self.system_tweaks.toggle_cortana()  # Assuming toggle_cortana toggles state
            if not success:
                TWEAKS[8]['switch_ref'].select()

    def setup_categories(self):
        """Настройка кнопок категорий в боковой панели"""
        for category in TWEAK_CATEGORIES:
            btn = ctk.CTkButton(
                self.sidebar,
                text=category,
                command=lambda c=category: self.show_category(c),
                corner_radius=9,
                fg_color=("gray85", "gray17"),  # цвет фона как у sidebar
                hover_color=("gray75", "gray25"),  # сплошной цвет при наведении
                text_color=("gray10", "gray90"),  # темный текст для светлой темы
                text_color_disabled="gray60"
            )
            btn.pack(pady=5, padx=10, fill="x")

    def setup_optimization_page(self):
        """Настройка страницы оптимизации и настроек - Твики генерируются динамически из config.py"""
        # Очистка текущего контента
        for widget in self.content.winfo_children():
            widget.destroy()

        frame = ctk.CTkFrame(self.content, corner_radius=0) # frame внутри ScrollableFrame
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # === Динамическое создание блоков твиков ===
        for tweak_config in TWEAKS:  # Используем TWEAKS из config.py
            tweak_frame = ctk.CTkFrame(frame, corner_radius=10)
            tweak_frame.pack(fill="x", padx=10, pady=1)

            text_frame = ctk.CTkFrame(tweak_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True, padx=10, pady=8)


            # Используем grid вместо pack для text_frame
            text_frame.grid_rowconfigure(0, weight=1) # Важно для вертикального растягивания
            text_frame.grid_columnconfigure(0, weight=1)


            tweak_label = ctk.CTkLabel(
                text_frame,
                text=tweak_config['title'],  # Заголовок из конфигурации
                font=("Arial", 16, "bold")
            )
            # tweak_label.pack(anchor="w") # Заменено на grid
            tweak_label.grid(row=0, column=0, sticky="w")


            tweak_desc = ctk.CTkLabel(
                text_frame,
                text=tweak_config['description'],  # Описание из конфигурации
                font=("Arial", 11),
                justify="left",
                text_color="#808080",
                wraplength=500 # Добавляем перенос текста
            )
            # tweak_desc.pack(anchor="w", pady=(2, 0)) # Заменено на grid
            tweak_desc.grid(row=1, column=0, sticky="w", pady=(2,0))



            tweak_switch = ctk.CTkSwitch(
                tweak_frame,
                text="",
                command=tweak_config['toggle_command']  # Функция переключения из конфигурации
            )
            tweak_switch.pack(side="right", padx=10, pady=8)

            # Сохраняем ссылку на switch, чтобы можно было обновить состояние
            tweak_config['switch_ref'] = tweak_switch  # Сохраняем ссылку в конфигурации

            # === Разделительная линия после каждого твика, кроме последнего ===
            if tweak_config != TWEAKS[-1]:  # Не добавляем разделитель после последнего элемента
                separator = ctk.CTkFrame(frame, height=1, fg_color="grey70")
                separator.pack(fill="x", padx=10, pady=(10, 5))

        # Обновление начальных состояний переключателей
        self.update_status()

    def show_category(self, category):
        """Отображение контента для выбранной категории"""
        # Очистка текущего контента
        for widget in self.content.winfo_children():
            widget.destroy()

        if category == "Оптимизация и настройки":
            self.setup_optimization_page()

    def update_status(self):
        """Обновление состояния переключателей на основе текущего состояния системы"""
        for tweak_config in TWEAKS:  # Обновляем состояние для каждого твика
            switch = tweak_config['switch_ref']  # Получаем ссылку на switch из конфигурации
            check_status_func = tweak_config['check_status_func']  # Функция проверки статуса
            if check_status_func():
                switch.select()
            else:
                switch.deselect()

    def toggle_power_plan(self):
        """Переключение оптимизации плана электропитания"""
        if TWEAKS[0]['switch_ref'].get():  # Используем ссылку на switch из TWEAKS[0]
            success = self.system_tweaks.optimize_power_plan()
            if not success:
                TWEAKS[0]['switch_ref'].deselect()  # Отменить выбор, если оптимизация не удалась
        else:
            success = self.system_tweaks.restore_default_power_plan()
            if not success:
                TWEAKS[0]['switch_ref'].select()  # Вернуть выбор, если восстановление не удалось

    def toggle_visual_effects(self):
        """Переключение оптимизации визуальных эффектов"""
        if TWEAKS[1]['switch_ref'].get():  # Используем ссылку на switch из TWEAKS[1]
            success = self.system_tweaks.optimize_visual_effects()
            if not success:
                TWEAKS[1]['switch_ref'].deselect()  # Отменить выбор, если оптимизация не удалась
        else:
            success = self.system_tweaks.restore_default_visual_effects()
            if not success:
                TWEAKS[1]['switch_ref'].select()  # Вернуть выбор, если восстановление не удалось


if __name__ == "__main__":
    app = ctk.CTk()
    app.title("ASX Hub Tweaks")
    app.geometry("800x700")

    tweaks_tab = TweaksTab(app)

    app.mainloop()