"""
MEDICARE Central Application Controller.
Coordinates database access, native C modules, local datasets,
patient services, triage engine, reporting, security, and UI launch.
"""
import logging
from pathlib import Path

from app.core.config import load_config, MedicareConfig
from app.core.logger import setup_logger, get_logger
from app.core.database import SQLiteDatabase
from app.core.native_loader import NativeLoader
from app.datasets.dataset_loader import DatasetLoader
from app.patients.patient_service import PatientService
from app.history.history_service import HistoryService
from app.history.handover_document_service import HandoverDocumentService
from app.triage.engine import TriageEngine
from app.security.encryption import SecurityManager
from app.synchronization.sync_service import SyncService
from app.healthcare.location_service import LocationService
from app.healthcare.offline_map_service import OfflineMapService

logger = logging.getLogger("medicare.controller")

class AppController:
    """Central singleton controller coordinating application subsystems."""

    def __init__(self, config: MedicareConfig = None):
        self.config = config or load_config()
        self.config.ensure_directories()
        self.logger = setup_logger(self.config.log_path, self.config.log_level)
        
        # Subsystems
        self.db: SQLiteDatabase = None
        self.native: NativeLoader = None
        self.dataset_loader: DatasetLoader = None
        self.patient_service: PatientService = None
        self.history_service: HistoryService = None
        self.handover_service: HandoverDocumentService = None
        self.triage_engine: TriageEngine = None
        self.security: SecurityManager = None
        self.sync_service: SyncService = None
        self.location_service: LocationService = None
        self.offline_map_service: OfflineMapService = None
        
        # Runtime State
        self.current_patient_id: int = 1
        self.assessment_staging: dict = {}
        self.last_triage_result = None
        self._initialized = False

    def initialize(self):
        """Initializes all underlying database, datasets, and clinical engines."""
        if self._initialized:
            return
            
        logger.info("Initializing MEDICARE Core Subsystems v%s", self.config.app_version)

        # 1. Database
        self.db = SQLiteDatabase(self.config.db_path)
        self.db.initialize()

        # 2. Security Manager
        self.security = SecurityManager(self.config.data_dir / ".medicare.key")

        # 3. Native C Modules
        self.native = NativeLoader(self.config.native_dir)

        # 4. Local Medical Datasets
        self.dataset_loader = DatasetLoader(self.config.data_dir, self.db)

        # 5. Core Business Services
        self.patient_service = PatientService(self.db)
        self.history_service = HistoryService(self.db)
        self.handover_service = HandoverDocumentService(self.db)
        self.triage_engine = TriageEngine(self.dataset_loader, self.native, self.db)
        self.sync_service = SyncService(self.config, self.db)
        self.location_service = LocationService(self.dataset_loader)
        self.offline_map_service = OfflineMapService(self.dataset_loader)

        # 6. Ensure default demonstration patient profile exists
        patients = self.patient_service.get_all_patients()
        if not patients:
            default_id = self.patient_service.create_patient({
                "display_name": "Ethan (Demonstration Profile)",
                "date_of_birth": "15/06/1990",
                "biological_sex": "male",
                "blood_group": "A+",
                "known_allergies": "No known drug allergies (NKDA)",
                "chronic_conditions": "None reported",
                "current_medications": "None",
                "emergency_contact": "+91-9876543210"
            })
            self.current_patient_id = default_id
        else:
            self.current_patient_id = patients[0]["id"]

        self.db.log_audit_event("APP_START", f"MEDICARE v{self.config.app_version} initialized")
        self._initialized = True
        logger.info("MEDICARE initialization complete. Active patient ID: %s", self.current_patient_id)

    def start(self):
        """Starts the Kivy user interface."""
        # Set window size BEFORE importing Kivy Window — Config must be set
        # before SDL2 creates the display, otherwise the size is ignored.
        from kivy.config import Config as KivyConfig
        KivyConfig.set("graphics", "width", "1366")
        KivyConfig.set("graphics", "height", "768")
        KivyConfig.set("graphics", "resizable", "1")
        KivyConfig.set("graphics", "fullscreen", "0")
        from app.ui.app import MedicareKivyApp
        app = MedicareKivyApp(self)
        return app.run()

    def shutdown(self):
        """Gracefully closes resources upon termination."""
        if self.db:
            self.db.log_audit_event("APP_STOP", "MEDICARE termination")
            self.db.close()
        logger.info("MEDICARE core successfully stopped.")
