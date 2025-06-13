from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# Customize the User admin
UserAdmin.list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
UserAdmin.list_filter = ('is_staff', 'is_superuser', 'date_joined')

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
