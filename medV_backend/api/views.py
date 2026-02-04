from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.

def my_view(request):
    data = {
            "status": "success",
            "message": "Welcome to the TEST api?",
        }
    return JsonResponse(data)