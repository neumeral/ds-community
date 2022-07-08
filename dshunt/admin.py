from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import AppUserChangeForm, AppUserCreationForm
from .models import (
    AppUser,
    Book,
    Category,
    PodcastEpisode,
    Post,
    PostComment,
    PostVote,
    Tutorial,
    Video,
)


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
