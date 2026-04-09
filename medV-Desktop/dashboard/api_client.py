"""
MediVision – Centralized API Client
====================================
All backend REST calls are routed through this module.

• AuthStore  – In-memory session store (token, username, role).
• APIClient  – Synchronous requests wrapper (call from ApiWorker thread).
• ApiWorker  – QThread that executes any API call off the main thread,
               emitting success / failure / no_auth signals.
"""

import requests
from PyQt6.QtCore import QThread, pyqtSignal

# ─── Base URL ────────────────────────────────────────────────────────────────
BASE_URL        = "https://prizm.pythonanywhere.com"
REQUEST_TIMEOUT = 20   # seconds


# ─────────────────────────────────────────────────────────────────────────────
# In-memory session store
# ─────────────────────────────────────────────────────────────────────────────
class AuthStore:
    """Holds the current JWT token and basic user info after login."""
    token:    str = ""
    username: str = ""
    role:     str = ""

    @classmethod
    def clear(cls) -> None:
        cls.token    = ""
        cls.username = ""
        cls.role     = ""

    @classmethod
    def is_authenticated(cls) -> bool:
        return bool(cls.token)


# ─────────────────────────────────────────────────────────────────────────────
# Synchronous API wrapper  (always call from inside ApiWorker.run)
# ─────────────────────────────────────────────────────────────────────────────
class APIClient:
    _BASE = BASE_URL

    # ── Auth ──────────────────────────────────────────────────────────────────
    @classmethod
    def login(cls, email: str, password: str, role: str) -> requests.Response:
        """POST /api/auth/login/  →  { access, refresh, user }"""
        return requests.post(
            f"{cls._BASE}/api/auth/login/",
            json={"email": email, "password": password, "role": role},
            timeout=REQUEST_TIMEOUT,
        )

    @classmethod
    def register(cls, data: dict) -> requests.Response:
        """POST /api/auth/register/"""
        return requests.post(
            f"{cls._BASE}/api/auth/register/",
            json=data,
            timeout=REQUEST_TIMEOUT,
        )

    # ── Patients ──────────────────────────────────────────────────────────────
    @classmethod
    def get_patients(cls) -> requests.Response:
        """GET /api/patients/"""
        return requests.get(
            f"{cls._BASE}/api/patients/",
            headers=cls._auth_headers(),
            timeout=REQUEST_TIMEOUT,
        )

    @classmethod
    def create_patient(cls, data: dict) -> requests.Response:
        """POST /api/patients/"""
        return requests.post(
            f"{cls._BASE}/api/patients/",
            json=data,
            headers=cls._auth_headers(),
            timeout=REQUEST_TIMEOUT,
        )

    # ── Inference ─────────────────────────────────────────────────────────────
    @classmethod
    def run_inference(cls, patient_id: str, image_path: str = "") -> requests.Response:
        """POST /api/inference/run/  →  { tb_score, risk_level, heatmap_url }"""
        return requests.post(
            f"{cls._BASE}/api/inference/run/",
            json={"patient_id": patient_id, "image_path": image_path},
            headers=cls._auth_headers(),
            timeout=REQUEST_TIMEOUT,
        )

    @classmethod
    def submit_feedback(cls, patient_id: str, status: str) -> requests.Response:
        """POST /api/inference/feedback/  status ∈ {approved, rejected}"""
        return requests.post(
            f"{cls._BASE}/api/inference/feedback/",
            json={"patient_id": patient_id, "status": status},
            headers=cls._auth_headers(),
            timeout=REQUEST_TIMEOUT,
        )

    # ── Lab Records ───────────────────────────────────────────────────────────
    @classmethod
    def get_lab_records(cls) -> requests.Response:
        """GET /api/lab-records/"""
        return requests.get(
            f"{cls._BASE}/api/lab-records/",
            headers=cls._auth_headers(),
            timeout=REQUEST_TIMEOUT,
        )

    @classmethod
    def create_lab_record(cls, data: dict) -> requests.Response:
        """POST /api/lab-records/"""
        return requests.post(
            f"{cls._BASE}/api/lab-records/",
            json=data,
            headers=cls._auth_headers(),
            timeout=REQUEST_TIMEOUT,
        )

    # ── Uploads ───────────────────────────────────────────────────────────────
    @classmethod
    def upload_xray(cls, patient_id: str, file_path: str) -> requests.Response:
        """POST /api/uploads/xray/  (multipart)"""
        with open(file_path, "rb") as fh:
            return requests.post(
                f"{cls._BASE}/api/uploads/xray/",
                files={"file": fh},
                data={"patient_id": patient_id},
                headers={"Authorization": f"Bearer {AuthStore.token}"},
                timeout=60,
            )

    # ── Reports ───────────────────────────────────────────────────────────────
    @classmethod
    def get_reports(cls) -> requests.Response:
        """GET /api/reports/"""
        return requests.get(
            f"{cls._BASE}/api/reports/",
            headers=cls._auth_headers(),
            timeout=REQUEST_TIMEOUT,
        )

    # ── System / Admin ────────────────────────────────────────────────────────
    @classmethod
    def get_system_logs(cls) -> requests.Response:
        return requests.get(
            f"{cls._BASE}/api/admin/logs/",
            headers=cls._auth_headers(),
            timeout=REQUEST_TIMEOUT,
        )

    @classmethod
    def get_users(cls) -> requests.Response:
        return requests.get(
            f"{cls._BASE}/api/admin/users/",
            headers=cls._auth_headers(),
            timeout=REQUEST_TIMEOUT,
        )

    @classmethod
    def create_user(cls, data: dict) -> requests.Response:
        return requests.post(
            f"{cls._BASE}/api/admin/users/",
            json=data,
            headers=cls._auth_headers(),
            timeout=REQUEST_TIMEOUT,
        )

    # ── Internal ──────────────────────────────────────────────────────────────
    @classmethod
    def _auth_headers(cls) -> dict:
        headers = {"Content-Type": "application/json"}
        if AuthStore.token:
            headers["Authorization"] = f"Bearer {AuthStore.token}"
        return headers


# ─────────────────────────────────────────────────────────────────────────────
# Non-blocking QThread Worker
# ─────────────────────────────────────────────────────────────────────────────
class ApiWorker(QThread):
    """
    Runs any APIClient method in a background thread.

    Usage
    -----
    worker = ApiWorker(APIClient.get_patients)
    worker.success.connect(self._on_patients)
    worker.failure.connect(self._on_error)
    worker.no_auth.connect(self._redirect_to_login)
    worker.start()

    # Keep a reference so the GC doesn't collect it:
    self._worker = worker
    """

    success = pyqtSignal(object)  # requests.Response on HTTP success
    failure = pyqtSignal(str)     # Human-readable error string
    no_auth = pyqtSignal()        # Emitted on HTTP 401

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self._fn     = fn
        self._args   = args
        self._kwargs = kwargs

    def run(self) -> None:
        try:
            resp = self._fn(*self._args, **self._kwargs)
            if resp.status_code == 401:
                AuthStore.clear()
                self.no_auth.emit()
            else:
                self.success.emit(resp)
        except requests.exceptions.ConnectionError:
            self.failure.emit(
                "Cannot reach the server.\nCheck your network connection."
            )
        except requests.exceptions.Timeout:
            self.failure.emit(
                "Request timed out.\nThe server is taking too long to respond."
            )
        except Exception as exc:
            self.failure.emit(f"Unexpected error: {exc}")
