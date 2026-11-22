"""
MEDICARE Custom UI Widgets and Layout Components.
Built with pure Kivy graphics and properties for Android and Windows cross-platform fidelity.
Includes WrappedLabel for zero-overlap multi-line text rendering.
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, RoundedRectangle, Line, Rectangle, Ellipse
from kivy.properties import ListProperty, NumericProperty, StringProperty, BooleanProperty

from app.ui.theme import (
    COLOR_NAVY_PRIMARY, COLOR_NAVY_LIGHT, COLOR_BLUE_ACCENT,
    COLOR_BG_LIGHT, COLOR_WHITE, COLOR_TEXT_DARK, COLOR_TEXT_LIGHT,
    COLOR_TEXT_MUTED, COLOR_BORDER, COLOR_BORDER_FOCUS,
    COLOR_URGENT_EMERGENCY, COLOR_URGENT_EARLY,
    COLOR_URGENT_ROUTINE, COLOR_URGENT_INSUFF,
    COLOR_EMERGENCY_TINT, COLOR_EARLY_TINT, COLOR_ROUTINE_TINT,
    COLOR_INFO_TINT, COLOR_OPTION_SELECT_BG
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
        self.height = max(value[1] + 4, 18)

class SectionTitle(WrappedLabel):
    """Clean prominent section header with robust height."""
    def __init__(self, text="", **kwargs):
        super().__init__(text=f"[b]{text}[/b]", **kwargs)
        self.font_size = "15sp"
        self.color = COLOR_NAVY_PRIMARY

class CardBox(BoxLayout):
    """Modern rounded card container with clean background and subtle border."""
    bg_color = ListProperty(COLOR_WHITE)
    border_color = ListProperty(COLOR_BORDER)
    corner_radius = NumericProperty(10)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._update_canvas, size=self._update_canvas, bg_color=self._update_canvas, border_color=self._update_canvas)

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[self.corner_radius])
            Color(*self.border_color)
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height, self.corner_radius), width=1)

class PrimaryButton(Button):
    """High-contrast rounded primary action button."""
    bg_color = ListProperty(COLOR_BLUE_ACCENT)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.color = COLOR_TEXT_LIGHT
        self.bold = True
        self.font_size = "13sp"
        self.bind(pos=self._update_canvas, size=self._update_canvas, state=self._update_canvas, bg_color=self._update_canvas)

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.state == "down":
                Color(self.bg_color[0]*0.82, self.bg_color[1]*0.82, self.bg_color[2]*0.82, self.bg_color[3])
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
        self.bold = True
        self.bind(pos=self._update_canvas, size=self._update_canvas, state=self._update_canvas)

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.state == "down":
                Color(0.92, 0.96, 1.0, 1.0)
            else:
                Color(1, 1, 1, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
            Color(*self.border_color)
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 8), width=1.2)

class OptionButton(Button):
    """Clean white card option button with selection highlight and zero grey artifact."""
    is_selected = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.font_size = kwargs.get("font_size", "13sp")
        self.halign = "left"
        self.valign = "middle"
        self.size_hint_y = None
        self.height = kwargs.get("height", 36)
        self.padding = [12, 6, 12, 6]
        self.bind(pos=self._update_canvas, size=self._update_canvas, is_selected=self._update_canvas, state=self._update_canvas)
        self.bind(size=self.setter("text_size"))

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.is_selected:
                Color(0.92, 0.96, 1.0, 1.0)
                RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
                Color(*COLOR_BLUE_ACCENT)
                Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 8), width=1.5)
                self.color = COLOR_BLUE_ACCENT
                self.bold = True
            else:
                if self.state == "down":
                    Color(0.96, 0.97, 0.99, 1.0)
                else:
                    Color(1.0, 1.0, 1.0, 1.0)
                RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
                Color(*COLOR_BORDER)
                Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 8), width=1)
                self.color = COLOR_TEXT_DARK
                self.bold = False

class QuestionOptionCard(ButtonBehavior, BoxLayout):
    """
    Modern Clinical Assessment Question Option Card matching reference UI:
    Large selectable card with custom radio indicator, bold title, and subtitle.
    """
    is_selected = BooleanProperty(False)
    option_code = StringProperty("")
    title_text = StringProperty("")
    desc_text = StringProperty("")

    def __init__(self, option_code="", title="", desc="", on_select=None, **kwargs):
        super().__init__(**kwargs)
        self.option_code = option_code
        self.title_text = title
        self.desc_text = desc
        self.on_select_cb = on_select
        
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.padding = [16, 12, 16, 12]
        self.spacing = 14
        self.height = 68

        # Left radio indicator container
        self.radio_box = BoxLayout(size_hint=(None, None), size=(24, 24), pos_hint={"center_y": 0.5})
        self.radio_box.bind(pos=self._update_canvas, size=self._update_canvas)
        self.add_widget(self.radio_box)

        # Right text container (Title + Description)
        text_col = BoxLayout(orientation="vertical", spacing=2, pos_hint={"center_y": 0.5})
        self.lbl_title = WrappedLabel(
            text=f"[b]{self.title_text}[/b]",
            font_size="14sp",
            color=COLOR_TEXT_DARK
        )
        self.lbl_desc = WrappedLabel(
            text=self.desc_text,
            font_size="12sp",
            color=COLOR_TEXT_MUTED
        )
        text_col.add_widget(self.lbl_title)
        if self.desc_text:
            text_col.add_widget(self.lbl_desc)
        self.add_widget(text_col)

        self.bind(pos=self._update_canvas, size=self._update_canvas, is_selected=self._update_canvas)

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.is_selected:
                Color(*COLOR_OPTION_SELECT_BG)
                RoundedRectangle(pos=self.pos, size=self.size, radius=[10])
                Color(*COLOR_BORDER_FOCUS)
                Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 10), width=1.8)
                self.lbl_title.color = COLOR_NAVY_PRIMARY
                self.lbl_desc.color = COLOR_TEXT_DARK
            else:
                Color(*COLOR_WHITE)
                RoundedRectangle(pos=self.pos, size=self.size, radius=[10])
                Color(*COLOR_BORDER)
                Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 10), width=1)
                self.lbl_title.color = COLOR_TEXT_DARK
                self.lbl_desc.color = COLOR_TEXT_MUTED

            # Draw radio indicator
            rx = self.radio_box.x + 12
            ry = self.radio_box.y + 12
            if self.is_selected:
                Color(*COLOR_BLUE_ACCENT)
                Line(circle=(rx, ry, 9), width=1.8)
                Color(*COLOR_BLUE_ACCENT)
                Ellipse(pos=(rx - 5, ry - 5), size=(10, 10))
            else:
                Color(0.72, 0.76, 0.82, 1.0)
                Line(circle=(rx, ry, 9), width=1.5)

    def on_release(self):
        if self.on_select_cb:
            self.on_select_cb(self.option_code, self)

class ProgressBarWidget(Widget):
    """Smooth horizontal progress bar indicating question progress."""
    progress = NumericProperty(0.33)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (90, 6)
        self.bind(pos=self._update_canvas, size=self._update_canvas, progress=self._update_canvas)

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # Background track
            Color(0.88, 0.91, 0.95, 1.0)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[3])
            # Filled portion
            fill_w = max(self.width * min(max(self.progress, 0.0), 1.0), 6)
            Color(*COLOR_BLUE_ACCENT)
            RoundedRectangle(pos=self.pos, size=(fill_w, self.height), radius=[3])

class StatusPill(BoxLayout):
    """Clean rounded status badge pill for categories and indicators."""
    def __init__(self, text="Status", style="routine", **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint = (None, None)
        self.height = 24
        self.padding = [10, 2, 10, 2]
        self.style = style

        # Color schemes by style
        if style == "emergency":
            self.bg_col = COLOR_EMERGENCY_TINT
            self.border_col = COLOR_URGENT_EMERGENCY
            self.txt_col = COLOR_URGENT_EMERGENCY
        elif style == "monitor" or style == "early":
            self.bg_col = COLOR_EARLY_TINT
            self.border_col = COLOR_URGENT_EARLY
            self.txt_col = (0.75, 0.45, 0.0, 1.0)
        elif style == "routine":
            self.bg_col = COLOR_ROUTINE_TINT
            self.border_col = COLOR_URGENT_ROUTINE
            self.txt_col = (0.05, 0.55, 0.25, 1.0)
        elif style == "offline":
            self.bg_col = (0.94, 0.98, 0.95, 1.0)
            self.border_col = (0.7, 0.85, 0.75, 1.0)
            self.txt_col = (0.08, 0.58, 0.28, 1.0)
        else:
            self.bg_col = (0.94, 0.96, 0.98, 1.0)
            self.border_col = COLOR_BORDER
            self.txt_col = COLOR_TEXT_MUTED

        lbl = Label(
            text=text,
            bold=True,
            font_size="10.5sp",
            color=self.txt_col,
            halign="center",
            valign="middle"
        )
        lbl.bind(size=lbl.setter("text_size"))
        self.lbl = lbl
        self.add_widget(lbl)

        # Estimate width from label text
        self.width = max(len(text) * 7 + 22, 60)
        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_col)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[12])
            Color(*self.border_col)
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 12), width=1)

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
    """
    Modern top navigation header matching design reference:
    White clean background with subtle border, bold navy branding,
    active patient info, and green offline status pill.
    """
    def __init__(self, app_controller, on_menu_toggle=None, **kwargs):
        super().__init__(**kwargs)
        self.app_controller = app_controller
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = 54
        self.padding = [18, 8, 18, 8]
        self.spacing = 12
        self.bind(pos=self._update_canvas, size=self._update_canvas)

        # 1. Branding / Logo label
        brand_lbl = Label(
            text="[b][size=16sp][color=#0A2342]MEDICARE[/color][/size][/b]  [size=11sp][color=#64748B]Smart Symptom Assessment[/color][/size]",
            markup=True,
            halign="left",
            valign="middle",
            size_hint_x=0.55
        )
        brand_lbl.bind(size=brand_lbl.setter("text_size"))
        self.add_widget(brand_lbl)

        # 2. Active patient label
        self.patient_lbl = Label(
            text="Patient: [b][color=#0A2342]General Profile[/color][/b]",
            markup=True,
            font_size="11.5sp",
            color=COLOR_TEXT_MUTED,
            halign="right",
            valign="middle",
            size_hint_x=0.3
        )
        self.patient_lbl.bind(size=self.patient_lbl.setter("text_size"))
        self.add_widget(self.patient_lbl)

        # 3. Offline Mode Badge Pill
        self.offline_pill = StatusPill(text="●  Offline", style="offline")
        self.offline_pill.pos_hint = {"center_y": 0.5}
        self.add_widget(self.offline_pill)

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*COLOR_WHITE)
            Rectangle(pos=self.pos, size=self.size)
            Color(*COLOR_BORDER)
            Line(points=[self.x, self.y, self.right, self.y], width=1)

    def update_patient_name(self, name: str):
        self.patient_lbl.text = f"Patient: [b][color=#0A2342]{name[:18]}[/color][/b]"
