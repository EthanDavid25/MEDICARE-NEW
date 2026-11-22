"""
MEDICARE Central Doctor Handover Downloads & Document Library Service.
Tracks downloaded clinical handovers in SQLite with disk status synchronization,
search capabilities, export management, and file deletion safeguards.
"""
import uuid
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

logger = logging.getLogger("medicare.handover_service")


class HandoverDocumentService:
    """Manages downloaded Doctor Handover PDF documents and their metadata."""

    def __init__(self, db):
        self.db = db

    def register_download(
        self,
        session_id: str,
        patient_id: int,
        patient_name: str,
        title: str,
        main_symptoms: str,
        pain_severity: int,
        triage_category: int,
        triage_label: str,
        file_path: str | Path
    ) -> dict:
        """
        Registers a downloaded doctor handover PDF in the SQLite database.
        Called ONLY when user explicitly triggers 'Download Doctor Handover'.
        """
        p = Path(file_path).resolve()
        file_size = p.stat().st_size if p.exists() else 0
        filename = p.name
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Check if already registered
        existing = self.db.fetchone(
            "SELECT * FROM downloaded_handovers WHERE session_id = ? OR file_path = ?",
            (session_id, str(p))
        )
        if existing:
            doc_id = existing["id"]
            self.db.execute(
                """
                UPDATE downloaded_handovers
                SET patient_name = ?, title = ?, main_symptoms = ?, pain_severity = ?,
                    triage_category = ?, triage_label = ?, filename = ?, file_path = ?,
                    file_size = ?, downloaded_at = ?, status = 'available'
                WHERE id = ?
                """,
                (
                    patient_name, title, main_symptoms, pain_severity,
                    triage_category, triage_label, filename, str(p),
                    file_size, now_str, doc_id
                )
            )
            logger.info("Updated existing handover download record: %s", doc_id)
            return self.get_handover_by_id(doc_id)

        doc_id = f"DOC_{uuid.uuid4().hex[:12].upper()}"
        data = {
            "id": doc_id,
            "session_id": session_id,
            "patient_id": patient_id,
            "patient_name": patient_name or "Anonymous Patient",
            "title": title or f"Clinical Summary — {session_id}",
            "main_symptoms": main_symptoms or "None reported",
            "pain_severity": int(pain_severity) if pain_severity is not None else 0,
            "triage_category": int(triage_category) if triage_category is not None else 3,
            "triage_label": triage_label or "Routine Care",
            "filename": filename,
            "file_path": str(p),
            "file_size": file_size,
            "created_at": now_str,
            "downloaded_at": now_str,
            "format": "PDF",
            "status": "available" if p.exists() else "missing"
        }
        self.db.insert("downloaded_handovers", data)
        self.db.log_audit_event("HANDOVER_DOWNLOAD_SAVED", f"Doc {doc_id} registered for session {session_id}")
        logger.info("Registered new handover download: %s (%s)", doc_id, filename)
        return data

    def get_downloaded_handovers(
        self,
        search_query: Optional[str] = None,
        sort_order: str = "newest",
        patient_id: Optional[int] = None
    ) -> list[dict]:
        """
        Retrieves all registered handover downloads matching optional search and filter.
        Verifies whether file is actually accessible on disk.
        """
        query = "SELECT * FROM downloaded_handovers WHERE 1=1"
        params = []

        if patient_id is not None:
            query += " AND patient_id = ?"
            params.append(patient_id)

        if search_query:
            q_like = f"%{search_query.strip()}%"
            query += """ AND (
                title LIKE ? OR 
                patient_name LIKE ? OR 
                filename LIKE ? OR 
                main_symptoms LIKE ? OR
                triage_label LIKE ? OR
                downloaded_at LIKE ?
            )"""
            params.extend([q_like, q_like, q_like, q_like, q_like, q_like])

        if sort_order == "oldest":
            query += " ORDER BY downloaded_at ASC"
        else:
            query += " ORDER BY downloaded_at DESC"

        rows = self.db.fetchall(query, tuple(params))
        results = []
        for r in rows:
            item = dict(r)
            fpath = Path(item.get("file_path", ""))
            if fpath.exists() and fpath.is_file():
                item["status"] = "available"
                item["file_size"] = fpath.stat().st_size
            else:
                item["status"] = "missing"
            results.append(item)
        return results

    def get_handover_by_id(self, doc_id: str) -> Optional[dict]:
        """Fetches a single handover document record by ID."""
        row = self.db.fetchone("SELECT * FROM downloaded_handovers WHERE id = ?", (doc_id,))
        if not row:
            return None
        item = dict(row)
        fpath = Path(item.get("file_path", ""))
        item["status"] = "available" if fpath.exists() and fpath.is_file() else "missing"
        if fpath.exists():
            item["file_size"] = fpath.stat().st_size
        return item

    def delete_handover(self, doc_id: str, delete_file: bool = True) -> bool:
        """Deletes handover record from database and optionally removes physical file."""
        row = self.db.fetchone("SELECT * FROM downloaded_handovers WHERE id = ?", (doc_id,))
        if not row:
            return False

        file_path = row.get("file_path")
        if delete_file and file_path:
            p = Path(file_path)
            try:
                if p.exists() and p.is_file():
                    p.unlink()
                    logger.info("Deleted physical file: %s", file_path)
            except Exception as exc:
                logger.warning("Could not delete file %s: %s", file_path, exc)

        self.db.execute("DELETE FROM downloaded_handovers WHERE id = ?", (doc_id,))
        self.db.log_audit_event("HANDOVER_DOCUMENT_DELETED", f"Doc {doc_id} deleted")
        return True

    def export_copy(self, doc_id: str, target_dir: str | Path) -> Optional[str]:
        """Exports a copy of the specified handover PDF to destination folder."""
        doc = self.get_handover_by_id(doc_id)
        if not doc or doc.get("status") != "available":
            return None

        src = Path(doc["file_path"])
        dest_dir = Path(target_dir)
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / src.name

        # Ensure no accidental self-overwrite
        if src.resolve() != dest.resolve():
            shutil.copy2(src, dest)
        return str(dest)
