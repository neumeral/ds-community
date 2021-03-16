from django import forms
from django.contrib.auth.forms import UserCreationForm,UserChangeForm as n
from .models import AppUser

class AppUserCreationForm(UserCreationForm):
    
    class Meta:
        model = AppUser
        fields = ['username']


class AppUserChangeForm(n):
    
    class Meta:
        model = AppUser
        fields = ['email',]