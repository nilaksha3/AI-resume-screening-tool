from django.contrib import admin
from .models import CustomUser  # Adjust the import based on your project

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')  # Ensure 'role' is listed
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email')

admin.site.register(CustomUser, CustomUserAdmin)
