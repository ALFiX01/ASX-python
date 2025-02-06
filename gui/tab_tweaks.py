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

        power_label = ctk.CTkLabel(power_frame, text="План электропитания ASX Hub")
        power_label.pack(side="left", padx=5)

        # Add status label for power plan
        self.power_status = ctk.CTkLabel(
            power_frame,
            text="ВЫКЛЮЧЕНО",
            text_color="red"
        )
        self.power_status.pack(side="left", padx=5)

        self.power_switch = ctk.CTkSwitch(
            power_frame,
            text="",
            command=self.toggle_power_plan
        )
        self.power_switch.pack(side="right", padx=5)

        # Visual Effects Optimization
        visual_frame = ctk.CTkFrame(frame)
        visual_frame.pack(fill="x", padx=10, pady=5)

        visual_label = ctk.CTkLabel(visual_frame, text="FSO и GameBar")
        visual_label.pack(side="left", padx=5)

        # Add status label for GameBar
        self.visual_status = ctk.CTkLabel(
            visual_frame,
            text="ВЫКЛЮЧЕНО",
            text_color="red"
        )
        self.visual_status.pack(side="left", padx=5)

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
        """Update status labels and switches based on current system state"""
        # Check power plan status
        power_enabled = self.system_tweaks.check_power_plan_status()
        if power_enabled:
            self.power_status.configure(text="ВКЛЮЧЕНО", text_color="green")
            self.power_switch.select()
        else:
            self.power_status.configure(text="ВЫКЛЮЧЕНО", text_color="red")
            self.power_switch.deselect()

        # Check GameBar status
        gamebar_enabled = self.system_tweaks.check_game_bar_status()
        if gamebar_enabled:
            self.visual_status.configure(text="ВКЛЮЧЕНО", text_color="green")
            self.visual_switch.select()
        else:
            self.visual_status.configure(text="ВЫКЛЮЧЕНО", text_color="red")
            self.visual_switch.deselect()

    def toggle_power_plan(self):
        """Toggle power plan optimization"""
        if self.power_switch.get():
            success = self.system_tweaks.optimize_power_plan()
            if success:
                self.power_status.configure(text="ВКЛЮЧЕНО", text_color="green")
            else:
                self.power_switch.deselect()
                self.power_status.configure(text="ВЫКЛЮЧЕНО", text_color="red")
        self.update_status()

    def toggle_visual_effects(self):
        """Toggle visual effects optimization"""
        if self.visual_switch.get():
            success = self.system_tweaks.optimize_visual_effects()
            if success:
                self.visual_status.configure(text="ВКЛЮЧЕНО", text_color="green")
            else:
                self.visual_switch.deselect()
                self.visual_status.configure(text="ВЫКЛЮЧЕНО", text_color="red")
        self.update_status()