"""Backend smoke test script for seeded MediVision data.

Checks:
- Hospitals exist
- Each hospital has at least 3 employees
- Each hospital has at least 5 patients

Usage:
  cd medV_backend
  python test.py
"""

import os
import sys

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "medV_api.settings")
django.setup()

from api.models import Hospital, Patient, User  # noqa: E402


def run() -> int:
    ok = True

    hospitals = Hospital.objects.all().order_by("name")
    if not hospitals.exists():
        print("FAIL: No hospitals found. Run seed_dummy_data.py first.")
        return 1

    print(f"Found hospitals: {hospitals.count()}")

    for hospital in hospitals:
        users_count = User.objects.filter(hospital=hospital).count()
        patients_count = Patient.objects.filter(hospital=hospital).count()

        if users_count < 3:
            ok = False
            print(f"FAIL: {hospital.code} has only {users_count} employees (expected >= 3)")
        else:
            print(f"PASS: {hospital.code} employees={users_count}")

        if patients_count < 5:
            ok = False
            print(f"FAIL: {hospital.code} has only {patients_count} patients (expected >= 5)")
        else:
            print(f"PASS: {hospital.code} patients={patients_count}")

        mismatched = (
            Patient.objects.filter(hospital=hospital)
            .exclude(clinician_id__hospital=hospital)
            .count()
        )
        if mismatched:
            ok = False
            print(f"FAIL: {hospital.code} has {mismatched} patients linked to clinician in another hospital")
        else:
            print(f"PASS: {hospital.code} patient-clinician hospital links are consistent")

    if ok:
        print("\nAll backend smoke checks passed.")
        return 0

    print("\nSome backend smoke checks failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(run())
