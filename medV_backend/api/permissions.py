from rest_framework.permissions import BasePermission

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
        if request.method == 'GET':
            if user.role in ['C', 'R']:
                return True
            if hasattr(obj, 'user') and user == obj.user:  
                return True
            return False
        elif request.method in ['PUT', 'PATCH']:
            return user.role in ['C', 'R']
        elif request.method == 'DELETE':
            return user.role == 'L'
        return False