"""
MEDICARE Kivy Application Entry and Window Layout.
Responsive Desktop & Mobile Layout Shell with Top Header, ScreenManager,
and adaptive Sidebar (Desktop) / Bottom Navigation (Mobile).
"""
import sys
from pathlib import Path

from kivy.config import Config as KivyConfig
KivyConfig.set("input", "mouse", "mouse,disable_multitouch")

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, SlideTransition, NoTransition
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.utils import get_color_from_hex

from app.ui.theme import (
    COLOR_NAVY_PRIMARY, COLOR_NAVY_LIGHT, COLOR_BLUE_ACCENT,
    COLOR_BLUE_TINT, COLOR_BG_LIGHT, COLOR_WHITE, COLOR_TEXT_LIGHT, COLOR_BORDER,
    is_desktop_layout
)
from app.ui.components import TopHeaderBar
from app.ui.screens import (
    DashboardScreen, PatientProfileScreen, SymptomAssessmentScreen,
    FollowupQuestionsScreen, TriageResultsScreen, PatientHistoryScreen,
    SymptomProgressionScreen, DoctorHandoverScreen, HandoverDownloadsScreen,
    PDFViewerScreen, HealthcareDirectoryScreen,
    MedicalReferencesScreen, SettingsScreen, AboutScreen
)

# Window Configuration for Desktop default
Window.clearcolor = get_color_from_hex("#F4F7FC")
Window.minimum_width = 380
Window.minimum_height = 640

class NavButton(Button):
    def __init__(self, screen_id, icon_text, is_active=False, **kwargs):
        super().__init__(**kwargs)
        self.screen_id = screen_id
        self.text = icon_text
        self.font_size = "13sp"
        self.bold = True
        self.background_color = (0, 0, 0, 0)
        self.color = COLOR_TEXT_LIGHT
        self.is_active = is_active
        self.size_hint_y = None
        self.height = 40
        self.halign = "left"
        self.valign = "middle"
        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.is_active:
                Color(*COLOR_BLUE_ACCENT)
                RoundedRectangle(pos=(self.x + 4, self.y + 2), size=(self.width - 8, self.height - 4), radius=[6])
            else:
                Color(0, 0, 0, 0)
                Rectangle(pos=self.pos, size=self.size)
        self.text_size = (max(self.width - 24, 50), self.height)

class MedicareKivyApp(App):
    """Main Kivy application class for MEDICARE."""

    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.title = "MEDICARE — Medical Symptoms Triage Advisor"

    def build(self):
        # Desktop layout: Full-height Left Sidebar + Right Area (Top Header + Screens)
        self.root_layout = BoxLayout(orientation="horizontal")

        # 1. Left Sidebar Navigation Panel
        self.sidebar = BoxLayout(
            orientation="vertical",
            size_hint_x=None,
            width=220 if is_desktop_layout() else 0,
            spacing=0,
            padding=0
        )
        self.sidebar.bind(pos=self._draw_sidebar_bg, size=self._draw_sidebar_bg)
        self._build_sidebar_items()
        self.root_layout.add_widget(self.sidebar)

        # 2. Right Content Area (Top Header Bar + ScreenManager + Mobile BottomNav)
        self.right_area = BoxLayout(orientation="vertical", spacing=0)

        # Top Header Bar
        self.header = TopHeaderBar(self.controller)
        self.right_area.add_widget(self.header)

        # Screen Manager
        self.sm = ScreenManager(transition=NoTransition())
        self.screens = {
            "dashboard": DashboardScreen(self.controller, name="dashboard"),
            "patient_profile": PatientProfileScreen(self.controller, name="patient_profile"),
            "symptom_assessment": SymptomAssessmentScreen(self.controller, name="symptom_assessment"),
            "followup_questions": FollowupQuestionsScreen(self.controller, name="followup_questions"),
            "triage_results": TriageResultsScreen(self.controller, name="triage_results"),
            "patient_history": PatientHistoryScreen(self.controller, name="patient_history"),
            "symptom_progression": SymptomProgressionScreen(self.controller, name="symptom_progression"),
            "doctor_handover": DoctorHandoverScreen(self.controller, name="doctor_handover"),
            "handover_downloads": HandoverDownloadsScreen(self.controller, name="handover_downloads"),
            "pdf_viewer": PDFViewerScreen(self.controller, name="pdf_viewer"),
            "healthcare_directory": HealthcareDirectoryScreen(self.controller, name="healthcare_directory"),
            "medical_references": MedicalReferencesScreen(self.controller, name="medical_references"),
            "settings": SettingsScreen(self.controller, name="settings"),
            "about": AboutScreen(self.controller, name="about")
        }
        for s in self.screens.values():
            self.sm.add_widget(s)
        self.right_area.add_widget(self.sm)

        # 3. Bottom Navigation Bar (for Mobile layout)
        self.bottom_nav = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=0 if is_desktop_layout() else 52,
            spacing=2
        )
        self._build_bottom_nav_items()
        self.right_area.add_widget(self.bottom_nav)

        self.root_layout.add_widget(self.right_area)

        # Responsive window resize listener
        Window.bind(on_resize=self._on_window_resize)

        # Update initial patient display
        curr_p = self.controller.patient_service.get_patient(self.controller.current_patient_id)
        if curr_p:
            self.header.update_patient_name(curr_p.get("display_name", "General Profile"))

        return self.root_layout

    def _draw_sidebar_bg(self, instance, *args):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*COLOR_NAVY_PRIMARY)
            Rectangle(pos=instance.pos, size=instance.size)

    def _build_sidebar_items(self):
        self.sidebar.clear_widgets()

        # 1. Prominent Logo & Title at the very top of sidebar
        brand_card = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=70,
            padding=[16, 12, 16, 6],
            spacing=2
        )
        logo_lbl = Label(
            text="[b]MEDICARE[/b]",
            markup=True,
            font_size="17sp",
            bold=True,
            color=COLOR_TEXT_LIGHT,
            size_hint_y=None,
            height=26,
            halign="left",
            valign="middle"
        )
        logo_lbl.bind(size=logo_lbl.setter("text_size"))
        brand_card.add_widget(logo_lbl)

        sub_lbl = Label(
            text="Symptoms Triage Advisor",
            font_size="11sp",
            color=COLOR_BLUE_TINT,
            size_hint_y=None,
            height=18,
            halign="left",
            valign="middle"
        )
        sub_lbl.bind(size=sub_lbl.setter("text_size"))
        brand_card.add_widget(sub_lbl)

        # Subtle divider under branding
        divider = Widget(size_hint_y=None, height=1)
        with divider.canvas.before:
            Color(0.2, 0.35, 0.55, 0.5)
            Rectangle(pos=divider.pos, size=divider.size)
        divider.bind(pos=lambda inst, *a: setattr(inst.canvas.before.children[-1], 'pos', inst.pos),
                     size=lambda inst, *a: setattr(inst.canvas.before.children[-1], 'size', inst.size))
        brand_card.add_widget(divider)

        self.sidebar.add_widget(brand_card)

        # 2. Scrollable top-aligned navigation items
        self.sidebar_scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, scroll_y=1)
        self.sidebar_anchor = AnchorLayout(anchor_x="center", anchor_y="top", size_hint=(1, None))
        
        self.nav_box = BoxLayout(orientation="vertical", size_hint=(1, None), spacing=3, padding=[8, 8, 8, 8])
        self.nav_box.bind(minimum_height=self.nav_box.setter("height"))

        def _update_anchor_height(*args):
            self.sidebar_anchor.height = max(self.nav_box.minimum_height, self.sidebar_scroll.height)
        
        self.sidebar_scroll.bind(height=_update_anchor_height)
        self.nav_box.bind(minimum_height=_update_anchor_height)

        nav_items = [
            ("dashboard", "•  Dashboard"),
            ("symptom_assessment", "•  New Assessment"),
            ("patient_profile", "•  Patient Profile"),
            ("patient_history", "•  Past Assessments"),
            ("symptom_progression", "•  Progression"),
            ("doctor_handover", "•  Doctor Handover"),
            ("handover_downloads", "•  Handover Downloads"),
            ("medical_references", "•  References"),
            ("settings", "•  Settings"),
            ("about", "•  About")
        ]
        self.nav_buttons = {}
        for scr_id, title in nav_items:
            btn = NavButton(
                scr_id,
                f" {title}",
                is_active=(scr_id == "dashboard"),
                halign="left",
                valign="middle"
            )
            btn.bind(on_release=lambda x, sid=scr_id: self.navigate_to(sid))
            self.nav_box.add_widget(btn)
            self.nav_buttons[scr_id] = btn

        self.sidebar_anchor.add_widget(self.nav_box)
        self.sidebar_scroll.add_widget(self.sidebar_anchor)
        self.sidebar.add_widget(self.sidebar_scroll)

    def _build_bottom_nav_items(self):
        self.bottom_nav.clear_widgets()
        mobile_items = [
            ("dashboard", "Dashboard"),
            ("symptom_assessment", "Triage"),
            ("patient_history", "History"),
            ("handover_downloads", "Handovers"),
            ("settings", "Settings")
        ]
        for scr_id, label_text in mobile_items:
            btn = Button(
                text=label_text,
                font_size="11sp",
                bold=True,
                background_color=COLOR_NAVY_PRIMARY,
                color=COLOR_TEXT_LIGHT
            )
            btn.bind(on_release=lambda x, sid=scr_id: self.navigate_to(sid))
            self.bottom_nav.add_widget(btn)

    def navigate_to(self, screen_id: str):
        if screen_id in self.screens:
            self.sm.current = screen_id
            for sid, btn in self.nav_buttons.items():
                btn.is_active = (sid == screen_id)
                btn._update_canvas()

    def open_pdf_viewer(self, doc_id_or_path: str):
        viewer = self.screens.get("pdf_viewer")
        if viewer:
            viewer.load_document(doc_id_or_path)
            self.navigate_to("pdf_viewer")

    def _on_window_resize(self, window, width, height):
        if width >= 800:
            self.sidebar.width = 220
            self.bottom_nav.height = 0
        else:
            self.sidebar.width = 0
            self.bottom_nav.height = 52
