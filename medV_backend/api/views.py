from django.http import JsonResponse
from .serializers import PatientSerializer, PatientDetailSerializer, UserRegisterSerializer
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
    serializer_class = PatientSerializer
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


class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]