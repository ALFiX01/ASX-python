import os
import tkinter as tk
try:
    import customtkinter as ctk
except ImportError:
    print("Error: CustomTkinter not found. Please install it using: pip install customtkinter")
    import sys
    sys.exit(1)

from config import TWEAK_CATEGORIES, TWEAKS
from utils.system_tweaks import SystemTweaks
from utils.tweaks.notifications import NotificationsTweak
from utils.tweaks.cortana import CortanaTweak


class TweaksTab:
    def __init__(self, parent):
        self.parent = parent
        self.system_tweaks = SystemTweaks()
        self._update_id = None

        # === UI Setup ===
        self.sidebar = ctk.CTkFrame(
            self.parent,
            width=150,
            corner_radius=10,
            fg_color=("gray85", "gray17")
        )
        self.sidebar.pack(side="left", fill="y", padx=5, pady=5)

        self.content = ctk.CTkScrollableFrame(self.parent)
        self.content.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # === Create Tweak Instances Dynamically ===
        self.tweaks = {}
        for tweak_config in TWEAKS:
            self.tweaks[tweak_config['key']] = self._create_tweak_data(tweak_config)

        self.setup_categories()
        self.show_category("Оптимизация и настройки")

    def _create_tweak_data(self, tweak_config):
        """Creates the tweak data dictionary."""
        tweak_data = {
            'category': tweak_config['category'],
            'instance': None,
            'switch_ref': None,  # Will be set later
        }

        if tweak_config['class_name']:
            module_name = tweak_config.get('module', tweak_config['key'])
            module = __import__(f"utils.tweaks.{module_name}", fromlist=[tweak_config['class_name']])
            tweak_class = getattr(module, tweak_config['class_name'])
            tweak_data['instance'] = tweak_class()
            tweak_data['check_status_func'] = tweak_data['instance'].check_status
        else:
            tweak_data['check_status_func'] = getattr(self.system_tweaks, f"check_{tweak_config['key']}_status", None)

        tweak_data['toggle_command'] = getattr(self, f"toggle_{tweak_config['key']}", None)
        if tweak_data['toggle_command'] is None:
            print(f"Warning: toggle_{tweak_config['key']} method not found in TweaksTab.")

        return tweak_data

    # --- Tweak Toggle Functions ---
    def toggle_spectre_meltdown(self):
        self._generic_toggle("spectre_meltdown", self.system_tweaks.toggle_spectre_meltdown, self.system_tweaks.toggle_spectre_meltdown)
    def toggle_nvidia_optimization(self):
        self._generic_toggle("nvidia_optimization", self.system_tweaks.toggle_nvidia_optimization, self.system_tweaks.toggle_nvidia_optimization)
    def toggle_hdcp(self):
        self._generic_toggle("hdcp", self.system_tweaks.toggle_hdcp, self.system_tweaks.toggle_hdcp)
    def toggle_power_throttling(self):
        self._generic_toggle("power_throttling", self.system_tweaks.toggle_power_throttling, self.system_tweaks.toggle_power_throttling)
    def toggle_uwp_background(self):
        self._generic_toggle("uwp_background", self.system_tweaks.toggle_uwp_background, self.system_tweaks.toggle_uwp_background)
    def toggle_FsoGameBar(self):
        self._generic_toggle("FsoGameBar", self.system_tweaks.toggle_FsoGameBar, self.system_tweaks.toggle_FsoGameBar)
    def toggle_power_plan(self):
        self._generic_toggle("power_plan", self.system_tweaks.toggle_powerplan, self.system_tweaks.toggle_powerplan)

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
        switch_ref = self.tweaks[tweak_key]['switch_ref']
        if switch_ref.get():
            success = enable_func()
            if not success:
                switch_ref.deselect()
        else:
            success = disable_func()
            if not success:
                switch_ref.select()

    def setup_categories(self):
        """Category button setup."""
        for category in TWEAK_CATEGORIES:
            btn = ctk.CTkButton(
                self.sidebar,
                text=category,
                command=lambda c=category: self.show_category(c),
                corner_radius=9,
                fg_color=("gray85", "gray17"),
                hover_color=("gray75", "gray25"),
                text_color=("gray10", "gray90"),
                text_color_disabled="gray60"
            )
            btn.pack(pady=5, padx=10, fill="x")

    def setup_tweaks_page(self, category):
        """Sets up the tweaks page for a given category."""
        for widget in self.content.winfo_children():
            widget.destroy()

        frame = ctk.CTkFrame(self.content, corner_radius=0)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        filtered_tweaks = {k: v for k, v in self.tweaks.items() if v['category'] == category}

        for tweak_key, tweak_data in filtered_tweaks.items():
            tweak_frame = ctk.CTkFrame(frame, corner_radius=10)
            tweak_frame.pack(fill="x", padx=10, pady=1)

            text_frame = ctk.CTkFrame(tweak_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True, padx=10, pady=8)
            text_frame.grid_rowconfigure(0, weight=1)
            text_frame.grid_columnconfigure(0, weight=1)

            if tweak_data['instance']:
                title = tweak_data['instance'].metadata.title
                description = tweak_data['instance'].metadata.description
            else:
                title = tweak_key.replace("_", " ").title()
                description = "No description available."

            tweak_label = ctk.CTkLabel(text_frame, text=title, font=("Arial", 16, "bold"))
            tweak_label.grid(row=0, column=0, sticky="w")

            tweak_desc = ctk.CTkLabel(
                text_frame,
                text=description,
                font=("Arial", 11),
                justify="left",
                text_color="#808080",
                wraplength=500
            )
            tweak_desc.grid(row=1, column=0, sticky="w", pady=(2, 0))

            # --- Create the switch and store the tweak key ---
            tweak_switch = ctk.CTkSwitch(
                tweak_frame,
                text="",
                command=tweak_data['toggle_command']
            )
            tweak_switch.pack(side="right", padx=10, pady=8)
            tweak_switch.tweak_key = tweak_key  # Store the key!
            tweak_data['switch_ref'] = tweak_switch


            tweak_keys = list(filtered_tweaks.keys())
            if tweak_key != tweak_keys[-1]:
                separator = ctk.CTkFrame(frame, height=1, fg_color="grey70")
                separator.pack(fill="x", padx=10, pady=(10, 5))

        if self._update_id is not None:
            self.parent.after_cancel(self._update_id)
        # Use after() with a delay
        self._update_id = self.parent.after(50, self.update_status)


    def show_category(self, category):
        """Show content for category."""
        self.setup_tweaks_page(category)

    def update_status(self):
        """Update switch states."""
        for tweak_key, tweak_data in self.tweaks.items():
            switch = tweak_data.get('switch_ref')
            check_status_func = tweak_data.get('check_status_func')

            # --- Check for existence using winfo_exists() ---
            if switch is not None and check_status_func and switch.winfo_exists():
                if check_status_func():
                    switch.select()
                else:
                    switch.deselect()
if __name__ == "__main__":
    app = ctk.CTk()
    app.title("ASX Hub Tweaks")
    app.geometry("800x700")
    tweaks_tab = TweaksTab(app)
    app.mainloop()