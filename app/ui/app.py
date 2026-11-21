"""
MEDICARE Kivy Application Entry and Window Layout.
Responsive Desktop & Mobile Layout Shell with Top Header, ScreenManager,
and adaptive Sidebar (Desktop) / Bottom Navigation (Mobile).
"""
import sys
from pathlib import Path

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, SlideTransition, NoTransition
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Line
from kivy.utils import get_color_from_hex

from app.ui.theme import (
    COLOR_NAVY_PRIMARY, COLOR_NAVY_LIGHT, COLOR_BLUE_ACCENT,
    COLOR_BG_LIGHT, COLOR_WHITE, COLOR_TEXT_LIGHT, COLOR_BORDER,
    is_desktop_layout
)
from app.ui.components import TopHeaderBar
from app.ui.screens import (
    DashboardScreen, PatientProfileScreen, SymptomAssessmentScreen,
    FollowupQuestionsScreen, TriageResultsScreen, PatientHistoryScreen,
    SymptomProgressionScreen, DoctorHandoverScreen, HealthcareDirectoryScreen,
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
        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.is_active:
                Color(*COLOR_BLUE_ACCENT)
            else:
                Color(*COLOR_NAVY_PRIMARY)
            Rectangle(pos=self.pos, size=self.size)

class MedicareKivyApp(App):
    """Main Kivy application class for MEDICARE."""

    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.title = "MEDICARE — Medical Symptoms Triage Advisor"

    def build(self):
        self.root_layout = BoxLayout(orientation="vertical")
        
        # 1. Top Header Bar
        self.header = TopHeaderBar(self.controller)
        self.root_layout.add_widget(self.header)

        # 2. Main Body (Sidebar + Content on Desktop, Content + BottomNav on Mobile)
        self.body_layout = BoxLayout(orientation="horizontal")

        # Sidebar navigation (for Desktop)
        self.sidebar = BoxLayout(
            orientation="vertical",
            size_hint_x=None,
            width=200 if is_desktop_layout() else 0,
            spacing=2
        )
        self.sidebar.bind(pos=self._draw_sidebar_bg, size=self._draw_sidebar_bg)
        
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
            "healthcare_directory": HealthcareDirectoryScreen(self.controller, name="healthcare_directory"),
            "medical_references": MedicalReferencesScreen(self.controller, name="medical_references"),
            "settings": SettingsScreen(self.controller, name="settings"),
            "about": AboutScreen(self.controller, name="about")
        }
        for s in self.screens.values():
            self.sm.add_widget(s)

        self._build_sidebar_items()
        self.body_layout.add_widget(self.sidebar)
        self.body_layout.add_widget(self.sm)
        self.root_layout.add_widget(self.body_layout)

        # 3. Bottom Navigation Bar (for Mobile layout)
        self.bottom_nav = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=0 if is_desktop_layout() else 52,
            spacing=2
        )
        self._build_bottom_nav_items()
        self.root_layout.add_widget(self.bottom_nav)

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
        nav_items = [
            ("dashboard", "🏠 Dashboard"),
            ("symptom_assessment", "🩺 New Assessment"),
            ("patient_profile", "👤 Profile"),
            ("patient_history", "📋 Past Assessments"),
            ("symptom_progression", "📈 Progression"),
            ("doctor_handover", "📄 Doctor Handover"),
            ("healthcare_directory", "🏥 Directory"),
            ("medical_references", "📚 References"),
            ("settings", "⚙️ Settings"),
            ("about", "ℹ️ About")
        ]
        self.nav_buttons = {}
        for scr_id, title in nav_items:
            btn = NavButton(scr_id, f"  {title}", is_active=(scr_id == "dashboard"), size_hint_y=None, height=44, halign="left")
            btn.bind(size=btn.setter("text_size"))
            btn.bind(on_release=lambda x, sid=scr_id: self.navigate_to(sid))
            self.sidebar.add_widget(btn)
            self.nav_buttons[scr_id] = btn

    def _build_bottom_nav_items(self):
        self.bottom_nav.clear_widgets()
        mobile_items = [
            ("dashboard", "Dashboard"),
            ("symptom_assessment", "Triage"),
            ("patient_history", "History"),
            ("healthcare_directory", "Facilities"),
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

    def _on_window_resize(self, window, width, height):
        if width >= 800:
            self.sidebar.width = 200
            self.bottom_nav.height = 0
        else:
            self.sidebar.width = 0
            self.bottom_nav.height = 52
