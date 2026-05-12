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

from .models import Patient, Screening
from .models import Hospital, Patient, Screening, ClinicalData, ImageRecord, LabResult, Feedback, AuditLog
from .permissions import IsAdminOrSelf, PatientPermission, RolePermission
from .serializers import (
    AuditSerializer,
    FeedbackSerializer,
    ImageSerializer,
    LabResultSerializer,
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
AI_ENGINE = None


def get_ai_engine():
    global AI_ENGINE
    if AI_ENGINE is None:
        try:
            from inference.engine import TBInferenceEngine
        except ImportError:
            return None
        AI_ENGINE = TBInferenceEngine()
        AI_ENGINE.load_models()
    return AI_ENGINE


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    return Response({
        "message": "MediVision API",
        "version": "1.0",
        "endpoints": {
            "auth": {
                "register": "/api/auth/register/",
                "login": "/api/auth/login/",
                "token": "/api/auth/token/",
                "refresh": "/api/auth/refresh/",
                "logout": "/api/auth/logout/"
            },
            "patients": "/api/patients/",
            "users": "/api/users/",
            "inference": "/api/inference/run/",
            "images": "/api/images/upload/",
            "labs": "/api/labs/",
            "screenings": "/api/screenings/",
            "reports": "/api/reports/<screening_id>/",
            "feedback": "/api/feedback/",
            "config": "/api/config/",
            "audits": "/api/audits/",
            "hms": {
                "import": "/api/hms/import/",
                "export": "/api/hms/export/"
            },
            "models": "/api/models/"
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def api_auth_root(request):
    return Response({
        "message": "Django REST Framework Authentication",
        "login": "/api-auth/login/",
        "logout": "/api-auth/logout/"
    })


def paginate_queryset(queryset, request):
    page = int(request.query_params.get("page", 1) or 1)
    limit = int(request.query_params.get("limit", 10) or 10)
    page = 1 if page < 1 else page
    limit = 10 if limit < 1 else min(limit, 100)
    start = (page - 1) * limit
    end = start + limit
    items = list(queryset[start:end])
    return items, page, limit


def create_audit(user, action, target_type="", target_id="", details=""):
    AuditLog.objects.create(
        user=user,
        action=action,
        target_type=target_type,
        target_id=str(target_id),
        details=details,
    )


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
from .serializers import PatientSerializer, PatientDetailSerializer, UserRegisterSerializer, ClinicalDataSerializer
from .models import Patient
from rest_framework import generics
from .permissions import PatientPermission
from rest_framework.permissions import AllowAny, IsAuthenticated

def my_view(request):
    data = {
            "status": "success",
            "message": "Welcome to the TEST api?",
        }
    return JsonResponse(data)


class PatientListCreateView(generics.ListCreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientApiSerializer
    permission_classes = [IsAuthenticated, PatientPermission]


    def perform_create(self, serializer):
        serializer.save(clinician_id=self.request.user)

class patientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientDetailSerializer
    permission_classes = [IsAuthenticated, PatientPermission]

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()


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
        serializer = ImageSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            image = serializer.save(uploaded_by=request.user, hospital=request.user.hospital)
            create_audit(request.user, "upload_image", "ImageRecord", image.id, f"patient={image.patient.id}")
            return Response({"success": True, "image": ImageSerializer(image).data})
        return Response({"success": False, "errors": serializer.errors}, status=400)


class ImagesDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, image_id):
        try:
            image = ImageRecord.objects.get(id=image_id, hospital=request.user.hospital)
        except ImageRecord.DoesNotExist:
            return Response({"success": False, "message": "Not found"}, status=404)
        data = ImageSerializer(image).data
        return Response({"success": True, "image": data})

    def delete(self, request, image_id):
        if request.user.role not in ["L", "C"]:
            return Response({"success": False, "message": "Forbidden"}, status=403)
        try:
            image = ImageRecord.objects.get(id=image_id, hospital=request.user.hospital)
        except ImageRecord.DoesNotExist:
            return Response({"success": False, "message": "Not found"}, status=404)
        image.delete()
        create_audit(request.user, "delete_image", "ImageRecord", image_id, "deleted image metadata")
        return Response({"success": True, "message": "Image metadata deleted."})


class LabsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role not in ["C", "R"]:
            return Response({"success": False, "message": "Forbidden"}, status=403)
        serializer = LabResultSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            lab = serializer.save()
            create_audit(request.user, "create_lab", "LabResult", lab.id, f"patient={lab.patient.id}")
            return Response({"success": True, "lab": LabResultSerializer(lab).data})
        return Response({"success": False, "errors": serializer.errors}, status=400)


class LabsByPatientView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id):
        if request.user.role not in ["C", "R", "L"]:
            return Response({"success": False, "message": "Forbidden"}, status=403)
        labs = LabResult.objects.filter(patient_id=patient_id, patient__hospital=request.user.hospital).order_by("-created_at")
        data = LabResultSerializer(labs, many=True).data
        return Response({"success": True, "results": data})


class LabsDetailView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles_by_method = {"PUT": ["C"]}

    def put(self, request, lab_id):
        try:
            lab = LabResult.objects.get(id=lab_id, patient__hospital=request.user.hospital)
        except LabResult.DoesNotExist:
            return Response({"success": False, "message": "Not found"}, status=404)
        serializer = LabResultSerializer(lab, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            updated = serializer.save()
            create_audit(request.user, "update_lab", "LabResult", updated.id, f"patient={updated.patient.id}")
            return Response({"success": True, "lab": LabResultSerializer(updated).data})
        return Response({"success": False, "errors": serializer.errors}, status=400)


class ScreeningsView(APIView):
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

        image_path = request.data.get("image_path")
        age = request.data.get("age")
        sex = request.data.get("sex")
        tb_score = request.data.get("tb_score")
        triage_recommendation = request.data.get("triage_recommendation", "")
        heatmap_url = request.data.get("heatmap_url", "")

        if tb_score is None:
            engine = get_ai_engine()
            normalized_sex = None
            if sex:
                sex_raw = str(sex).strip().lower()
                if sex_raw in ["m", "male"]:
                    normalized_sex = "M"
                elif sex_raw in ["f", "female"]:
                    normalized_sex = "F"
            if engine is not None and engine.loaded:
                result = engine.predict(image_path=image_path, age=age, sex=normalized_sex)
                if "error" not in result:
                    tb_score = result["tb_score"]
                    triage_recommendation = result["triage_recommendation"]
                    heatmap_url = heatmap_url or ""
                else:
                    return Response({"success": False, "message": result["error"]}, status=400)
            else:
                return Response({"success": False, "message": "AI models not available; provide tb_score."}, status=503)

        screening = Screening.objects.create(
            patient=patient,
            requested_by=request.user,
            hospital=request.user.hospital,
            tb_score=tb_score,
            heatmap_url=heatmap_url,
            triage_recommendation=triage_recommendation,
        )
        create_audit(request.user, "create_screening", "Screening", screening.id, f"patient={patient.id}")
        return Response({"success": True, "screening": ScreeningSerializer(screening).data})


class AIInferenceRunView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles_by_method = {"POST": ["C", "R"]}

    def post(self, request):
        patient_id = request.data.get("patient_id")
        image_path = request.data.get("image_path")
        age = request.data.get("age")
        sex = request.data.get("sex")

        if not patient_id:
            return Response({"success": False, "message": "patient_id is required."}, status=400)
        try:
            patient = Patient.objects.get(id=patient_id, hospital=request.user.hospital)
        except Patient.DoesNotExist:
            return Response({"success": False, "message": "Patient not found in your hospital."}, status=404)

        sex_normalized = None
        if sex:
            sex_raw = str(sex).strip().lower()
            if sex_raw in ["m", "male"]:
                sex_normalized = "M"
            elif sex_raw in ["f", "female"]:
                sex_normalized = "F"

        modality = "tabular"
        if image_path and age is not None and sex_normalized:
            modality = "fusion"
        elif image_path:
            modality = "image"

        tb_score = 72.5
        image_prob = None
        tabular_prob = None
        triage_recommendation = "high risk - refer to GeneXpert"
        model_source = "fallback"
        engine = get_ai_engine()
        if engine is not None and engine.loaded:
            try:
                result = engine.predict(image_path=image_path, age=age, sex=sex_normalized)
                if "error" not in result:
                    tb_score = result["tb_score"]
                    image_prob = result.get("image_prob")
                    tabular_prob = result.get("tabular_prob")
                    triage_recommendation = result["triage_recommendation"]
                    model_source = "medi_ai"
                else:
                    triage_recommendation = "Fallback recommendation due to missing inputs"
            except Exception:
                triage_recommendation = "Fallback recommendation due to inference error"
        else:
            triage_recommendation = "Fallback recommendation while AI models are unavailable"

        screening = Screening.objects.create(
            patient=patient,
            requested_by=request.user,
            hospital=request.user.hospital,
            tb_score=tb_score,
            heatmap_url="",
            triage_recommendation=triage_recommendation,
        )
        create_audit(request.user, "run_inference", "Screening", screening.id, f"modality={modality}")
        payload = {
            "success": True,
            "screening_id": str(screening.id),
            "patient_id": patient.id,
            "tb_score": screening.tb_score,
            "image_prob": image_prob,
            "tabular_prob": tabular_prob,
            "heatmap_url": screening.heatmap_url,
            "triage_recommendation": screening.triage_recommendation,
            "input_modality": modality,
            "model_source": model_source,
        }
        if model_source != "medi_ai":
            payload["message"] = "AI models are not loaded; returning fallback results."
        return Response(payload, status=status.HTTP_200_OK)


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
        data["labs"] = LabResultSerializer(screening.patient.lab_results.all(), many=True).data
        data["images"] = ImageSerializer(screening.patient.images.all(), many=True).data
        data["feedback"] = FeedbackSerializer(screening.feedbacks.all(), many=True).data
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
        try:
            screening = Screening.objects.get(id=screening_id, hospital=request.user.hospital)
        except Screening.DoesNotExist:
            return Response({"success": False, "message": "Not found"}, status=404)

        clinical_data = getattr(screening.patient, 'clinical_data', None)
        report = {
            "screening": ScreeningSerializer(screening).data,
            "patient": PatientApiSerializer(screening.patient).data,
            "clinical_data": ClinicalDataSerializer(clinical_data).data if clinical_data is not None else None,
            "lab_results": LabResultSerializer(screening.patient.lab_results.all(), many=True).data,
            "images": ImageSerializer(screening.patient.images.all(), many=True).data,
            "feedback": FeedbackSerializer(screening.feedbacks.all(), many=True).data,
        }
        return Response({"success": True, "report": report})


class FeedbackView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles_by_method = {"POST": ["C", "R"]}

    def post(self, request):
        serializer = FeedbackSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            feedback = serializer.save()
            create_audit(request.user, "create_feedback", "Feedback", feedback.id, f"screening={feedback.screening.id}")
            return Response({"success": True, "feedback": FeedbackSerializer(feedback).data})
        return Response({"success": False, "errors": serializer.errors}, status=400)


class FeedbackDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, feedback_id):
        if request.user.role not in ["L", "A"]:
            return Response({"success": False, "message": "Forbidden"}, status=403)
        try:
            feedback = Feedback.objects.get(id=feedback_id, screening__hospital=request.user.hospital)
        except Feedback.DoesNotExist:
            return Response({"success": False, "message": "Not found"}, status=404)
        return Response({"success": True, "feedback": FeedbackSerializer(feedback).data})


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
        audits = AuditLog.objects.select_related('user').order_by('-created_at')[:50]
        data = AuditSerializer(audits, many=True).data
        return Response({"success": True, "results": data})


class HMSImportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role not in ["L", "C"]:
            return Response({"success": False, "message": "Forbidden"}, status=403)
        create_audit(request.user, "hms_import", "HMS", "", "Imported HMS data")
        return Response({"success": True, "message": "HMS import completed."})


class HMSExportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role not in ["L", "C"]:
            return Response({"success": False, "message": "Forbidden"}, status=403)
        create_audit(request.user, "hms_export", "HMS", "", "Exported HMS data")
        return Response({"success": True, "message": "HMS export completed."})


class ModelsUpdateView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles_by_method = {"POST": ["L"]}

    def post(self, request):
        engine = get_ai_engine()
        if engine is None:
            return Response({"success": False, "message": "AI backend unavailable."}, status=503)

        engine.load_models()
        ready = any([engine.cnn_model is not None, engine.xgb_model is not None, engine.fusion_model is not None, engine.scaler is not None])
        return Response({"success": True, "models_loaded": ready})


class ModelsListView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles_by_method = {"GET": ["L"]}

    def get(self, request):
        engine = get_ai_engine()
        if engine is None:
            return Response({"success": True, "models": [], "loaded": False})

        return Response(
            {
                "success": True,
                "loaded": engine.loaded,
                "models": [
                    {"name": "cnn", "loaded": engine.cnn_model is not None},
                    {"name": "xgboost", "loaded": engine.xgb_model is not None},
                    {"name": "fusion", "loaded": engine.fusion_model is not None},
                    {"name": "scaler", "loaded": engine.scaler is not None},
                ],
            }
        )


# Backward-compat endpoint names retained.
class patientDetailView(PatientDetailView):
    pass
    permission_classes = [AllowAny]
