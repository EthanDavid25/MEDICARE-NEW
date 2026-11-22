"""
MEDICARE Kivy Theme and Responsive Layout Configuration.
Navy Blue, White, and Light Blue Healthcare Palette.
"""
from kivy.utils import get_color_from_hex
from kivy.core.window import Window

# Color Palette (HEX to Kivy RGBA)
COLOR_NAVY_DARK    = get_color_from_hex("#07192F") # Deep Navy Sidebar
COLOR_NAVY_PRIMARY = get_color_from_hex("#0A2342") # Main Brand Navy
COLOR_NAVY_LIGHT   = get_color_from_hex("#123B6B") # Card/Header Navy
COLOR_BLUE_ACCENT  = get_color_from_hex("#0D6EFD") # Healthcare Blue
COLOR_BLUE_LIGHT   = get_color_from_hex("#4EA8DE") # Light Sky Blue
COLOR_BLUE_TINT    = get_color_from_hex("#E8F1FC") # Soft Background Tint
COLOR_BG_LIGHT     = get_color_from_hex("#F4F7FC") # Main Light Background
COLOR_WHITE        = get_color_from_hex("#FFFFFF") # Pure White
COLOR_TEXT_DARK    = get_color_from_hex("#1E293B") # Slate Black text
COLOR_TEXT_MUTED   = get_color_from_hex("#64748B") # Muted Gray text
COLOR_TEXT_LIGHT   = get_color_from_hex("#F8FAFC") # Bright White text
COLOR_BORDER       = get_color_from_hex("#E2E8F0") # Subtle Card Border
COLOR_BORDER_FOCUS = get_color_from_hex("#0D6EFD") # Active Focus Border

# Triage Urgency Colors
COLOR_URGENT_EMERGENCY = get_color_from_hex("#DC2626") # Red (Cat 1)
COLOR_URGENT_EARLY     = get_color_from_hex("#F59E0B") # Amber (Cat 2)
COLOR_URGENT_ROUTINE   = get_color_from_hex("#10B981") # Green (Cat 3)
COLOR_URGENT_INSUFF    = get_color_from_hex("#6B7280") # Gray (Cat 4)

# Status and Surface Tints
COLOR_EMERGENCY_TINT   = get_color_from_hex("#FEE2E2") # Light Red Tint
COLOR_EARLY_TINT       = get_color_from_hex("#FEF3C7") # Light Amber Tint
COLOR_ROUTINE_TINT     = get_color_from_hex("#DCFCE7") # Light Green Tint
COLOR_INFO_TINT        = get_color_from_hex("#EFF6FF") # Soft Blue Info Tint
COLOR_OPTION_SELECT_BG = get_color_from_hex("#F0F6FF") # Active Option Card BG

def is_desktop_layout() -> bool:
    """Returns True if viewport width is indicative of laptop/desktop."""
    return Window.width >= 800

def get_sidebar_width() -> float:
    """Sidebar width for desktop layout; 0 on mobile."""
    return 240.0 if is_desktop_layout() else 0.0
