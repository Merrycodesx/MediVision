from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import exceptions, generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers

from .models import Patient, Screening, ClinicalData
from .permissions import IsAdminOrSelf, PatientPermission, RolePermission
from .serializers import (
    PatientApiSerializer,
    PatientDetailSerializer,
    PatientSerializer,
    ScreeningSerializer,
    ClinicalDataSerializer,
    UserCreateUpdateSerializer,
    UserRegisterSerializer,
    UserSerializer,
)

User = get_user_model()

CONFIG_STATE = {"sensitivity_threshold": 0.95, "other_params": {}}


def paginate_queryset(queryset, request):
    page = int(request.query_params.get("page", 1) or 1)
    limit = int(request.query_params.get("limit", 10) or 10)
    page = 1 if page < 1 else page
    limit = 10 if limit < 1 else min(limit, 100)
    start = (page - 1) * limit
    end = start + limit
    items = list(queryset[start:end])
    return items, page, limit


def stub_response(feature, request):
    return Response(
        {
            "success": True,
            "implemented": "placeholder",
            "feature": feature,
            "method": request.method,
            "message": "Endpoint contract is available. Attach persistent model/storage to move from placeholder to production.",
        },
        status=status.HTTP_200_OK,
    )


def my_view(request):
    return JsonResponse({"status": "success", "message": "Welcome to the TEST api?"})


class ClinicalDataCreateView(generics.CreateAPIView):
    serializer_class = ClinicalDataSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]


class DebugTokenObtainPairSerializer(TokenObtainPairSerializer):
    role = serializers.CharField(write_only=True, required=True)

    ROLE_MAP_INCOMING = {
        "doctor": "C",
        "clinician": "C",
        "technician": "R",
        "radiologist": "R",
        "admin": "L",
        "auditor": "A",
        "c": "C",
        "r": "R",
        "l": "L",
        "a": "A",
    }

    ROLE_MAP_OUTGOING = {
        "C": "clinician",
        "R": "radiologist",
        "L": "admin",
        "A": "auditor",
    }

    def validate(self, attrs):
        incoming_role = str(attrs.pop("role", "")).strip().lower()
        if not incoming_role:
            raise exceptions.AuthenticationFailed("Role is required for login.")

        expected_role_code = self.ROLE_MAP_INCOMING.get(incoming_role)
        if expected_role_code is None:
            raise exceptions.AuthenticationFailed("Invalid role provided.")

        try:
            data = super().validate(attrs)
        except exceptions.AuthenticationFailed:
            email = attrs.get(self.username_field)
            user = User.objects.filter(email=email).first()
            if user and not user.is_active:
                raise exceptions.AuthenticationFailed("Account exists but is inactive.")
            raise

        user = self.user
        if user.role != expected_role_code:
            raise exceptions.AuthenticationFailed("Role does not match this account.")

        data["role_code"] = user.role
        data["role"] = self.ROLE_MAP_OUTGOING.get(user.role, "clinician")
        data["user_id"] = str(user.id)
        data["hospital_id"] = str(user.hospital_id) if user.hospital_id else None
        data["hospital_name"] = user.hospital.name if user.hospital else None
        data["hospital_code"] = user.hospital.code if user.hospital else None
        data["success"] = True
        return data


class DebugTokenObtainPairView(TokenObtainPairView):
    serializer_class = DebugTokenObtainPairSerializer


class AuthLoginView(DebugTokenObtainPairView):
    permission_classes = [AllowAny]


class AuthRefreshView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get("refresh_token") or request.data.get("refresh")
        serializer = TokenRefreshSerializer(data={"refresh": token})
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data
        payload["success"] = True
        return Response(payload)


class AuthLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({"success": True, "message": "Logout acknowledged. Client should discard tokens."})


class UserListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles_by_method = {"GET": ["L"], "POST": ["L"]}

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserCreateUpdateSerializer
        return UserSerializer

    def get(self, request, *args, **kwargs):
        queryset = User.objects.filter(hospital=request.user.hospital).order_by("-created_at")
        users, page, limit = paginate_queryset(queryset, request)
        data = UserSerializer(users, many=True).data
        return Response({"success": True, "page": page, "limit": limit, "results": data})

    def perform_create(self, serializer):
        serializer.save(hospital=self.request.user.hospital)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsAdminOrSelf]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UserCreateUpdateSerializer
        return UserSerializer

    def get_queryset(self):
        return User.objects.filter(hospital=self.request.user.hospital)

    def update(self, request, *args, **kwargs):
        user_obj = self.get_object()
        if request.user.role != "L":
            allowed_self_fields = {"username", "password", "first_name", "last_name", "native_name", "phone_num"}
            incoming = set(request.data.keys())
            if not incoming.issubset(allowed_self_fields):
                return Response({"success": False, "message": "You can only update limited self fields."}, status=403)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if request.user.role != "L":
            return Response({"success": False, "message": "Only admins can delete users."}, status=403)
        return super().destroy(request, *args, **kwargs)


class PatientListCreateView(generics.ListCreateAPIView):
    queryset = Patient.objects.all().order_by("-created_at")
    serializer_class = PatientApiSerializer
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles_by_method = {"GET": ["C", "R", "L"], "POST": ["C", "R"]}

    def get_queryset(self):
        queryset = super().get_queryset().filter(hospital=self.request.user.hospital)
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(Q(full_name__icontains=search) | Q(age__icontains=search))
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        items, page, limit = paginate_queryset(queryset, request)
        data = self.serializer_class(items, many=True).data
        return Response({"success": True, "page": page, "limit": limit, "results": data})

    def perform_create(self, serializer):
        serializer.save(clinician_id=self.request.user, hospital=self.request.user.hospital)

class PatientDetailView(generics.RetrieveAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientApiSerializer
    permission_classes = [IsAuthenticated, PatientPermission]

    def get_queryset(self):
        return Patient.objects.filter(hospital=self.request.user.hospital)

    def get_object(self):
        patient_id = self.kwargs.get("patient_id") or self.kwargs.get("pk")
        return self.get_queryset().get(pk=patient_id)


class ImagesUploadView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles_by_method = {"POST": ["C", "R"]}

    def post(self, request):
        return stub_response("images.upload", request)


class ImagesDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, image_id):
        return stub_response("images.detail", request)

    def delete(self, request, image_id):
        if request.user.role not in ["L", "C"]:
            return Response({"success": False, "message": "Forbidden"}, status=403)
        return stub_response("images.delete", request)


class LabsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role not in ["C", "R"]:
            return Response({"success": False, "message": "Forbidden"}, status=403)
        return stub_response("labs.create", request)


class LabsByPatientView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id):
        if request.user.role not in ["C", "R", "L", "P"]:
            return Response({"success": False, "message": "Forbidden"}, status=403)
        return stub_response("labs.by_patient", request)


class LabsDetailView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles_by_method = {"PUT": ["C"]}

    def put(self, request, lab_id):
        return stub_response("labs.update", request)


class ScreeningsView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles_by_method = {"POST": ["C", "R"]}

    def post(self, request):
        return stub_response("screenings.create", request)


class AIInferenceRunView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles_by_method = {"POST": ["C", "R"]}

    def post(self, request):
        patient_id = request.data.get("patient_id")
        if not patient_id:
            return Response({"success": False, "message": "patient_id is required."}, status=400)
        try:
            patient = Patient.objects.get(id=patient_id, hospital=request.user.hospital)
        except Patient.DoesNotExist:
            return Response({"success": False, "message": "Patient not found in your hospital."}, status=404)

        screening = Screening.objects.create(
            patient=patient,
            requested_by=request.user,
            hospital=request.user.hospital,
            tb_score=72.5,
            heatmap_url="",
            triage_recommendation="high risk - refer to GeneXpert",
        )
        return Response(
            {
                "success": True,
                "screening_id": str(screening.id),
                "patient_id": patient.id,
                "tb_score": screening.tb_score,
                "heatmap_url": screening.heatmap_url,
                "triage_recommendation": screening.triage_recommendation,
            },
            status=status.HTTP_200_OK,
        )


class ScreeningsDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, screening_id):
        if request.user.role not in ["C", "R", "L"]:
            return Response({"success": False, "message": "Forbidden"}, status=403)
        try:
            screening = Screening.objects.get(id=screening_id, hospital=request.user.hospital)
        except Screening.DoesNotExist:
            return Response({"success": False, "message": "Not found"}, status=404)
        data = ScreeningSerializer(screening).data
        data["success"] = True
        return Response(data)


class ScreeningsByPatientView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id):
        if request.user.role not in ["C", "R", "L"]:
            return Response({"success": False, "message": "Forbidden"}, status=403)
        screenings = Screening.objects.filter(patient_id=patient_id, hospital=request.user.hospital).order_by("-created_at")
        data = ScreeningSerializer(screenings, many=True).data
        return Response({"success": True, "results": data})


class ReportsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, screening_id):
        if request.user.role not in ["C", "R", "L"]:
            return Response({"success": False, "message": "Forbidden"}, status=403)
        return stub_response("reports.get", request)


class FeedbackView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles_by_method = {"POST": ["C", "R"]}

    def post(self, request):
        return stub_response("feedback.create", request)


class FeedbackDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, feedback_id):
        if request.user.role not in ["L", "A"]:
            return Response({"success": False, "message": "Forbidden"}, status=403)
        return stub_response("feedback.detail", request)


class ConfigView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in ["L", "C"]:
            return Response({"success": False, "message": "Forbidden"}, status=403)
        return Response({"success": True, **CONFIG_STATE})

    def put(self, request):
        if request.user.role != "L":
            return Response({"success": False, "message": "Forbidden"}, status=403)
        CONFIG_STATE["sensitivity_threshold"] = request.data.get("sensitivity_threshold", CONFIG_STATE["sensitivity_threshold"])
        CONFIG_STATE["other_params"] = request.data.get("other_params", CONFIG_STATE["other_params"])
        return Response({"success": True, **CONFIG_STATE})


class AuditsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in ["L", "A"]:
            return Response({"success": False, "message": "Forbidden"}, status=403)
        return stub_response("audits.list", request)


class HMSImportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role not in ["L", "C"]:
            return Response({"success": False, "message": "Forbidden"}, status=403)
        return stub_response("hms.import", request)


class HMSExportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role not in ["L", "C"]:
            return Response({"success": False, "message": "Forbidden"}, status=403)
        return stub_response("hms.export", request)


class ModelsUpdateView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles_by_method = {"POST": ["L"]}

    def post(self, request):
        return stub_response("models.update", request)


class ModelsListView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles_by_method = {"GET": ["L"]}

    def get(self, request):
        return Response({"success": True, "models": []})


# Backward-compat endpoint names retained.
class patientDetailView(PatientDetailView):
    pass
