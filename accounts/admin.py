from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import AppUserCreationForm,AppUserChangeForm
from .models import AppUser


class AppUserAdmin(UserAdmin):
    add_form = AppUserCreationForm
    form = AppUserChangeForm
    model = AppUser

admin.site.register(AppUser,AppUserAdmin)
