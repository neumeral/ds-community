from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import AppUserChangeForm, AppUserCreationForm
from .models import (
    AppUser,
    Book,
    Category,
    Challenges,
    Collection,
    PodcastEpisode,
    Post,
    PostComment,
    PostVote,
    Tutorial,
    UserProfile,
    Video,
)


class AppUserAdmin(BaseUserAdmin):
    add_form = AppUserCreationForm
    form = AppUserChangeForm
    model = AppUser


admin.site.register(AppUser, AppUserAdmin)
admin.site.register(UserProfile)

admin.site.register(Category)

admin.site.register(Challenges)


admin.site.register(Post)
admin.site.register(PostVote)
admin.site.register(PostComment)
admin.site.register(Book)
admin.site.register(Video)
admin.site.register(Tutorial)
admin.site.register(PodcastEpisode)

admin.site.register(Collection)
