from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import AppUser, Post, Category


class AppUserCreationForm(UserCreationForm):
    
    class Meta:
        model = AppUser
        fields = ['username']


class AppUserChangeForm(UserChangeForm):
    
    class Meta:
        model = AppUser
        fields = ['email',]


class CreatePostForm(forms.ModelForm):
    POST_TYPES = (
                ('Video','video'),
                ('Book','Book'),
                ('Tutorial','Tutorial'),
            )
    post_type = forms.ChoiceField(choices=POST_TYPES)
    
    class Meta:
        model = Post
        exclude = ['submitted_user', 'approved']
