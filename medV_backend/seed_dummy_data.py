"""Seed dummy MediVision data for local development.

Creates Ethiopian-named hospitals and, for each created hospital,
adds 3 employees and 5 patients.

Usage:
  cd medV_backend
  python seed_dummy_data.py
  python seed_dummy_data.py --hospitals 3 --password "ChangeMe123!"
"""

import argparse
import os
import random
from typing import List

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "medV_api.settings")
django.setup()

from api.models import Hospital, Patient, User  # noqa: E402


ETHIOPIAN_HOSPITALS = [
    ("Tikur Anbessa Specialized Hospital", "TASH"),
    ("St. Paul Hospital Millennium Medical College", "SPHMMC"),
    ("Yekatit 12 Hospital Medical College", "Y12H"),
    ("Black Lion Teaching Hospital", "BLTH"),
    ("Adama General Hospital and Medical College", "AGHMC"),
    ("Hawassa University Comprehensive Specialized Hospital", "HUCSH"),
]

_NAMES = [
    "Abebe", "Bekele", "Tadesse", "Mekdes", "Selam", "Hana", "Dawit", "Tigist", "Alemu", "Yared",
    "Biniyam", "Rahel", "Kebede", "Eden", "Natnael", "Samrawit", "Temesgen", "Liya", "Haimanot", "Fitsum",
]

SYMPTOM_POOL = [
    "Cough >2 weeks",
    "Fever",
    "Weight Loss",
    "Night Sweats",
    "Chest Pain",
    "Fatigue",
]


ROLE_TEMPLATE = [
    ("L", "admin"),
    ("C", "clinician"),
    ("R", "radiologist"),
]


def _pick_name(i: int) -> str:
    return _NAMES[i % len(_NAMES)]


def create_or_update_user(
    hospital: Hospital,
    role_code: str,
    role_label: str,
    idx: int,
    password: str,
) -> User:
    base = f"{hospital.code.lower()}_{role_label}_{idx}"
    email = f"{base}@medivision.local"
    username = f"{hospital.code.lower()[:8]}_{role_label}_{idx}"

    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            "username": username[:15],
            "first_name": _pick_name(idx),
            "last_name": "MediVision",
            "native_name": _pick_name(idx + 3),
            "phone_num": f"091{idx:07d}"[:12],
            "role": role_code,
            "hospital": hospital,
            "is_active": True,
        },
    )

    changed = False
    if user.hospital_id != hospital.id:
        user.hospital = hospital
        changed = True
    if user.role != role_code:
        user.role = role_code
        changed = True
    if not user.is_active:
        user.is_active = True
        changed = True

    if created or not user.has_usable_password():
        user.set_password(password)
        changed = True

    if changed:
        user.save()

    return user


def create_patients_for_hospital(hospital: Hospital, clinician: User, count: int) -> int:
    created_count = 0

    for i in range(1, count + 1):
        full_name = f"{_pick_name(i)} {_pick_name(i + 7)}"
        age = random.randint(18, 70)
        sex = random.choice(["M", "F"])
        hiv_status = random.choice([True, False])
        symptoms = random.sample(SYMPTOM_POOL, k=random.randint(2, 4))

        patient, created = Patient.objects.get_or_create(
            full_name=full_name,
            age=age,
            sex=sex,
            clinician_id=clinician,
            defaults={
                "hiv_Status": hiv_status,
                "symptoms": symptoms,
                "hospital": hospital,
            },
        )

        changed = False
        if patient.hospital_id != hospital.id:
            patient.hospital = hospital
            changed = True
        if patient.clinician_id_id != clinician.id:
            patient.clinician_id = clinician
            changed = True

        if changed:
            patient.save()

        if created:
            created_count += 1

    return created_count


def seed(hospital_count: int, password: str, patients_per_hospital: int) -> None:
    if hospital_count < 1:
        raise ValueError("hospital_count must be >= 1")

    if hospital_count > len(ETHIOPIAN_HOSPITALS):
        raise ValueError(
            f"hospital_count={hospital_count} exceeds available Ethiopian hospital templates ({len(ETHIOPIAN_HOSPITALS)})."
        )

    print("Seeding dummy data...")

    total_users = 0
    total_new_patients = 0

    for h_idx, (name, code) in enumerate(ETHIOPIAN_HOSPITALS[:hospital_count], start=1):
        hospital, _ = Hospital.objects.get_or_create(code=code, defaults={"name": name})
        if hospital.name != name:
            hospital.name = name
            hospital.save(update_fields=["name"])

        users: List[User] = []
        for u_idx, (role_code, role_label) in enumerate(ROLE_TEMPLATE, start=1):
            user = create_or_update_user(hospital, role_code, role_label, idx=(h_idx * 10 + u_idx), password=password)
            users.append(user)

        clinician = next((u for u in users if u.role == "C"), users[0])
        new_patients = create_patients_for_hospital(hospital, clinician, patients_per_hospital)

        total_users += len(users)
        total_new_patients += new_patients

        print(
            f"- {hospital.name} ({hospital.code}): ensured 3 employees, added {new_patients}/{patients_per_hospital} new patients"
        )

    print("Done.")
    print(f"Employees ensured: {total_users}")
    print(f"New patients created: {total_new_patients}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed MediVision dummy data.")
    parser.add_argument(
        "--hospitals",
        type=int,
        default=1,
        help="How many Ethiopian hospitals to seed (default: 1).",
    )
    parser.add_argument(
        "--patients-per-hospital",
        type=int,
        default=5,
        help="How many patients per hospital to create (default: 5).",
    )
    parser.add_argument(
        "--password",
        type=str,
        default="ChangeMe123!",
        help="Password used for generated employees.",
    )

    args = parser.parse_args()
    seed(args.hospitals, args.password, args.patients_per_hospital)
