from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse

from .choices import POST_TYPES

# ---------------- User ---------------- #


class AppUser(AbstractUser):
    pass


class UserProfile(models.Model):
    user = models.OneToOneField(AppUser, on_delete=models.CASCADE)
    headline = models.CharField(
        max_length=255,
    )
    avatar = models.ImageField(upload_to="user_avatar/", blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    twitter_profile = models.CharField(max_length=50, blank=True, null=True)
    github_profile = models.CharField(max_length=50, blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    youtube_channel = models.URLField(blank=True, null=True)


# ------------- POSTS -------------- #


class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Channel(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Podcast(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    post_type = models.CharField(max_length=20, choices=POST_TYPES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    tags = ArrayField(models.CharField(max_length=255), default=list)
    link = models.URLField(blank=True, null=True)
    author = models.CharField(max_length=255, blank=True, null=True)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, blank=True, null=True)
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE, blank=True, null=True)
    published_at = models.DateTimeField(blank=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    created_user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_votes = models.IntegerField(null=False, default=0, blank=False)

    def __str__(self):
        return "{}-{}".format(self.title, self.approved)

    def get_vote_count(self):
        return self.postvote_set.count()

    def is_voted(self, user):
        voted = self.postvote_set.filter(created_user=user).exists()
        return voted


class PostVote(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.post.title


class PostComment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.TextField()
    created_user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        from django.urls import reverse_lazy

        return reverse_lazy("post-detail", kwargs={"pk": self.post.pk})

    def is_commented(self, user):
        return self.created_user.id == user.id


class Collection(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    posts = models.ManyToManyField(Post)
    is_staffpick = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    created_user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# Proxy Models


class PostQuerySet(models.QuerySet):
    def all(self):
        return self.filter(approved=True)

    def sorted_by_upvotes(self):
        return self.order_by("-total_votes")


class PostManager(models.Manager):
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db).all()

    def get_sorted_query(self, query):
        query = sorted(query, key=lambda obj: obj.get_vote_count(), reverse=True)
        return query

    def books(self):
        return self.get_queryset().filter(post_type="Book")

    def videos(self):
        return self.get_queryset().filter(post_type="Video")

    def tutorials(self):
        return self.get_queryset().filter(post_type="Tutorial")

    def podcasts(self):
        return self.get_queryset().filter(post_type="Podcast")


class Book(Post):
    class Meta:
        proxy = True

    objects = PostManager()


class Video(Post):
    objects = PostManager()

    class Meta:
        proxy = True

    def get_absolute_url(self):
        return reverse("post-submit")


class Tutorial(Post):
    class Meta:
        proxy = True

    objects = PostManager()


class PodcastEpisode(Post):
    class Meta:
        proxy = True

    def get_absolute_url(self):
        return reverse("post-submit")

    objects = PostManager()
