from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name


class Post(models.Model):
    post_type = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    link = models.URLField()
    date_published = models.DateField(auto_now=True)
    submitted_user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return "{}-{}".format(self.title,self.approved)

    def get_absolure_url(self):
        return reverse('post-create', args=[str(self.id)])


class PostVote(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    vote = models.IntegerField(default=0)