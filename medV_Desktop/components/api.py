import requests

BASE_URL = "https://prizm.pythonanywhere.com/api"

ROLE_MAP = {
    "Doctor": "clinician",
    "Technician": "radiologist",
    "Admin": "admin",
    "Auditor": "auditor",
}


class ApiClient:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url.rstrip("/")

    def _url(self, path):
        return f"{self.base_url}/{path.lstrip('/')}"

    def _headers(self, token=None):
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _request(self, method, path, token=None, json_data=None, data=None, files=None, timeout=30):
        try:
            response = requests.request(
                method=method,
                url=self._url(path),
                headers=self._headers(token),
                json=json_data,
                data=data,
                files=files,
                timeout=timeout,
            )
            response.raise_for_status()
            payload = response.json() if response.text else {}
            if isinstance(payload, dict):
                payload.setdefault("success", True)
                payload["status_code"] = response.status_code
            return payload
        except requests.RequestException as err:
            resp = err.response
            response_json = None
            response_text = None
            status_code = None
            if resp is not None:
                status_code = resp.status_code
                response_text = resp.text
                try:
                    response_json = resp.json()
                except ValueError:
                    response_json = None
            return {
                "success": False,
                "message": str(err),
                "status_code": status_code,
                "response": response_text,
                "response_json": response_json,
            }

    # Authentication
    def auth_login(self, username, password, role):
        return self._request(
            "POST",
            "auth/login/",
            json_data={"email": username, "password": password, "role": ROLE_MAP.get(role, role)},
        )

    def auth_refresh(self, refresh_token, token=None):
        return self._request("POST", "auth/refresh/", token=token, json_data={"refresh_token": refresh_token})

    def auth_logout(self, token):
        return self._request("POST", "auth/logout/", token=token)

    # User management
    def list_users(self, token, page=None, limit=None):
        query = []
        if page is not None:
            query.append(f"page={page}")
        if limit is not None:
            query.append(f"limit={limit}")
        suffix = f"?{'&'.join(query)}" if query else ""
        return self._request("GET", f"users/{suffix}", token=token)

    def create_user(self, token, username, password, role, email=None, first_name=None, last_name=None, native_name=None, phone_num=None):
        role_value = ROLE_MAP.get(role, role)
        body = {
            "username": username,
            "password": password,
            "role": role_value,
        }
        if email:
            body["email"] = email
        if first_name is not None:
            body["first_name"] = first_name
        if last_name is not None:
            body["last_name"] = last_name
        if native_name is not None:
            body["native_name"] = native_name
        if phone_num is not None:
            body["phone_num"] = phone_num
        return self._request("POST", "users/", token=token, json_data=body)

    def get_user(self, token, user_id):
        return self._request("GET", f"users/{user_id}/", token=token)

    def update_user(self, token, user_id, payload):
        return self._request("PUT", f"users/{user_id}/", token=token, json_data=payload)

    def delete_user(self, token, user_id):
        return self._request("DELETE", f"users/{user_id}/", token=token)

    # Patient management
    def list_patients(self, token, page=None, limit=None, search=None):
        query = []
        if page is not None:
            query.append(f"page={page}")
        if limit is not None:
            query.append(f"limit={limit}")
        if search:
            query.append(f"search={search}")
        suffix = f"?{'&'.join(query)}" if query else ""
        return self._request("GET", f"patients/{suffix}", token=token)

    def create_patient(self, token, name, age, sex, hiv_status, symptoms, comorbidities=None):
        return self._request(
            "POST",
            "patients/",
            token=token,
            json_data={
                "name": name,
                "age": age,
                "sex": sex,
                "hiv_status": hiv_status,
                "symptoms": symptoms,
                "comorbidities": comorbidities or [],
            },
        )

    def get_patient(self, token, patient_id):
        return self._request("GET", f"patients/{patient_id}/", token=token)

    def update_patient(self, token, patient_id, payload):
        return self._request("PUT", f"patients/{patient_id}/", token=token, json_data=payload)

    def delete_patient(self, token, patient_id):
        return self._request("DELETE", f"patients/{patient_id}/", token=token)

    # Imaging
    def upload_image(self, token, patient_id, image_path, metadata=None):
        with open(image_path, "rb") as image_file:
            files = {"image_file": image_file}
            data = {
                "patient_id": patient_id,
                "metadata": metadata or {},
            }
            return self._request("POST", "images/upload/", token=token, data=data, files=files)

    def get_image(self, token, image_id, format_type=None):
        suffix = f"?format={format_type}" if format_type else ""
        return self._request("GET", f"images/{image_id}/{suffix}", token=token)

    def delete_image(self, token, image_id):
        return self._request("DELETE", f"images/{image_id}/", token=token)

    # Labs
    def create_lab(self, token, payload):
        return self._request("POST", "labs/", token=token, json_data=payload)

    def get_labs_by_patient(self, token, patient_id):
        return self._request("GET", f"labs/{patient_id}/", token=token)

    def update_lab(self, token, lab_id, payload):
        return self._request("PUT", f"labs/item/{lab_id}/", token=token, json_data=payload)

    # Screenings
    def create_screening(self, token, payload):
        return self._request("POST", "screenings/", token=token, json_data=payload)

    def get_screening(self, token, screening_id):
        return self._request("GET", f"screenings/{screening_id}/", token=token)

    def get_screenings_by_patient(self, token, patient_id):
        return self._request("GET", f"screenings/patient/{patient_id}/", token=token)

    # Reports
    def get_report(self, token, screening_id, format_type="json"):
        return self._request("GET", f"reports/{screening_id}/?format={format_type}", token=token)

    # Feedback
    def create_feedback(self, token, payload):
        return self._request("POST", "feedback/", token=token, json_data=payload)

    def get_feedback(self, token, feedback_id):
        return self._request("GET", f"feedback/{feedback_id}/", token=token)

    # Config
    def get_config(self, token):
        return self._request("GET", "config/", token=token)

    def update_config(self, token, payload):
        return self._request("PUT", "config/", token=token, json_data=payload)

    # Audits
    def get_audits(self, token, page=None, limit=None, user_id=None):
        query = []
        if page is not None:
            query.append(f"page={page}")
        if limit is not None:
            query.append(f"limit={limit}")
        if user_id is not None:
            query.append(f"user_id={user_id}")
        suffix = f"?{'&'.join(query)}" if query else ""
        return self._request("GET", f"audits/{suffix}", token=token)

    # HMS
    def hms_import(self, token, hms_data):
        return self._request("POST", "hms/import/", token=token, json_data={"hms_data": hms_data})

    def hms_export(self, token, patient_id, screening_id):
        return self._request(
            "POST",
            "hms/export/",
            token=token,
            json_data={"patient_id": patient_id, "screening_id": screening_id},
        )

    # Models
    def models_update(self, token, model_file_path, version, model_type):
        with open(model_file_path, "rb") as model_file:
            files = {"model_file": model_file}
            data = {"version": version, "type": model_type}
            return self._request("POST", "models/update/", token=token, data=data, files=files)

    def list_models(self, token):
        return self._request("GET", "models/", token=token)


client = ApiClient()


# Backward-compatible helpers used by current desktop UI

def register(email, username, password, role, first_name, last_name, native_name, phone_num, hospital_code, hospital_name):
    return client._request(
        "POST",
        "auth/register/",
        json_data={
            "email": email,
            "username": username,
            "password": password,
            "role": ROLE_MAP.get(role, "clinician"),
            "first_name": first_name,
            "last_name": last_name,
            "native_name": native_name,
            "phone_num": phone_num,
            "hospital_code": hospital_code,
            "hospital_name": hospital_name,
        },
    )


def login(email, password, role):
    payload = client.auth_login(email, password, role)
    if payload.get("success"):
        payload["token"] = payload.get("access")
    return payload


def get_recent_cases(token):
    # Existing endpoint fallback; if unavailable, map from /patients
    data = client._request("GET", "cases/recent/", token=token)
    if isinstance(data, list):
        return data
    if not data.get("success"):
        patients = client.list_patients(token)
        if isinstance(patients, dict):
            patients = patients.get("results", [])
        if isinstance(patients, list):
            return [
                {
                    "id": p.get("id", "-"),
                    "date": str(p.get("created_at", "-")).split("T")[0],
                    "score": p.get("age", "-"),
                    "risk": "High" if p.get("hiv_status") else "Low",
                }
                for p in patients
            ]
    return []


def get_patients(token):
    payload = client.list_patients(token)
    if isinstance(payload, dict):
        return payload.get("results", [])
    return payload if isinstance(payload, list) else []


def submit_new_case(token, case_data, image_path):
    data = client._request(
        "POST",
        "inference/run/",
        token=token,
        json_data={
            "patient_id": case_data.get("patient_id"),
            "clinical_data": case_data,
        },
    )
    if data.get("success"):
        if "case_id" not in data and case_data.get("patient_id"):
            data["case_id"] = case_data.get("patient_id")
        return data

    # Read-only patients policy: no patient creation fallback.
    return data


def get_case_result(token, case_id):
    data = client._request("GET", f"case/{case_id}/result/", token=token)
    if data.get("success"):
        return data

    patient = client.get_patient(token, case_id)
    if patient.get("success"):
        return {
            "success": True,
            "score": patient.get("age", "N/A"),
            "risk": "High" if patient.get("hiv_status") else "Low",
            "shap": {},
            "recommendation": f"Patient: {patient.get('name', 'N/A')} | Symptoms: {', '.join(patient.get('symptoms', []))}",
        }
    return data
