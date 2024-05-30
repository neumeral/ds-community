from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

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

    def __str__(self):
        return str(self.headline)

    def get_absolute_url(self):
        return reverse('user-profile', kwargs={'pk': self.user.pk})


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
    link = models.URLField(blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Podcast(models.Model):
    name = models.CharField(max_length=100)
    link = models.URLField(blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class PostType(models.TextChoices):
    BOOK = "book", _("Book")
    VIDEO = "video", _("Video")
    TUTORIAL = "tutorial", _("Tutorial")
    PODCAST = "podcast", _("Podcast")


class Post(models.Model):
    post_type = models.CharField(max_length=20, choices=PostType.choices)
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
        return self.total_votes

    def is_voted(self, user):
        voted = self.postvote_set.filter(created_user=user).exists()
        return voted

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        from django.utils import timezone

        if self.pk:
            p = Post.objects.get(pk=self.pk)
            if not p.approved and self.approved:
                self.approved_at = timezone.now()
        else:
            self.published_at = timezone.now()

        return super().save(force_insert=False, force_update=False, using=None, update_fields=None)


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


class BookManager(models.Manager):
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db).filter(post_type=PostType.BOOK)


class VideoManager(models.Manager):
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db).filter(post_type=PostType.VIDEO)


class TutorialManager(models.Manager):
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db).filter(
            post_type=PostType.TUTORIAL
        )


class PodcastManager(models.Manager):
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db).filter(post_type=PostType.PODCAST)


class Book(Post):
    class Meta:
        proxy = True

    objects = BookManager()


class Video(Post):
    objects = VideoManager()

    class Meta:
        proxy = True

    def get_absolute_url(self):
        return reverse("post-submit")


class Tutorial(Post):
    class Meta:
        proxy = True

    objects = TutorialManager()


class PodcastEpisode(Post):
    class Meta:
        proxy = True

    def get_absolute_url(self):
        return reverse("post-submit")

    objects = PodcastManager()
