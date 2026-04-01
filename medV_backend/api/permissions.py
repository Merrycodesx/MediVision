from rest_framework.permissions import BasePermission


ROLE_CODE_MAP = {
    "doctor": "C",
    "clinician": "C",
    "c": "C",
    "technician": "R",
    "radiologist": "R",
    "r": "R",
    "admin": "L",
    "l": "L",
    "auditor": "A",
    "a": "A",
}


def normalize_role(role_value):
    value = str(role_value or "").strip().lower()
    return ROLE_CODE_MAP.get(value, str(role_value or "").strip())


class RolePermission(BasePermission):
    """
    View can define allowed_roles_by_method = {"GET": ["L"], "POST": ["L"]}
    where roles are codes from User.role.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        allowed = getattr(view, "allowed_roles_by_method", {}).get(request.method)
        if allowed is None:
            return True
        normalized_allowed = {normalize_role(role) for role in allowed}
        return normalize_role(user.role) in normalized_allowed


class IsAdminOrSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return normalize_role(user.role) == "L" or obj == user

class PatientPermission(BasePermission):
    """
    Custom permission for Patient detail views:
    - GET: Allowed for clinicians, radiologists, the patient themselves, and admins.
    - PUT/PATCH: Allowed for clinicians and radiologists.
    - DELETE: Allowed only for admins.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if hasattr(obj, 'hospital') and user.hospital_id and obj.hospital_id != user.hospital_id:
            return False
        role = normalize_role(user.role)
        if request.method == 'GET':
            return role in ['C', 'R', 'L']
        if request.method in ['PUT', 'PATCH']:
            return role in ['C', 'R']
        if request.method == 'DELETE':
            return role == 'L'
        return role in ['C', 'R', 'L']