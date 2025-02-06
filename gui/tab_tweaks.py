import os
import tkinter as tk
try:
    import customtkinter as ctk
except ImportError:
    print("Error: CustomTkinter not found. Please install it using: pip install customtkinter")
    import sys
    sys.exit(1)

from config import TWEAK_CATEGORIES
from utils.system_tweaks import SystemTweaks

class TweaksTab:
    def __init__(self, parent):
        self.parent = parent
        self.system_tweaks = SystemTweaks()

        # Create left sidebar for categories
        self.sidebar = ctk.CTkFrame(self.parent, width=200)
        self.sidebar.pack(side="left", fill="y", padx=5, pady=5)

        # Create main content area
        self.content = ctk.CTkFrame(self.parent)
        self.content.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.setup_categories()
        self.setup_optimization_page()

    def setup_categories(self):
        """Setup category buttons in sidebar"""
        for category in TWEAK_CATEGORIES:
            btn = ctk.CTkButton(
                self.sidebar,
                text=category,
                command=lambda c=category: self.show_category(c)
            )
            btn.pack(pady=5, padx=10, fill="x")

    def setup_optimization_page(self):
        """Setup the optimization and settings page"""
        # Clear current content
        for widget in self.content.winfo_children():
            widget.destroy()

        frame = ctk.CTkFrame(self.content)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Power Plan Optimization
        power_frame = ctk.CTkFrame(frame)
        power_frame.pack(fill="x", padx=10, pady=5)

        # Create text frame for title and description
        power_text_frame = ctk.CTkFrame(power_frame, fg_color="transparent")
        power_text_frame.pack(side="left", fill="x", expand=True, padx=5)

        power_label = ctk.CTkLabel(
            power_text_frame,
            text="План электропитания ASX Hub",
            font=("Arial", 14, "bold")
        )
        power_label.pack(anchor="w")

        power_desc = ctk.CTkLabel(
            power_text_frame,
            text="Оптимизированный план электропитания для максимальной производительности.\nУменьшает задержки и увеличивает FPS в играх.",
            font=("Arial", 12),
            justify="left"
        )
        power_desc.pack(anchor="w")

        self.power_switch = ctk.CTkSwitch(
            power_frame,
            text="",
            command=self.toggle_power_plan
        )
        self.power_switch.pack(side="right", padx=5)

        # Visual Effects Optimization
        visual_frame = ctk.CTkFrame(frame)
        visual_frame.pack(fill="x", padx=10, pady=(15, 5))

        # Create text frame for title and description
        visual_text_frame = ctk.CTkFrame(visual_frame, fg_color="transparent")
        visual_text_frame.pack(side="left", fill="x", expand=True, padx=5)

        visual_label = ctk.CTkLabel(
            visual_text_frame,
            text="FSO и GameBar",
            font=("Arial", 14, "bold")
        )
        visual_label.pack(anchor="w")

        visual_desc = ctk.CTkLabel(
            visual_text_frame,
            text="Оптимизация игровых настроек Windows для лучшей производительности.\nОтключает ненужные визуальные эффекты и игровую панель Windows.",
            font=("Arial", 12),
            justify="left"
        )
        visual_desc.pack(anchor="w")

        self.visual_switch = ctk.CTkSwitch(
            visual_frame,
            text="",
            command=self.toggle_visual_effects
        )
        self.visual_switch.pack(side="right", padx=5)

        # Update initial states
        self.update_status()

    def show_category(self, category):
        """Show content for selected category"""
        # Clear current content
        for widget in self.content.winfo_children():
            widget.destroy()

        if category == "Оптимизация и настройки":
            self.setup_optimization_page()

    def update_status(self):
        """Update switches based on current system state"""
        # Check power plan status
        power_enabled = self.system_tweaks.check_power_plan_status()
        if power_enabled:
            self.power_switch.select()
        else:
            self.power_switch.deselect()

        # Check GameBar status
        gamebar_enabled = self.system_tweaks.check_game_bar_status()
        if gamebar_enabled:
            self.visual_switch.select()
        else:
            self.visual_switch.deselect()

    def toggle_power_plan(self):
        """Toggle power plan optimization"""
        if self.power_switch.get():
            success = self.system_tweaks.optimize_power_plan()
            if not success:
                self.power_switch.deselect()
        else:
            success = self.system_tweaks.restore_default_power_plan()
            if not success:
                self.power_switch.select()

    def toggle_visual_effects(self):
        """Toggle visual effects optimization"""
        if self.visual_switch.get():
            success = self.system_tweaks.optimize_visual_effects()
            if not success:
                self.visual_switch.deselect()