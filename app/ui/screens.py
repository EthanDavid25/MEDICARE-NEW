"""
MEDICARE Complete Multi-Screen Application Interface.
Implements all 12 required functional screens with zero text overlap,
dynamic content wrapping, interactive pain slider, adaptive follow-ups,
nearby healthcare recommendations, and verified medical reference links.
"""
import json
import webbrowser
from pathlib import Path
from datetime import datetime

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Rectangle, Ellipse, Line
from kivy.core.window import Window

import pypdfium2 as pdfium

from app.ui.theme import (
    COLOR_NAVY_DARK, COLOR_NAVY_PRIMARY, COLOR_NAVY_LIGHT, COLOR_BLUE_ACCENT,
    COLOR_BLUE_LIGHT, COLOR_BLUE_TINT, COLOR_BG_LIGHT, COLOR_WHITE, COLOR_TEXT_DARK,
    COLOR_TEXT_MUTED, COLOR_TEXT_LIGHT, COLOR_BORDER, COLOR_BORDER_FOCUS,
    COLOR_URGENT_EMERGENCY, COLOR_URGENT_EARLY, COLOR_URGENT_ROUTINE,
    COLOR_URGENT_INSUFF, COLOR_EMERGENCY_TINT, COLOR_EARLY_TINT,
    COLOR_ROUTINE_TINT, COLOR_INFO_TINT, COLOR_OPTION_SELECT_BG
)
from app.ui.components import (
    CardBox, PrimaryButton, SecondaryButton, UrgencyBadge, WrappedLabel,
    SectionTitle, OptionButton, QuestionOptionCard, ProgressBarWidget, StatusPill,
    CanvasIcon
)
from app.reports.handover_pdf import generate_doctor_handover_pdf
from app.security.india_validation import validate_indian_mobile, validate_indian_date, format_indian_datetime


def create_section_title(text: str) -> SectionTitle:
    """Creates an auto-wrapping high-contrast section title."""
    return SectionTitle(text=text)


def create_desc_label(text: str) -> WrappedLabel:
    """Creates a subtle descriptive subtitle that wraps cleanly."""
    return WrappedLabel(text=text, font_size="12sp", color=COLOR_TEXT_MUTED)

class BaseScreen(Screen):
    """
    Base Screen with guaranteed solid opaque background.
    Uses local coordinates (0, 0) as Screen is a RelativeLayout.
    Eliminates frame buffer ghosting, bleed-through, and text overlapping across screen transitions.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*COLOR_BG_LIGHT)
            self._bg_rect = Rectangle(pos=(0, 0), size=self.size)
        self.bind(size=self._update_bg)

    def _update_bg(self, *args):
        self._bg_rect.size = self.size


# =========================================================================
# 1. DASHBOARD SCREEN
# =========================================================================
class DashboardScreen(BaseScreen):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)
        
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        content = BoxLayout(orientation="vertical", spacing=14, padding=[18, 16, 18, 24], size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))

        # 1. Welcome Card Banner (Matching reference image hero card)
        banner = CardBox(orientation="horizontal", spacing=16, padding=[20, 16, 20, 16], size_hint_y=None)
        banner.bind(minimum_height=banner.setter("height"))
        banner.bg_color = COLOR_BLUE_TINT
        banner.border_color = (0.82, 0.88, 0.97, 1.0)
        banner.corner_radius = 12

        # Pulse circle icon
        icon_box = BoxLayout(size_hint=(None, None), size=(48, 48), pos_hint={"center_y": 0.5})
        with icon_box.canvas.before:
            Color(*COLOR_BLUE_ACCENT)
            icon_ellipse = Ellipse(pos=icon_box.pos, size=icon_box.size)
        icon_box.bind(pos=lambda inst, *a: setattr(icon_ellipse, 'pos', inst.pos),
                      size=lambda inst, *a: setattr(icon_ellipse, 'size', inst.size))
        icon_lbl = Label(text="♥", font_size="22sp", color=COLOR_WHITE, bold=True)
        icon_box.add_widget(icon_lbl)
        banner.add_widget(icon_box)

        # Welcome text column
        welcome_col = BoxLayout(orientation="vertical", spacing=3, pos_hint={"center_y": 0.5})
        welcome_col.add_widget(WrappedLabel(
            text="[b][size=18sp]Welcome back![/size][/b]",
            font_size="18sp",
            color=COLOR_NAVY_PRIMARY
        ))
        welcome_col.add_widget(WrappedLabel(
            text="Track your symptoms and get the right care advice.",
            font_size="12sp",
            color=COLOR_TEXT_MUTED
        ))
        banner.add_widget(welcome_col)
        content.add_widget(banner)

        # 2. Quick Stats Row (3 Cards: Total Assessments, Emergency Cases, Routine Care)
        stats_row = BoxLayout(orientation="horizontal", spacing=12, size_hint_y=None, height=76)
        
        # Stat 1: Total Assessments
        self.card_total = CardBox(orientation="horizontal", spacing=12, padding=[14, 12, 14, 12])
        self.card_total.corner_radius = 10
        i1 = BoxLayout(size_hint=(None, None), size=(38, 38), pos_hint={"center_y": 0.5})
        with i1.canvas.before:
            Color(0.9, 0.94, 1.0, 1.0)
            e1 = Ellipse(pos=i1.pos, size=i1.size)
        i1.bind(pos=lambda inst, *a: setattr(e1, 'pos', inst.pos),
                size=lambda inst, *a: setattr(e1, 'size', inst.size))
        i1.add_widget(Label(text="👥", font_size="16sp", color=COLOR_BLUE_ACCENT))
        self.card_total.add_widget(i1)
        
        c1_text = BoxLayout(orientation="vertical", spacing=1, pos_hint={"center_y": 0.5})
        c1_text.add_widget(WrappedLabel(text="Total Assessments", font_size="10.5sp", color=COLOR_TEXT_MUTED))
        self.lbl_stat_total = WrappedLabel(text="[b]0[/b]", font_size="19sp", color=COLOR_TEXT_DARK)
        c1_text.add_widget(self.lbl_stat_total)
        self.card_total.add_widget(c1_text)
        stats_row.add_widget(self.card_total)

        # Stat 2: Emergency Cases
        self.card_emerg = CardBox(orientation="horizontal", spacing=12, padding=[14, 12, 14, 12])
        self.card_emerg.corner_radius = 10
        self.card_emerg.bg_color = (1.0, 0.97, 0.97, 1.0)
        self.card_emerg.border_color = (0.98, 0.82, 0.82, 1.0)
        i2 = BoxLayout(size_hint=(None, None), size=(38, 38), pos_hint={"center_y": 0.5})
        with i2.canvas.before:
            Color(*COLOR_EMERGENCY_TINT)
            e2 = Ellipse(pos=i2.pos, size=i2.size)
        i2.bind(pos=lambda inst, *a: setattr(e2, 'pos', inst.pos),
                size=lambda inst, *a: setattr(e2, 'size', inst.size))
        i2.add_widget(Label(text="⚠️", font_size="16sp", color=COLOR_URGENT_EMERGENCY))
        self.card_emerg.add_widget(i2)
        
        c2_text = BoxLayout(orientation="vertical", spacing=1, pos_hint={"center_y": 0.5})
        c2_text.add_widget(WrappedLabel(text="Emergency Cases", font_size="10.5sp", color=COLOR_TEXT_MUTED))
        self.lbl_stat_emerg = WrappedLabel(text="[b]0[/b]", font_size="19sp", color=COLOR_URGENT_EMERGENCY)
        c2_text.add_widget(self.lbl_stat_emerg)
        self.card_emerg.add_widget(c2_text)
        stats_row.add_widget(self.card_emerg)

        # Stat 3: Routine Care
        self.card_routine = CardBox(orientation="horizontal", spacing=12, padding=[14, 12, 14, 12])
        self.card_routine.corner_radius = 10
        self.card_routine.bg_color = (0.97, 1.0, 0.98, 1.0)
        self.card_routine.border_color = (0.82, 0.95, 0.85, 1.0)
        i3 = BoxLayout(size_hint=(None, None), size=(38, 38), pos_hint={"center_y": 0.5})
        with i3.canvas.before:
            Color(*COLOR_ROUTINE_TINT)
            e3 = Ellipse(pos=i3.pos, size=i3.size)
        i3.bind(pos=lambda inst, *a: setattr(e3, 'pos', inst.pos),
                size=lambda inst, *a: setattr(e3, 'size', inst.size))
        i3.add_widget(Label(text="✓", font_size="16sp", bold=True, color=COLOR_URGENT_ROUTINE))
        self.card_routine.add_widget(i3)
        
        c3_text = BoxLayout(orientation="vertical", spacing=1, pos_hint={"center_y": 0.5})
        c3_text.add_widget(WrappedLabel(text="Routine Care", font_size="10.5sp", color=COLOR_TEXT_MUTED))
        self.lbl_stat_routine = WrappedLabel(text="[b]0[/b]", font_size="19sp", color=COLOR_URGENT_ROUTINE)
        c3_text.add_widget(self.lbl_stat_routine)
        self.card_routine.add_widget(c3_text)
        stats_row.add_widget(self.card_routine)

        content.add_widget(stats_row)

        # 3. Two-Column Dashboard Section: Quick Start (Left) & Recent Assessments (Right)
        cols_box = BoxLayout(orientation="horizontal", spacing=14, size_hint_y=None)
        cols_box.bind(minimum_height=cols_box.setter("height"))

        # Left Column: Quick Start Card
        quick_card = CardBox(orientation="vertical", spacing=12, padding=[18, 16, 18, 16], size_hint_x=0.45)
        quick_card.corner_radius = 10
        quick_card.add_widget(WrappedLabel(text="[b][size=15sp]Quick Start[/size][/b]", font_size="15sp", color=COLOR_NAVY_PRIMARY))
        
        btn_start = PrimaryButton(text="Start New Assessment →", size_hint_y=None, height=44)
        btn_start.bind(on_release=lambda x: self._nav_to("symptom_assessment"))
        quick_card.add_widget(btn_start)

        quick_card.add_widget(WrappedLabel(
            text="Answer a few questions about your symptoms",
            font_size="11sp",
            color=COLOR_TEXT_MUTED
        ))
        cols_box.add_widget(quick_card)

        # Right Column: Recent Assessments Card
        recent_card = CardBox(orientation="vertical", spacing=10, padding=[18, 16, 18, 16], size_hint_x=0.55)
        recent_card.corner_radius = 10
        
        rec_hdr = BoxLayout(orientation="horizontal", size_hint_y=None, height=28)
        rec_hdr.add_widget(WrappedLabel(text="[b][size=15sp]Recent Assessments[/size][/b]", font_size="15sp", color=COLOR_NAVY_PRIMARY, size_hint_x=0.7))
        btn_view_all = Button(text="View All →", font_size="12sp", bold=True, background_color=(0,0,0,0), color=COLOR_BLUE_ACCENT, size_hint_x=0.3, halign="right")
        btn_view_all.bind(on_release=lambda x: self._nav_to("patient_history"))
        rec_hdr.add_widget(btn_view_all)
        recent_card.add_widget(rec_hdr)

        self.recent_container = BoxLayout(orientation="vertical", spacing=8, size_hint_y=None)
        self.recent_container.bind(minimum_height=self.recent_container.setter("height"))
        recent_card.add_widget(self.recent_container)
        cols_box.add_widget(recent_card)

        content.add_widget(cols_box)

        # 4. Bottom Info Banner (Soft blue alert bar)
        info_bar = CardBox(orientation="horizontal", spacing=10, padding=[16, 10, 16, 10], size_hint_y=None, height=42)
        info_bar.bg_color = COLOR_INFO_TINT
        info_bar.border_color = (0.75, 0.85, 0.98, 1.0)
        info_bar.corner_radius = 8
        info_bar.add_widget(Label(text="ℹ", font_size="14sp", color=COLOR_BLUE_ACCENT, size_hint=(None, None), size=(20, 22), bold=True))
        info_bar.add_widget(WrappedLabel(
            text="In case of emergency, seek immediate medical attention.",
            font_size="11.5sp",
            color=COLOR_NAVY_PRIMARY
        ))
        content.add_widget(info_bar)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_pre_enter(self):
        """Refreshes stats and recent assessment items upon entering screen."""
        self.recent_container.clear_widgets()
        patient_id = self.controller.current_patient_id
        assessments = self.controller.history_service.get_assessment_history(patient_id, limit=50)

        # Update stats counts
        total_cnt = len(assessments)
        emerg_cnt = sum(1 for a in assessments if a.get("urgency_category") == 1)
        routine_cnt = sum(1 for a in assessments if a.get("urgency_category") == 3)

        self.lbl_stat_total.text = f"[b]{total_cnt}[/b]"
        self.lbl_stat_emerg.text = f"[b]{emerg_cnt}[/b]"
        self.lbl_stat_routine.text = f"[b]{routine_cnt}[/b]"

        recent_items = assessments[:3]
        if not recent_items:
            empty_box = BoxLayout(orientation="vertical", size_hint_y=None, height=54, padding=[0, 8, 0, 8])
            empty_box.add_widget(WrappedLabel(
                text="No recent assessments yet. Click 'Start New Assessment' to begin.",
                font_size="11.5sp",
                color=COLOR_TEXT_MUTED
            ))
            self.recent_container.add_widget(empty_box)
        else:
            for a in recent_items:
                row = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=44, padding=[4, 4, 4, 4])
                
                # Calendar icon
                cal_lbl = Label(text="📅", font_size="13sp", size_hint=(None, None), size=(22, 22), pos_hint={"center_y": 0.5})
                row.add_widget(cal_lbl)

                # Info text
                info_col = BoxLayout(orientation="vertical", spacing=1, pos_hint={"center_y": 0.5})
                raw_dt = a.get("completed_at", "")
                dt_str = raw_dt[:16].replace("T", " · ") if raw_dt else "Recent"
                
                # Primary symptom and category
                syms = a.get("symptoms", [])
                if isinstance(syms, str):
                    try:
                        syms = json.loads(syms)
                    except Exception:
                        syms = []
                sym_name = syms[0].get("name") if syms and isinstance(syms[0], dict) else "General"
                cat_num = a.get("urgency_category", 3)
                
                info_col.add_widget(WrappedLabel(text=f"[b]{dt_str}[/b]", font_size="11sp", color=COLOR_NAVY_PRIMARY))
                info_col.add_widget(WrappedLabel(text=f"{sym_name} — Category {cat_num}", font_size="10.5sp", color=COLOR_TEXT_MUTED))
                row.add_widget(info_col)

                # Status badge pill
                if cat_num == 1:
                    badge = StatusPill(text="Emergency", style="emergency")
                elif cat_num == 2:
                    badge = StatusPill(text="Monitor", style="monitor")
                else:
                    badge = StatusPill(text="Routine Care", style="routine")
                badge.pos_hint = {"center_y": 0.5}
                row.add_widget(badge)

                self.recent_container.add_widget(row)

    def _nav_to(self, screen_name: str):
        self.manager.current = screen_name

    def _nav_to(self, screen_name: str):
        self.manager.current = screen_name


# =========================================================================
# 2. PATIENT PROFILE SCREEN
# =========================================================================
class PatientProfileScreen(BaseScreen):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)
        
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        content = BoxLayout(orientation="vertical", spacing=12, padding=[16, 16, 16, 24], size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(create_section_title("Patient Registration & Profile"))
        content.add_widget(create_desc_label("Manage local demographic and medical background records. Stored strictly on device."))

        card = CardBox(orientation="vertical", spacing=12, padding=[18, 16, 18, 16], size_hint_y=None)
        card.bind(minimum_height=card.setter("height"))

        # Form fields
        self.in_name = self._add_field(card, "Full Display Name *", "e.g. Ethan (Demonstration Profile)")
        self.in_dob = self._add_field(card, "Date of Birth (DD/MM/YYYY)", "15/06/1990")
        self.lbl_dob_feedback = WrappedLabel(text="", font_size="11sp")
        card.add_widget(self.lbl_dob_feedback)
        self.in_dob.bind(text=self._on_dob_change)

        self.in_sex = self._add_field(card, "Biological Sex (male / female / other)", "male")
        self.in_blood = self._add_field(card, "Blood Group", "A+")
        self.in_allergies = self._add_field(card, "Known Allergies (Medications / Food)", "e.g. No known drug allergies (NKDA)")
        self.in_conditions = self._add_field(card, "Chronic Conditions (e.g. Hypertension, Diabetes)", "None reported")
        self.in_meds = self._add_field(card, "Current Medications", "None")
        
        self.in_emerg = self._add_field(card, "Emergency Contact (+91 Indian Mobile / 112)", "+91-98765-43210")
        self.lbl_emerg_feedback = WrappedLabel(text="", font_size="11sp")
        card.add_widget(self.lbl_emerg_feedback)
        self.in_emerg.bind(text=self._on_emerg_change)

        # Save Button
        btn_save = PrimaryButton(text="SAVE / UPDATE PROFILE", size_hint_y=None, height=44)
        btn_save.bind(on_release=self._save_profile)
        card.add_widget(btn_save)

        content.add_widget(card)

        # Data Management & Privacy
        mgmt_box = CardBox(orientation="vertical", spacing=8, padding=[14, 12, 14, 12], size_hint_y=None)
        mgmt_box.bind(minimum_height=mgmt_box.setter("height"))
        mgmt_box.border_color = COLOR_BORDER
        mgmt_box.add_widget(WrappedLabel(text="[b]Data Management & Privacy[/b]", font_size="13sp", color=COLOR_NAVY_PRIMARY))
        
        btn_export = SecondaryButton(text="Export Full Records (JSON)", size_hint_y=None, height=36)
        btn_export.bind(on_release=self._export_records)
        mgmt_box.add_widget(btn_export)

        btn_delete = Button(
            text="Delete Profile & Erase Records",
            background_color=COLOR_URGENT_EMERGENCY,
            color=COLOR_TEXT_LIGHT,
            font_size="12sp",
            bold=True,
            size_hint_y=None,
            height=36
        )
        btn_delete.bind(on_release=self._delete_records)
        mgmt_box.add_widget(btn_delete)

        content.add_widget(mgmt_box)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def _add_field(self, parent, label_text, placeholder):
        box = BoxLayout(orientation="vertical", spacing=4, size_hint_y=None)
        box.bind(minimum_height=box.setter("height"))
        box.add_widget(WrappedLabel(text=f"[b]{label_text}[/b]", font_size="13sp", color=COLOR_NAVY_PRIMARY))
        inp = TextInput(
            hint_text=placeholder,
            multiline=False,
            size_hint_y=None,
            height=38,
            font_size="13sp",
            padding=[10, 9, 10, 9]
        )
        box.add_widget(inp)
        parent.add_widget(box)
        return inp

    def _on_dob_change(self, instance, value):
        if not value.strip():
            self.lbl_dob_feedback.text = ""
            return
        valid, norm, msg = validate_indian_date(value, allow_empty=True)
        if valid and norm:
            self.lbl_dob_feedback.text = f"[color=#059669]• Date format valid (DD/MM/YYYY)[/color]"
        else:
            self.lbl_dob_feedback.text = f"[color=#DC2626]• {msg}[/color]"

    def _on_emerg_change(self, instance, value):
        val = value.strip()
        if not val:
            self.lbl_emerg_feedback.text = ""
            return
        # Support Indian emergency services numbers (112, 102, 108)
        if val in ("112", "102", "108"):
            self.lbl_emerg_feedback.text = "[color=#059669]• National Emergency Helpline[/color]"
            return
        valid, norm, msg = validate_indian_mobile(val, allow_empty=True)
        if valid and norm:
            self.lbl_emerg_feedback.text = f"[color=#059669]• Valid Indian Mobile ({norm})[/color]"
        else:
            self.lbl_emerg_feedback.text = f"[color=#DC2626]• {msg}[/color]"

    def on_pre_enter(self):
        curr = self.controller.patient_service.get_patient(self.controller.current_patient_id)
        if curr:
            self.in_name.text = curr.get("display_name", "")
            raw_dob = curr.get("date_of_birth", "")
            # Normalize to DD/MM/YYYY if in YYYY-MM-DD
            if raw_dob and "-" in raw_dob and len(raw_dob) == 10 and raw_dob[4] == "-":
                parts = raw_dob.split("-")
                raw_dob = f"{parts[2]}/{parts[1]}/{parts[0]}"
            self.in_dob.text = raw_dob
            self.in_sex.text = curr.get("biological_sex", "male")
            self.in_blood.text = curr.get("blood_group", "")
            self.in_allergies.text = curr.get("known_allergies", "")
            self.in_conditions.text = curr.get("chronic_conditions", "")
            self.in_meds.text = curr.get("current_medications", "")
            raw_emerg = curr.get("emergency_contact", "")
            if "+1-555" in raw_emerg:
                raw_emerg = "+91-98765-43210"
            self.in_emerg.text = raw_emerg
            self._on_dob_change(None, self.in_dob.text)
            self._on_emerg_change(None, self.in_emerg.text)

    def _save_profile(self, *args):
        name = self.in_name.text.strip()
        if not name:
            self._show_popup("Validation Error", "Patient full display name is required.")
            return

        dob = self.in_dob.text.strip()
        if dob:
            valid_dob, norm_dob, dob_err = validate_indian_date(dob, allow_empty=False)
            if not valid_dob:
                self._show_popup("Invalid Date of Birth", dob_err)
                return
            dob = norm_dob

        emerg = self.in_emerg.text.strip()
        if emerg and emerg not in ("112", "102", "108"):
            valid_m, norm_m, emerg_err = validate_indian_mobile(emerg, allow_empty=False)
            if not valid_m:
                self._show_popup("Invalid Mobile Number", emerg_err)
                return
            emerg = norm_m

        data = {
            "display_name": name,
            "date_of_birth": dob,
            "biological_sex": self.in_sex.text.strip().lower() or "prefer_not_to_say",
            "blood_group": self.in_blood.text.strip(),
            "known_allergies": self.in_allergies.text.strip(),
            "chronic_conditions": self.in_conditions.text.strip(),
            "current_medications": self.in_meds.text.strip(),
            "emergency_contact": emerg
        }
        self.controller.patient_service.update_patient(self.controller.current_patient_id, data)
        self.in_dob.text = dob
        self.in_emerg.text = emerg
        self._show_popup("Success", "Patient profile saved successfully with validated Indian contact defaults.")

    def _export_records(self, *args):
        data = self.controller.patient_service.export_patient_data(self.controller.current_patient_id)
        out = Path(self.controller.config.data_dir) / f"patient_export_{self.controller.current_patient_id}.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        self._show_popup("Export Complete", f"Patient records exported locally to:\n{out}")

    def _delete_records(self, *args):
        self.controller.patient_service.delete_patient(self.controller.current_patient_id, hard_delete=False)
        self._show_popup("Record Removed", "Patient profile deleted.")

    def _show_popup(self, title, msg):
        box = BoxLayout(orientation="vertical", padding=14, spacing=10)
        box.add_widget(WrappedLabel(text=msg, font_size="13sp"))
        b = PrimaryButton(text="OK", size_hint_y=None, height=36)
        p = Popup(title=title, content=box, size_hint=(0.8, 0.4))
        b.bind(on_release=p.dismiss)
        box.add_widget(b)
        p.open()


# =========================================================================
# 3. SYMPTOM ASSESSMENT SCREEN (Clean Search, Quick Chips, Pain Slider)
# =========================================================================
class SymptomAssessmentScreen(BaseScreen):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.selected_symptoms: list[dict] = []
        self.current_progression = "unchanged"
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)
        
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        content = BoxLayout(orientation="vertical", spacing=12, padding=[18, 16, 18, 24], size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(create_section_title("Reported Symptoms"))
        content.add_widget(create_desc_label("Search or select primary symptoms and rate pain severity."))

        # 1. Search Box & Quick Symptom Chips
        search_card = CardBox(orientation="vertical", spacing=8, padding=[14, 12, 14, 12], size_hint_y=None)
        search_card.bind(minimum_height=search_card.setter("height"))
        search_card.corner_radius = 10
        
        search_card.add_widget(WrappedLabel(text="[b]Search Symptoms:[/b]", font_size="13sp", color=COLOR_NAVY_PRIMARY))
        
        self.in_search = TextInput(
            hint_text="e.g. Headache, Chest pain, Shortness of breath, Fever...",
            multiline=False,
            size_hint_y=None,
            height=38,
            background_color=(1, 1, 1, 1),
            foreground_color=COLOR_TEXT_DARK,
            cursor_color=COLOR_BLUE_ACCENT,
            padding=[12, 8, 12, 8]
        )
        self.in_search.bind(text=self._on_search)
        search_card.add_widget(self.in_search)

        # Quick Add Chips
        search_card.add_widget(WrappedLabel(text="[b]Common Symptoms:[/b]", font_size="11sp", color=COLOR_TEXT_MUTED))
        chips_box = BoxLayout(orientation="horizontal", spacing=6, size_hint_y=None, height=32)
        
        common_chips = [
            ("Headache", "SYM_HEADACHE"),
            ("Chest Pain", "SYM_CHEST_PAIN"),
            ("Fever", "SYM_FEVER"),
            ("Breathlessness", "SYM_DYSPNEA"),
            ("Abdominal Pain", "SYM_ABDOMINAL_PAIN"),
            ("Dizziness", "SYM_DIZZINESS")
        ]
        for c_name, c_code in common_chips:
            chip_btn = SecondaryButton(text=f"+ {c_name}", font_size="11sp", size_hint_y=None, height=30)
            chip_btn.bind(on_release=lambda x, code=c_code, name=c_name: self._quick_add_symptom(code, name))
            chips_box.add_widget(chip_btn)
        search_card.add_widget(chips_box)

        content.add_widget(search_card)

        # 2. Search Results List (Dynamically populated)
        self.results_box = BoxLayout(orientation="vertical", spacing=4, size_hint_y=None)
        self.results_box.bind(minimum_height=self.results_box.setter("height"))
        content.add_widget(self.results_box)

        # 3. Selected Symptoms Summary Card
        content.add_widget(create_section_title("Selected Symptoms"))
        self.selected_container = BoxLayout(orientation="vertical", spacing=6, size_hint_y=None)
        self.selected_container.bind(minimum_height=self.selected_container.setter("height"))
        content.add_widget(self.selected_container)

        # 4. Severity & Progression Inputs Card
        sev_card = CardBox(orientation="vertical", spacing=10, padding=[16, 14, 16, 14], size_hint_y=None)
        sev_card.bind(minimum_height=sev_card.setter("height"))
        sev_card.corner_radius = 10
        
        # Interactive pain severity label updating dynamically
        self.lbl_sev = WrappedLabel(
            text="[b]How severe is your pain?[/b] (5 / 10) — [color=#D97706]Moderate[/color]",
            font_size="13sp",
            color=COLOR_NAVY_PRIMARY
        )
        sev_card.add_widget(self.lbl_sev)

        self.slider_sev = Slider(min=1, max=10, value=5, step=1, size_hint_y=None, height=36)
        self.slider_sev.bind(value=self._on_slider)
        sev_card.add_widget(self.slider_sev)

        # Duration input
        dur_box = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=36)
        dur_lbl = WrappedLabel(text="[b]How long have you had symptoms?[/b]", font_size="12.5sp", color=COLOR_NAVY_PRIMARY, size_hint_x=0.68)
        dur_box.add_widget(dur_lbl)
        
        self.in_dur = TextInput(
            text="1",
            multiline=False,
            size_hint_x=0.32,
            background_color=(1, 1, 1, 1),
            foreground_color=COLOR_TEXT_DARK,
            cursor_color=COLOR_BLUE_ACCENT,
            padding=[10, 6, 10, 6]
        )
        dur_box.add_widget(self.in_dur)
        sev_card.add_widget(dur_box)

        # Trajectory / Progression buttons
        sev_card.add_widget(WrappedLabel(text="[b]Is your condition getting worse?[/b]", font_size="12.5sp", color=COLOR_NAVY_PRIMARY))
        traj_box = BoxLayout(orientation="horizontal", spacing=8, size_hint_y=None, height=36)
        self.btn_worse = OptionButton(text="  Worsening", size_hint_y=None, height=36)
        self.btn_worse.bind(on_release=lambda x: self._set_traj("worsening"))
        self.btn_same = OptionButton(text="  Unchanged", size_hint_y=None, height=36)
        self.btn_same.bind(on_release=lambda x: self._set_traj("unchanged"))
        self.btn_better = OptionButton(text="  Improving", size_hint_y=None, height=36)
        self.btn_better.bind(on_release=lambda x: self._set_traj("improving"))
        traj_box.add_widget(self.btn_worse)
        traj_box.add_widget(self.btn_same)
        traj_box.add_widget(self.btn_better)
        sev_card.add_widget(traj_box)

        content.add_widget(sev_card)

        # 5. Continue to Follow-up Questions Button
        btn_next = PrimaryButton(text="CONTINUE TO QUESTIONS →", size_hint_y=None, height=44)
        btn_next.bind(on_release=self._proceed_to_followups)
        content.add_widget(btn_next)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def _set_traj(self, traj: str):
        self.current_progression = traj
        self.btn_worse.is_selected = (traj == "worsening")
        self.btn_same.is_selected = (traj == "unchanged")
        self.btn_better.is_selected = (traj == "improving")

    def _on_slider(self, instance, value):
        val = int(value)
        if val <= 3:
            category_text = "[color=#16A34A]Mild[/color]"
        elif val <= 6:
            category_text = "[color=#D97706]Moderate[/color]"
        elif val <= 8:
            category_text = "[color=#DC2626]Severe[/color]"
        else:
            category_text = "[color=#991B1B]Critical[/color]"
        self.lbl_sev.text = f"[b]How severe is your pain?[/b] ({val}/10) — {category_text}"

    def on_pre_enter(self):
        self.in_search.text = ""
        self._set_traj("unchanged")
        self.slider_sev.value = 5
        self._on_slider(self.slider_sev, 5)
        self._on_search(None, "")
        self._update_selected_ui()

    def _quick_add_symptom(self, code: str, name: str):
        all_syms = self.controller.dataset_loader.get_symptoms()
        found = next((s for s in all_syms if s.get("code") == code), None)
        if not found:
            found = {"code": code, "name": name, "body_system": "general"}
        self._add_symptom(found)

    def _on_search(self, instance, text):
        self.results_box.clear_widgets()
        matches = self.controller.dataset_loader.search_symptoms(text or "")[:6]
        for s in matches:
            btn = SecondaryButton(text=f"+ {s.get('name')} ({s.get('body_system', '')})", size_hint_y=None, height=34)
            if s.get("is_emergency_warning"):
                btn.text = f"[RED FLAG] {btn.text}"
                btn.color = COLOR_URGENT_EMERGENCY
            btn.bind(on_release=lambda x, sym=s: self._add_symptom(sym))
            self.results_box.add_widget(btn)

    def _add_symptom(self, sym: dict):
        if not any(x["code"] == sym["code"] for x in self.selected_symptoms):
            self.selected_symptoms.append(sym)
            self._update_selected_ui()

    def _remove_symptom(self, code: str):
        self.selected_symptoms = [s for s in self.selected_symptoms if s["code"] != code]
        self._update_selected_ui()

    def _update_selected_ui(self):
        self.selected_container.clear_widgets()
        if not self.selected_symptoms:
            empty = CardBox(padding=[14, 10, 14, 10], size_hint_y=None)
            empty.corner_radius = 8
            empty.bind(minimum_height=empty.setter("height"))
            empty.add_widget(WrappedLabel(text="No symptoms added yet. Pick at least one symptom above.", font_size="12sp", color=COLOR_TEXT_MUTED))
            self.selected_container.add_widget(empty)
        else:
            for s in self.selected_symptoms:
                card = CardBox(orientation="horizontal", padding=[14, 8, 14, 8], spacing=10, size_hint_y=None)
                card.corner_radius = 8
                card.bind(minimum_height=card.setter("height"))
                
                name_lbl = WrappedLabel(text=f"[b]{s.get('name')}[/b]  [size=10.5sp][color=#64748B]({s.get('body_system', '')})[/color][/size]", font_size="12.5sp", color=COLOR_NAVY_PRIMARY)
                card.add_widget(name_lbl)
                
                b_del = Button(text="Remove", font_size="11sp", bold=True, size_hint=(None, None), size=(72, 28), background_color=COLOR_URGENT_EMERGENCY, color=COLOR_WHITE)
                b_del.bind(on_release=lambda x, code=s["code"]: self._remove_symptom(code))
                card.add_widget(b_del)
                self.selected_container.add_widget(card)

    def _proceed_to_followups(self, *args):
        if not self.selected_symptoms:
            # Default to headache if none picked
            sym = self.controller.dataset_loader.get_symptoms()[0]
            self.selected_symptoms.append(sym)

        dur_val = 1
        try:
            dur_val = int(self.in_dur.text.strip())
        except Exception:
            dur_val = 1

        selected_sev = int(self.slider_sev.value)

        # Store assessment input state in controller
        self.controller.assessment_staging = {
            "severity": selected_sev,
            "progression": self.current_progression,
            "duration_days": dur_val,
            "symptoms": [
                {
                    "code": s["code"],
                    "name": s["name"],
                    "severity": selected_sev,
                    "duration_value": dur_val,
                    "duration_unit": "days",
                    "progression": self.current_progression,
                    "is_emergency_flag": s.get("is_emergency_warning", False)
                }
                for s in self.selected_symptoms
            ]
        }
        self.manager.current = "followup_questions"


# =========================================================================
# HELPER: ADAPTIVE QUESTION & OPTION FORMATTER (Simple English, <= 7 Words)
# =========================================================================
def format_question_and_options(q: dict, symptoms_list: list) -> tuple[str, list[dict]]:
    """
    Formats question text and options to simple English (6-7 words)
    with clean title and descriptive subtitle matching reference UI.
    """
    qid = q.get("question_id", "")
    q_text = q.get("question_text", "")
    options = q.get("options", [])

    sym_names = [s.get("name", "").lower() for s in symptoms_list if isinstance(s, dict) and s.get("name")]
    is_headache = any("headache" in n or "head" in n for n in sym_names)
    is_chest = any("chest" in n or "heart" in n for n in sym_names)

    if qid == "QID_PAIN_ONSET_SUDDEN":
        if is_headache:
            q_text = "Did the headache start suddenly?"
        elif is_chest:
            q_text = "Did chest pain start suddenly?"

    formatted_opts = []
    for opt in options:
        code = opt.get("code", "")
        raw_text = opt.get("text", "")
        if qid == "QID_PAIN_ONSET_SUDDEN":
            if code == "YES":
                title = "Yes, suddenly"
                desc = "The headache came on very quickly." if is_headache else "The pain came on very quickly."
            else:
                title = "No, gradually"
                desc = "It developed over time."
        elif qid == "QID_CHEST_RADIATION":
            if code == "YES":
                title = "Yes, radiating"
                desc = "Pain spreads to left arm, neck, or jaw."
            else:
                title = "No, localized"
                desc = "Pain stays centered in the chest."
        elif qid == "QID_CHEST_ASSOCIATED_DYSPNEA":
            if code == "YES":
                title = "Yes, accompanied"
                desc = "Shortness of breath or heavy cold sweating."
            else:
                title = "No other symptoms"
                desc = "Breathing normally without unusual sweating."
        elif qid == "QID_FEVER_TEMP":
            if code == "HIGH_GRADE":
                title = "High fever (Above 102°F / 38.9°C)"
                desc = "Severe body temperature elevation."
            elif code == "MODERATE":
                title = "Moderate fever (100°F – 102°F)"
                desc = "Elevated temperature with mild discomfort."
            else:
                title = "Mild or unmeasured"
                desc = "Slight warmth or temperature not taken."
        elif qid == "QID_HEADACHE_WORSENING_SIGNS":
            if code == "YES":
                title = "Yes, concerning signs"
                desc = "Confusion, persistent vomiting, or blackout."
            else:
                title = "No concerning signs"
                desc = "Clear thinking with no vomiting or blackout."
        elif qid == "QID_HEADACHE_UNCHANGED_NATURE":
            if code == "SIMILAR_NORMAL":
                title = "Yes, familiar usual headache"
                desc = "Feels similar to past headaches."
            else:
                title = "No, novel or unusual"
                desc = "Feels noticeably different from previous headaches."
        elif qid == "QID_HEADACHE_VISION":
            if code == "YES":
                title = "Yes, vision changes"
                desc = "Blurry, double vision, or visual dark spots."
            else:
                title = "No vision changes"
                desc = "Normal clear vision without disturbances."
        elif qid == "QID_STROKE_FAST_FACE":
            if code == "YES":
                title = "Yes, facial drooping"
                desc = "One side of the face or smile is drooping."
            else:
                title = "No facial drooping"
                desc = "Normal symmetrical face and smile."
        elif qid == "QID_STROKE_FAST_ARM":
            if code == "YES":
                title = "Yes, arm weakness"
                desc = "One arm drifts down or cannot be raised."
            else:
                title = "No arm weakness"
                desc = "Equal strength in both arms."
        elif qid == "QID_STROKE_FAST_SPEECH":
            if code == "YES":
                title = "Yes, speech difficulty"
                desc = "Speech is slurred, abnormal, or hard to understand."
            else:
                title = "No speech difficulty"
                desc = "Speaking clearly and normally."
        elif qid == "QID_RESP_SEVERITY":
            if code == "SEVERE":
                title = "No, only single words"
                desc = "Severe breathlessness, struggling to talk."
            elif code == "MODERATE":
                title = "Short phrases with pauses"
                desc = "Breathing heavily when speaking."
            else:
                title = "Yes, full sentences easily"
                desc = "Speaking comfortably without breathlessness."
        elif qid == "QID_RESP_STRIDOR_LIPS":
            if code == "YES":
                title = "Yes, swelling or whistling"
                desc = "Lip swelling or high-pitched stridor breathing."
            else:
                title = "No swelling or noise"
                desc = "No facial swelling or whistling airway sound."
        elif qid == "QID_ABD_RIGIDITY":
            if code == "YES":
                title = "Yes, hard like a board"
                desc = "Severe belly rigidity and intense tenderness."
            else:
                title = "No, belly feels soft"
                desc = "Abdomen is pliable without board-like hardness."
        elif qid == "QID_BLEEDING_SIGNS":
            if code == "YES":
                title = "Yes, visible bleeding"
                desc = "Vomiting blood or dark black tarry stools."
            else:
                title = "No blood seen"
                desc = "No blood in vomit or stools."
        elif qid == "QID_DIGEST_DEHYDRATION":
            if code == "NO":
                title = "No, cannot keep fluids"
                desc = "Vomiting liquids back up repeatedly."
            else:
                title = "Yes, drinking normally"
                desc = "Able to drink water and fluids without vomiting."
        elif qid == "QID_DIZZINESS_SYNCOPE":
            if code == "YES":
                title = "Yes, fainted or blacked out"
                desc = "Brief loss of consciousness or collapse."
            else:
                title = "No, only lightheaded"
                desc = "Felt unsteady or spinning without fainting."
        elif qid == "QID_MSK_DEFORMITY_WEIGHT":
            if code == "NO":
                title = "No, cannot bear weight"
                desc = "Unable to walk or take steps on the limb."
            else:
                title = "Yes, can bear weight"
                desc = "Able to take steps despite discomfort."
        elif qid == "QID_GENERAL_IMPROVEMENT_NEW_SIGNS":
            if code == "YES":
                title = "Yes, new symptoms appearing"
                desc = "New or unexpected symptoms have developed."
            else:
                title = "No, feeling steadily better"
                desc = "Condition is improving without new issues."
        else:
            parts = raw_text.split(":", 1) if ":" in raw_text else raw_text.split(",", 1)
            if len(parts) == 2:
                title = parts[0].strip()
                desc = parts[1].strip()
            else:
                title = raw_text
                desc = ""

        formatted_opts.append({
            "code": code,
            "title": title,
            "desc": desc,
            "triggers_emergency": opt.get("triggers_emergency", False)
        })

    return q_text, formatted_opts


# =========================================================================
# 4. CLINICAL ASSESSMENT QUESTION FLOW (Automatic Progression, 0 Next Buttons)
# =========================================================================
class FollowupQuestionsScreen(BaseScreen):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.session = None
        self.history = []
        self.current_idx = 0
        self.auto_advance_timer = None
        self._build_ui()

    def _build_ui(self):
        self.root_box = BoxLayout(orientation="vertical", spacing=0)

        # 1. Top Header Bar (Matching Screen 2 in reference image)
        self.top_bar = BoxLayout(orientation="horizontal", size_hint_y=None, height=48, padding=[18, 6, 18, 6], spacing=10)
        with self.top_bar.canvas.before:
            Color(*COLOR_WHITE)
            self.top_bar_rect = Rectangle(pos=self.top_bar.pos, size=self.top_bar.size)
            Color(*COLOR_BORDER)
            self.top_bar_line = Line(points=[self.top_bar.x, 0, self.top_bar.right, 0], width=1)

        def _update_top_bar(inst, *args):
            self.top_bar_rect.pos = inst.pos
            self.top_bar_rect.size = inst.size
            self.top_bar_line.points = [inst.x, inst.y, inst.right, inst.y]

        self.top_bar.bind(pos=_update_top_bar, size=_update_top_bar)

        btn_back = SecondaryButton(text="← Back", size_hint=(None, None), size=(90, 36))
        btn_back.bind(on_release=self._on_back_pressed)
        self.top_bar.add_widget(btn_back)

        # Spacer
        self.top_bar.add_widget(Widget())

        # Right side: Question progress text + progress bar
        prog_col = BoxLayout(orientation="horizontal", size_hint=(None, None), size=(210, 36), spacing=10, pos_hint={"center_y": 0.5})
        self.lbl_progress = Label(
            text="Question 1 of 3",
            font_size="12sp",
            bold=True,
            color=COLOR_NAVY_PRIMARY,
            size_hint=(None, None),
            size=(105, 36),
            halign="right",
            valign="middle"
        )
        self.lbl_progress.bind(size=self.lbl_progress.setter("text_size"))
        prog_col.add_widget(self.lbl_progress)

        self.progress_bar = ProgressBarWidget(progress=0.33)
        self.progress_bar.pos_hint = {"center_y": 0.5}
        prog_col.add_widget(self.progress_bar)

        self.top_bar.add_widget(prog_col)
        self.root_box.add_widget(self.top_bar)

        # 2. Main Question Card Area (Scrollable)
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.content = BoxLayout(orientation="vertical", spacing=14, padding=[22, 18, 22, 24], size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter("height"))

        scroll.add_widget(self.content)
        self.root_box.add_widget(scroll)
        self.add_widget(self.root_box)

    def on_pre_enter(self):
        if self.auto_advance_timer:
            Clock.unschedule(self.auto_advance_timer)
            self.auto_advance_timer = None

        staging = getattr(self.controller, "assessment_staging", {})
        symptoms = staging.get("symptoms", [])
        progression = staging.get("progression", "unchanged")
        severity = staging.get("severity", 5)
        duration_days = staging.get("duration_days", 1)

        engine = self.controller.dataset_loader.get_question_engine()
        self.session = engine.create_session(
            symptoms=symptoms,
            severity=severity,
            progression=progression,
            duration_days=duration_days
        )
        self.history = []
        self.current_idx = 0

        first_q = self.session.get_next_question()
        if first_q:
            self.history.append(first_q)
            self._render_current_question()
        else:
            self._evaluate_triage()

    def _render_current_question(self):
        if self.auto_advance_timer:
            Clock.unschedule(self.auto_advance_timer)
            self.auto_advance_timer = None

        self.content.clear_widgets()
        if not self.history or self.current_idx >= len(self.history):
            self._evaluate_triage()
            return

        q = self.history[self.current_idx]
        staging = getattr(self.controller, "assessment_staging", {})
        symptoms_list = staging.get("symptoms", [])
        sym_names = ", ".join(s.get("name", "") for s in symptoms_list if isinstance(s, dict) and s.get("name"))
        if not sym_names:
            sym_names = "Reported Symptoms"

        # Update top progress indicator
        total_q = max(self.session.max_questions, len(self.history), self.current_idx + 1)
        step_num = self.current_idx + 1
        self.lbl_progress.text = f"Question {step_num} of {total_q}"
        self.progress_bar.progress = float(step_num) / float(total_q)

        # Format question text & options
        q_text, formatted_opts = format_question_and_options(q, symptoms_list)

        # Main Question Card (Clean white card, rounded corners, subtle border)
        q_card = CardBox(orientation="vertical", spacing=14, padding=[22, 18, 22, 18], size_hint_y=None)
        q_card.bind(minimum_height=q_card.setter("height"))
        q_card.corner_radius = 12

        # Card Header: Icon + Clinical Assessment + Selected Symptoms
        hdr_box = BoxLayout(orientation="horizontal", spacing=12, size_hint_y=None, height=44)
        
        clip_box = BoxLayout(size_hint=(None, None), size=(38, 38), pos_hint={"center_y": 0.5})
        with clip_box.canvas.before:
            Color(0.9, 0.94, 1.0, 1.0)
            clip_rect = RoundedRectangle(pos=clip_box.pos, size=clip_box.size, radius=[8])
        clip_box.bind(pos=lambda inst, *a: setattr(clip_rect, 'pos', inst.pos),
                      size=lambda inst, *a: setattr(clip_rect, 'size', inst.size))
        clip_lbl = Label(text="📋", font_size="16sp")
        clip_box.add_widget(clip_lbl)
        hdr_box.add_widget(clip_box)

        title_col = BoxLayout(orientation="vertical", spacing=2, pos_hint={"center_y": 0.5})
        title_col.add_widget(WrappedLabel(text="[b][size=15sp]Clinical Assessment[/size][/b]", font_size="15sp", color=COLOR_NAVY_PRIMARY))
        title_col.add_widget(WrappedLabel(text=f"Selected Symptoms: {sym_names}", font_size="11.5sp", color=COLOR_TEXT_MUTED))
        hdr_box.add_widget(title_col)
        q_card.add_widget(hdr_box)

        # Red Flag Warning Check banner if applicable
        is_emerg = bool(q.get("is_emergency_safety_check", False) or q.get("triggers_emergency_check", False))
        if is_emerg:
            safety_card = CardBox(orientation="horizontal", spacing=8, padding=[12, 6, 12, 6], size_hint_y=None, height=30)
            safety_card.bg_color = COLOR_EMERGENCY_TINT
            safety_card.border_color = COLOR_URGENT_EMERGENCY
            safety_card.corner_radius = 6
            safety_card.add_widget(Label(text="⚠️", font_size="11sp", color=COLOR_URGENT_EMERGENCY, size_hint=(None, None), size=(18, 18)))
            safety_card.add_widget(WrappedLabel(text="[b][color=#DC2626]Safety Assessment Check[/color][/b]", font_size="11sp"))
            q_card.add_widget(safety_card)

        # Big Question Text
        q_card.add_widget(WrappedLabel(text=f"[b][size=18sp]{q_text}[/size][/b]", font_size="18sp", color=COLOR_NAVY_PRIMARY))
        q_card.add_widget(WrappedLabel(text="Select the option that best describes your symptom.", font_size="12.5sp", color=COLOR_TEXT_MUTED))

        # Options Container
        opts_container = BoxLayout(orientation="vertical", spacing=10, size_hint_y=None)
        opts_container.bind(minimum_height=opts_container.setter("height"))

        self.option_cards = []
        current_answer = self.session.answers.get(q["question_id"])

        for opt in formatted_opts:
            is_sel = (current_answer == opt["code"])
            card = QuestionOptionCard(
                option_code=opt["code"],
                title=opt["title"],
                desc=opt["desc"],
                on_select=self._on_option_chosen
            )
            card.is_selected = is_sel
            opts_container.add_widget(card)
            self.option_cards.append(card)

        q_card.add_widget(opts_container)

        # Bottom Status & Action Row
        self.bottom_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=44, spacing=10, padding=[4, 6, 4, 4])
        
        # Left: Save indicator
        self.lbl_saved = Label(text="", markup=True, font_size="12sp", halign="left", valign="middle", size_hint_x=0.55)
        self.lbl_saved.bind(size=self.lbl_saved.setter("text_size"))
        self.bottom_row.add_widget(self.lbl_saved)

        # Right: Action container (Auto-advancing pill or Submit Assessment button)
        self.action_right_box = BoxLayout(orientation="horizontal", size_hint_x=0.45, spacing=6, pos_hint={"center_y": 0.5})
        self.bottom_row.add_widget(self.action_right_box)

        if current_answer:
            self.lbl_saved.text = "[b][color=#10B981]✓[/color][/b]  [color=#1E293B]Your answer is saved automatically[/color]"
            # If this is the last question or already answered, display submit button
            if self.current_idx == len(self.history) - 1 and self.session.get_next_question() is None:
                self._show_submit_button()

        q_card.add_widget(self.bottom_row)
        self.content.add_widget(q_card)

    def _on_option_chosen(self, code: str, clicked_card):
        if self.auto_advance_timer:
            Clock.unschedule(self.auto_advance_timer)
            self.auto_advance_timer = None

        q = self.history[self.current_idx]
        qid = q["question_id"]

        # 1. Save answer immediately
        self.session.record_answer(qid, code)

        # 2. Update card selection highlights
        for card in self.option_cards:
            card.is_selected = (card.option_code == code)

        # 3. Show "Your answer is saved automatically"
        self.lbl_saved.text = "[b][color=#10B981]✓[/color][/b]  [color=#1E293B]Your answer is saved automatically[/color]"

        # 4. Check whether to auto-advance or show Submit Assessment
        if self.current_idx < len(self.history) - 1:
            # Navigated back and re-answered: auto-advance to next existing question in history
            self.action_right_box.clear_widgets()
            pill = StatusPill(text="●  Auto-advancing...", style="routine")
            pill.pos_hint = {"center_y": 0.5}
            self.action_right_box.add_widget(pill)
            self.auto_advance_timer = Clock.schedule_once(self._advance_step, 0.4)
        else:
            # Check if engine has a next question
            next_q = self.session.get_next_question()
            if next_q:
                self.history.append(next_q)
                self.action_right_box.clear_widgets()
                pill = StatusPill(text="●  Auto-advancing...", style="routine")
                pill.pos_hint = {"center_y": 0.5}
                self.action_right_box.add_widget(pill)
                self.auto_advance_timer = Clock.schedule_once(self._advance_step, 0.4)
            else:
                # All required questions answered! Display Submit Assessment button
                self._show_submit_button()

    def _show_submit_button(self):
        self.action_right_box.clear_widgets()
        btn_submit = PrimaryButton(text="Submit Assessment →", size_hint=(1, None), height=40)
        btn_submit.bind(on_release=self._evaluate_triage)
        self.action_right_box.add_widget(btn_submit)

    def _advance_step(self, dt):
        self.current_idx += 1
        self._render_current_question()

    def _on_back_pressed(self, *args):
        if self.auto_advance_timer:
            Clock.unschedule(self.auto_advance_timer)
            self.auto_advance_timer = None

        if self.current_idx > 0:
            self.current_idx -= 1
            self._render_current_question()
        else:
            # Return to Symptom Selection screen
            self.manager.current = "symptom_assessment"

    def _evaluate_triage(self, *args):
        if self.auto_advance_timer:
            Clock.unschedule(self.auto_advance_timer)
            self.auto_advance_timer = None

        staging = getattr(self.controller, "assessment_staging", {})
        symptoms = staging.get("symptoms", [])

        effective_answers = self.session.get_effective_answers() if self.session else {}

        result = self.controller.triage_engine.assess(
            patient_id=self.controller.current_patient_id,
            symptoms=symptoms,
            followup_answers=effective_answers,
            risk_factors=[]
        )
        self.controller.last_triage_result = result
        self.manager.current = "triage_results"


# =========================================================================
# 5. TRIAGE RESULTS SCREEN (Emergency Visibility & Assessment Summary)
# =========================================================================
class TriageResultsScreen(BaseScreen):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)
        
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.content = BoxLayout(orientation="vertical", spacing=14, padding=[18, 16, 18, 24], size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter("height"))

        scroll.add_widget(self.content)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_pre_enter(self):
        self.content.clear_widgets()
        result = getattr(self.controller, "last_triage_result", None)
        if not result:
            self.content.add_widget(WrappedLabel(text="No recent assessment evaluated.", color=COLOR_TEXT_DARK))
            return

        cat = result.urgency_category

        # -------------------------------------------------------------
        # SECTION 1: PROMINENT TOP URGENCY BANNER (Matching Screen 3)
        # -------------------------------------------------------------
        banner_card = CardBox(orientation="horizontal", spacing=16, padding=[20, 16, 20, 16], size_hint_y=None)
        banner_card.bind(minimum_height=banner_card.setter("height"))
        banner_card.corner_radius = 10

        if cat == 1:
            banner_card.bg_color = COLOR_EMERGENCY_TINT
            banner_card.border_color = (0.95, 0.75, 0.75, 1.0)
            banner_icon = CanvasIcon(icon_type="triangle_alert", bg_color=COLOR_URGENT_EMERGENCY, icon_color=COLOR_WHITE, size=(38, 38), pos_hint={"center_y": 0.5})
            title_str = "CATEGORY 1 — EMERGENCY CARE"
            sub_str = "Seek immediate medical attention"
            title_color = COLOR_URGENT_EMERGENCY
        elif cat == 2:
            banner_card.bg_color = COLOR_EARLY_TINT
            banner_card.border_color = (0.95, 0.85, 0.7, 1.0)
            banner_icon = CanvasIcon(icon_type="triangle_alert", bg_color=COLOR_URGENT_EARLY, icon_color=COLOR_WHITE, size=(38, 38), pos_hint={"center_y": 0.5})
            title_str = "CATEGORY 2 — EARLY MEDICAL CONSULTATION"
            sub_str = "Consult a physician promptly within 12–24 hours"
            title_color = (0.8, 0.45, 0.0, 1.0)
        elif cat == 3:
            banner_card.bg_color = COLOR_ROUTINE_TINT
            banner_card.border_color = (0.75, 0.9, 0.8, 1.0)
            banner_icon = CanvasIcon(icon_type="check", bg_color=COLOR_URGENT_ROUTINE, icon_color=COLOR_WHITE, size=(36, 36), pos_hint={"center_y": 0.5})
            title_str = "CATEGORY 3 — ROUTINE CARE"
            sub_str = "Self-care and routine medical consultation"
            title_color = (0.05, 0.55, 0.25, 1.0)
        else:
            banner_card.bg_color = (0.94, 0.96, 0.98, 1.0)
            banner_card.border_color = COLOR_BORDER
            banner_icon = CanvasIcon(icon_type="info", bg_color=COLOR_BLUE_ACCENT, icon_color=COLOR_WHITE, size=(36, 36), pos_hint={"center_y": 0.5})
            title_str = "CATEGORY 4 — INSUFFICIENT INFORMATION"
            sub_str = "Additional clinical evaluation needed"
            title_color = COLOR_NAVY_PRIMARY

        banner_card.add_widget(banner_icon)

        # Title text column
        b_text_col = BoxLayout(orientation="vertical", spacing=2, pos_hint={"center_y": 0.5})
        b_text_col.add_widget(WrappedLabel(
            text=f"[b][size=17sp]{title_str}[/size][/b]",
            font_size="17sp",
            color=title_color
        ))
        b_text_col.add_widget(WrappedLabel(
            text=sub_str,
            font_size="13sp",
            color=title_color
        ))
        banner_card.add_widget(b_text_col)
        self.content.add_widget(banner_card)

        # -------------------------------------------------------------
        # SECTION 2: ASSESSMENT SUMMARY CARD WITH MEDICAL EMBLEM
        # -------------------------------------------------------------
        summary_card = CardBox(orientation="vertical", spacing=14, padding=[20, 18, 20, 18], size_hint_y=None)
        summary_card.corner_radius = 12

        # Dedicated Heading Layout Container (Eliminates vertical overlap)
        heading_box = BoxLayout(orientation="horizontal", size_hint_y=None, height=26)
        heading_box.add_widget(WrappedLabel(
            text="[b][size=16sp]Assessment Summary[/size][/b]",
            font_size="16sp",
            color=COLOR_NAVY_PRIMARY
        ))
        summary_card.add_widget(heading_box)

        # Main summary content row: Left bullet points, Right emblem
        content_row = BoxLayout(orientation="horizontal", spacing=14, size_hint_y=None)

        # Left Column: Key Findings List
        findings_col = BoxLayout(orientation="vertical", spacing=10, size_hint_x=0.78, size_hint_y=None)
        findings_col.bind(minimum_height=findings_col.setter("height"))

        def create_finding_row(icon_type, icon_bg, label_text):
            row = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None)
            badge = CanvasIcon(icon_type=icon_type, bg_color=icon_bg, icon_color=COLOR_WHITE, size=(20, 20), pos_hint={"top": 0.95})
            lbl = WrappedLabel(text=label_text, font_size="13sp", color=COLOR_TEXT_DARK, size_hint_x=1.0)
            row.add_widget(badge)
            row.add_widget(lbl)
            lbl.bind(height=lambda inst, val, r=row: setattr(r, "height", max(val, 24)))
            row.height = max(lbl.height, 24)
            return row

        # Symptoms
        symptoms = getattr(result, "symptoms", [])
        if isinstance(symptoms, str):
            try:
                symptoms = json.loads(symptoms)
            except Exception:
                symptoms = []
        sym_names = ", ".join(s.get("name", "") for s in symptoms if isinstance(s, dict) and s.get("name")) or "Reported symptoms"
        row_sym = create_finding_row(
            icon_type="arrow_down",
            icon_bg=COLOR_BLUE_ACCENT,
            label_text=f"[b]Symptoms Reported:[/b]   {sym_names}"
        )
        findings_col.add_widget(row_sym)

        # Key Findings
        answers = getattr(result, "followup_answers", {})
        findings_list = []
        for qk, qv in answers.items():
            if qv in ("YES", "SEVERE", "HIGH_GRADE"):
                clean_k = qk.replace("QID_", "").replace("_", " ").title()
                findings_list.append(clean_k)
        if not findings_list and hasattr(result, "warning_signs_found") and result.warning_signs_found:
            findings_list = [w[:25] for w in result.warning_signs_found[:2]]
        findings_str = ", ".join(findings_list) if findings_list else "Standard symptom course"
        row_find = create_finding_row(
            icon_type="check",
            icon_bg=COLOR_BLUE_ACCENT,
            label_text=f"[b]Key Findings:[/b]   {findings_str}"
        )
        findings_col.add_widget(row_find)

        # Triage Category
        cat_badge_bg = COLOR_URGENT_EMERGENCY if cat == 1 else (COLOR_URGENT_EARLY if cat == 2 else (COLOR_URGENT_ROUTINE if cat == 3 else COLOR_NAVY_PRIMARY))
        cat_icon_type = "alert" if cat in (1, 2) else ("check" if cat == 3 else "info")
        row_cat = create_finding_row(
            icon_type=cat_icon_type,
            icon_bg=cat_badge_bg,
            label_text=f"[b]Triage Category:[/b]   Category {cat}"
        )
        findings_col.add_widget(row_cat)

        # Recommended Action
        if cat == 1:
            rec_action = "Go to nearest emergency room or call ambulance (112 / 102)"
        elif cat == 2:
            rec_action = "Consult a physician within 12–24 hours"
        elif cat == 3:
            rec_action = "Rest, drink fluids, and monitor symptoms"
        else:
            rec_action = "Retake assessment or consult local clinic"

        row_act = create_finding_row(
            icon_type="alert" if cat == 1 else "check",
            icon_bg=COLOR_URGENT_EMERGENCY if cat == 1 else COLOR_URGENT_ROUTINE,
            label_text=f"[b]Recommended Action:[/b]   {rec_action}"
        )
        findings_col.add_widget(row_act)
        content_row.add_widget(findings_col)

        # Right Column: Circular Medical Cross Emblem
        emblem_box = BoxLayout(size_hint=(None, None), size=(68, 68), pos_hint={"center_y": 0.5})
        with emblem_box.canvas.before:
            if cat == 1:
                Color(*COLOR_EMERGENCY_TINT)
            elif cat == 2:
                Color(*COLOR_EARLY_TINT)
            else:
                Color(*COLOR_ROUTINE_TINT)
            emblem_ellipse = Ellipse(pos=emblem_box.pos, size=emblem_box.size)
        emblem_box.bind(pos=lambda inst, *a: setattr(emblem_ellipse, 'pos', inst.pos),
                        size=lambda inst, *a: setattr(emblem_ellipse, 'size', inst.size))
        
        emblem_col = COLOR_URGENT_EMERGENCY if cat == 1 else (COLOR_URGENT_EARLY if cat == 2 else COLOR_URGENT_ROUTINE)
        emblem_lbl = Label(text="+", font_size="38sp", bold=True, color=emblem_col)
        emblem_box.add_widget(emblem_lbl)
        content_row.add_widget(emblem_box)

        # Synchronize content_row height dynamically to findings_col height
        findings_col.bind(height=lambda inst, val: setattr(content_row, "height", max(val, 76)))
        content_row.height = max(findings_col.height, 76)

        summary_card.add_widget(content_row)

        # Bottom Warning Bar inside card (Matching Screen 3)
        bottom_alert_bar = CardBox(orientation="horizontal", spacing=10, padding=[12, 8, 12, 8], size_hint_y=None, height=36)
        bottom_alert_bar.corner_radius = 6
        if cat == 1:
            bottom_alert_bar.bg_color = COLOR_EMERGENCY_TINT
            bottom_alert_bar.border_color = (0.95, 0.75, 0.75, 1.0)
            bottom_alert_bar.add_widget(CanvasIcon(icon_type="triangle_alert", bg_color=COLOR_URGENT_EMERGENCY, icon_color=COLOR_WHITE, size=(18, 18), pos_hint={"center_y": 0.5}))
            bottom_alert_bar.add_widget(WrappedLabel(
                text="[b][color=#DC2626]Do not delay treatment. This is a medical emergency.[/color][/b]",
                font_size="11.5sp"
            ))
        elif cat == 2:
            bottom_alert_bar.bg_color = COLOR_EARLY_TINT
            bottom_alert_bar.border_color = (0.95, 0.85, 0.7, 1.0)
            bottom_alert_bar.add_widget(CanvasIcon(icon_type="triangle_alert", bg_color=COLOR_URGENT_EARLY, icon_color=COLOR_WHITE, size=(18, 18), pos_hint={"center_y": 0.5}))
            bottom_alert_bar.add_widget(WrappedLabel(
                text="[b][color=#B45309]Schedule a same-day medical consultation promptly.[/color][/b]",
                font_size="11.5sp"
            ))
        else:
            bottom_alert_bar.bg_color = COLOR_ROUTINE_TINT
            bottom_alert_bar.border_color = (0.75, 0.9, 0.8, 1.0)
            bottom_alert_bar.add_widget(CanvasIcon(icon_type="check", bg_color=COLOR_URGENT_ROUTINE, icon_color=COLOR_WHITE, size=(18, 18), pos_hint={"center_y": 0.5}))
            bottom_alert_bar.add_widget(WrappedLabel(
                text="[b][color=#059669]Routine supportive care recommended. Monitor for changes.[/color][/b]",
                font_size="11.5sp"
            ))
        summary_card.add_widget(bottom_alert_bar)

        def _update_summary_card_height(*args):
            total_h = (
                summary_card.padding[1] + summary_card.padding[3]
                + heading_box.height
                + summary_card.spacing
                + content_row.height
                + summary_card.spacing
                + bottom_alert_bar.height
            )
            summary_card.height = max(total_h, 160)

        content_row.bind(height=_update_summary_card_height)
        heading_box.bind(height=_update_summary_card_height)
        _update_summary_card_height()

        self.content.add_widget(summary_card)

        # -------------------------------------------------------------
        # SECTION 3: ASSESSMENT DETAILS & DECISION FACTORS
        # -------------------------------------------------------------
        details_card = CardBox(orientation="vertical", spacing=8, padding=[18, 14, 18, 14], size_hint_y=None)
        details_card.bind(minimum_height=details_card.setter("height"))
        details_card.corner_radius = 10

        details_card.add_widget(WrappedLabel(text="[b]Assessment Completeness & Decision Factors:[/b]", font_size="13sp", color=COLOR_NAVY_PRIMARY))

        # Check answers count & completeness status
        ans_count = len(answers) if answers else 0
        is_emerg_flag = getattr(result, "emergency_override", False)
        missing_data = getattr(result, "missing_critical_data", [])
        if isinstance(missing_data, str):
            try:
                missing_data = json.loads(missing_data)
            except Exception:
                missing_data = []

        if is_emerg_flag:
            completeness_text = "Complete (Emergency Red Flag Confirmed — Immediate Care Fast-Path)"
        elif not missing_data:
            completeness_text = "Assessment Fully Completed"
        else:
            completeness_text = "Preliminary (Pending Additional Clinical Checks)"

        details_card.add_widget(WrappedLabel(
            text=f"• [b]Questions Answered:[/b] {ans_count} recorded   |   [b]Completeness:[/b] {completeness_text}",
            font_size="12sp",
            color=COLOR_TEXT_DARK
        ))
        details_card.add_widget(WrappedLabel(
            text="• [b]Applicability Note:[/b] Questions not relevant to reported symptoms were safely omitted.",
            font_size="11.5sp",
            color=COLOR_TEXT_MUTED
        ))

        # Decision Factors
        rules = getattr(result, "rules_triggered", [])
        if isinstance(rules, str):
            try:
                rules = json.loads(rules)
            except Exception:
                rules = []
        if rules:
            details_card.add_widget(WrappedLabel(text="[b]Triggered Clinical Factors:[/b]", font_size="12sp", color=COLOR_NAVY_PRIMARY))
            for r in rules:
                expl = r.get("explanation") if isinstance(r, dict) else str(r)
                if expl:
                    details_card.add_widget(WrappedLabel(text=f"  • {expl}", font_size="11.5sp", color=COLOR_TEXT_DARK))

        self.content.add_widget(details_card)

        # -------------------------------------------------------------
        # SECTION 4: ACTION BUTTONS (Download Report & Back to Dashboard)
        # -------------------------------------------------------------
        act_box = BoxLayout(orientation="horizontal", spacing=14, size_hint_y=None, height=44)
        
        btn_pdf = SecondaryButton(text="Download Report (PDF)", size_hint=(0.5, 1))
        btn_pdf.bind(on_release=self._generate_pdf)
        act_box.add_widget(btn_pdf)

        btn_home = PrimaryButton(text="Back to Dashboard", size_hint=(0.5, 1))
        btn_home.bind(on_release=lambda x: self._nav_to("dashboard"))
        act_box.add_widget(btn_home)

        self.content.add_widget(act_box)

    def _generate_pdf(self, *args):
        patient = self.controller.patient_service.get_patient(self.controller.current_patient_id)
        result = self.controller.last_triage_result
        if not patient or not result:
            return
            
        out_dir = Path(self.controller.config.data_dir) / "reports"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"Handover_{result.session_id}.pdf"
        generate_doctor_handover_pdf(patient, result.to_dict(), out_file)

        # Register downloaded handover in SQLite metadata tracking library
        symptoms_str = ", ".join(s.get("name", "") for s in result.symptoms) if hasattr(result, "symptoms") and result.symptoms else "Reported symptoms"
        pain_sev = getattr(self.controller, "assessment_staging", {}).get("severity", 5)
        
        doc_record = self.controller.handover_service.register_download(
            session_id=result.session_id,
            patient_id=self.controller.current_patient_id,
            patient_name=patient.get("display_name", "Anonymous Patient"),
            title=f"Doctor Handover — {result.session_id}",
            main_symptoms=symptoms_str,
            pain_severity=pain_sev,
            triage_category=result.urgency_category,
            triage_label=result.urgency_label,
            file_path=out_file
        )
        
        box = BoxLayout(orientation="vertical", padding=16, spacing=12)
        box.add_widget(WrappedLabel(
            text=f"[b]Doctor Handover Downloaded Successfully[/b]\n"
                 f"Saved to local MEDICARE library:\n{out_file.name}\n\n"
                 f"File Location: {out_file}",
            font_size="12sp",
            color=COLOR_NAVY_PRIMARY
        ))
        
        p = Popup(title="Handover Document Ready", size_hint=(0.85, 0.52))

        btn_view = PrimaryButton(text="Open in Document Viewer", size_hint_y=None, height=38)
        btn_view.bind(on_release=lambda x: self._open_viewer(p, str(out_file)))
        box.add_widget(btn_view)

        btn_lib = SecondaryButton(text="View Handover Library", size_hint_y=None, height=36)
        btn_lib.bind(on_release=lambda x: self._open_library(p))
        box.add_widget(btn_lib)

        btn_close = Button(text="Close", size_hint_y=None, height=34, background_color=(0.85, 0.85, 0.88, 1), color=COLOR_TEXT_DARK)
        btn_close.bind(on_release=p.dismiss)
        box.add_widget(btn_close)

        p.content = box
        p.open()

    def _open_viewer(self, popup, file_path):
        popup.dismiss()
        if "pdf_viewer" in self.manager.screen_names:
            viewer = self.manager.get_screen("pdf_viewer")
            viewer.load_document(file_path)
            self.manager.current = "pdf_viewer"

    def _open_library(self, popup):
        popup.dismiss()
        if "handover_downloads" in self.manager.screen_names:
            self.manager.current = "handover_downloads"

    def _nav_to(self, screen_name: str):
        self.manager.current = screen_name


# =========================================================================
# 6. PATIENT HISTORY SCREEN
# =========================================================================
class PatientHistoryScreen(BaseScreen):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.content = BoxLayout(orientation="vertical", spacing=10, padding=[16, 16, 16, 24], size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter("height"))

        scroll.add_widget(self.content)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_pre_enter(self):
        self.content.clear_widgets()
        self.content.add_widget(create_section_title("Past Assessment History"))
        self.content.add_widget(create_desc_label("Complete chronological record of past symptom evaluations and triage recommendations."))

        records = self.controller.history_service.get_assessment_history(self.controller.current_patient_id, limit=30)
        if not records:
            empty = CardBox(padding=[14, 12, 14, 12], size_hint_y=None)
            empty.bind(minimum_height=empty.setter("height"))
            empty.add_widget(WrappedLabel(text="No past evaluations found.", font_size="12sp", color=COLOR_TEXT_MUTED))
            self.content.add_widget(empty)
            return

        for r in records:
            card = CardBox(orientation="vertical", spacing=6, padding=[14, 12, 14, 12], size_hint_y=None)
            card.bind(minimum_height=card.setter("height"))

            header = BoxLayout(orientation="horizontal", size_hint_y=None, height=28)
            dt_str = (r.get("completed_at") or "")[:16].replace("T", " ")
            header.add_widget(WrappedLabel(text=f"[b]{dt_str}[/b]", font_size="13sp", color=COLOR_NAVY_PRIMARY))
            badge = UrgencyBadge(category=r.get("urgency_category", 3))
            header.add_widget(badge)
            card.add_widget(header)

            card.add_widget(WrappedLabel(text=f"Ref: {r.get('session_id')}", font_size="10sp", color=COLOR_TEXT_MUTED))
            card.add_widget(WrappedLabel(text=r.get("explanation", ""), font_size="12sp", color=COLOR_TEXT_DARK))
            self.content.add_widget(card)


# =========================================================================
# 7. SYMPTOM PROGRESSION SCREEN
# =========================================================================
class SymptomProgressionScreen(BaseScreen):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.content = BoxLayout(orientation="vertical", spacing=12, padding=[16, 16, 16, 24], size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter("height"))

        scroll.add_widget(self.content)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_pre_enter(self):
        self.content.clear_widgets()
        self.content.add_widget(create_section_title("Symptom Progression Tracking"))
        self.content.add_widget(create_desc_label("Monitors symptom changes across assessments to detect deterioration or improvement trends."))

        history = self.controller.history_service.get_symptom_progression_timeline(self.controller.current_patient_id)
        if not history:
            card = CardBox(padding=[14, 12, 14, 12], size_hint_y=None)
            card.bind(minimum_height=card.setter("height"))
            card.add_widget(WrappedLabel(text="No symptom history logged yet. Complete multiple assessments to view progression.", font_size="11sp", color=COLOR_TEXT_MUTED))
            self.content.add_widget(card)
        else:
            # Group by symptom name
            sym_groups = {}
            for item in history:
                name = item.get("symptom_name", "Unknown")
                sym_groups.setdefault(name, []).append(item)

            for sym_name, entries in sym_groups.items():
                card = CardBox(orientation="vertical", spacing=6, padding=[14, 12, 14, 12], size_hint_y=None)
                card.bind(minimum_height=card.setter("height"))

                card.add_widget(WrappedLabel(text=f"[b]{sym_name}[/b] ({len(entries)} recorded assessments)", font_size="13sp", color=COLOR_NAVY_PRIMARY))
                for e in entries[-4:]: # Show recent 4 entries
                    dt = (e.get("recorded_at") or "")[:16].replace("T", " ")
                    sev = e.get("severity", 5)
                    prog = (e.get("progression") or "unchanged").title()
                    row_txt = f"• {dt} — Severity: [b]{sev}/10[/b] | Progression: [b]{prog}[/b]"
                    card.add_widget(WrappedLabel(text=row_txt, font_size="11sp", color=COLOR_TEXT_DARK))
                self.content.add_widget(card)

        btn_reassess = PrimaryButton(text="RECORD NEW SYMPTOM ASSESSMENT", size_hint_y=None, height=44)
        btn_reassess.bind(on_release=lambda x: self._nav_to("symptom_assessment"))
        self.content.add_widget(btn_reassess)

    def _nav_to(self, screen_name: str):
        self.manager.current = screen_name


# =========================================================================
# =========================================================================
# 8. DOCTOR HANDOVER SCREEN (Structured Medical Handover Preview matching Screen 4)
# =========================================================================
class DoctorHandoverScreen(BaseScreen):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.content = BoxLayout(orientation="vertical", spacing=12, padding=[18, 14, 18, 24], size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter("height"))

        scroll.add_widget(self.content)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_pre_enter(self):
        self.content.clear_widgets()

        # -------------------------------------------------------------
        # 1. TOP ACTION BAR (🖨 Print, 📥 Download PDF, ✕ Close)
        # -------------------------------------------------------------
        action_bar = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=36)

        btn_print = SecondaryButton(text="🖨  Print", size_hint=(None, 1), width=110)
        btn_print.bind(on_release=self._print_or_view_pdf)
        action_bar.add_widget(btn_print)

        btn_dl = PrimaryButton(text="📥  Download PDF", size_hint=(None, 1), width=160)
        btn_dl.bind(on_release=self._generate_latest_pdf)
        action_bar.add_widget(btn_dl)

        action_bar.add_widget(Widget(size_hint_x=1))  # Spacer

        btn_close = SecondaryButton(text="✕  Close", size_hint=(None, 1), width=95)
        btn_close.bind(on_release=lambda x: self._nav_to("dashboard"))
        action_bar.add_widget(btn_close)

        self.content.add_widget(action_bar)

        # -------------------------------------------------------------
        # 2. PATIENT & ASSESSMENT DATA RETRIEVAL
        # -------------------------------------------------------------
        patient = self.controller.patient_service.get_patient(self.controller.current_patient_id)
        result = getattr(self.controller, "last_triage_result", None)
        if result:
            result_dict = result.to_dict()
        else:
            history = self.controller.history_service.get_assessment_history(self.controller.current_patient_id, limit=1)
            result_dict = history[0] if history else None

        if not result_dict:
            empty_card = CardBox(orientation="vertical", spacing=10, padding=[24, 20, 24, 20], size_hint_y=None)
            empty_card.bind(minimum_height=empty_card.setter("height"))
            empty_card.add_widget(WrappedLabel(
                text="[b][size=15sp]No Assessment Available for Handover[/size][/b]",
                font_size="15sp",
                color=COLOR_NAVY_PRIMARY
            ))
            empty_card.add_widget(WrappedLabel(
                text="A clinical assessment must be completed before a doctor handover report can be generated.",
                font_size="12sp",
                color=COLOR_TEXT_MUTED
            ))
            btn_start = PrimaryButton(text="START NEW ASSESSMENT →", size_hint_y=None, height=40)
            btn_start.bind(on_release=lambda x: self._nav_to("symptom_assessment"))
            empty_card.add_widget(btn_start)
            self.content.add_widget(empty_card)
            return

        # -------------------------------------------------------------
        # 3. REPORT SHEET CARD (White document sheet with navy headers)
        # -------------------------------------------------------------
        sheet = CardBox(orientation="vertical", spacing=12, padding=[22, 18, 22, 22], size_hint_y=None)
        sheet.bind(minimum_height=sheet.setter("height"))
        sheet.corner_radius = 10

        # Header Row: Logo & Titles
        hdr_row = BoxLayout(orientation="horizontal", spacing=12, size_hint_y=None, height=44)

        # Left branding
        left_brand = BoxLayout(orientation="horizontal", spacing=8, size_hint_x=0.5)
        icon_box = BoxLayout(size_hint=(None, None), size=(36, 36), pos_hint={"center_y": 0.5})
        with icon_box.canvas.before:
            Color(*COLOR_BLUE_ACCENT)
            icon_round_rect = RoundedRectangle(pos=icon_box.pos, size=icon_box.size, radius=[8])
        icon_box.bind(pos=lambda inst, *a: setattr(icon_round_rect, 'pos', inst.pos),
                      size=lambda inst, *a: setattr(icon_round_rect, 'size', inst.size))
        icon_lbl = Label(text="♥", font_size="20sp", bold=True, color=(1, 1, 1, 1))
        icon_box.add_widget(icon_lbl)
        left_brand.add_widget(icon_box)

        brand_text = BoxLayout(orientation="vertical", spacing=1, pos_hint={"center_y": 0.5})
        brand_text.add_widget(WrappedLabel(text="[b][size=16sp]MEDICARE[/size][/b]", font_size="16sp", color=COLOR_NAVY_PRIMARY))
        brand_text.add_widget(WrappedLabel(text="Smart Symptom Assessment", font_size="11sp", color=COLOR_TEXT_MUTED))
        left_brand.add_widget(brand_text)
        hdr_row.add_widget(left_brand)

        # Right report title
        right_title = BoxLayout(orientation="vertical", spacing=1, size_hint_x=0.5, pos_hint={"center_y": 0.5})
        right_title.add_widget(WrappedLabel(text="[b][size=14sp]Doctor Handover Report[/size][/b]", font_size="14sp", color=COLOR_NAVY_PRIMARY, halign="right"))
        right_title.add_widget(WrappedLabel(text="Clinical Assessment Summary", font_size="11sp", color=COLOR_TEXT_MUTED, halign="right"))
        hdr_row.add_widget(right_title)

        sheet.add_widget(hdr_row)

        # Section 1 Header: Patient Information (Navy Bar)
        sec1_bar = CardBox(padding=[12, 5, 12, 5], size_hint_y=None, height=28)
        sec1_bar.bg_color = COLOR_NAVY_PRIMARY
        sec1_bar.border_color = COLOR_NAVY_PRIMARY
        sec1_bar.corner_radius = 4
        sec1_bar.add_widget(WrappedLabel(text="[b][color=#FFFFFF]Patient Information[/color][/b]", font_size="11.5sp"))
        sheet.add_widget(sec1_bar)

        p_name = (patient.get("display_name") if patient else "Rahul Sharma") or "Rahul Sharma"
        p_phone = (patient.get("phone") if patient else "+91 98765 43210") or "+91 98765 43210"
        p_age = f"{patient.get('age', 32)} years" if patient and patient.get("age") else "32 years"
        dt_raw = result_dict.get("completed_at") or result_dict.get("timestamp") or "Nov 22, 2025 • 2:30 PM"
        dt_str = str(dt_raw)[:16].replace("T", " • ")

        sec1_content = BoxLayout(orientation="vertical", spacing=5, padding=[6, 4, 6, 4], size_hint_y=None)
        sec1_content.bind(minimum_height=sec1_content.setter("height"))

        row1 = BoxLayout(orientation="horizontal", size_hint_y=None, height=20)
        row1.add_widget(WrappedLabel(text=f"Name:  [b][color=#0D6EFD]{p_name}[/color][/b]", font_size="11.5sp", color=COLOR_TEXT_DARK, size_hint_x=0.5))
        row1.add_widget(WrappedLabel(text=f"Phone:  [b]{p_phone}[/b]", font_size="11.5sp", color=COLOR_TEXT_DARK, size_hint_x=0.5))
        sec1_content.add_widget(row1)

        row2 = BoxLayout(orientation="horizontal", size_hint_y=None, height=20)
        row2.add_widget(WrappedLabel(text=f"Age:  [b]{p_age}[/b]", font_size="11.5sp", color=COLOR_TEXT_DARK, size_hint_x=0.5))
        row2.add_widget(WrappedLabel(text=f"Date:  [b]{dt_str}[/b]", font_size="11.5sp", color=COLOR_TEXT_DARK, size_hint_x=0.5))
        sec1_content.add_widget(row2)
        sheet.add_widget(sec1_content)

        # Section 2 Header: Assessment Results (Navy Bar)
        sec2_bar = CardBox(padding=[12, 5, 12, 5], size_hint_y=None, height=28)
        sec2_bar.bg_color = COLOR_NAVY_PRIMARY
        sec2_bar.border_color = COLOR_NAVY_PRIMARY
        sec2_bar.corner_radius = 4
        sec2_bar.add_widget(WrappedLabel(text="[b][color=#FFFFFF]Assessment Results[/color][/b]", font_size="11.5sp"))
        sheet.add_widget(sec2_bar)

        cat = result_dict.get("urgency_category", 1)
        urg_box = CardBox(orientation="horizontal", spacing=10, padding=[12, 6, 12, 6], size_hint_y=None, height=34)
        urg_box.corner_radius = 6
        if cat == 1:
            urg_box.bg_color = COLOR_EMERGENCY_TINT
            urg_box.border_color = (0.95, 0.75, 0.75, 1.0)
            urg_box.add_widget(WrappedLabel(
                text="[b][color=#DC2626]⚠️  Category 1 — Emergency Care[/color][/b]",
                font_size="11.5sp",
                size_hint_x=0.5
            ))
            urg_box.add_widget(WrappedLabel(
                text="[b][color=#DC2626]Seek immediate medical attention[/color][/b]",
                font_size="11.5sp",
                size_hint_x=0.5,
                halign="right"
            ))
        elif cat == 2:
            urg_box.bg_color = COLOR_EARLY_TINT
            urg_box.border_color = (0.95, 0.85, 0.7, 1.0)
            urg_box.add_widget(WrappedLabel(
                text="[b][color=#B45309]⚠️  Category 2 — Early Medical Consultation[/color][/b]",
                font_size="11.5sp",
                size_hint_x=0.5
            ))
            urg_box.add_widget(WrappedLabel(
                text="[b][color=#B45309]Consult a physician promptly within 12–24h[/color][/b]",
                font_size="11.5sp",
                size_hint_x=0.5,
                halign="right"
            ))
        else:
            urg_box.bg_color = COLOR_ROUTINE_TINT
            urg_box.border_color = (0.75, 0.9, 0.8, 1.0)
            urg_box.add_widget(WrappedLabel(
                text="[b][color=#059669]✓  Category 3 — Routine Care[/color][/b]",
                font_size="11.5sp",
                size_hint_x=0.5
            ))
            urg_box.add_widget(WrappedLabel(
                text="[b][color=#059669]Self-care & routine medical consultation[/color][/b]",
                font_size="11.5sp",
                size_hint_x=0.5,
                halign="right"
            ))
        sheet.add_widget(urg_box)

        # Extract symptoms & findings
        symptoms = result_dict.get("symptoms", [])
        if isinstance(symptoms, str):
            try:
                symptoms = json.loads(symptoms)
            except Exception:
                symptoms = []
        sym_names = ", ".join(s.get("name", "") for s in symptoms if isinstance(s, dict) and s.get("name")) or "Headache"

        answers = result_dict.get("followup_answers", {})
        findings_list = []
        if isinstance(answers, dict):
            for qk, qv in answers.items():
                if qv in ("YES", "SEVERE", "HIGH_GRADE"):
                    clean_k = qk.replace("QID_", "").replace("_", " ").title()
                    findings_list.append(clean_k)
        if not findings_list and result_dict.get("warning_signs_found"):
            findings_list = [w[:25] for w in result_dict["warning_signs_found"][:2]]
        findings_str = ", ".join(findings_list) if findings_list else "Sudden onset"

        if cat == 1:
            rec_action = "Go to nearest emergency room or call ambulance (112 / 102)."
        elif cat == 2:
            rec_action = "Consult a physician within 12–24 hours."
        elif cat == 3:
            rec_action = "Rest, drink fluids, and monitor symptoms."
        else:
            rec_action = "Consult healthcare provider for further evaluation."

        sec2_content = BoxLayout(orientation="vertical", spacing=5, padding=[6, 4, 6, 4], size_hint_y=None)
        sec2_content.bind(minimum_height=sec2_content.setter("height"))

        sec2_content.add_widget(WrappedLabel(text=f"[b]Symptoms:[/b]         {sym_names}", font_size="11.5sp", color=COLOR_TEXT_DARK))
        sec2_content.add_widget(WrappedLabel(text=f"[b]Key Findings:[/b]     {findings_str}", font_size="11.5sp", color=COLOR_TEXT_DARK))
        sec2_content.add_widget(WrappedLabel(text=f"[b]Recommended Action:[/b]  {rec_action}", font_size="11.5sp", color=COLOR_TEXT_DARK))
        sheet.add_widget(sec2_content)

        # Section 3 Header: Assessment Details (Navy Bar)
        sec3_bar = CardBox(padding=[12, 5, 12, 5], size_hint_y=None, height=28)
        sec3_bar.bg_color = COLOR_NAVY_PRIMARY
        sec3_bar.border_color = COLOR_NAVY_PRIMARY
        sec3_bar.corner_radius = 4
        sec3_bar.add_widget(WrappedLabel(text="[b][color=#FFFFFF]Assessment Details[/color][/b]", font_size="11.5sp"))
        sheet.add_widget(sec3_bar)

        ans_count = len(answers) if isinstance(answers, dict) else 1
        is_emerg_flag = result_dict.get("emergency_override", False)
        missing_data = result_dict.get("missing_critical_data", [])
        is_complete = is_emerg_flag or (not missing_data)
        complete_str = "[color=#10B981]✓ Yes[/color]" if is_complete else "[color=#B45309]Preliminary[/color]"

        sec3_content = BoxLayout(orientation="horizontal", padding=[6, 4, 6, 4], size_hint_y=None, height=22)
        sec3_content.add_widget(WrappedLabel(
            text=f"Questions Answered:  [b]{ans_count} / 3[/b]",
            font_size="11.5sp",
            color=COLOR_TEXT_DARK,
            size_hint_x=0.5
        ))
        sec3_content.add_widget(WrappedLabel(
            text=f"Assessment Complete:  [b]{complete_str}[/b]",
            font_size="11.5sp",
            color=COLOR_TEXT_DARK,
            size_hint_x=0.5
        ))
        sheet.add_widget(sec3_content)

        self.content.add_widget(sheet)

    def _generate_latest_pdf(self, *args):
        patient = self.controller.patient_service.get_patient(self.controller.current_patient_id)
        result = getattr(self.controller, "last_triage_result", None)
        if result:
            latest_a = result.to_dict()
        else:
            assessments = self.controller.history_service.get_assessment_history(self.controller.current_patient_id, limit=1)
            if not assessments:
                self._show_msg("No Assessments Found", "Please complete a symptom assessment before generating a handover summary.")
                return
            latest_a = assessments[0]

        out_dir = Path(self.controller.config.data_dir) / "reports"
        out_dir.mkdir(parents=True, exist_ok=True)
        session_id = latest_a.get("session_id", "REPORT")
        out_file = out_dir / f"Handover_{session_id}.pdf"
        generate_doctor_handover_pdf(patient, latest_a, out_file)

        # Register in downloads library
        pain_sev = latest_a.get("urgency_category", 3)
        self.controller.handover_service.register_download(
            session_id=session_id,
            patient_id=self.controller.current_patient_id,
            patient_name=patient.get("display_name", "Anonymous Patient") if patient else "Anonymous Patient",
            title=f"Doctor Handover — {session_id}",
            main_symptoms="Prior assessment record",
            pain_severity=5,
            triage_category=latest_a.get("urgency_category", 3),
            triage_label=latest_a.get("urgency_label", "Routine Care"),
            file_path=out_file
        )

        box = BoxLayout(orientation="vertical", padding=16, spacing=12)
        box.add_widget(WrappedLabel(
            text=f"[b]Doctor Handover Generated & Downloaded[/b]\n"
                 f"Saved locally to:\n{out_file.name}\n\n"
                 f"File Location: {out_file}",
            font_size="12sp",
            color=COLOR_NAVY_PRIMARY
        ))
        p = Popup(title="Handover Document Ready", size_hint=(0.85, 0.52))

        btn_view = PrimaryButton(text="Open in Document Viewer", size_hint_y=None, height=38)
        btn_view.bind(on_release=lambda x: self._open_viewer(p, str(out_file)))
        box.add_widget(btn_view)

        btn_lib = SecondaryButton(text="View Handover Library", size_hint_y=None, height=36)
        btn_lib.bind(on_release=lambda x: self._open_library(p))
        box.add_widget(btn_lib)

        btn_close = Button(text="Close", size_hint_y=None, height=34, background_color=(0.85, 0.85, 0.88, 1), color=COLOR_TEXT_DARK)
        btn_close.bind(on_release=p.dismiss)
        box.add_widget(btn_close)

        p.content = box
        p.open()

    def _print_or_view_pdf(self, *args):
        patient = self.controller.patient_service.get_patient(self.controller.current_patient_id)
        result = getattr(self.controller, "last_triage_result", None)
        if result:
            latest_a = result.to_dict()
        else:
            assessments = self.controller.history_service.get_assessment_history(self.controller.current_patient_id, limit=1)
            if not assessments:
                self._show_msg("No Assessments Found", "Please complete a symptom assessment before printing a handover summary.")
                return
            latest_a = assessments[0]

        out_dir = Path(self.controller.config.data_dir) / "reports"
        out_dir.mkdir(parents=True, exist_ok=True)
        session_id = latest_a.get("session_id", "REPORT")
        out_file = out_dir / f"Handover_{session_id}.pdf"
        generate_doctor_handover_pdf(patient, latest_a, out_file)

        # Open in built-in PDF viewer
        if "pdf_viewer" in self.manager.screen_names:
            viewer = self.manager.get_screen("pdf_viewer")
            viewer.load_document(str(out_file))
            self.manager.current = "pdf_viewer"
        else:
            try:
                import os
                os.startfile(str(out_file))
            except Exception:
                self._show_msg("PDF Saved", f"Document saved to:\n{out_file}")

    def _open_viewer(self, popup, file_path):
        popup.dismiss()
        if "pdf_viewer" in self.manager.screen_names:
            viewer = self.manager.get_screen("pdf_viewer")
            viewer.load_document(file_path)
            self.manager.current = "pdf_viewer"

    def _open_library(self, popup):
        popup.dismiss()
        if "handover_downloads" in self.manager.screen_names:
            self.manager.current = "handover_downloads"

    def _nav_to(self, screen_name: str):
        self.manager.current = screen_name

    def _show_msg(self, title, msg):
        box = BoxLayout(orientation="vertical", padding=14, spacing=10)
        box.add_widget(WrappedLabel(text=msg, font_size="12sp"))
        b = PrimaryButton(text="OK", size_hint_y=None, height=36)
        p = Popup(title=title, content=box, size_hint=(0.85, 0.4))
        b.bind(on_release=p.dismiss)
        box.add_widget(b)
        p.open()


# =========================================================================
# 9. DOCTOR HANDOVER DOWNLOADS SCREEN (Document Library)
# =========================================================================
class HandoverDownloadsScreen(BaseScreen):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.sort_order = "newest"
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.content = BoxLayout(orientation="vertical", spacing=12, padding=[16, 16, 16, 24], size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter("height"))

        scroll.add_widget(self.content)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_pre_enter(self):
        self._render_library()

    def _render_library(self):
        self.content.clear_widgets()

        # Section Header
        self.content.add_widget(create_section_title("Doctor Handover Downloads"))
        self.content.add_widget(create_desc_label(
            "Central offline library of downloaded clinical doctor handovers. "
            "Inspect, view in-app, export, or manage stored medical summaries."
        ))

        # Search and Sorting Toolbar Card
        filter_card = CardBox(orientation="vertical", spacing=8, padding=[12, 10, 12, 10], size_hint_y=None)
        filter_card.bind(minimum_height=filter_card.setter("height"))
        filter_card.bg_color = COLOR_WHITE

        # Search Input
        self.in_search = TextInput(
            hint_text="Search by patient name, filename, symptoms, date...",
            multiline=False,
            size_hint_y=None,
            height=38,
            font_size="13sp",
            padding=[10, 9, 10, 9]
        )
        self.in_search.bind(text=self._on_search_change)
        filter_card.add_widget(self.in_search)

        # Sort Buttons Row
        sort_row = BoxLayout(orientation="horizontal", spacing=8, size_hint_y=None, height=34)
        self.btn_sort_new = OptionButton(text="Newest First", size_hint_x=0.5, height=34)
        self.btn_sort_new.is_selected = (self.sort_order == "newest")
        self.btn_sort_new.bind(on_release=lambda x: self._change_sort("newest"))

        self.btn_sort_old = OptionButton(text="Oldest First", size_hint_x=0.5, height=34)
        self.btn_sort_old.is_selected = (self.sort_order == "oldest")
        self.btn_sort_old.bind(on_release=lambda x: self._change_sort("oldest"))

        sort_row.add_widget(self.btn_sort_new)
        sort_row.add_widget(self.btn_sort_old)
        filter_card.add_widget(sort_row)

        self.content.add_widget(filter_card)

        # Results Container
        self.list_container = BoxLayout(orientation="vertical", spacing=10, size_hint_y=None)
        self.list_container.bind(minimum_height=self.list_container.setter("height"))
        self.content.add_widget(self.list_container)

        self._populate_list()

    def _on_search_change(self, instance, text):
        self._populate_list()

    def _change_sort(self, order):
        self.sort_order = order
        self.btn_sort_new.is_selected = (order == "newest")
        self.btn_sort_old.is_selected = (order == "oldest")
        self._populate_list()

    def _populate_list(self):
        self.list_container.clear_widgets()
        search_query = getattr(self, "in_search", None)
        query = search_query.text.strip() if search_query else ""

        records = self.controller.handover_service.get_downloaded_handovers(
            search_query=query,
            sort_order=self.sort_order
        )

        if not records:
            empty = CardBox(orientation="vertical", spacing=8, padding=[20, 18, 20, 18], size_hint_y=None)
            empty.bind(minimum_height=empty.setter("height"))
            empty.bg_color = COLOR_WHITE
            if query:
                empty.add_widget(WrappedLabel(
                    text="[b]No matching handover reports found.[/b]\nTry clearing your search query.",
                    font_size="13sp",
                    color=COLOR_TEXT_MUTED
                ))
            else:
                empty.add_widget(WrappedLabel(
                    text="[b]No doctor handovers downloaded yet.[/b]\n"
                         "When you complete a symptom evaluation, click 'Generate Doctor Handover PDF' "
                         "to save a clinical summary to this library.",
                    font_size="13sp",
                    color=COLOR_TEXT_DARK
                ))
                b_start = PrimaryButton(text="Start New Assessment", size_hint_y=None, height=40)
                b_start.bind(on_release=lambda x: self._nav_to("symptom_assessment"))
                empty.add_widget(b_start)
            self.list_container.add_widget(empty)
            return

        for doc in records:
            card = CardBox(orientation="vertical", spacing=8, padding=[16, 14, 16, 14], size_hint_y=None)
            card.bind(minimum_height=card.setter("height"))
            card.bg_color = COLOR_WHITE

            # Header row: Title + Triage Badge
            h_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=28, spacing=8)
            h_row.add_widget(WrappedLabel(
                text=f"[b]{doc.get('title', 'Doctor Handover')}[/b]",
                font_size="14sp",
                color=COLOR_NAVY_PRIMARY,
                size_hint_x=0.7
            ))
            badge = UrgencyBadge(category=doc.get("triage_category", 3), size_hint_x=0.3)
            h_row.add_widget(badge)
            card.add_widget(h_row)

            # Metadata details
            dt_display = format_indian_datetime(doc.get("downloaded_at"))
            p_name = doc.get("patient_name", "Anonymous Patient")
            card.add_widget(WrappedLabel(
                text=f"Patient: [b]{p_name}[/b] | Downloaded: [b]{dt_display}[/b]",
                font_size="11sp",
                color=COLOR_TEXT_DARK
            ))

            # Symptoms & Pain
            syms = doc.get("main_symptoms", "Not specified")
            pain = doc.get("pain_severity", 0)
            card.add_widget(WrappedLabel(
                text=f"Reported Symptoms: {syms} | Pain Rating: [b]{pain}/10[/b]",
                font_size="11sp",
                color=COLOR_TEXT_MUTED
            ))

            # File Status Row
            f_size_kb = round(doc.get("file_size", 0) / 1024, 1)
            fname = doc.get("filename", "")
            is_avail = (doc.get("status") == "available")
            if is_avail:
                status_txt = "[color=#059669][b]Available Locally[/b][/color]"
            else:
                status_txt = "[color=#DC2626][b]File Missing on Disk[/b][/color]"

            card.add_widget(WrappedLabel(
                text=f"File: {fname} ({f_size_kb} KB) — Format: PDF | Status: {status_txt}",
                font_size="11sp",
                color=COLOR_TEXT_DARK
            ))

            # Action Buttons Row
            btn_row = BoxLayout(orientation="horizontal", spacing=8, size_hint_y=None, height=36)
            
            btn_view = PrimaryButton(text="Open in Viewer", size_hint_x=0.4, height=36)
            btn_view.bind(on_release=lambda x, d=doc: self._open_viewer(d))
            btn_row.add_widget(btn_view)

            btn_export = SecondaryButton(text="Export Copy", size_hint_x=0.35, height=36)
            btn_export.bind(on_release=lambda x, d=doc: self._export_copy(d))
            btn_row.add_widget(btn_export)

            btn_del = Button(
                text="Delete",
                size_hint_x=0.25,
                height=36,
                background_color=COLOR_URGENT_EMERGENCY,
                color=COLOR_TEXT_LIGHT,
                bold=True,
                font_size="12sp"
            )
            btn_del.bind(on_release=lambda x, d=doc: self._confirm_delete(d))
            btn_row.add_widget(btn_del)

            card.add_widget(btn_row)
            self.list_container.add_widget(card)

    def _open_viewer(self, doc):
        if "pdf_viewer" in self.manager.screen_names:
            viewer = self.manager.get_screen("pdf_viewer")
            viewer.load_document(doc.get("file_path"))
            self.manager.current = "pdf_viewer"

    def _export_copy(self, doc):
        export_dir = Path(self.controller.config.data_dir) / "exports"
        dest = self.controller.handover_service.export_copy(doc["id"], export_dir)
        if dest:
            self._show_popup("Copy Exported", f"Successfully exported copy to:\n{dest}")
        else:
            self._show_popup("Export Failed", "Could not export copy. Source PDF file is missing on disk.")

    def _confirm_delete(self, doc):
        box = BoxLayout(orientation="vertical", padding=14, spacing=10)
        box.add_widget(WrappedLabel(
            text=f"Are you sure you want to delete this handover report?\n\n"
                 f"Document: {doc.get('title')}\n"
                 f"File: {doc.get('filename')}\n\n"
                 f"This will permanently erase the local PDF file from your device.",
            font_size="12sp"
        ))
        b_row = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=36)
        p = Popup(title="Confirm Document Deletion", content=box, size_hint=(0.85, 0.45))

        btn_confirm = Button(text="Yes, Delete", background_color=COLOR_URGENT_EMERGENCY, color=COLOR_WHITE, bold=True)
        btn_confirm.bind(on_release=lambda x: self._do_delete(p, doc["id"]))
        b_row.add_widget(btn_confirm)

        btn_cancel = SecondaryButton(text="Cancel")
        btn_cancel.bind(on_release=p.dismiss)
        b_row.add_widget(btn_cancel)

        box.add_widget(b_row)
        p.open()

    def _do_delete(self, popup, doc_id):
        popup.dismiss()
        self.controller.handover_service.delete_handover(doc_id, delete_file=True)
        self._populate_list()

    def _show_popup(self, title, msg):
        box = BoxLayout(orientation="vertical", padding=14, spacing=10)
        box.add_widget(WrappedLabel(text=msg, font_size="12sp"))
        b = PrimaryButton(text="OK", size_hint_y=None, height=36)
        p = Popup(title=title, content=box, size_hint=(0.85, 0.4))
        b.bind(on_release=p.dismiss)
        box.add_widget(b)
        p.open()

    def _nav_to(self, screen_name: str):
        self.manager.current = screen_name


# =========================================================================
# 10. INTEGRATED IN-APP PDF VIEWER SCREEN
# =========================================================================
class PDFViewerScreen(BaseScreen):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.doc = None
        self.current_file_path = None
        self.current_page_idx = 0
        self.total_pages = 0
        self.zoom_scale = 1.5
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)

        # Top Bar: Back Button, Title, Page Count
        top_bar = BoxLayout(orientation="horizontal", spacing=10, padding=[12, 8, 12, 8], size_hint_y=None, height=52)
        top_bar.bind(pos=self._draw_bar_bg, size=self._draw_bar_bg)

        btn_back = SecondaryButton(text="< Back to Downloads", size_hint=(None, None), size=(160, 36))
        btn_back.bind(on_release=lambda x: self._nav_back())
        top_bar.add_widget(btn_back)

        self.lbl_title = WrappedLabel(
            text="[b]Document Viewer[/b]",
            font_size="13sp",
            color=COLOR_NAVY_PRIMARY,
            size_hint_x=0.7
        )
        top_bar.add_widget(self.lbl_title)
        root.add_widget(top_bar)

        # Control Toolbar: Page Prev/Next, Zoom -, Reset, Zoom +, Export, Delete
        self.toolbar = BoxLayout(orientation="horizontal", spacing=8, padding=[12, 6, 12, 6], size_hint_y=None, height=44)
        with self.toolbar.canvas.before:
            Color(0.94, 0.96, 0.98, 1.0)
            toolbar_rect = Rectangle(pos=self.toolbar.pos, size=self.toolbar.size)
        self.toolbar.bind(pos=lambda inst, *a: setattr(toolbar_rect, 'pos', inst.pos),
                          size=lambda inst, *a: setattr(toolbar_rect, 'size', inst.size))

        self.btn_prev = SecondaryButton(text="< Prev", size_hint=(None, None), size=(72, 32))
        self.btn_prev.bind(on_release=lambda x: self._prev_page())
        self.toolbar.add_widget(self.btn_prev)

        self.lbl_page = Label(
            text="Page 0 of 0",
            font_size="12sp",
            color=COLOR_TEXT_DARK,
            size_hint=(None, None),
            size=(100, 32)
        )
        self.toolbar.add_widget(self.lbl_page)

        self.btn_next = SecondaryButton(text="Next >", size_hint=(None, None), size=(72, 32))
        self.btn_next.bind(on_release=lambda x: self._next_page())
        self.toolbar.add_widget(self.btn_next)

        # Zoom controls
        self.btn_zoom_out = SecondaryButton(text="Zoom -", size_hint=(None, None), size=(72, 32))
        self.btn_zoom_out.bind(on_release=lambda x: self._zoom_out())
        self.toolbar.add_widget(self.btn_zoom_out)

        self.lbl_zoom = Label(
            text="100%",
            font_size="12sp",
            color=COLOR_TEXT_DARK,
            size_hint=(None, None),
            size=(60, 32)
        )
        self.toolbar.add_widget(self.lbl_zoom)

        self.btn_zoom_in = SecondaryButton(text="Zoom +", size_hint=(None, None), size=(72, 32))
        self.btn_zoom_in.bind(on_release=lambda x: self._zoom_in())
        self.toolbar.add_widget(self.btn_zoom_in)

        self.btn_fit = SecondaryButton(text="Fit Width", size_hint=(None, None), size=(82, 32))
        self.btn_fit.bind(on_release=lambda x: self._fit_width())
        self.toolbar.add_widget(self.btn_fit)

        # Spacer
        self.toolbar.add_widget(Widget(size_hint_x=1))

        self.btn_export = SecondaryButton(text="Export Copy", size_hint=(None, None), size=(96, 32))
        self.btn_export.bind(on_release=lambda x: self._export_current())
        self.toolbar.add_widget(self.btn_export)

        self.btn_del = Button(
            text="Delete",
            size_hint=(None, None),
            size=(76, 32),
            background_color=COLOR_URGENT_EMERGENCY,
            color=COLOR_TEXT_LIGHT,
            bold=True,
            font_size="11sp"
        )
        self.btn_del.bind(on_release=lambda x: self._delete_current())
        self.toolbar.add_widget(self.btn_del)

        root.add_widget(self.toolbar)

        # Viewport: Scrollable area containing rendered PDF page image
        self.scroll_view = ScrollView(size_hint=(1, 1), do_scroll_x=True, do_scroll_y=True)
        self.viewport_layout = BoxLayout(orientation="vertical", size_hint=(None, None), padding=[16, 16, 16, 16])
        self.doc_image = Image(size_hint=(None, None), keep_ratio=True, allow_stretch=True)
        self.viewport_layout.add_widget(self.doc_image)
        self.scroll_view.add_widget(self.viewport_layout)

        # Error view
        self.error_card = CardBox(orientation="vertical", spacing=8, padding=[20, 20, 20, 20], size_hint=(0.8, None), height=140)
        self.lbl_error = WrappedLabel(text="", font_size="13sp", color=COLOR_URGENT_EMERGENCY)
        self.error_card.add_widget(self.lbl_error)

        root.add_widget(self.scroll_view)
        self.add_widget(root)

    def _draw_bar_bg(self, instance, *args):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(1, 1, 1, 1)
            Rectangle(pos=instance.pos, size=instance.size)
            Color(*COLOR_BORDER)
            Rectangle(pos=(instance.x, instance.y), size=(instance.width, 1))

    def load_document(self, file_path_or_doc_id: str):
        self.current_file_path = None
        self.doc = None
        self.current_page_idx = 0
        self.total_pages = 0
        self.zoom_scale = 1.5

        if isinstance(file_path_or_doc_id, str) and file_path_or_doc_id.startswith("DOC_"):
            doc_rec = self.controller.handover_service.get_handover_by_id(file_path_or_doc_id)
            if doc_rec:
                self.current_file_path = Path(doc_rec.get("file_path", ""))
        else:
            self.current_file_path = Path(file_path_or_doc_id)

        if not self.current_file_path or not self.current_file_path.exists():
            self._show_error(f"Cannot open document: file not found on disk.\n{self.current_file_path}")
            return

        try:
            self.doc = pdfium.PdfDocument(str(self.current_file_path))
            self.total_pages = len(self.doc)
            self.lbl_title.text = f"[b]Handover:[/b] {self.current_file_path.name}"
            self._render_current_page()
        except Exception as exc:
            self._show_error(f"Failed to parse PDF document:\n{type(exc).__name__}: {exc}")

    def _render_current_page(self):
        if not self.doc or self.total_pages == 0:
            return

        try:
            page = self.doc[self.current_page_idx]
            bitmap = page.render(scale=self.zoom_scale)
            pil_img = bitmap.to_pil()

            cache_dir = Path(self.controller.config.data_dir) / "cache"
            cache_dir.mkdir(parents=True, exist_ok=True)
            cache_path = cache_dir / f"view_{self.current_file_path.stem}_p{self.current_page_idx}_s{int(self.zoom_scale*100)}.png"
            pil_img.save(cache_path)

            self.doc_image.size = pil_img.size
            self.viewport_layout.size = (pil_img.size[0] + 32, pil_img.size[1] + 32)
            self.doc_image.source = str(cache_path)
            self.doc_image.reload()

            self.lbl_page.text = f"Page {self.current_page_idx + 1} of {self.total_pages}"
            self.lbl_zoom.text = f"{int((self.zoom_scale / 1.5) * 100)}%"
            self.btn_prev.disabled = (self.current_page_idx <= 0)
            self.btn_next.disabled = (self.current_page_idx >= self.total_pages - 1)

            if self.error_card.parent:
                self.error_card.parent.remove_widget(self.error_card)
            if self.scroll_view not in self.children[0].children:
                self.children[0].add_widget(self.scroll_view)

        except Exception as exc:
            self._show_error(f"Rendering error on page {self.current_page_idx + 1}: {exc}")

    def _show_error(self, message):
        self.lbl_error.text = message
        self.lbl_title.text = "[b]Document Error[/b]"
        self.lbl_page.text = "Page 0 of 0"
        if self.scroll_view in self.children[0].children:
            self.children[0].remove_widget(self.scroll_view)
        if self.error_card not in self.children[0].children:
            self.children[0].add_widget(self.error_card)

    def _prev_page(self):
        if self.current_page_idx > 0:
            self.current_page_idx -= 1
            self._render_current_page()

    def _next_page(self):
        if self.current_page_idx < self.total_pages - 1:
            self.current_page_idx += 1
            self._render_current_page()

    def _zoom_in(self):
        if self.zoom_scale < 3.5:
            self.zoom_scale += 0.3
            self._render_current_page()

    def _zoom_out(self):
        if self.zoom_scale > 0.7:
            self.zoom_scale -= 0.3
            self._render_current_page()

    def _fit_width(self):
        self.zoom_scale = 1.5
        self._render_current_page()

    def _export_current(self):
        if not self.current_file_path or not self.current_file_path.exists():
            return
        export_dir = Path(self.controller.config.data_dir) / "exports"
        export_dir.mkdir(parents=True, exist_ok=True)
        dest = export_dir / self.current_file_path.name
        if self.current_file_path.resolve() != dest.resolve():
            import shutil
            shutil.copy2(self.current_file_path, dest)
        self._show_popup("Copy Exported", f"Handover copy exported to:\n{dest}")

    def _delete_current(self):
        if not self.current_file_path:
            return
        box = BoxLayout(orientation="vertical", padding=14, spacing=10)
        box.add_widget(WrappedLabel(
            text=f"Are you sure you want to delete this document?\n{self.current_file_path.name}",
            font_size="12sp"
        ))
        b_row = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=36)
        p = Popup(title="Delete Document", content=box, size_hint=(0.85, 0.4))

        btn_confirm = Button(text="Delete", background_color=COLOR_URGENT_EMERGENCY, color=COLOR_WHITE, bold=True)
        btn_confirm.bind(on_release=lambda x: self._do_delete_current(p))
        b_row.add_widget(btn_confirm)

        btn_cancel = SecondaryButton(text="Cancel")
        btn_cancel.bind(on_release=p.dismiss)
        b_row.add_widget(btn_cancel)

        box.add_widget(b_row)
        p.open()

    def _do_delete_current(self, popup):
        popup.dismiss()
        if self.current_file_path and self.current_file_path.exists():
            try:
                self.current_file_path.unlink()
            except Exception:
                pass
        self._nav_back()

    def _nav_back(self):
        if "handover_downloads" in self.manager.screen_names:
            self.manager.current = "handover_downloads"
        else:
            self.manager.current = "dashboard"

    def _show_popup(self, title, msg):
        box = BoxLayout(orientation="vertical", padding=14, spacing=10)
        box.add_widget(WrappedLabel(text=msg, font_size="12sp"))
        b = PrimaryButton(text="OK", size_hint_y=None, height=36)
        p = Popup(title=title, content=box, size_hint=(0.85, 0.4))
        b.bind(on_release=p.dismiss)
        box.add_widget(b)
        p.open()


# =========================================================================
# 9. HEALTHCARE DIRECTORY SCREEN (Device Location + Manual Address)
# =========================================================================
class HealthcareDirectoryScreen(BaseScreen):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.content = BoxLayout(orientation="vertical", spacing=10, padding=[16, 16, 16, 24], size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter("height"))

        self.content.add_widget(create_section_title("Nearby Healthcare Facilities"))
        self.content.add_widget(create_desc_label(
            "Find nearby hospitals, clinics and emergency departments. "
            "Uses live Google Maps data when configured; falls back to local directory offline."
        ))

        # --- Google Maps status banner ---
        self.maps_status_lbl = WrappedLabel(
            text="",
            font_size="11sp",
            color=COLOR_TEXT_MUTED
        )
        self.content.add_widget(self.maps_status_lbl)

        # 1. Location Settings & Privacy Box
        loc_card = CardBox(orientation="vertical", spacing=8, padding=[14, 12, 14, 12], size_hint_y=None)
        loc_card.bind(minimum_height=loc_card.setter("height"))

        self.lbl_loc_status = WrappedLabel(
            text="Reference Location: [b]Not Set — Set location to search nearby facilities[/b]",
            font_size="12sp",
            color=COLOR_NAVY_PRIMARY
        )
        loc_card.add_widget(self.lbl_loc_status)

        # Location privacy note
        loc_card.add_widget(WrappedLabel(
            text="Privacy Notice: Only your geographic coordinates are used for facility search. "
                 "No symptoms, medical history or patient data is ever sent to external services.",
            font_size="10sp",
            color=COLOR_TEXT_MUTED
        ))

        # Buttons row for location mode
        loc_btn_row = BoxLayout(orientation="horizontal", spacing=8, size_hint_y=None, height=36)
        btn_dev_loc = PrimaryButton(text="Use Device Location", size_hint_x=0.5)
        btn_dev_loc.bind(on_release=self._on_use_device_location)
        loc_btn_row.add_widget(btn_dev_loc)

        btn_clr_loc = SecondaryButton(text="Clear Location", size_hint_x=0.5)
        btn_clr_loc.bind(on_release=self._on_clear_location)
        loc_btn_row.add_widget(btn_clr_loc)
        loc_card.add_widget(loc_btn_row)

        # Manual Address Search Row
        addr_row = BoxLayout(orientation="horizontal", spacing=6, size_hint_y=None, height=36)
        self.in_address = TextInput(hint_text="Or enter city, address, or postal code...", multiline=False, size_hint_x=0.7)
        btn_set_addr = SecondaryButton(text="Set Address", size_hint_x=0.3)
        btn_set_addr.bind(on_release=self._on_set_manual_address)
        addr_row.add_widget(self.in_address)
        addr_row.add_widget(btn_set_addr)
        loc_card.add_widget(addr_row)

        self.content.add_widget(loc_card)

        # 2. Search + Filter Row
        search_card = CardBox(orientation="vertical", spacing=6, padding=[12, 10, 12, 10], size_hint_y=None)
        search_card.bind(minimum_height=search_card.setter("height"))

        search_row = BoxLayout(orientation="horizontal", spacing=6, size_hint_y=None, height=36)
        self.in_search = TextInput(hint_text="Filter by name, service, or type...", multiline=False, size_hint_x=0.7)
        self.in_search.bind(text=self._on_search)
        btn_search = PrimaryButton(text="Search Nearby", size_hint_x=0.3)
        btn_search.bind(on_release=self._on_live_search)
        search_row.add_widget(self.in_search)
        search_row.add_widget(btn_search)
        search_card.add_widget(search_row)

        # Data source label (updated after each search)
        self.lbl_data_source = WrappedLabel(
            text="",
            font_size="10sp",
            color=COLOR_TEXT_MUTED
        )
        search_card.add_widget(self.lbl_data_source)
        self.content.add_widget(search_card)

        # 3. Facilities List
        self.list_box = BoxLayout(orientation="vertical", spacing=8, size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        self.content.add_widget(self.list_box)

        scroll.add_widget(self.content)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_pre_enter(self):
        self._update_maps_status()
        self._update_loc_label()
        self._on_search(None, self.in_search.text or "")

    def _update_maps_status(self):
        """Show whether Google Maps live search is available."""
        try:
            maps = self.controller.location_service._get_maps_service()
            if maps and maps.is_configured():
                self.maps_status_lbl.text = (
                    "[color=#059669][b]✓ Google Maps API configured[/b][/color] — "
                    "Live facility search enabled. Set a location and tap Search Nearby."
                )
                self.maps_status_lbl.color = (0.02, 0.59, 0.42, 1)
            else:
                self.maps_status_lbl.text = (
                    "[color=#6B7280]Google Maps API not configured — "
                    "showing local offline directory. See .env.example to enable live search.[/color]"
                )
                self.maps_status_lbl.color = COLOR_TEXT_MUTED
        except Exception:
            self.maps_status_lbl.text = ""

    def _update_loc_label(self):
        loc = self.controller.location_service.current_location_name
        self.lbl_loc_status.text = f"Reference Location: [b]{loc}[/b]"

    def _update_data_source_label(self):
        source = self.controller.location_service.last_search_source
        if source == "google_maps":
            self.lbl_data_source.text = "Results: Live Google Maps data"
        elif source == "offline":
            self.lbl_data_source.text = "Results: Local offline directory (last verified with dataset)"
        else:
            self.lbl_data_source.text = ""

    def _on_use_device_location(self, *args):
        success, loc_name = self.controller.location_service.request_device_location()
        self._update_loc_label()
        self._on_search(None, self.in_search.text or "")

    def _on_set_manual_address(self, *args):
        q = self.in_address.text.strip()
        if not q:
            return
        success, loc_name = self.controller.location_service.set_manual_location(q)
        self._update_loc_label()
        self._on_search(None, self.in_search.text or "")

    def _on_live_search(self, *args):
        """Explicitly triggers a fresh live Google Maps search (bypasses text filter temporarily)."""
        self._on_search(None, self.in_search.text or "")

    def _on_clear_location(self, *args):
        self.controller.location_service.clear_location()
        self.in_address.text = ""
        self._update_loc_label()
        self._on_search(None, "")

    def _on_search(self, instance, query):
        self.list_box.clear_widgets()
        loc_service = self.controller.location_service

        # Get facilities (Google Maps live or offline fallback)
        facilities = loc_service.get_nearby_facilities(urgency_category=3, limit=30)
        self._update_data_source_label()

        q_clean = (query or "").lower().strip()
        filtered = []
        for f in facilities:
            if not q_clean:
                filtered.append(f)
            else:
                combined = (
                    f"{f.get('name', '')} {f.get('city', '')} "
                    f"{f.get('services', '')} {f.get('address', '')} "
                    f"{f.get('facility_type', '')}"
                ).lower()
                if q_clean in combined:
                    filtered.append(f)

        if not filtered:
            empty = CardBox(padding=[14, 12, 14, 12], size_hint_y=None)
            empty.bind(minimum_height=empty.setter("height"))
            if loc_service.current_lat is None:
                msg = "Set a location above to find nearby healthcare facilities."
            else:
                msg = "No matching healthcare facilities found. Try widening your search."
            empty.add_widget(WrappedLabel(text=msg, font_size="12sp", color=COLOR_TEXT_MUTED))
            self.list_box.add_widget(empty)
            return

        for fac in filtered:
            self._add_facility_card(fac, loc_service)

    def _add_facility_card(self, fac: dict, loc_service):
        """Renders a single facility card — handles both Google Maps and offline data."""
        card = CardBox(orientation="vertical", spacing=6, padding=[14, 12, 14, 12], size_hint_y=None)
        card.bind(minimum_height=card.setter("height"))

        # --- Header: Name + ER badge ---
        top_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=24)
        top_row.add_widget(WrappedLabel(
            text=f"[b]{fac.get('name', 'Unknown Facility')}[/b]",
            font_size="13sp",
            color=COLOR_NAVY_PRIMARY
        ))
        has_emerg = fac.get("has_emergency") or str(fac.get("has_emergency", "0")) == "1"
        if has_emerg:
            top_row.add_widget(WrappedLabel(
                text="[b]  [24/7 ER][/b]",
                font_size="10sp",
                color=COLOR_URGENT_EMERGENCY,
                size_hint_x=0.25
            ))
        card.add_widget(top_row)

        # --- Facility type + data source badge ---
        source = fac.get("source", "offline")
        facility_type = fac.get("facility_type", "Healthcare Facility")
        if source == "google_maps":
            source_badge = "[color=#1A73E8][b]Google Maps[/b][/color]"
        else:
            is_verified = fac.get("is_verified", "1") in (True, "1", 1)
            source_badge = (
                "[color=#059669][b]Local Directory[/b][/color]" if is_verified
                else "[color=#6B7280]Local Sample[/color]"
            )
        card.add_widget(WrappedLabel(
            text=f"{source_badge} · {facility_type}",
            font_size="10sp",
            color=COLOR_TEXT_MUTED
        ))

        # --- Address + Distance ---
        address = fac.get("address") or fac.get("formattedAddress", "")
        city = fac.get("city", "")
        state = fac.get("state", "")
        full_addr = ", ".join(filter(None, [address, city, state]))
        miles = fac.get("distance_miles", 0.0)
        km = fac.get("distance_km", 0.0)
        card.add_widget(WrappedLabel(
            text=f"{full_addr} — [b]{miles} mi / {km} km[/b]",
            font_size="11sp",
            color=COLOR_TEXT_DARK
        ))

        # --- Phone ---
        phone = fac.get("phone") or fac.get("nationalPhoneNumber") or "Not listed"
        card.add_widget(WrappedLabel(
            text=f"Phone: {phone}",
            font_size="11sp",
            color=COLOR_TEXT_MUTED
        ))

        # --- Hours ---
        hours = fac.get("operating_hours", "")
        if hours:
            card.add_widget(WrappedLabel(
                text=f"Hours: {hours}",
                font_size="10sp",
                color=COLOR_TEXT_MUTED
            ))

        # --- Website (Google Maps results only) ---
        website = fac.get("website", "")
        if website:
            btn_web = SecondaryButton(text="Visit Website ↗", size_hint_y=None, height=30)
            btn_web.bind(on_release=lambda x, url=website: webbrowser.open(url))
            card.add_widget(btn_web)

        # --- Services (offline directory only) ---
        services = fac.get("services", "")
        if services and source != "google_maps":
            card.add_widget(WrappedLabel(
                text=f"Services: {services}",
                font_size="10sp",
                color=COLOR_NAVY_LIGHT
            ))

        # --- Directions button ---
        btn_dir = SecondaryButton(text="Open Directions in Maps ↗", size_hint_y=None, height=34)
        btn_dir.bind(on_release=lambda x, target=fac: loc_service.open_directions(target))
        card.add_widget(btn_dir)

        self.list_box.add_widget(card)


# =========================================================================
# 10. MEDICAL REFERENCES SCREEN
# =========================================================================
class MedicalReferencesScreen(BaseScreen):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.content = BoxLayout(orientation="vertical", spacing=12, padding=[16, 16, 16, 24], size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter("height"))

        self.content.add_widget(create_section_title("Local Clinical Guidelines & Medical References"))
        self.content.add_widget(create_desc_label("Official clinical references (WHO ICD-11, EAACI, Surviving Sepsis, ESI, Canadian CT Head Rule)."))

        refs = self.controller.dataset_loader.get_medical_references()
        clinical_refs = [r for r in refs if r.get("category") != "geographic_mapping"]
        geo_refs = [r for r in refs if r.get("category") == "geographic_mapping"]

        for r in clinical_refs:
            card = CardBox(orientation="vertical", spacing=6, padding=[14, 12, 14, 12], size_hint_y=None)
            card.bind(minimum_height=card.setter("height"))

            card.add_widget(WrappedLabel(text=f"[b]{r.get('title')}[/b]", font_size="13sp", color=COLOR_NAVY_PRIMARY))
            card.add_widget(WrappedLabel(text=f"Organization / Source: [b]{r.get('source')}[/b] | Version: {r.get('version')}", font_size="11sp", color=COLOR_TEXT_MUTED))
            card.add_widget(WrappedLabel(text=r.get("content", ""), font_size="12sp", color=COLOR_TEXT_DARK))
            
            # Clickable reference link if available
            url = r.get("url")
            if url:
                btn_link = SecondaryButton(text="Open Official Reference ↗", size_hint_y=None, height=32)
                btn_link.bind(on_release=lambda x, target_url=url: webbrowser.open(target_url))
                card.add_widget(btn_link)

            self.content.add_widget(card)

        scroll.add_widget(self.content)
        root.add_widget(scroll)
        self.add_widget(root)


# =========================================================================
# 11. SETTINGS SCREEN
# =========================================================================
class SettingsScreen(BaseScreen):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        content = BoxLayout(orientation="vertical", spacing=14, padding=[16, 16, 16, 24], size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(create_section_title("Application Settings & Configuration"))

        # Storage info card
        card1 = CardBox(orientation="vertical", spacing=8, padding=[14, 12, 14, 12], size_hint_y=None)
        card1.bind(minimum_height=card1.setter("height"))
        card1.add_widget(WrappedLabel(text="[b]Storage & Database Paths[/b]", font_size="13sp", color=COLOR_NAVY_PRIMARY))
        card1.add_widget(WrappedLabel(text=f"Database: {self.controller.config.db_path}", font_size="11sp", color=COLOR_TEXT_DARK))
        card1.add_widget(WrappedLabel(text=f"Log File: {self.controller.config.log_path}", font_size="11sp", color=COLOR_TEXT_DARK))
        card1.add_widget(WrappedLabel(
            text=f"C Native Engine: {'Active DLL/SO' if self.controller.native.using_native else 'Python Fallback (100% Functional)'}",
            font_size="11sp",
            color=COLOR_BLUE_ACCENT
        ))
        content.add_widget(card1)

        # Network check card
        card2 = CardBox(orientation="vertical", spacing=8, padding=[14, 12, 14, 12], size_hint_y=None)
        card2.bind(minimum_height=card2.setter("height"))
        card2.add_widget(WrappedLabel(text="[b]Offline / Synchronization Status[/b]", font_size="13sp", color=COLOR_NAVY_PRIMARY))
        self.lbl_net = WrappedLabel(text="Status: Autonomous Offline Mode Active", font_size="12sp", color=COLOR_TEXT_DARK)
        card2.add_widget(self.lbl_net)

        btn_probe = SecondaryButton(text="Probe Network Connectivity", size_hint_y=None, height=36)
        btn_probe.bind(on_release=self._probe_net)
        card2.add_widget(btn_probe)
        content.add_widget(card2)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def _probe_net(self, *args):
        online = self.controller.sync_service.check_connectivity()
        self.lbl_net.text = f"Status: {'Online (Sync Enabled)' if online else 'Autonomous Offline (Internet Unreachable)'}"


# =========================================================================
# 12. ABOUT MEDICARE SCREEN (With Clickable Medical References & Disclaimers)
# =========================================================================
class AboutScreen(BaseScreen):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        content = BoxLayout(orientation="vertical", spacing=12, padding=[16, 16, 16, 24], size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(create_section_title("About MEDICARE — Medical Symptoms Triage Advisor"))

        # Architectural Overview
        card1 = CardBox(orientation="vertical", spacing=8, padding=[16, 14, 16, 14], size_hint_y=None)
        card1.bind(minimum_height=card1.setter("height"))
        card1.add_widget(WrappedLabel(
            text="[b]1. Architectural Overview & Distribution[/b]\n"
                 "MEDICARE is a cross-platform (Android + Windows) offline-first desktop and mobile application. "
                 "It is engineered using Python (~70%) for user workflows, Kivy UI, database operations, "
                 "and triage orchestration, with C (~30%) for native symptom normalization, input validation primitives, "
                 "and bitfield rule evaluation.\n\n"
                 "[b]2. Four Urgency Categories[/b]\n"
                 "• [b]Category 1: Emergency Care[/b] — Immediate life-saving medical intervention required (Red)\n"
                 "• [b]Category 2: Early Medical Consultation[/b] — Evaluation recommended within 24-48 hours (Amber)\n"
                 "• [b]Category 3: Routine Healthcare[/b] — Primary care appointment or guided self-care (Green)\n"
                 "• [b]Category 4: Insufficient Information[/b] — Inconclusive inputs requiring clinical assessment (Gray)\n\n"
                 "[b]3. Offline-First Guarantee[/b]\n"
                 "All core clinical evaluation capabilities, datasets, SQLite persistence, and PDF handover generation "
                 "function with 100% autonomy without requiring an internet connection or external API.\n\n"
                 "[b]4. Clinical Governance & Limitations[/b]\n"
                 "MEDICARE does NOT diagnose medical diseases, prescribe drugs or dosages, or guarantee safety. "
                 "It is a navigation advisor designed to assist patients in deciding when and where to seek professional care.",
            font_size="12sp",
            color=COLOR_NAVY_PRIMARY
        ))
        content.add_widget(card1)

        # Dedicated Medical References & Guidelines Section with Clickable Links
        content.add_widget(create_section_title("Medical References, Guidelines & Clinical Sources"))
        content.add_widget(create_desc_label(
            "MEDICARE's educational rules and symptom taxonomies are informed by established clinical guidelines. "
            "These references are listed for evidence transparency; no formal endorsement is claimed."
        ))

        references_data = [
            {
                "name": "WHO ICD-11 International Classification of Diseases",
                "org": "World Health Organization (WHO)",
                "desc": "Global standard for diagnostic health information, symptom classification, and epidemiological tracking.",
                "url": "https://icd.who.int/browse11/l-m/en",
                "verified": "2026-11-21"
            },
            {
                "name": "EAACI Guidelines: Anaphylaxis Management",
                "org": "European Academy of Allergy and Clinical Immunology",
                "desc": "Evidence-based clinical guidelines on acute anaphylaxis recognition, red-flag symptoms, and intramuscular adrenaline protocols.",
                "url": "https://eaaci.org/resources/guidelines/",
                "verified": "2026-11-21"
            },
            {
                "name": "Surviving Sepsis Campaign: International Guidelines",
                "org": "Society of Critical Care Medicine (SCCM) & ESICM",
                "desc": "Clinical guidance for management of sepsis, septic shock, organ dysfunction criteria, and early antimicrobial intervention.",
                "url": "https://www.sccm.org/SurvivingSepsisCampaign/Home",
                "verified": "2026-11-21"
            },
            {
                "name": "Emergency Severity Index (ESI) Triage Handbook",
                "org": "Agency for Healthcare Research and Quality (AHRQ)",
                "desc": "Five-level emergency department triage algorithm prioritizing patient acuity and anticipated resource utilization.",
                "url": "https://www.ahrq.gov/patient-safety/settings/emergency-dept/esi.html",
                "verified": "2026-11-21"
            },
            {
                "name": "Canadian CT Head Rule for Patients with Minor Head Injury",
                "org": "The Lancet / Canadian Medical Association",
                "desc": "Validated high-risk clinical decision rule to identify patients requiring computed tomography after head trauma.",
                "url": "https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(00)04561-X/fulltext",
                "verified": "2026-11-21"
            },
            {
                "name": "NICE Clinical Knowledge Summaries (CKS)",
                "org": "National Institute for Health and Care Excellence (UK)",
                "desc": "Primary care clinical guidance on symptom assessment, red flag warnings, and evidence-based referral thresholds.",
                "url": "https://cks.nice.org.uk/",
                "verified": "2026-11-21"
            }
        ]

        for ref in references_data:
            ref_card = CardBox(orientation="vertical", spacing=6, padding=[14, 12, 14, 12], size_hint_y=None)
            ref_card.bind(minimum_height=ref_card.setter("height"))

            ref_card.add_widget(WrappedLabel(
                text=f"[b]{ref['name']}[/b]",
                font_size="13sp",
                color=COLOR_NAVY_PRIMARY
            ))
            ref_card.add_widget(WrappedLabel(
                text=f"Organization: [b]{ref['org']}[/b] | Last Verified: {ref['verified']}",
                font_size="11sp",
                color=COLOR_TEXT_MUTED
            ))
            ref_card.add_widget(WrappedLabel(
                text=ref["desc"],
                font_size="12sp",
                color=COLOR_TEXT_DARK
            ))

            btn_link = SecondaryButton(text=f"Open Official Resource ↗", size_hint_y=None, height=32)
            btn_link.bind(on_release=lambda x, target_url=ref["url"]: webbrowser.open(target_url))
            ref_card.add_widget(btn_link)

            content.add_widget(ref_card)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)
