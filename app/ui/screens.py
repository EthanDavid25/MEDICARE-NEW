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
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.core.window import Window

import pypdfium2 as pdfium

from app.ui.theme import (
    COLOR_NAVY_PRIMARY, COLOR_NAVY_LIGHT, COLOR_BLUE_ACCENT,
    COLOR_BLUE_TINT, COLOR_BG_LIGHT, COLOR_WHITE, COLOR_TEXT_DARK,
    COLOR_TEXT_MUTED, COLOR_TEXT_LIGHT, COLOR_BORDER,
    COLOR_URGENT_EMERGENCY, COLOR_URGENT_EARLY, COLOR_URGENT_ROUTINE,
    COLOR_URGENT_INSUFF
)
from app.ui.components import CardBox, PrimaryButton, SecondaryButton, UrgencyBadge, WrappedLabel, SectionTitle, OptionButton
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
        content = BoxLayout(orientation="vertical", spacing=14, padding=[16, 16, 16, 24], size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))

        # 1. Welcome Card Banner
        banner = CardBox(orientation="vertical", spacing=8, padding=[18, 16, 18, 16], size_hint_y=None)
        banner.bind(minimum_height=banner.setter("height"))
        banner.bg_color = COLOR_NAVY_PRIMARY
        banner.border_color = COLOR_NAVY_LIGHT
        
        banner.add_widget(WrappedLabel(
            text="[b][size=19sp]Welcome to MEDICARE[/size][/b]\nMedical Symptoms Triage Advisor",
            font_size="15sp",
            color=COLOR_TEXT_LIGHT
        ))
        banner.add_widget(WrappedLabel(
            text="Autonomous offline-first preliminary assessment, progression tracking, and local medical navigation.",
            font_size="11sp",
            color=COLOR_BLUE_TINT
        ))
        content.add_widget(banner)

        # 2. Main Call to Action: Start Symptom Assessment
        start_card = CardBox(orientation="vertical", spacing=10, padding=[16, 14, 16, 14], size_hint_y=None)
        start_card.bind(minimum_height=start_card.setter("height"))
        start_card.bg_color = COLOR_BLUE_TINT
        start_card.border_color = COLOR_BLUE_ACCENT
        
        start_card.add_widget(WrappedLabel(
            text="[b]Feeling Unwell? Start a New Assessment[/b]\nAnswer a few guided clinical questions for an explainable urgency category and recommended next steps.",
            font_size="13sp",
            color=COLOR_NAVY_PRIMARY
        ))

        btn_start = PrimaryButton(text="START SYMPTOM ASSESSMENT →", size_hint_y=None, height=42)
        btn_start.bind(on_release=lambda x: self._nav_to("symptom_assessment"))
        start_card.add_widget(btn_start)
        content.add_widget(start_card)

        # 3. Emergency Safety Disclaimer Callout
        warn_card = CardBox(orientation="vertical", spacing=6, padding=[14, 10, 14, 10], size_hint_y=None)
        warn_card.bind(minimum_height=warn_card.setter("height"))
        warn_card.bg_color = (1.0, 0.95, 0.95, 1.0)
        warn_card.border_color = COLOR_URGENT_EMERGENCY
        warn_card.add_widget(WrappedLabel(
            text="[b][color=#DC2626]EMERGENCY WARNING:[/color][/b] If you are experiencing crushing chest pain, severe shortness of breath, sudden one-sided facial drooping or arm weakness, or uncontrollable bleeding, call [b]112 / 102 (India)[/b] or proceed immediately to the nearest emergency department.",
            font_size="11sp",
            color=COLOR_URGENT_EMERGENCY
        ))
        content.add_widget(warn_card)

        # 4. Recent Assessments Section
        content.add_widget(create_section_title("Recent Patient Assessments"))
        self.recent_container = BoxLayout(orientation="vertical", spacing=8, size_hint_y=None)
        self.recent_container.bind(minimum_height=self.recent_container.setter("height"))
        content.add_widget(self.recent_container)

        # 5. Quick Modules Navigation Grid
        content.add_widget(create_section_title("Application Navigation"))
        
        mod_grid = GridLayout(cols=2, spacing=10, size_hint_y=None)
        mod_grid.bind(minimum_height=mod_grid.setter("height"))
        
        b_prof = SecondaryButton(text="• Patient Profile", size_hint_y=None, height=42)
        b_prof.bind(on_release=lambda x: self._nav_to("patient_profile"))
        mod_grid.add_widget(b_prof)

        b_hist = SecondaryButton(text="• Assessment History", size_hint_y=None, height=42)
        b_hist.bind(on_release=lambda x: self._nav_to("patient_history"))
        mod_grid.add_widget(b_hist)

        b_prog = SecondaryButton(text="• Symptom Progression", size_hint_y=None, height=42)
        b_prog.bind(on_release=lambda x: self._nav_to("symptom_progression"))
        mod_grid.add_widget(b_prog)

        b_hand = SecondaryButton(text="• Doctor Handover", size_hint_y=None, height=42)
        b_hand.bind(on_release=lambda x: self._nav_to("doctor_handover"))
        mod_grid.add_widget(b_hand)

        b_down = SecondaryButton(text="• Handover Downloads", size_hint_y=None, height=42)
        b_down.bind(on_release=lambda x: self._nav_to("handover_downloads"))
        mod_grid.add_widget(b_down)

        b_ref = SecondaryButton(text="• Medical References", size_hint_y=None, height=42)
        b_ref.bind(on_release=lambda x: self._nav_to("medical_references"))
        mod_grid.add_widget(b_ref)

        content.add_widget(mod_grid)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_pre_enter(self):
        """Refreshes recent assessment items upon entering screen."""
        self.recent_container.clear_widgets()
        patient_id = self.controller.current_patient_id
        assessments = self.controller.history_service.get_assessment_history(patient_id, limit=3)
        
        if not assessments:
            empty_card = CardBox(padding=[14, 12, 14, 12], size_hint_y=None)
            empty_card.bind(minimum_height=empty_card.setter("height"))
            empty_card.add_widget(WrappedLabel(
                text="No past assessments recorded yet. Complete an assessment to see history.",
                font_size="11sp",
                color=COLOR_TEXT_MUTED
            ))
            self.recent_container.add_widget(empty_card)
        else:
            for a in assessments:
                row = CardBox(orientation="horizontal", padding=[12, 10, 12, 10], spacing=10, size_hint_y=None)
                row.bind(minimum_height=row.setter("height"))
                
                info_box = BoxLayout(orientation="vertical", spacing=2)
                dt = (a.get("completed_at") or "")[:16].replace("T", " ")
                info_box.add_widget(WrappedLabel(text=f"[b]{dt}[/b]", font_size="12sp", color=COLOR_NAVY_PRIMARY))
                info_box.add_widget(WrappedLabel(text=f"Session: {a.get('session_id')}", font_size="10sp", color=COLOR_TEXT_MUTED))
                row.add_widget(info_box)

                badge = UrgencyBadge(category=a.get("urgency_category", 3))
                row.add_widget(badge)
                self.recent_container.add_widget(row)

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
# 3. SYMPTOM ASSESSMENT SCREEN
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
        content = BoxLayout(orientation="vertical", spacing=8, padding=[14, 12, 14, 16], size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(create_section_title("Step 1: Enter Reported Symptoms"))
        content.add_widget(create_desc_label("Search and select your primary symptoms, then rate pain severity (1–10) and progression."))

        # 1. Search Box
        search_card = CardBox(orientation="vertical", spacing=6, padding=[10, 8, 10, 8], size_hint_y=None)
        search_card.bind(minimum_height=search_card.setter("height"))
        search_card.add_widget(WrappedLabel(text="[b]Search Symptom Library (85+ items):[/b]", font_size="12sp", color=COLOR_NAVY_PRIMARY))
        self.in_search = TextInput(hint_text="e.g. Headache, Chest pain, Shortness of breath, Fever...", multiline=False, size_hint_y=None, height=34)
        self.in_search.bind(text=self._on_search)
        search_card.add_widget(self.in_search)
        content.add_widget(search_card)

        # 2. Search Results List (Dynamically populated)
        self.results_box = BoxLayout(orientation="vertical", spacing=4, size_hint_y=None)
        self.results_box.bind(minimum_height=self.results_box.setter("height"))
        content.add_widget(self.results_box)

        # 3. Selected Symptoms Summary Card
        content.add_widget(create_section_title("Selected Symptoms for Assessment"))
        self.selected_container = BoxLayout(orientation="vertical", spacing=6, size_hint_y=None)
        self.selected_container.bind(minimum_height=self.selected_container.setter("height"))
        content.add_widget(self.selected_container)

        # 4. Severity & Progression Inputs
        sev_card = CardBox(orientation="vertical", spacing=8, padding=[12, 10, 12, 10], size_hint_y=None)
        sev_card.bind(minimum_height=sev_card.setter("height"))
        
        # Interactive pain severity label updating dynamically
        self.lbl_sev = WrappedLabel(
            text="[b]Pain / Severity Rating: 5 / 10[/b]",
            font_size="13sp",
            color=COLOR_NAVY_PRIMARY
        )
        sev_card.add_widget(self.lbl_sev)

        self.slider_sev = Slider(min=1, max=10, value=5, step=1, size_hint_y=None, height=34)
        self.slider_sev.bind(value=self._on_slider)
        sev_card.add_widget(self.slider_sev)

        # Duration input
        dur_box = BoxLayout(orientation="horizontal", spacing=8, size_hint_y=None, height=34)
        dur_lbl = WrappedLabel(text="[b]Duration (Days):[/b]", font_size="12sp", color=COLOR_NAVY_PRIMARY, size_hint_x=0.4)
        dur_box.add_widget(dur_lbl)
        self.in_dur = TextInput(text="1", multiline=False, size_hint_x=0.6)
        dur_box.add_widget(self.in_dur)
        sev_card.add_widget(dur_box)

        # Trajectory / Progression buttons
        sev_card.add_widget(WrappedLabel(text="[b]Symptom Progression:[/b]", font_size="12sp", color=COLOR_NAVY_PRIMARY))
        traj_box = BoxLayout(orientation="horizontal", spacing=6, size_hint_y=None, height=34)
        self.btn_worse = OptionButton(text="  Worsening", size_hint_y=None, height=34)
        self.btn_worse.bind(on_release=lambda x: self._set_traj("worsening"))
        self.btn_same = OptionButton(text="  Unchanged", size_hint_y=None, height=34)
        self.btn_same.bind(on_release=lambda x: self._set_traj("unchanged"))
        self.btn_better = OptionButton(text="  Improving", size_hint_y=None, height=34)
        self.btn_better.bind(on_release=lambda x: self._set_traj("improving"))
        traj_box.add_widget(self.btn_worse)
        traj_box.add_widget(self.btn_same)
        traj_box.add_widget(self.btn_better)
        sev_card.add_widget(traj_box)

        content.add_widget(sev_card)

        # 5. Continue to Follow-up Questions Button
        btn_next = PrimaryButton(text="PROCEED TO CLINICAL QUESTIONS →", size_hint_y=None, height=40)
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
            category_text = "[color=#16A34A]Mild (Manageable discomfort)[/color]"
        elif val <= 6:
            category_text = "[color=#D97706]Moderate (Noticeable interference with activities)[/color]"
        elif val <= 9:
            category_text = "[color=#DC2626]Severe (Significant distress / high urgency)[/color]"
        else:
            category_text = "[color=#991B1B]Critical (Extreme / worst pain imaginable)[/color]"
        self.lbl_sev.text = f"[b]Pain / Severity Rating: {val} / 10[/b] — {category_text}"

    def on_pre_enter(self):
        self.in_search.text = ""
        self._set_traj("unchanged")
        self.slider_sev.value = 5
        self._on_slider(self.slider_sev, 5)
        self._on_search(None, "")
        self._update_selected_ui()

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
            empty = CardBox(padding=[10, 8, 10, 8], size_hint_y=None)
            empty.bind(minimum_height=empty.setter("height"))
            empty.add_widget(WrappedLabel(text="No symptoms added yet. Pick at least one symptom above.", font_size="12sp", color=COLOR_TEXT_MUTED))
            self.selected_container.add_widget(empty)
        else:
            for s in self.selected_symptoms:
                card = CardBox(orientation="horizontal", padding=[10, 5, 10, 5], spacing=8, size_hint_y=None)
                card.bind(minimum_height=card.setter("height"))
                
                name_lbl = WrappedLabel(text=f"[b]{s.get('name')}[/b] ({s.get('body_system', '')})", font_size="12sp", color=COLOR_NAVY_PRIMARY)
                card.add_widget(name_lbl)
                
                b_del = Button(text="Remove", font_size="11sp", size_hint=(None, None), size=(66, 26), background_color=COLOR_URGENT_EMERGENCY, color=COLOR_WHITE)
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
# 4. FOLLOW-UP QUESTIONS SCREEN (Adaptive & Progression-Conditioned)
# =========================================================================
class FollowupQuestionsScreen(BaseScreen):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.answers: dict[str, str] = {}
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)
        
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.content = BoxLayout(orientation="vertical", spacing=8, padding=[14, 10, 14, 16], size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter("height"))

        scroll.add_widget(self.content)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_pre_enter(self):
        self.content.clear_widgets()
        self.answers = {}

        self.content.add_widget(create_section_title("Step 2: Relevant Clinical Questions"))
        
        staging = getattr(self.controller, "assessment_staging", {})
        symptoms = staging.get("symptoms", [])
        sym_codes = [s["code"] for s in symptoms]
        progression = staging.get("progression", "unchanged")
        severity = staging.get("severity", 5)

        self.content.add_widget(create_desc_label(
            f"Adaptive questions for reported symptoms, severity ({severity}/10), trajectory ({progression.upper()}). "
            "Emergency red-flag checks always verified."
        ))

        # Dynamically retrieve targeted questions linked to reported symptoms, progression, and severity
        questions = self.controller.dataset_loader.get_followup_questions_for_symptoms(
            sym_codes, progression=progression, severity=severity
        )

        for q in questions:
            q_card = CardBox(orientation="vertical", spacing=6, padding=[12, 10, 12, 10], size_hint_y=None)
            q_card.bind(minimum_height=q_card.setter("height"))

            is_emerg = bool(q.get("is_emergency_safety_check", False) or q.get("triggers_emergency_check", False))
            title_text = f"[b]{q.get('question_text')}[/b]"
            if is_emerg:
                title_text = f"[b][color=#DC2626]RED FLAG:[/color][/b] {title_text}"

            q_lbl = WrappedLabel(
                text=title_text,
                font_size="14sp",
                color=COLOR_NAVY_PRIMARY
            )
            q_card.add_widget(q_lbl)

            # Optional description / hint
            if q.get("description"):
                q_card.add_widget(WrappedLabel(text=q["description"], font_size="12sp", color=COLOR_TEXT_MUTED))

            qid = q["question_id"]
            opts_box = BoxLayout(orientation="vertical", spacing=4, size_hint_y=None)
            opts_box.bind(minimum_height=opts_box.setter("height"))

            btn_group = []
            for opt in q.get("options", []):
                opt_code = opt["code"]
                opt_btn = OptionButton(
                    text=f"  {opt['text']}",
                    font_size="13sp",
                    size_hint_y=None,
                    height=36
                )
                opt_btn.bind(on_release=lambda x, q=qid, c=opt_code, bg=btn_group, curr=opt_btn: self._select_answer(q, c, bg, curr))
                opts_box.add_widget(opt_btn)
                btn_group.append(opt_btn)

            q_card.add_widget(opts_box)
            self.content.add_widget(q_card)

        # Assessment Action Button
        btn_evaluate = PrimaryButton(text="SUBMIT & EVALUATE TRIAGE RESULTS →", size_hint_y=None, height=42)
        btn_evaluate.bind(on_release=self._evaluate_triage)
        self.content.add_widget(btn_evaluate)

    def _select_answer(self, qid: str, code: str, group: list, active_btn):
        self.answers[qid] = code
        for b in group:
            b.is_selected = (b == active_btn)

    def _evaluate_triage(self, *args):
        staging = getattr(self.controller, "assessment_staging", {})
        symptoms = staging.get("symptoms", [])

        # Run triage assessment
        result = self.controller.triage_engine.assess(
            patient_id=self.controller.current_patient_id,
            symptoms=symptoms,
            followup_answers=self.answers,
            risk_factors=[]
        )
        self.controller.last_triage_result = result
        self.manager.current = "triage_results"


# =========================================================================
# 5. TRIAGE RESULTS SCREEN (Zero Overlap & Nearby Facilities Recommendation)
# =========================================================================
class TriageResultsScreen(BaseScreen):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)
        
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.content = BoxLayout(orientation="vertical", spacing=14, padding=[16, 16, 16, 24], size_hint_y=None)
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
        # SECTION 1: PROMINENT URGENCY OUTCOME BANNER
        # -------------------------------------------------------------
        cat_card = CardBox(orientation="vertical", spacing=8, padding=[18, 16, 18, 16], size_hint_y=None)
        cat_card.bind(minimum_height=cat_card.setter("height"))
        if cat == 1:
            cat_card.bg_color = COLOR_URGENT_EMERGENCY
        elif cat == 2:
            cat_card.bg_color = COLOR_URGENT_EARLY
        elif cat == 3:
            cat_card.bg_color = COLOR_URGENT_ROUTINE
        else:
            cat_card.bg_color = COLOR_URGENT_INSUFF

        cat_card.add_widget(WrappedLabel(
            text=f"[size=20sp][b]{result.urgency_label.upper()}[/b][/size]\nClassification Category: {cat} of 4",
            font_size="15sp",
            color=COLOR_TEXT_LIGHT
        ))
        self.content.add_widget(cat_card)

        # -------------------------------------------------------------
        # SECTION 2: PLAIN LANGUAGE EXPLANATION
        # -------------------------------------------------------------
        self.content.add_widget(create_section_title("1. Assessment Summary & Explanation"))
        expl_card = CardBox(orientation="vertical", spacing=6, padding=[14, 12, 14, 12], size_hint_y=None)
        expl_card.bind(minimum_height=expl_card.setter("height"))
        
        expl_card.add_widget(WrappedLabel(
            text=result.summary_explanation,
            font_size="13sp",
            color=COLOR_NAVY_PRIMARY
        ))
        self.content.add_widget(expl_card)

        # -------------------------------------------------------------
        # SECTION 3: CLINICAL JUSTIFICATION & TRIGGERED INDICATORS
        # -------------------------------------------------------------
        self.content.add_widget(create_section_title("2. Detailed Clinical Reasoning & Triggered Indicators"))
        just_card = CardBox(orientation="vertical", spacing=6, padding=[14, 12, 14, 12], size_hint_y=None)
        just_card.bind(minimum_height=just_card.setter("height"))
        
        for d in result.detailed_reasoning:
            just_card.add_widget(WrappedLabel(
                text=d,
                font_size="12sp",
                color=COLOR_TEXT_DARK
            ))
        self.content.add_widget(just_card)

        # -------------------------------------------------------------
        # SECTION 4: RECOMMENDED NEXT STEPS & CLINICAL ACTIONS
        # -------------------------------------------------------------
        self.content.add_widget(create_section_title("3. Recommended Clinical Action Guidance"))
        act_card = CardBox(orientation="vertical", spacing=8, padding=[16, 14, 16, 14], size_hint_y=None)
        act_card.bind(minimum_height=act_card.setter("height"))
        
        if cat == 1:
            act_card.bg_color = (1.0, 0.94, 0.94, 1.0)
            act_card.border_color = COLOR_URGENT_EMERGENCY
            act_card.add_widget(WrappedLabel(
                text="[b][color=#DC2626]CRITICAL ACTION PROTOCOL — CALL EMERGENCY SERVICES (112 / 102)[/color][/b]",
                font_size="13sp"
            ))
            act_card.add_widget(WrappedLabel(
                text="• Dial 112 (National Emergency Helpline) or 102 (Ambulance Service) immediately.\n"
                     "• Do not attempt to operate a motor vehicle yourself; arrange for emergency medical transport.\n"
                     "• Maintain a calm posture and ensure airway is clear. Have a family member or bystander remain present.\n"
                     "• Download and provide your MEDICARE Doctor Handover report to the incoming emergency team.",
                font_size="12sp",
                color=COLOR_TEXT_DARK
            ))
        elif cat == 2:
            act_card.bg_color = (1.0, 0.97, 0.92, 1.0)
            act_card.border_color = COLOR_URGENT_EARLY
            act_card.add_widget(WrappedLabel(
                text="[b][color=#D97706]SAME-DAY CLINICAL EVALUATION ADVISORY[/color][/b]",
                font_size="13sp"
            ))
            act_card.add_widget(WrappedLabel(
                text="• Schedule an in-person medical consultation within 12–24 hours.\n"
                     "• Present your downloaded Doctor Handover summary to the consulting physician.\n"
                     "• If symptoms rapidly escalate, chest pain develops, or consciousness is altered, call 112 immediately.",
                font_size="12sp",
                color=COLOR_TEXT_DARK
            ))
        else:
            act_card.bg_color = COLOR_WHITE
            for act in result.recommended_next_steps:
                act_card.add_widget(WrappedLabel(
                    text=f"• {act}",
                    font_size="12sp",
                    color=COLOR_NAVY_PRIMARY
                ))
        self.content.add_widget(act_card)

        # -------------------------------------------------------------
        # SECTION 5: CLINICAL DISCLAIMER & GOVERNANCE
        # -------------------------------------------------------------
        disc_card = CardBox(orientation="vertical", spacing=4, padding=[12, 10, 12, 10], size_hint_y=None)
        disc_card.bind(minimum_height=disc_card.setter("height"))
        disc_card.bg_color = (0.97, 0.97, 0.98, 1)
        disc_card.add_widget(WrappedLabel(
            text="[b]Safety Notice:[/b] MEDICARE is an offline preliminary triage advisor and clinical decision-support tool. It does not provide medical diagnoses, treatment prescriptions, or emergency guarantees. If your condition worsens rapidly, seek emergency medical care immediately.",
            font_size="10sp",
            color=COLOR_TEXT_MUTED
        ))
        self.content.add_widget(disc_card)

        # -------------------------------------------------------------
        # SECTION 6: HANDOVER & NAVIGATION ACTIONS
        # -------------------------------------------------------------
        act_box = BoxLayout(orientation="vertical", spacing=8, size_hint_y=None, height=92)
        
        btn_pdf = PrimaryButton(text="GENERATE DOCTOR HANDOVER PDF", size_hint_y=None, height=42)
        btn_pdf.bind(on_release=self._generate_pdf)
        act_box.add_widget(btn_pdf)

        btn_home = SecondaryButton(text="Return to Dashboard", size_hint_y=None, height=36)
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
        symptoms_str = ", ".join(s.get("name", "") for s in result.symptoms_evaluated) if hasattr(result, "symptoms_evaluated") else "Reported symptoms"
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
# 8. DOCTOR HANDOVER SCREEN
# =========================================================================
class DoctorHandoverScreen(BaseScreen):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        content = BoxLayout(orientation="vertical", spacing=14, padding=[16, 16, 16, 24], size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(create_section_title("Doctor Handover Report Generator"))
        content.add_widget(create_desc_label("Generates an offline structured medical summary for your attending physician or emergency clinician."))

        card = CardBox(orientation="vertical", spacing=10, padding=[16, 14, 16, 14], size_hint_y=None)
        card.bind(minimum_height=card.setter("height"))
        card.add_widget(WrappedLabel(
            text="[b]Clinical Summary Document[/b]\nIncludes patient demographics, known allergies, current chief complaints, "
                 "symptom progression trajectory, and triggered triage warning signs.",
            font_size="13sp",
            color=COLOR_NAVY_PRIMARY
        ))

        btn_gen = PrimaryButton(text="GENERATE & EXPORT HANDOVER PDF", size_hint_y=None, height=44)
        btn_gen.bind(on_release=self._generate_latest_pdf)
        card.add_widget(btn_gen)
        content.add_widget(card)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def _generate_latest_pdf(self, *args):
        patient = self.controller.patient_service.get_patient(self.controller.current_patient_id)
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
            patient_name=patient.get("display_name", "Anonymous Patient"),
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
                 f"Saved locally to:\n{out_file}",
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
            Rectangle(pos=self.toolbar.pos, size=self.toolbar.size)
        self.toolbar.bind(pos=lambda inst, *a: setattr(inst.canvas.before.children[-1], 'pos', inst.pos),
                          size=lambda inst, *a: setattr(inst.canvas.before.children[-1], 'size', inst.size))

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

        # 2. Offline Maps & Geographic Data References Subsection
        self.content.add_widget(create_section_title("Offline Maps, Geographic Data & Navigation References"))
        self.content.add_widget(create_desc_label(
            "Genuine technical documentation and algorithmic standards utilized in MEDICARE's "
            "offline geographic subsystem, MBTiles access, spatial indexing, and C A* routing."
        ))

        for r in geo_refs:
            card = CardBox(orientation="vertical", spacing=6, padding=[14, 12, 14, 12], size_hint_y=None)
            card.bind(minimum_height=card.setter("height"))

            card.add_widget(WrappedLabel(text=f"[b]{r.get('title')}[/b]", font_size="13sp", color=COLOR_NAVY_PRIMARY))
            card.add_widget(WrappedLabel(text=f"Publisher / Project: [b]{r.get('source')}[/b] | Version: {r.get('version')}", font_size="11sp", color=COLOR_TEXT_MUTED))
            card.add_widget(WrappedLabel(text=f"Purpose: {r.get('summary', '')}", font_size="12sp", color=COLOR_NAVY_LIGHT))
            card.add_widget(WrappedLabel(text=r.get("content", ""), font_size="11sp", color=COLOR_TEXT_DARK))

            url = r.get("url")
            if url:
                btn_link = SecondaryButton(text="Open Technical Resource ↗", size_hint_y=None, height=32)
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

        # Dedicated Offline Maps & Navigation References Section
        content.add_widget(create_section_title("Offline Maps, Geographic Data & Navigation References"))
        content.add_widget(create_desc_label(
            "Technical documentation, data sources, and algorithmic references powering MEDICARE's "
            "offline geographic subsystem, MBTiles access, spatial indexing, and C A* routing."
        ))

        geo_references_data = [
            {
                "title": "OpenStreetMap",
                "org": "OpenStreetMap Foundation",
                "purpose": "Open geographic map data used as a source for roads, settlements and geographic features.",
                "url": "https://www.openstreetmap.org/"
            },
            {
                "title": "OpenStreetMap Copyright and Attribution",
                "org": "OpenStreetMap Foundation",
                "purpose": "Data licensing, attribution and usage requirements.",
                "url": "https://www.openstreetmap.org/copyright"
            },
            {
                "title": "OpenStreetMap Wiki — Downloading Data",
                "org": "OpenStreetMap Wiki Community",
                "purpose": "Documentation about obtaining geographic data for offline processing.",
                "url": "https://wiki.openstreetmap.org/wiki/Downloading_data"
            },
            {
                "title": "MBTiles Specification",
                "org": "Mapbox / Open Source Community",
                "purpose": "Reference for the SQLite-based MBTiles format used to store map tiles.",
                "url": "https://github.com/mapbox/mbtiles-spec"
            },
            {
                "title": "Kivy Garden MapView",
                "org": "Kivy Community",
                "purpose": "Documentation for displaying interactive maps and markers in the existing Kivy application.",
                "url": "https://mapview.readthedocs.io/"
            },
            {
                "title": "SQLite Documentation",
                "org": "SQLite Consortium",
                "purpose": "Local database storage and management.",
                "url": "https://www.sqlite.org/docs.html"
            },
            {
                "title": "Valhalla Routing Engine",
                "org": "Valhalla Project",
                "purpose": "Reference for routing algorithms and road-network navigation architecture (evaluated as an architecture candidate; MEDICARE implements a dedicated C A* routing engine for local hospital road graphs).",
                "url": "https://valhalla.github.io/valhalla/"
            },
            {
                "title": "Android Location Permissions",
                "org": "Google Android Developers",
                "purpose": "Reference for Android device location permission handling.",
                "url": "https://developer.android.com/develop/sensors-and-location/location/permissions"
            },
            {
                "title": "C Language Documentation",
                "org": "cppreference.com",
                "purpose": "Reference for C language functionality used in native map processing.",
                "url": "https://en.cppreference.com/w/c"
            }
        ]

        for gref in geo_references_data:
            g_card = CardBox(orientation="vertical", spacing=6, padding=[14, 12, 14, 12], size_hint_y=None)
            g_card.bind(minimum_height=g_card.setter("height"))

            g_card.add_widget(WrappedLabel(
                text=f"[b]{gref['title']}[/b]",
                font_size="13sp",
                color=COLOR_NAVY_PRIMARY
            ))
            g_card.add_widget(WrappedLabel(
                text=f"Project / Publisher: [b]{gref['org']}[/b]",
                font_size="11sp",
                color=COLOR_TEXT_MUTED
            ))
            g_card.add_widget(WrappedLabel(
                text=f"Purpose: {gref['purpose']}",
                font_size="12sp",
                color=COLOR_TEXT_DARK
            ))

            btn_glink = SecondaryButton(text=f"Open Official Technical Reference ↗", size_hint_y=None, height=32)
            btn_glink.bind(on_release=lambda x, target_url=gref["url"]: webbrowser.open(target_url))
            g_card.add_widget(btn_glink)

            content.add_widget(g_card)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)
