from django.urls import path
from . import views

# Variable must be named 'urlpatterns'
urlpatterns = [
    path('test/', views.my_view, name='test_view'),
]
