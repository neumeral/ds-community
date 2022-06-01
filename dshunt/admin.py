from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import AppUser, Category, Post, PostVote
from .forms import AppUserChangeForm, AppUserCreationForm


class AppUserAdmin(BaseUserAdmin):
    add_form = AppUserCreationForm
    form = AppUserChangeForm
    model = AppUser

admin.site.register(AppUser, AppUserAdmin)

admin.site.register(Category)
admin.site.register(Post)
admin.site.register(PostVote)
