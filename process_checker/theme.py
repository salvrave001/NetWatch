"""NetWatch design tokens."""

from __future__ import annotations

COLORS = {
    "bg": "#0D0D0D",
    "bg_panel": "#111111",
    "bg_row": "#0D0D0D",
    "bg_row_alt": "#141414",
    "bg_row_hover": "#1A1A1A",
    "bg_row_selected": "#1F1214",
    "border": "#333333",
    "border_dim": "#222222",
    "text": "#FFFFFF",
    "text_dim": "#A0A0A0",
    "text_muted": "#666666",
    "accent": "#FF3B3F",
    "accent_dim": "#CC2F32",
    "accent_glow": "#FF3B3F33",
    "success": "#3DFF9A",
    "warning": "#FFB84D",
}

FONTS = {
    "title": ("Segoe UI", 22, "bold"),
    "heading": ("Segoe UI", 12, "bold"),
    "body": ("Consolas", 13),
    "body_sm": ("Consolas", 12),
    "caption": ("Segoe UI", 11),
    "mono_lg": ("Consolas", 16, "bold"),
}

SIZES = {
    "btn_height": 38,
    "entry_height": 38,
    "chip_height": 34,
    "chip_width": 72,
    "dot": 8,
    "sidebar": 200,
}

SORT_KEYS = {
    "protocol": "protocol",
    "local": "local_addr",
    "remote": "remote_addr",
    "state": "state",
    "pid": "pid",
    "process": "process_name",
}

QUICK_PORTS = (3000, 4200, 5000, 5173, 5432, 6379, 8000, 8080, 8443, 9000, 27017, 3306)

STATE_COLORS = {
    "LISTENING": COLORS["accent"],
    "ESTABLISHED": COLORS["success"],
    "TIME_WAIT": COLORS["text_muted"],
    "CLOSE_WAIT": COLORS["warning"],
    "FIN_WAIT_2": COLORS["warning"],
    "SYN_SENT": COLORS["text_dim"],
    "SYN_RECEIVED": COLORS["text_dim"],
}
