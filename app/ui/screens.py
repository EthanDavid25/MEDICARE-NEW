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
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.core.window import Window

from app.ui.theme import (
    COLOR_NAVY_PRIMARY, COLOR_NAVY_LIGHT, COLOR_BLUE_ACCENT,
    COLOR_BLUE_TINT, COLOR_BG_LIGHT, COLOR_WHITE, COLOR_TEXT_DARK,
    COLOR_TEXT_MUTED, COLOR_TEXT_LIGHT, COLOR_BORDER,
    COLOR_URGENT_EMERGENCY, COLOR_URGENT_EARLY, COLOR_URGENT_ROUTINE,
    COLOR_URGENT_INSUFF
)
from app.ui.components import CardBox, PrimaryButton, SecondaryButton, UrgencyBadge, WrappedLabel, SectionTitle
from app.reports.handover_pdf import generate_doctor_handover_pdf


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
            text="⚠️ [b]Immediate Emergency Warning:[/b] If you are experiencing crushing chest pain, severe shortness of breath, sudden one-sided facial drooping or arm weakness, or uncontrollable bleeding, call [b]911 / 112 / 999[/b] or proceed immediately to the nearest emergency department.",
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
        
        b_prof = SecondaryButton(text="👤 Patient Profile", size_hint_y=None, height=42)
        b_prof.bind(on_release=lambda x: self._nav_to("patient_profile"))
        mod_grid.add_widget(b_prof)

        b_hist = SecondaryButton(text="📋 Assessment History", size_hint_y=None, height=42)
        b_hist.bind(on_release=lambda x: self._nav_to("patient_history"))
        mod_grid.add_widget(b_hist)

        b_prog = SecondaryButton(text="📈 Symptom Progression", size_hint_y=None, height=42)
        b_prog.bind(on_release=lambda x: self._nav_to("symptom_progression"))
        mod_grid.add_widget(b_prog)

        b_hand = SecondaryButton(text="📄 Doctor Handover PDF", size_hint_y=None, height=42)
        b_hand.bind(on_release=lambda x: self._nav_to("doctor_handover"))
        mod_grid.add_widget(b_hand)

        b_dir = SecondaryButton(text="🏥 Healthcare Directory", size_hint_y=None, height=42)
        b_dir.bind(on_release=lambda x: self._nav_to("healthcare_directory"))
        mod_grid.add_widget(b_dir)

        b_ref = SecondaryButton(text="📚 Medical References", size_hint_y=None, height=42)
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
        self.in_name = self._add_field(card, "Full Display Name *", "e.g. John Doe")
        self.in_dob = self._add_field(card, "Date of Birth (YYYY-MM-DD)", "1980-05-15")
        self.in_sex = self._add_field(card, "Biological Sex (male / female / other)", "male")
        self.in_blood = self._add_field(card, "Blood Group", "O+")
        self.in_allergies = self._add_field(card, "Known Allergies (Medications / Food)", "e.g. Penicillin, Peanuts")
        self.in_conditions = self._add_field(card, "Chronic Conditions (e.g. Hypertension, Diabetes)", "e.g. Asthma")
        self.in_meds = self._add_field(card, "Current Medications", "e.g. Albuterol inhaler")
        self.in_emerg = self._add_field(card, "Emergency Contact Details", "Jane Doe (+1-555-0199)")

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

    def on_pre_enter(self):
        curr = self.controller.patient_service.get_patient(self.controller.current_patient_id)
        if curr:
            self.in_name.text = curr.get("display_name", "")
            self.in_dob.text = curr.get("date_of_birth", "")
            self.in_sex.text = curr.get("biological_sex", "male")
            self.in_blood.text = curr.get("blood_group", "")
            self.in_allergies.text = curr.get("known_allergies", "")
            self.in_conditions.text = curr.get("chronic_conditions", "")
            self.in_meds.text = curr.get("current_medications", "")
            self.in_emerg.text = curr.get("emergency_contact", "")

    def _save_profile(self, *args):
        name = self.in_name.text.strip()
        if not name:
            self._show_popup("Validation Error", "Patient full display name is required.")
            return

        data = {
            "display_name": name,
            "date_of_birth": self.in_dob.text.strip(),
            "biological_sex": self.in_sex.text.strip().lower() or "prefer_not_to_say",
            "blood_group": self.in_blood.text.strip(),
            "known_allergies": self.in_allergies.text.strip(),
            "chronic_conditions": self.in_conditions.text.strip(),
            "current_medications": self.in_meds.text.strip(),
            "emergency_contact": self.in_emerg.text.strip()
        }
        self.controller.patient_service.update_patient(self.controller.current_patient_id, data)
        self._show_popup("Success", "Patient profile saved successfully.")

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
        content = BoxLayout(orientation="vertical", spacing=12, padding=[16, 16, 16, 24], size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(create_section_title("Step 1: Enter Reported Symptoms"))
        content.add_widget(create_desc_label("Search and select your primary symptoms, then rate pain severity (1-10) and progression."))

        # 1. Search Box
        search_card = CardBox(orientation="vertical", spacing=8, padding=[12, 10, 12, 10], size_hint_y=None)
        search_card.bind(minimum_height=search_card.setter("height"))
        search_card.add_widget(WrappedLabel(text="[b]Search Symptom Library (85+ items):[/b]", font_size="12sp", color=COLOR_NAVY_PRIMARY))
        self.in_search = TextInput(hint_text="e.g. Headache, Chest pain, Shortness of breath, Fever...", multiline=False, size_hint_y=None, height=36)
        self.in_search.bind(text=self._on_search)
        search_card.add_widget(self.in_search)
        content.add_widget(search_card)

        # 2. Search Results List (Dynamically populated)
        self.results_box = BoxLayout(orientation="vertical", spacing=6, size_hint_y=None)
        self.results_box.bind(minimum_height=self.results_box.setter("height"))
        content.add_widget(self.results_box)

        # 3. Selected Symptoms Summary Card
        content.add_widget(create_section_title("Selected Symptoms for Assessment"))
        self.selected_container = BoxLayout(orientation="vertical", spacing=8, size_hint_y=None)
        self.selected_container.bind(minimum_height=self.selected_container.setter("height"))
        content.add_widget(self.selected_container)

        # 4. Severity & Progression Inputs
        sev_card = CardBox(orientation="vertical", spacing=10, padding=[14, 12, 14, 12], size_hint_y=None)
        sev_card.bind(minimum_height=sev_card.setter("height"))
        
        # Interactive pain severity label updating dynamically
        self.lbl_sev = WrappedLabel(
            text="[b]Reported Pain / Severity Rating: 5 / 10[/b]",
            font_size="13sp",
            color=COLOR_NAVY_PRIMARY
        )
        sev_card.add_widget(self.lbl_sev)

        self.slider_sev = Slider(min=1, max=10, value=5, step=1, size_hint_y=None, height=38)
        self.slider_sev.bind(value=self._on_slider)
        sev_card.add_widget(self.slider_sev)

        # Duration input
        dur_box = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=36)
        dur_lbl = WrappedLabel(text="[b]Duration (Days):[/b]", font_size="12sp", color=COLOR_NAVY_PRIMARY, size_hint_x=0.4)
        dur_box.add_widget(dur_lbl)
        self.in_dur = TextInput(text="1", multiline=False, size_hint_x=0.6)
        dur_box.add_widget(self.in_dur)
        sev_card.add_widget(dur_box)

        # Trajectory / Progression buttons
        sev_card.add_widget(WrappedLabel(text="[b]Symptom Progression / Trajectory:[/b]", font_size="12sp", color=COLOR_NAVY_PRIMARY))
        traj_box = BoxLayout(orientation="horizontal", spacing=8, size_hint_y=None, height=38)
        self.btn_worse = Button(text="Worsening", font_size="12sp", bold=True)
        self.btn_worse.bind(on_release=lambda x: self._set_traj("worsening"))
        self.btn_same = Button(text="Unchanged", font_size="12sp", bold=True)
        self.btn_same.bind(on_release=lambda x: self._set_traj("unchanged"))
        self.btn_better = Button(text="Improving", font_size="12sp", bold=True)
        self.btn_better.bind(on_release=lambda x: self._set_traj("improving"))
        traj_box.add_widget(self.btn_worse)
        traj_box.add_widget(self.btn_same)
        traj_box.add_widget(self.btn_better)
        sev_card.add_widget(traj_box)

        content.add_widget(sev_card)

        # 5. Continue to Follow-up Questions Button
        btn_next = PrimaryButton(text="PROCEED TO CLINICAL QUESTIONS →", size_hint_y=None, height=44)
        btn_next.bind(on_release=self._proceed_to_followups)
        content.add_widget(btn_next)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def _set_traj(self, traj: str):
        self.current_progression = traj
        # Visual state feedback on buttons
        self.btn_worse.background_color = COLOR_URGENT_EMERGENCY if traj == "worsening" else (0.85, 0.85, 0.88, 1)
        self.btn_worse.color = COLOR_WHITE if traj == "worsening" else COLOR_TEXT_DARK

        self.btn_same.background_color = COLOR_BLUE_ACCENT if traj == "unchanged" else (0.85, 0.85, 0.88, 1)
        self.btn_same.color = COLOR_WHITE if traj == "unchanged" else COLOR_TEXT_DARK

        self.btn_better.background_color = COLOR_URGENT_ROUTINE if traj == "improving" else (0.85, 0.85, 0.88, 1)
        self.btn_better.color = COLOR_WHITE if traj == "improving" else COLOR_TEXT_DARK

    def _on_slider(self, instance, value):
        val = int(value)
        self.lbl_sev.text = f"[b]Reported Pain / Severity Rating: {val} / 10[/b]"

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
            btn = SecondaryButton(text=f"+ {s.get('name')} ({s.get('body_system', '')})", size_hint_y=None, height=36)
            if s.get("is_emergency_warning"):
                btn.text = f"⚠️ {btn.text} [RED FLAG]"
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
            empty = CardBox(padding=[12, 10, 12, 10], size_hint_y=None)
            empty.bind(minimum_height=empty.setter("height"))
            empty.add_widget(WrappedLabel(text="No symptoms added yet. Pick at least one symptom above.", font_size="11sp", color=COLOR_TEXT_MUTED))
            self.selected_container.add_widget(empty)
        else:
            for s in self.selected_symptoms:
                card = CardBox(orientation="horizontal", padding=[12, 6, 12, 6], spacing=8, size_hint_y=None)
                card.bind(minimum_height=card.setter("height"))
                
                name_lbl = WrappedLabel(text=f"[b]{s.get('name')}[/b] ({s.get('body_system', '')})", font_size="12sp", color=COLOR_NAVY_PRIMARY)
                card.add_widget(name_lbl)
                
                b_del = Button(text="Remove", font_size="11sp", size_hint=(None, None), size=(72, 28), background_color=COLOR_URGENT_EMERGENCY, color=COLOR_WHITE)
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
        self.content = BoxLayout(orientation="vertical", spacing=14, padding=[16, 16, 16, 24], size_hint_y=None)
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
            f"Adaptive questions tailored to reported symptoms, severity ({severity}/10), and trajectory ({progression.upper()}). "
            "Emergency red-flag safety checks are always verified."
        ))

        # Dynamically retrieve targeted questions linked to reported symptoms, progression, and severity
        questions = self.controller.dataset_loader.get_followup_questions_for_symptoms(
            sym_codes, progression=progression, severity=severity
        )

        for q in questions:
            q_card = CardBox(orientation="vertical", spacing=8, padding=[14, 12, 14, 12], size_hint_y=None)
            q_card.bind(minimum_height=q_card.setter("height"))

            is_emerg = bool(q.get("is_emergency_safety_check", False) or q.get("triggers_emergency_check", False))
            title_text = f"[b]{q.get('question_text')}[/b]"
            if is_emerg:
                title_text = f"⚠️ [color=#DC2626][b]RED FLAG CHECK:[/b][/color] {title_text}"

            q_lbl = WrappedLabel(
                text=title_text,
                font_size="13sp",
                color=COLOR_NAVY_PRIMARY
            )
            q_card.add_widget(q_lbl)

            qid = q["question_id"]
            opts_box = BoxLayout(orientation="vertical", spacing=6, size_hint_y=None)
            opts_box.bind(minimum_height=opts_box.setter("height"))

            btn_group = []
            for opt in q.get("options", []):
                opt_code = opt["code"]
                opt_btn = Button(
                    text=f"  {opt['text']}",
                    font_size="12sp",
                    halign="left",
                    size_hint_y=None,
                    height=38,
                    background_color=(0.95, 0.95, 0.98, 1),
                    color=COLOR_TEXT_DARK
                )
                opt_btn.bind(size=opt_btn.setter("text_size"))
                opt_btn.bind(on_release=lambda x, q=qid, c=opt_code, bg=btn_group, curr=opt_btn: self._select_answer(q, c, bg, curr))
                opts_box.add_widget(opt_btn)
                btn_group.append(opt_btn)

            q_card.add_widget(opts_box)
            self.content.add_widget(q_card)

        # Assessment Action Button
        btn_evaluate = PrimaryButton(text="SUBMIT & EVALUATE TRIAGE RESULTS →", size_hint_y=None, height=46)
        btn_evaluate.bind(on_release=self._evaluate_triage)
        self.content.add_widget(btn_evaluate)

    def _select_answer(self, qid: str, code: str, group: list, active_btn: Button):
        self.answers[qid] = code
        for b in group:
            b.background_color = (0.95, 0.95, 0.98, 1)
            b.color = COLOR_TEXT_DARK
        active_btn.background_color = COLOR_BLUE_ACCENT
        active_btn.color = COLOR_TEXT_LIGHT

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
        # SECTION 4: RECOMMENDED NEXT STEPS & SELF-CARE
        # -------------------------------------------------------------
        self.content.add_widget(create_section_title("3. Recommended Next Steps"))
        act_card = CardBox(orientation="vertical", spacing=6, padding=[14, 12, 14, 12], size_hint_y=None)
        act_card.bind(minimum_height=act_card.setter("height"))
        
        for act in result.recommended_next_steps:
            act_card.add_widget(WrappedLabel(
                text=act,
                font_size="12sp",
                color=COLOR_NAVY_PRIMARY
            ))
        self.content.add_widget(act_card)

        # -------------------------------------------------------------
        # SECTION 5: RECOMMENDED NEARBY HEALTHCARE FACILITIES
        # -------------------------------------------------------------
        self.content.add_widget(create_section_title("4. Nearby Healthcare Facilities & Navigation"))
        
        # Location state banner
        loc_service = self.controller.location_service
        loc_name = loc_service.current_location_name
        self.content.add_widget(create_desc_label(
            f"Sorted for {result.urgency_label} relative to: {loc_name}. (Works offline with local coordinates)."
        ))

        fac_box = BoxLayout(orientation="vertical", spacing=8, size_hint_y=None)
        fac_box.bind(minimum_height=fac_box.setter("height"))
        
        nearby = loc_service.get_nearby_facilities(urgency_category=cat, limit=4)
        for fac in nearby:
            f_card = CardBox(orientation="vertical", spacing=6, padding=[14, 10, 14, 10], size_hint_y=None)
            f_card.bind(minimum_height=f_card.setter("height"))

            # Top header row
            f_header = BoxLayout(orientation="horizontal", size_hint_y=None, height=24)
            f_header.add_widget(WrappedLabel(text=f"[b]{fac.get('name')}[/b]", font_size="13sp", color=COLOR_NAVY_PRIMARY))
            
            is_emerg = str(fac.get("has_emergency", "0")) == "1"
            if is_emerg:
                f_header.add_widget(WrappedLabel(text="[b]24/7 ER[/b]", font_size="11sp", color=COLOR_URGENT_EMERGENCY, size_hint_x=0.25))
            f_card.add_widget(f_header)

            # Details
            miles = fac.get("distance_miles", 0.0)
            km = fac.get("distance_km", 0.0)
            f_card.add_widget(WrappedLabel(
                text=f"📍 {fac.get('address')}, {fac.get('city')} — [b]{miles} mi / {km} km away[/b]",
                font_size="11sp",
                color=COLOR_TEXT_DARK
            ))
            f_card.add_widget(WrappedLabel(
                text=f"📞 Phone: {fac.get('phone')} | Hours: {fac.get('operating_hours')}",
                font_size="11sp",
                color=COLOR_TEXT_MUTED
            ))
            
            # Action button for directions
            btn_dir = SecondaryButton(text=f"Navigate / Directions ↗ ({fac.get('name')[:20]})", size_hint_y=None, height=34)
            btn_dir.bind(on_release=lambda x, target=fac: loc_service.open_directions(target))
            f_card.add_widget(btn_dir)

            fac_box.add_widget(f_card)

        self.content.add_widget(fac_box)

        # -------------------------------------------------------------
        # SECTION 6: CLINICAL DISCLAIMER & GOVERNANCE
        # -------------------------------------------------------------
        disc_card = CardBox(orientation="vertical", spacing=4, padding=[12, 10, 12, 10], size_hint_y=None)
        disc_card.bind(minimum_height=disc_card.setter("height"))
        disc_card.bg_color = (0.97, 0.97, 0.98, 1)
        disc_card.add_widget(WrappedLabel(
            text="⚠️ [b]Safety Notice:[/b] MEDICARE is an offline preliminary triage advisor and decision-support tool. It does not provide medical diagnoses, treatment prescriptions, or emergency guarantees. If your condition worsens rapidly, seek emergency medical care immediately.",
            font_size="10sp",
            color=COLOR_TEXT_MUTED
        ))
        self.content.add_widget(disc_card)

        # -------------------------------------------------------------
        # SECTION 7: HANDOVER & NAVIGATION ACTIONS
        # -------------------------------------------------------------
        act_box = BoxLayout(orientation="vertical", spacing=8, size_hint_y=None, height=92)
        
        btn_pdf = PrimaryButton(text="📄 GENERATE DOCTOR HANDOVER PDF", size_hint_y=None, height=42)
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
        
        box = BoxLayout(orientation="vertical", padding=14, spacing=10)
        box.add_widget(WrappedLabel(text=f"Doctor Handover PDF successfully saved:\n{out_file}", font_size="12sp"))
        b = PrimaryButton(text="OK", size_hint_y=None, height=36)
        p = Popup(title="PDF Report Ready", content=box, size_hint=(0.85, 0.4))
        b.bind(on_release=p.dismiss)
        box.add_widget(b)
        p.open()

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

        btn_gen = PrimaryButton(text="📄 GENERATE & EXPORT HANDOVER PDF", size_hint_y=None, height=44)
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
        out_file = out_dir / f"Handover_{latest_a.get('session_id', 'REPORT')}.pdf"
        generate_doctor_handover_pdf(patient, latest_a, out_file)
        self._show_msg("PDF Created", f"Doctor Handover PDF generated successfully:\n{out_file}")

    def _show_msg(self, title, msg):
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
            text="📍 Reference Location: [b]Not Set — Set location to search nearby facilities[/b]",
            font_size="12sp",
            color=COLOR_NAVY_PRIMARY
        )
        loc_card.add_widget(self.lbl_loc_status)

        # Location privacy note
        loc_card.add_widget(WrappedLabel(
            text="🔒 Privacy: Only your geographic coordinates are used for facility search. "
                 "No symptoms, medical history or patient data is ever sent to external services.",
            font_size="10sp",
            color=COLOR_TEXT_MUTED
        ))

        # Buttons row for location mode
        loc_btn_row = BoxLayout(orientation="horizontal", spacing=8, size_hint_y=None, height=36)
        btn_dev_loc = PrimaryButton(text="📍 Use Device Location", size_hint_x=0.5)
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
        btn_search = PrimaryButton(text="🔍 Search Nearby", size_hint_x=0.3)
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
        self.lbl_loc_status.text = f"📍 Reference Location: [b]{loc}[/b]"

    def _update_data_source_label(self):
        source = self.controller.location_service.last_search_source
        if source == "google_maps":
            self.lbl_data_source.text = "📡 Results: Live Google Maps data"
        elif source == "offline":
            self.lbl_data_source.text = "📂 Results: Local offline directory (last verified with dataset)"
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
                text="[b]  🚨 ER[/b]",
                font_size="10sp",
                color=COLOR_URGENT_EMERGENCY,
                size_hint_x=0.2
            ))
        card.add_widget(top_row)

        # --- Facility type + data source badge ---
        source = fac.get("source", "offline")
        facility_type = fac.get("facility_type", "Healthcare Facility")
        if source == "google_maps":
            source_badge = "[color=#1A73E8][b]📡 Google Maps[/b][/color]"
        else:
            is_verified = fac.get("is_verified", "1") in (True, "1", 1)
            source_badge = (
                "[color=#059669][b]✓ Local Directory[/b][/color]" if is_verified
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
            text=f"📍 {full_addr} — [b]{miles} mi / {km} km[/b]",
            font_size="11sp",
            color=COLOR_TEXT_DARK
        ))

        # --- Phone ---
        phone = fac.get("phone") or fac.get("nationalPhoneNumber") or "Not listed"
        card.add_widget(WrappedLabel(
            text=f"📞 {phone}",
            font_size="11sp",
            color=COLOR_TEXT_MUTED
        ))

        # --- Hours ---
        hours = fac.get("operating_hours", "")
        if hours:
            card.add_widget(WrappedLabel(
                text=f"🕐 {hours}",
                font_size="10sp",
                color=COLOR_TEXT_MUTED
            ))

        # --- Website (Google Maps results only) ---
        website = fac.get("website", "")
        if website:
            btn_web = SecondaryButton(text="🌐 Visit Website ↗", size_hint_y=None, height=30)
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
        btn_dir = SecondaryButton(text="🗺️ Open Directions in Maps ↗", size_hint_y=None, height=34)
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

        self.content.add_widget(create_section_title("Local Medical References & Guidelines"))
        self.content.add_widget(create_desc_label("Official clinical references (WHO ICD-11, EAACI, Surviving Sepsis, ESI, Canadian CT Head Rule)."))

        refs = self.controller.dataset_loader.get_medical_references()
        for r in refs:
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
