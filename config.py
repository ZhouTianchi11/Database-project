import customtkinter as ctk

def set_theme():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

COLOR = {
    "primary": "#3b82f6",
    "success": "#10b981",
    "danger": "#ef4444",
    "gray": "#64748b",
    "light": "#f8fafc"
}

FONT = {
    "title": ("Arial", 24, "bold"),
    "subtitle": ("Arial", 16, "bold"),
    "text": ("Arial", 14),
    "small": ("Arial", 12)
}