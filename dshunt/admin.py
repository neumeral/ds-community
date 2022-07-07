from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import AppUser, Category, Post, PostVote, Book, Video, Tutorial, PodcastEpisode, PostComment
from .forms import AppUserChangeForm, AppUserCreationForm


class AppUserAdmin(BaseUserAdmin):
    add_form = AppUserCreationForm
    form = AppUserChangeForm
    model = AppUser

admin.site.register(AppUser, AppUserAdmin)

admin.site.register(Category)
admin.site.register(Post)
admin.site.register(PostVote)
admin.site.register(PostComment)
admin.site.register(Book)
admin.site.register(Video)
admin.site.register(Tutorial)
admin.site.register(PodcastEpisode)
