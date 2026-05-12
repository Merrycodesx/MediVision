"""
MediVision – ThemeManager
Defines light (Medical Blue) and dark (Navy) color palettes.
"""

class ThemeManager:
    LIGHT = {
        "bg":             "#EBF2FF",
        "sidebar":        "#FFFFFF",
        "card":           "#FFFFFF",
        "card_alt":       "#F4F7FF",
        "text_primary":   "#0E2A47",
        "text_secondary": "#4B6680",
        "text_muted":     "#8FA3BB",
        "primary":        "#2A6FDB",
        "primary_hover":  "#1F59B6",
        "primary_light":  "#DDE9FF",
        "border":         "#D0DCEE",
        "success":        "#22C55E",
        "success_bg":     "#DCFCE7",
        "warning":        "#F59E0B",
        "warning_bg":     "#FEF3C7",
        "danger":         "#EF4444",
        "danger_bg":      "#FEE2E2",
        "input_bg":       "#F8FAFF",
        "table_header":   "#F0F5FF",
        "table_row_alt":  "#F8FAFF",
        "separator":      "#E4EAF5",
        "topbar":         "#FFFFFF",
        "sidebar_active": "#DDE9FF",
        "sidebar_hover":  "#F0F5FF",
    }

    DARK = {
        "bg":             "#0B1E2D",
        "sidebar":        "#0F2132",
        "card":           "#111F2E",
        "card_alt":       "#162636",
        "text_primary":   "#E5EAF0",
        "text_secondary": "#8FA3BB",
        "text_muted":     "#4B6680",
        "primary":        "#3B82F6",
        "primary_hover":  "#2563EB",
        "primary_light":  "#172A48",
        "border":         "#1E3144",
        "success":        "#22C55E",
        "success_bg":     "#052E16",
        "warning":        "#F59E0B",
        "warning_bg":     "#1C1A08",
        "danger":         "#F87171",
        "danger_bg":      "#3B0808",
        "input_bg":       "#162636",
        "table_header":   "#0F2132",
        "table_row_alt":  "#121F2D",
        "separator":      "#1E3144",
        "topbar":         "#0F2132",
        "sidebar_active": "#172A48",
        "sidebar_hover":  "#152138",
    }

    def __init__(self):
        self.is_dark = False

    def get_colors(self):
        return self.DARK if self.is_dark else self.LIGHT

    def toggle(self):
        self.is_dark = not self.is_dark
