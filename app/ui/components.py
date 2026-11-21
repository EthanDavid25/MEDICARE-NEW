"""
MEDICARE Custom UI Widgets and Layout Components.
Built with pure Kivy graphics and properties for Android and Windows cross-platform fidelity.
Includes WrappedLabel for zero-overlap multi-line text rendering.
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle, Line, Rectangle
from kivy.properties import ListProperty, NumericProperty, StringProperty, BooleanProperty

from app.ui.theme import (
    COLOR_NAVY_PRIMARY, COLOR_NAVY_LIGHT, COLOR_BLUE_ACCENT,
    COLOR_BG_LIGHT, COLOR_WHITE, COLOR_TEXT_DARK, COLOR_TEXT_LIGHT,
    COLOR_BORDER, COLOR_URGENT_EMERGENCY, COLOR_URGENT_EARLY,
    COLOR_URGENT_ROUTINE, COLOR_URGENT_INSUFF
)

class WrappedLabel(Label):
    """
    A label that automatically wraps text to its container width
    and dynamically sets its height to texture_size[1].
    Eliminates text clipping and vertical overlap across all screen resolutions.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.markup = True
        self.valign = "top"
        self.halign = "left"
        self.color = kwargs.get("color", COLOR_TEXT_DARK)
        self.font_size = kwargs.get("font_size", "13sp")
        self.bind(width=self._update_text_size, texture_size=self._update_height)

    def _update_text_size(self, instance, value):
        self.text_size = (max(value, 50), None)

    def _update_height(self, instance, value):
        # Texture height plus subtle vertical breathing space
        self.height = max(value[1] + 4, 18)

class SectionTitle(WrappedLabel):
    """Clean prominent section header with robust height."""
    def __init__(self, text="", **kwargs):
        super().__init__(text=f"[b]{text}[/b]", **kwargs)
        self.font_size = "15sp"
        self.color = COLOR_NAVY_PRIMARY

class CardBox(BoxLayout):
    """Modern rounded card container with background and optional border."""
    bg_color = ListProperty(COLOR_WHITE)
    border_color = ListProperty(COLOR_BORDER)
    corner_radius = NumericProperty(10)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._update_canvas, size=self._update_canvas, bg_color=self._update_canvas)

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[self.corner_radius])
            Color(*self.border_color)
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height, self.corner_radius), width=1)

class PrimaryButton(Button):
    """High-contrast rounded action button."""
    bg_color = ListProperty(COLOR_BLUE_ACCENT)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.color = COLOR_TEXT_LIGHT
        self.bold = True
        self.font_size = "14sp"
        self.bind(pos=self._update_canvas, size=self._update_canvas, state=self._update_canvas)

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.state == "down":
                Color(self.bg_color[0]*0.8, self.bg_color[1]*0.8, self.bg_color[2]*0.8, self.bg_color[3])
            else:
                Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[8])

class SecondaryButton(Button):
    """Subtle outline / secondary button."""
    border_color = ListProperty(COLOR_BLUE_ACCENT)
    text_color = ListProperty(COLOR_BLUE_ACCENT)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.color = self.text_color
        self.font_size = "13sp"
        self.bind(pos=self._update_canvas, size=self._update_canvas, state=self._update_canvas)

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.state == "down":
                Color(0.9, 0.95, 1.0, 1.0)
            else:
                Color(1, 1, 1, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
            Color(*self.border_color)
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 8), width=1)

class UrgencyBadge(Label):
    """Colored pill badge indicating triage category."""
    category = NumericProperty(3)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bold = True
        self.font_size = "12sp"
        self.size_hint = (None, None)
        self.height = 28
        self.width = 170
        self.color = COLOR_TEXT_LIGHT
        self.bind(pos=self._update_canvas, size=self._update_canvas, category=self._update_canvas)

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.category == 1:
                Color(*COLOR_URGENT_EMERGENCY)
                self.text = "EMERGENCY CARE"
            elif self.category == 2:
                Color(*COLOR_URGENT_EARLY)
                self.text = "EARLY CONSULTATION"
            elif self.category == 3:
                Color(*COLOR_URGENT_ROUTINE)
                self.text = "ROUTINE CARE"
            else:
                Color(*COLOR_URGENT_INSUFF)
                self.text = "INSUFFICIENT INFO"
            RoundedRectangle(pos=self.pos, size=self.size, radius=[14])

class TopHeaderBar(BoxLayout):
    """Universal top navigation header with title and offline indicator."""
    def __init__(self, app_controller, on_menu_toggle=None, **kwargs):
        super().__init__(**kwargs)
        self.app_controller = app_controller
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = 56
        self.padding = [14, 8, 14, 8]
        self.spacing = 10
        self.bind(pos=self._update_canvas, size=self._update_canvas)

        # 1. Branding / Logo label
        brand_lbl = Label(
            text="[b]MEDICARE[/b] [size=12sp]| Triage Advisor[/size]",
            markup=True,
            font_size="17sp",
            color=COLOR_TEXT_LIGHT,
            halign="left",
            valign="middle",
            size_hint_x=0.5
        )
        brand_lbl.bind(size=brand_lbl.setter("text_size"))
        self.add_widget(brand_lbl)

        # 2. Active patient label
        self.patient_lbl = Label(
            text="Patient: [b]General Profile[/b]",
            markup=True,
            font_size="12sp",
            color=COLOR_TEXT_LIGHT,
            halign="right",
            valign="middle",
            size_hint_x=0.3
        )
        self.patient_lbl.bind(size=self.patient_lbl.setter("text_size"))
        self.add_widget(self.patient_lbl)

        # 3. Offline Mode Badge Pill
        self.offline_pill = Label(
            text="OFFLINE",
            bold=True,
            font_size="10sp",
            size_hint=(None, None),
            height=24,
            width=70,
            color=COLOR_TEXT_LIGHT
        )
        self.offline_pill.bind(pos=self._update_pill, size=self._update_pill)
        self.add_widget(self.offline_pill)

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*COLOR_NAVY_PRIMARY)
            Rectangle(pos=self.pos, size=self.size)

    def _update_pill(self, *args):
        self.offline_pill.canvas.before.clear()
        with self.offline_pill.canvas.before:
            Color(0.06, 0.72, 0.5, 0.9) # Emerald Green for autonomous offline mode
            RoundedRectangle(pos=self.offline_pill.pos, size=self.offline_pill.size, radius=[12])

    def update_patient_name(self, name: str):
        self.patient_lbl.text = f"Patient: [b]{name[:18]}[/b]"
