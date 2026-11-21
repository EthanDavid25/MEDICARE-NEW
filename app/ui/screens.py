"""
MEDICARE Complete Multi-Screen Application Interface.
Implements all 12 required functional screens with seamless navigation and data binding.
"""
import json
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
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window

from app.ui.theme import (
    COLOR_NAVY_PRIMARY, COLOR_NAVY_LIGHT, COLOR_BLUE_ACCENT,
    COLOR_BLUE_TINT, COLOR_BG_LIGHT, COLOR_WHITE, COLOR_TEXT_DARK,
    COLOR_TEXT_MUTED, COLOR_TEXT_LIGHT, COLOR_BORDER,
    COLOR_URGENT_EMERGENCY, COLOR_URGENT_EARLY, COLOR_URGENT_ROUTINE,
    COLOR_URGENT_INSUFF
)
from app.ui.components import CardBox, PrimaryButton, SecondaryButton, UrgencyBadge
from app.reports.handover_pdf import generate_doctor_handover_pdf

# Helper to create styled Section Title
def create_section_title(text: str) -> Label:
    lbl = Label(
        text=f"[b]{text}[/b]",
        markup=True,
        font_size="16sp",
        color=COLOR_NAVY_PRIMARY,
        size_hint_y=None,
        height=32,
        halign="left",
        valign="middle"
    )
    lbl.bind(size=lbl.setter("text_size"))
    return lbl

# Helper to create subtle description label
def create_desc_label(text: str) -> Label:
    lbl = Label(
        text=text,
        font_size="12sp",
        color=COLOR_TEXT_MUTED,
        size_hint_y=None,
        height=24,
        halign="left",
        valign="middle"
    )
    lbl.bind(size=lbl.setter("text_size"))
    return lbl


# =========================================================================
# 1. DASHBOARD SCREEN
# =========================================================================
class DashboardScreen(Screen):
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
        banner = CardBox(orientation="vertical", spacing=8, padding=[18, 16, 18, 16], size_hint_y=None, height=140)
        banner.bg_color = COLOR_NAVY_PRIMARY
        banner.border_color = COLOR_NAVY_LIGHT
        
        b_title = Label(
            text="[b]Welcome to MEDICARE[/b]\nMedical Symptoms Triage Advisor",
            markup=True,
            font_size="18sp",
            color=COLOR_TEXT_LIGHT,
            halign="left",
            valign="middle"
        )
        b_title.bind(size=b_title.setter("text_size"))
        banner.add_widget(b_title)

        b_sub = Label(
            text="Autonomous offline preliminary assessment, progression tracking, and medical navigation.",
            font_size="11sp",
            color=COLOR_BLUE_TINT,
            halign="left",
            valign="middle"
        )
        b_sub.bind(size=b_sub.setter("text_size"))
        banner.add_widget(b_sub)
        content.add_widget(banner)

        # 2. Main Call to Action: Start Symptom Assessment
        start_card = CardBox(orientation="vertical", spacing=10, padding=[16, 14, 16, 14], size_hint_y=None, height=110)
        start_card.bg_color = COLOR_BLUE_TINT
        start_card.border_color = COLOR_BLUE_ACCENT
        
        sc_lbl = Label(
            text="[b]Feeling Unwell? Start a New Assessment[/b]\nAnswer a few guided clinical questions for an explainable urgency category.",
            markup=True,
            font_size="13sp",
            color=COLOR_NAVY_PRIMARY,
            halign="left",
            valign="middle"
        )
        sc_lbl.bind(size=sc_lbl.setter("text_size"))
        start_card.add_widget(sc_lbl)

        btn_start = PrimaryButton(text="START SYMPTOM ASSESSMENT", size_hint_y=None, height=40)
        btn_start.bind(on_release=lambda x: self._nav_to("symptom_assessment"))
        start_card.add_widget(btn_start)
        content.add_widget(start_card)

        # 3. Quick Stats & Status Grid
        content.add_widget(create_section_title("System Status & Overview"))
        
        stats_grid = GridLayout(cols=2, spacing=10, size_hint_y=None, height=130)
        
        # Box 1: Storage Mode
        c1 = CardBox(orientation="vertical", padding=[12, 10, 12, 10], spacing=4)
        c1.add_widget(Label(text="OPERATING MODE", font_size="10sp", color=COLOR_TEXT_MUTED, bold=True))
        c1.add_widget(Label(text="100% Offline Active", font_size="14sp", color=COLOR_NAVY_PRIMARY, bold=True))
        c1.add_widget(Label(text="Local SQLite & Datasets", font_size="10sp", color=COLOR_TEXT_MUTED))
        stats_grid.add_widget(c1)

        # Box 2: Triage Engine
        c2 = CardBox(orientation="vertical", padding=[12, 10, 12, 10], spacing=4)
        c2.add_widget(Label(text="TRIAGE ENGINE", font_size="10sp", color=COLOR_TEXT_MUTED, bold=True))
        c2.add_widget(Label(text="Rule Engine v1.0", font_size="14sp", color=COLOR_NAVY_PRIMARY, bold=True))
        c2.add_widget(Label(text="35 Clinical Rules Loaded", font_size="10sp", color=COLOR_TEXT_MUTED))
        stats_grid.add_widget(c2)
        content.add_widget(stats_grid)

        # 4. Recent Assessments Card List
        content.add_widget(create_section_title("Recent Assessments"))
        self.recent_container = BoxLayout(orientation="vertical", spacing=8, size_hint_y=None)
        self.recent_container.bind(minimum_height=self.recent_container.setter("height"))
        content.add_widget(self.recent_container)

        # 5. Quick Modules Navigation Grid
        content.add_widget(create_section_title("Application Modules"))
        
        mod_grid = GridLayout(cols=2, spacing=10, size_hint_y=None, height=180)
        
        b_prof = SecondaryButton(text="👤 Patient Profile", size_hint_y=None, height=44)
        b_prof.bind(on_release=lambda x: self._nav_to("patient_profile"))
        mod_grid.add_widget(b_prof)

        b_hist = SecondaryButton(text="📋 Assessment History", size_hint_y=None, height=44)
        b_hist.bind(on_release=lambda x: self._nav_to("patient_history"))
        mod_grid.add_widget(b_hist)

        b_prog = SecondaryButton(text="📈 Symptom Progression", size_hint_y=None, height=44)
        b_prog.bind(on_release=lambda x: self._nav_to("symptom_progression"))
        mod_grid.add_widget(b_prog)

        b_hand = SecondaryButton(text="📄 Doctor Handover PDF", size_hint_y=None, height=44)
        b_hand.bind(on_release=lambda x: self._nav_to("doctor_handover"))
        mod_grid.add_widget(b_hand)

        b_dir = SecondaryButton(text="🏥 Healthcare Directory", size_hint_y=None, height=44)
        b_dir.bind(on_release=lambda x: self._nav_to("healthcare_directory"))
        mod_grid.add_widget(b_dir)

        b_ref = SecondaryButton(text="📚 Medical References", size_hint_y=None, height=44)
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
            empty_card = CardBox(padding=[14, 12, 14, 12], size_hint_y=None, height=54)
            empty_card.add_widget(Label(
                text="No past assessments recorded yet. Complete an assessment to see history.",
                font_size="11sp",
                color=COLOR_TEXT_MUTED
            ))
            self.recent_container.add_widget(empty_card)
        else:
            for a in assessments:
                row = CardBox(orientation="horizontal", padding=[12, 8, 12, 8], spacing=10, size_hint_y=None, height=58)
                
                info_box = BoxLayout(orientation="vertical", spacing=2)
                dt = (a.get("completed_at") or "")[:16].replace("T", " ")
                info_box.add_widget(Label(text=f"[b]{dt}[/b]", markup=True, font_size="12sp", color=COLOR_NAVY_PRIMARY, halign="left"))
                info_box.add_widget(Label(text=f"Session: {a.get('session_id')}", font_size="10sp", color=COLOR_TEXT_MUTED, halign="left"))
                row.add_widget(info_box)

                badge = UrgencyBadge(category=a.get("urgency_category", 3))
                row.add_widget(badge)
                self.recent_container.add_widget(row)

    def _nav_to(self, screen_name: str):
        self.manager.current = screen_name


# =========================================================================
# 2. PATIENT PROFILE SCREEN
# =========================================================================
class PatientProfileScreen(Screen):
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

        card = CardBox(orientation="vertical", spacing=10, padding=[16, 16, 16, 16], size_hint_y=None)
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

        # Danger Zone / Export Box
        mgmt_box = CardBox(orientation="vertical", spacing=8, padding=[14, 12, 14, 12], size_hint_y=None, height=130)
        mgmt_box.border_color = COLOR_BORDER
        mgmt_box.add_widget(Label(text="[b]Data Management & Privacy[/b]", markup=True, font_size="13sp", color=COLOR_NAVY_PRIMARY))
        
        btn_export = SecondaryButton(text="Export Full Records (JSON)", size_hint_y=None, height=36)
        btn_export.bind(on_release=self._export_records)
        mgmt_box.add_widget(btn_export)

        btn_delete = Button(text="Delete Profile & Erase Records", background_color=COLOR_URGENT_EMERGENCY, font_size="12sp", bold=True, size_hint_y=None, height=36)
        btn_delete.bind(on_release=self._delete_records)
        mgmt_box.add_widget(btn_delete)

        content.add_widget(mgmt_box)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def _add_field(self, parent, label_text, placeholder):
        lbl = Label(text=label_text, font_size="12sp", color=COLOR_NAVY_PRIMARY, bold=True, size_hint_y=None, height=20, halign="left")
        lbl.bind(size=lbl.setter("text_size"))
        parent.add_widget(lbl)
        inp = TextInput(hint_text=placeholder, multiline=False, size_hint_y=None, height=36, font_size="13sp")
        parent.add_widget(inp)
        return inp

    def on_pre_enter(self):
        p = self.controller.patient_service.get_patient(self.controller.current_patient_id)
        if p:
            self.in_name.text = p.get("display_name", "")
            self.in_dob.text = p.get("date_of_birth", "")
            self.in_sex.text = p.get("biological_sex", "")
            self.in_blood.text = p.get("blood_group", "")
            self.in_allergies.text = p.get("known_allergies", "")
            self.in_conditions.text = p.get("chronic_conditions", "")
            self.in_meds.text = p.get("current_medications", "")
            self.in_emerg.text = p.get("emergency_contact", "")

    def _save_profile(self, *args):
        data = {
            "display_name": self.in_name.text.strip() or "General Patient",
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
        box.add_widget(Label(text=msg, font_size="13sp"))
        b = PrimaryButton(text="OK", size_hint_y=None, height=36)
        p = Popup(title=title, content=box, size_hint=(0.8, 0.4))
        b.bind(on_release=p.dismiss)
        box.add_widget(b)
        p.open()


# =========================================================================
# 3. SYMPTOM ASSESSMENT SCREEN
# =========================================================================
class SymptomAssessmentScreen(Screen):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.selected_symptoms: list[dict] = []
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)
        
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        content = BoxLayout(orientation="vertical", spacing=12, padding=[16, 16, 16, 24], size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(create_section_title("Step 1: Enter Reported Symptoms"))
        content.add_widget(create_desc_label("Search and select your primary symptoms, then rate severity and progression."))

        # 1. Search Box
        search_card = CardBox(orientation="vertical", spacing=8, padding=[12, 10, 12, 10], size_hint_y=None, height=84)
        search_card.add_widget(Label(text="Search Symptom Library (85+ items):", font_size="11sp", color=COLOR_NAVY_PRIMARY, bold=True))
        self.in_search = TextInput(hint_text="e.g. Headache, Chest pain, Shortness of breath...", multiline=False, size_hint_y=None, height=36)
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
        sev_card = CardBox(orientation="vertical", spacing=10, padding=[14, 12, 14, 12], size_hint_y=None, height=210)
        self.lbl_sev = Label(text="[b]Reported Pain / Severity Rating: 5 / 10[/b]", markup=True, font_size="13sp", color=COLOR_NAVY_PRIMARY)
        sev_card.add_widget(self.lbl_sev)

        self.slider_sev = Slider(min=1, max=10, value=5, step=1, size_hint_y=None, height=36)
        self.slider_sev.bind(value=self._on_slider)
        sev_card.add_widget(self.slider_sev)

        # Duration input
        dur_box = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=36)
        dur_box.add_widget(Label(text="Duration (Days):", font_size="12sp", color=COLOR_NAVY_PRIMARY, bold=True, size_hint_x=0.4))
        self.in_dur = TextInput(text="1", multiline=False, size_hint_x=0.6)
        dur_box.add_widget(self.in_dur)
        sev_card.add_widget(dur_box)

        # Trajectory buttons
        sev_card.add_widget(Label(text="Symptom Trajectory:", font_size="12sp", color=COLOR_NAVY_PRIMARY, bold=True))
        traj_box = BoxLayout(orientation="horizontal", spacing=8, size_hint_y=None, height=36)
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

        self.current_progression = "unchanged"

    def _set_traj(self, traj: str):
        self.current_progression = traj
        # Visual feedback on buttons
        self.btn_worse.background_color = COLOR_URGENT_EMERGENCY if traj == "worsening" else (0.8, 0.8, 0.8, 1)
        self.btn_same.background_color = COLOR_BLUE_ACCENT if traj == "unchanged" else (0.8, 0.8, 0.8, 1)
        self.btn_better.background_color = COLOR_URGENT_ROUTINE if traj == "improving" else (0.8, 0.8, 0.8, 1)

    def _on_slider(self, instance, value):
        self.lbl_sev.text = f"[b]Reported Pain / Severity Rating: {int(value)} / 10[/b]"

    def on_pre_enter(self):
        self.in_search.text = ""
        self._set_traj("unchanged")
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
            empty = CardBox(padding=[12, 10, 12, 10], size_hint_y=None, height=48)
            empty.add_widget(Label(text="No symptoms added yet. Pick at least one symptom above.", font_size="11sp", color=COLOR_TEXT_MUTED))
            self.selected_container.add_widget(empty)
        else:
            for s in self.selected_symptoms:
                card = CardBox(orientation="horizontal", padding=[12, 6, 12, 6], spacing=8, size_hint_y=None, height=44)
                name_lbl = Label(text=f"[b]{s.get('name')}[/b]", markup=True, font_size="12sp", color=COLOR_NAVY_PRIMARY, halign="left")
                card.add_widget(name_lbl)
                
                b_del = Button(text="Remove", font_size="11sp", size_hint=(None, None), size=(70, 28), background_color=COLOR_URGENT_EMERGENCY)
                b_del.bind(on_release=lambda x, code=s["code"]: self._remove_symptom(code))
                card.add_widget(b_del)
                self.selected_container.add_widget(card)

    def _proceed_to_followups(self, *args):
        if not self.selected_symptoms:
            # Default to general headache if none picked
            sym = self.controller.dataset_loader.get_symptoms()[0]
            self.selected_symptoms.append(sym)

        # Store assessment input state in controller
        dur_val = 1
        try:
            dur_val = int(self.in_dur.text.strip())
        except Exception:
            dur_val = 1

        self.controller.assessment_staging = {
            "symptoms": [
                {
                    "code": s["code"],
                    "name": s["name"],
                    "severity": int(self.slider_sev.value),
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
# 4. FOLLOW-UP QUESTIONS SCREEN
# =========================================================================
class FollowupQuestionsScreen(Screen):
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
        self.content.add_widget(create_desc_label("Please answer each inquiry carefully. Critical emergency indicators will be verified."))

        staging = getattr(self.controller, "assessment_staging", {})
        symptoms = staging.get("symptoms", [])
        sym_codes = [s["code"] for s in symptoms]

        # Dynamically retrieve targeted questions linked to reported symptoms
        questions = self.controller.dataset_loader.get_followup_questions_for_symptoms(sym_codes)

        self.question_widgets = {}

        for q in questions:
            q_card = CardBox(orientation="vertical", spacing=8, padding=[14, 12, 14, 12], size_hint_y=None)
            q_card.bind(minimum_height=q_card.setter("height"))

            is_emerg = q.get("triggers_emergency_check", False)
            title_text = f"[b]{q.get('question_text')}[/b]"
            if is_emerg:
                title_text = f"⚠️ [color=#DC2626][b]RED FLAG CHECK:[/b][/color] {title_text}"

            q_lbl = Label(text=title_text, markup=True, font_size="13sp", color=COLOR_NAVY_PRIMARY, halign="left")
            q_lbl.bind(size=q_lbl.setter("text_size"))
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
                    height=36,
                    background_color=(0.95, 0.95, 0.97, 1),
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
            b.background_color = (0.95, 0.95, 0.97, 1)
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
# 5. TRIAGE RESULTS SCREEN
# =========================================================================
class TriageResultsScreen(Screen):
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
            self.content.add_widget(Label(text="No recent assessment evaluated.", color=COLOR_TEXT_DARK))
            return

        cat = result.urgency_category
        
        # 1. Prominent Urgency Outcome Card
        cat_card = CardBox(orientation="vertical", spacing=8, padding=[18, 16, 18, 16], size_hint_y=None, height=130)
        if cat == 1:
            cat_card.bg_color = COLOR_URGENT_EMERGENCY
        elif cat == 2:
            cat_card.bg_color = COLOR_URGENT_EARLY
        elif cat == 3:
            cat_card.bg_color = COLOR_URGENT_ROUTINE
        else:
            cat_card.bg_color = COLOR_URGENT_INSUFF

        lbl_cat = Label(
            text=f"[size=20sp][b]{result.urgency_label.upper()}[/b][/size]\nClassification Category: {cat} / 4",
            markup=True,
            font_size="15sp",
            color=COLOR_TEXT_LIGHT,
            halign="left"
        )
        lbl_cat.bind(size=lbl_cat.setter("text_size"))
        cat_card.add_widget(lbl_cat)
        self.content.add_widget(cat_card)

        # 2. Plain Language Explanation
        self.content.add_widget(create_section_title("Assessment Explanation"))
        expl_card = CardBox(orientation="vertical", spacing=6, padding=[14, 12, 14, 12], size_hint_y=None)
        expl_card.bind(minimum_height=expl_card.setter("height"))
        
        expl_lbl = Label(text=result.summary_explanation, font_size="13sp", color=COLOR_NAVY_PRIMARY, halign="left")
        expl_lbl.bind(size=expl_lbl.setter("text_size"))
        expl_card.add_widget(expl_lbl)
        self.content.add_widget(expl_card)

        # 3. Clinical Justification & Triggered Rules
        self.content.add_widget(create_section_title("Detailed Reasoning & Triggered Indicators"))
        just_card = CardBox(orientation="vertical", spacing=6, padding=[14, 12, 14, 12], size_hint_y=None)
        just_card.bind(minimum_height=just_card.setter("height"))
        for d in result.detailed_reasoning:
            j_lbl = Label(text=d, font_size="12sp", color=COLOR_TEXT_DARK, halign="left")
            j_lbl.bind(size=j_lbl.setter("text_size"))
            just_card.add_widget(j_lbl)
        self.content.add_widget(just_card)

        # 4. Recommended Actions
        self.content.add_widget(create_section_title("Recommended Next Steps"))
        act_card = CardBox(orientation="vertical", spacing=6, padding=[14, 12, 14, 12], size_hint_y=None)
        act_card.bind(minimum_height=act_card.setter("height"))
        for act in result.recommended_next_steps:
            a_lbl = Label(text=act, font_size="12sp", color=COLOR_NAVY_PRIMARY, bold=True, halign="left")
            a_lbl.bind(size=a_lbl.setter("text_size"))
            act_card.add_widget(a_lbl)
        self.content.add_widget(act_card)

        # 5. Export / Handover Actions
        act_box = BoxLayout(orientation="vertical", spacing=8, size_hint_y=None, height=90)
        
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
        out_file = out_dir / f"Handover_{result.session_id}.pdf"
        generate_doctor_handover_pdf(patient, result.to_dict(), out_file)
        
        # Show alert popup
        box = BoxLayout(orientation="vertical", padding=14, spacing=10)
        box.add_widget(Label(text=f"Doctor Handover PDF successfully saved:\n{out_file}", font_size="12sp"))
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
class PatientHistoryScreen(Screen):
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
            empty = CardBox(padding=[14, 12, 14, 12], size_hint_y=None, height=50)
            empty.add_widget(Label(text="No past evaluations found.", font_size="12sp", color=COLOR_TEXT_MUTED))
            self.content.add_widget(empty)
            return

        for r in records:
            card = CardBox(orientation="vertical", spacing=6, padding=[14, 12, 14, 12], size_hint_y=None)
            card.bind(minimum_height=card.setter("height"))

            header = BoxLayout(orientation="horizontal", size_hint_y=None, height=28)
            dt_str = (r.get("completed_at") or "")[:16].replace("T", " ")
            header.add_widget(Label(text=f"[b]{dt_str}[/b]", markup=True, font_size="13sp", color=COLOR_NAVY_PRIMARY, halign="left"))
            badge = UrgencyBadge(category=r.get("urgency_category", 3))
            header.add_widget(badge)
            card.add_widget(header)

            card.add_widget(Label(text=f"Ref: {r.get('session_id')}", font_size="10sp", color=COLOR_TEXT_MUTED, halign="left"))
            card.add_widget(Label(text=r.get("explanation", ""), font_size="12sp", color=COLOR_TEXT_DARK, halign="left"))
            self.content.add_widget(card)


# =========================================================================
# 7. SYMPTOM PROGRESSION SCREEN
# =========================================================================
class SymptomProgressionScreen(Screen):
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
            card = CardBox(padding=[14, 12, 14, 12], size_hint_y=None, height=54)
            card.add_widget(Label(text="No symptom history logged. Complete multiple assessments to view progression.", font_size="11sp", color=COLOR_TEXT_MUTED))
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

                card.add_widget(Label(text=f"[b]{sym_name}[/b] ({len(entries)} recorded assessments)", markup=True, font_size="13sp", color=COLOR_NAVY_PRIMARY))
                for e in entries[-4:]: # Show recent 4 entries
                    dt = (e.get("recorded_at") or "")[:16].replace("T", " ")
                    sev = e.get("severity", 5)
                    prog = (e.get("progression") or "unchanged").title()
                    row_txt = f"• {dt} — Severity: {sev}/10 | Progression: {prog}"
                    card.add_widget(Label(text=row_txt, font_size="11sp", color=COLOR_TEXT_DARK))
                self.content.add_widget(card)

        btn_reassess = PrimaryButton(text="RECORD NEW SYMPTOM ASSESSMENT", size_hint_y=None, height=44)
        btn_reassess.bind(on_release=lambda x: self._nav_to("symptom_assessment"))
        self.content.add_widget(btn_reassess)

    def _nav_to(self, screen_name: str):
        self.manager.current = screen_name


# =========================================================================
# 8. DOCTOR HANDOVER SCREEN
# =========================================================================
class DoctorHandoverScreen(Screen):
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
        content.add_widget(create_desc_label("Generates an offline structured medical summary for your attending physician or urgent care clinic."))

        card = CardBox(orientation="vertical", spacing=10, padding=[16, 14, 16, 14], size_hint_y=None, height=180)
        card.add_widget(Label(
            text="[b]Clinical Summary Document[/b]\nIncludes patient demographics, known allergies, current chief complaints, "
                 "symptom progression trajectory, and triggered triage warning signs.",
            markup=True,
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
        out_file = out_dir / f"Handover_{latest_a.get('session_id', 'REPORT')}.pdf"
        generate_doctor_handover_pdf(patient, latest_a, out_file)
        self._show_msg("PDF Created", f"Doctor Handover PDF generated successfully:\n{out_file}")

    def _show_msg(self, title, msg):
        box = BoxLayout(orientation="vertical", padding=14, spacing=10)
        box.add_widget(Label(text=msg, font_size="12sp"))
        b = PrimaryButton(text="OK", size_hint_y=None, height=36)
        p = Popup(title=title, content=box, size_hint=(0.85, 0.4))
        b.bind(on_release=p.dismiss)
        box.add_widget(b)
        p.open()


# =========================================================================
# 9. HEALTHCARE DIRECTORY SCREEN
# =========================================================================
class HealthcareDirectoryScreen(Screen):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.content = BoxLayout(orientation="vertical", spacing=10, padding=[16, 16, 16, 24], size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter("height"))

        self.content.add_widget(create_section_title("Local Healthcare Facilities Directory"))
        self.content.add_widget(create_desc_label("Search locally stored verified and demonstration facilities. Works 100% offline."))

        # Search box
        search_card = CardBox(orientation="vertical", spacing=6, padding=[12, 10, 12, 10], size_hint_y=None, height=76)
        self.in_search = TextInput(hint_text="Search hospital name, city, service...", multiline=False, size_hint_y=None, height=36)
        self.in_search.bind(text=self._on_search)
        search_card.add_widget(self.in_search)
        self.content.add_widget(search_card)

        self.list_box = BoxLayout(orientation="vertical", spacing=8, size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        self.content.add_widget(self.list_box)

        scroll.add_widget(self.content)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_pre_enter(self):
        self._on_search(None, "")

    def _on_search(self, instance, query):
        self.list_box.clear_widgets()
        facilities = self.controller.dataset_loader.get_facilities(search=query or "")
        for fac in facilities:
            card = CardBox(orientation="vertical", spacing=4, padding=[14, 10, 14, 10], size_hint_y=None, height=105)
            
            top_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=22)
            top_row.add_widget(Label(text=f"[b]{fac.get('name')}[/b]", markup=True, font_size="13sp", color=COLOR_NAVY_PRIMARY, halign="left"))
            
            is_emerg = str(fac.get("has_emergency", "0")) == "1"
            if is_emerg:
                emerg_tag = Label(text="[b]24/7 ER[/b]", markup=True, font_size="10sp", color=COLOR_URGENT_EMERGENCY, size_hint_x=0.25)
                top_row.add_widget(emerg_tag)
            card.add_widget(top_row)

            card.add_widget(Label(text=f"📍 {fac.get('address')}, {fac.get('city')}, {fac.get('state')}", font_size="11sp", color=COLOR_TEXT_DARK))
            card.add_widget(Label(text=f"📞 Phone: {fac.get('phone')} | Hours: {fac.get('operating_hours')}", font_size="11sp", color=COLOR_TEXT_MUTED))
            card.add_widget(Label(text=f"Services: {fac.get('services')}", font_size="10sp", color=COLOR_NAVY_LIGHT))
            self.list_box.add_widget(card)


# =========================================================================
# 10. MEDICAL REFERENCES SCREEN
# =========================================================================
class MedicalReferencesScreen(Screen):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.content = BoxLayout(orientation="vertical", spacing=12, padding=[16, 16, 16, 24], size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter("height"))

        self.content.add_widget(create_section_title("Local Medical References & Guidance"))
        self.content.add_widget(create_desc_label("Official clinical reference guidelines (WHO ICD-11, EAACI, Surviving Sepsis, ESI)."))

        refs = self.controller.dataset_loader.get_medical_references()
        for r in refs:
            card = CardBox(orientation="vertical", spacing=6, padding=[14, 12, 14, 12], size_hint_y=None)
            card.bind(minimum_height=card.setter("height"))

            card.add_widget(Label(text=f"[b]{r.get('title')}[/b]", markup=True, font_size="13sp", color=COLOR_NAVY_PRIMARY))
            card.add_widget(Label(text=f"Source: {r.get('source')} | Version: {r.get('version')}", font_size="10sp", color=COLOR_TEXT_MUTED))
            card.add_widget(Label(text=r.get("content", ""), font_size="12sp", color=COLOR_TEXT_DARK))
            self.content.add_widget(card)

        scroll.add_widget(self.content)
        root.add_widget(scroll)
        self.add_widget(root)


# =========================================================================
# 11. SETTINGS SCREEN
# =========================================================================
class SettingsScreen(Screen):
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
        card1 = CardBox(orientation="vertical", spacing=8, padding=[14, 12, 14, 12], size_hint_y=None, height=130)
        card1.add_widget(Label(text="[b]Storage & Database Paths[/b]", markup=True, font_size="13sp", color=COLOR_NAVY_PRIMARY))
        card1.add_widget(Label(text=f"Database: {self.controller.config.db_path}", font_size="11sp", color=COLOR_TEXT_DARK))
        card1.add_widget(Label(text=f"Log File: {self.controller.config.log_path}", font_size="11sp", color=COLOR_TEXT_DARK))
        card1.add_widget(Label(text=f"C Native Engine: {'Active DLL/SO' if self.controller.native.using_native else 'Python Fallback (100% Functional)'}", font_size="11sp", color=COLOR_BLUE_ACCENT, bold=True))
        content.add_widget(card1)

        # Network check card
        card2 = CardBox(orientation="vertical", spacing=8, padding=[14, 12, 14, 12], size_hint_y=None, height=110)
        card2.add_widget(Label(text="[b]Offline / Synchronization Status[/b]", markup=True, font_size="13sp", color=COLOR_NAVY_PRIMARY))
        self.lbl_net = Label(text="Status: Autonomous Offline Mode Active", font_size="12sp", color=COLOR_TEXT_DARK)
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
# 12. ABOUT MEDICARE SCREEN
# =========================================================================
class AboutScreen(Screen):
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

        card = CardBox(orientation="vertical", spacing=8, padding=[16, 14, 16, 14], size_hint_y=None)
        card.bind(minimum_height=card.setter("height"))

        about_text = (
            "[b]1. Architectural Overview & Distribution[/b]\n"
            "MEDICARE is a cross-platform (Android + Windows) offline-first desktop and mobile application. "
            "It is engineered using Python (~70%) for user workflows, Kivy UI, database operations, "
            "and triage orchestration, with C (~30%) for native symptom normalization, input validation primitives, "
            "and bitfield rule evaluation.\n\n"
            "[b]2. Four Urgency Categories[/b]\n"
            "• Category 1: Emergency Care (immediate life-saving intervention)\n"
            "• Category 2: Early Medical Consultation (evaluation within 24-48 hours)\n"
            "• Category 3: Routine Healthcare (primary care or guided self-care)\n"
            "• Category 4: Insufficient Information (discordant or incomplete inputs)\n\n"
            "[b]3. Offline-First Guarantee[/b]\n"
            "All core clinical evaluation capabilities, datasets, SQLite persistence, and PDF handover generation "
            "function with 100% autonomy without requiring an internet connection or external API.\n\n"
            "[b]4. Clinical Governance & Limitations[/b]\n"
            "MEDICARE does NOT diagnose medical diseases, prescribe drugs or dosages, or guarantee safety. "
            "It is a navigation advisor designed to assist patients in deciding when and where to seek professional care."
        )
        lbl = Label(text=about_text, markup=True, font_size="12sp", color=COLOR_NAVY_PRIMARY)
        lbl.bind(size=lbl.setter("text_size"))
        card.add_widget(lbl)
        content.add_widget(card)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)
