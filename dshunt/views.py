import datetime
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.views import View
from django.views.generic import CreateView

from .forms import CreatePostForm
from .models import AppUser, Post, Category, PostVote

def post_list(request):
    di = {}
    d = datetime.date.today()
    postvote = PostVote.objects.all()
    post = Post.objects.all()

    for i in range(7):
        idate = d-datetime.timedelta(days=i)
        post = PostVote.objects.filter(post__date_published = idate, post__approved=True).order_by('-vote')[:5]
        di[idate] = [(x.post, x.vote) for x in post]
    
    # di[d-datetime.timedelta(days=2)] = Post.objects.filter(date_published=d-datetime.timedelta(days=2))
    # di[d-datetime.timedelta(days=3)] = Post.objects.filter(date_published=d-datetime.timedelta(days=3))
    # di[d-datetime.timedelta(days=4)] = Post.objects.filter(date_published=d-datetime.timedelta(days=4))
    # di[d-datetime.timedelta(days=5)] = Post.objects.filter(date_published=d-datetime.timedelta(days=5))
    # di[d-datetime.timedelta(days=6)] = Post.objects.filter(date_published=d-datetime.timedelta(days=6))
    
    context = {'post':di, 'd':d-datetime.timedelta(days=1)}
    return render(request, 'posts.html', context)


class PostCreateView(View):
    form_class = CreatePostForm
    template_name = 'dshunt/post_submit.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.submitted_user = request.user
            form.save()

            # save to PostVote
            p = PostVote(post = form)
            p.save()
        else:
            return render(request, self.template_name, {'form': form})
        return redirect(postList)


# Voting to Post
class Vote(View):

    def post(self, request, id):
        post = Post.objects.get(id=id)
        postvote = PostVote.objects.filter(post=post)
        if postvote.exists():
            for i in postvote:
                i.vote = i.vote + 1
                i.save()
        else:
            postvote = PostVote(
                post=post, vote=1
            )
            postvote.save()
        return redirect(postList)

# CATEGORY
def category(request):
    cat = Category.objects.all()
    context = {'category':cat}
    return render(request, 'dshunt/category.html', context)

