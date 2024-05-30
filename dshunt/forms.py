from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import AppUser, UserProfile, Post, Book, Video, Tutorial, PodcastEpisode, PostType
from .models import (Podcast, Channel, PostComment, Collection)


class AppUserCreationForm(UserCreationForm):
    
    class Meta:
        model = AppUser
        fields = ['username']


class AppUserChangeForm(UserChangeForm):
    
    class Meta:
        model = AppUser
        fields = ['email']


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'headline',
            'avatar',
            'website',
            'twitter_profile',
            'github_profile',
            'linkedin',
            'youtube_channel',
        ]


class PostTypeForm(forms.Form):
    post_type = forms.ChoiceField(choices=PostType.choices)


class BookCreateForm(forms.ModelForm):
    author = forms.CharField()
    link = forms.URLField()

    class Meta:
        model = Book
        fields = (
            'category',
            'title',
            'description',
            'author',
            'link',
            'tags'
        )


class VideoCreateForm(forms.ModelForm):
    channel = forms.ModelChoiceField(queryset=Channel.objects.all())
    link = forms.URLField()

    class Meta:
        model = Video
        fields = (
            'category',
            'title',
            'description',
            'link',
            'channel',
            'tags'
        )


class TutorialCreateForm(forms.ModelForm):
    author = forms.CharField()
    link = forms.URLField()

    class Meta:
        model = Tutorial
        fields = (
            'category',
            'title',
            'description',
            'channel',
            'link',
            'author',
            'tags'
        )


class PodcastEpisodeCreateForm(forms.ModelForm):
    podcast = forms.ModelChoiceField(queryset=Podcast.objects.all())
    link = forms.URLField()

    class Meta:
        model = PodcastEpisode
        fields = (
            'category',
            'title',
            'description',
            'link',
            'tags',
            'podcast'
        )


class CommentForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={'cols': 50, 'rows': 3}))

    class Meta:
        model = PostComment
        fields = (
            'content',
        )


class CollectionForm(forms.ModelForm):

    class Meta:
        model = Collection
        fields = (
            'title',
            'description',
            'posts',
            'is_staffpick',
            'is_public'
        )

    def clean_title(self):
        title = self.cleaned_data.get('title')
        cols = Collection.objects.filter(title__iexact=title).select_related()
        if cols.exists():
            raise forms.ValidationError("Title already exists")
        return title


class AddtoCollectionForm(forms.Form):
    post = forms.ModelChoiceField(queryset=Post.objects.filter(approved=True))


class CollectionListForm(forms.Form):
    collection = forms.ModelChoiceField(queryset=Collection.objects.all())
