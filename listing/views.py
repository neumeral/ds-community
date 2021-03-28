from django.shortcuts import render,redirect
from .models import Post,Category
from accounts.models import AppUser
from django.views.generic import CreateView
from django.views import View
from django.http import HttpResponse

from listing.forms import CreatePostForm
import datetime

def postList(request):
    di = {}
    d = datetime.date.today()
    post = Post.objects.all()
    di[f"Today - {datetime.date.today()}"] = Post.objects.filter(date_published=d, approved=True)
    di[f"Yesterday - {d-datetime.timedelta(days=1)}"] = Post.objects.filter(date_published=d-datetime.timedelta(days=1), approved=True)

    for i in range(2,7):
        di[d-datetime.timedelta(days=i)] = Post.objects.filter(date_published=d-datetime.timedelta(days=i),approved=True)
    
    # di[d-datetime.timedelta(days=2)] = Post.objects.filter(date_published=d-datetime.timedelta(days=2))
    # di[d-datetime.timedelta(days=3)] = Post.objects.filter(date_published=d-datetime.timedelta(days=3))
    # di[d-datetime.timedelta(days=4)] = Post.objects.filter(date_published=d-datetime.timedelta(days=4))
    # di[d-datetime.timedelta(days=5)] = Post.objects.filter(date_published=d-datetime.timedelta(days=5))
    # di[d-datetime.timedelta(days=6)] = Post.objects.filter(date_published=d-datetime.timedelta(days=6))
    
    return render(request, 'layout.html', {'post':di})


class PostCreateView(View):
    form_class = CreatePostForm
    template_name = 'listing/post_submit.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        form = form.save(commit=False)
        user = AppUser.objects.get(id=request.user.id)
        form.submitted_user = user
        form.save()
        return redirect(postList)
