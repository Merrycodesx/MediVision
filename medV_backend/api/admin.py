from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.
from .models import *

# admin.site.register(User)
admin.site.register(Patient)
admin.site.register(Hospital)
admin.site.register(Screening)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    pass
