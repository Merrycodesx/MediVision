from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

# Variable must be named 'urlpatterns'
urlpatterns = [
<<<<<<< HEAD
    # Patient management
    path('patients/', views.PatientListCreateView.as_view(), name='patients-list-create'),
    path('patients/<int:pk>/', views.patientDetailView.as_view(), name='patient-detail-legacy'),
    path('patients/<int:patient_id>/', views.PatientDetailView.as_view(), name='patient-detail'),
    path('clinical/', views.ClinicalDataCreateView.as_view(), name='clinical-create'),
    path('auth/register/', views.RegisterView.as_view(), name='auth-register'),
    path('auth/login/', views.AuthLoginView.as_view(), name='auth-login'),
    path('auth/refresh/', views.AuthRefreshView.as_view(), name='auth-refresh'),
    path('auth/logout/', views.AuthLogoutView.as_view(), name='auth-logout'),
    # Backward-compatible JWT routes
    path('auth/token/', views.DebugTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # User management
    path('users/', views.UserListCreateView.as_view(), name='users-list-create'),
    path('users/<uuid:pk>/', views.UserDetailView.as_view(), name='users-detail'),

    # Dedicated AI inference route
    path('inference/run/', views.AIInferenceRunView.as_view(), name='inference-run'),

    # Imaging
    path('images/upload/', views.ImagesUploadView.as_view(), name='images-upload'),
    path('images/<int:image_id>/', views.ImagesDetailView.as_view(), name='images-detail'),

    # Labs
    path('labs/', views.LabsView.as_view(), name='labs-create'),
    path('labs/<int:patient_id>/', views.LabsByPatientView.as_view(), name='labs-by-patient'),
    path('labs/item/<int:lab_id>/', views.LabsDetailView.as_view(), name='labs-update'),

    # Screenings
    path('screenings/', views.ScreeningsView.as_view(), name='screenings-create'),
    path('screenings/<int:screening_id>/', views.ScreeningsDetailView.as_view(), name='screenings-detail'),
    path('screenings/patient/<int:patient_id>/', views.ScreeningsByPatientView.as_view(), name='screenings-by-patient'),

    # Reports
    path('reports/<int:screening_id>/', views.ReportsView.as_view(), name='reports-get'),

    # Feedback
    path('feedback/', views.FeedbackView.as_view(), name='feedback-create'),
    path('feedback/<int:feedback_id>/', views.FeedbackDetailView.as_view(), name='feedback-detail'),

    # Configuration
    path('config/', views.ConfigView.as_view(), name='config'),

    # Audits
    path('audits/', views.AuditsView.as_view(), name='audits-list'),

    # HMS integration
    path('hms/import/', views.HMSImportView.as_view(), name='hms-import'),
    path('hms/export/', views.HMSExportView.as_view(), name='hms-export'),

    # Model management
    path('models/update/', views.ModelsUpdateView.as_view(), name='models-update'),
    path('models/', views.ModelsListView.as_view(), name='models-list'),
=======
    path('test/', views.my_view, name='test_view'),
    path('patients/', views.PatientListCreateView.as_view(), name='patients-list-create'),
    path('patients/<int:pk>/', views.patientDetailView.as_view(), name='patient-detail'),
    path('clinical/', views.ClinicalDataCreateView.as_view(), name='clinical-create'),
    path('auth/register/', views.RegisterView.as_view(), name='auth-register'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
>>>>>>> bf1dbb5 (some update)
]
