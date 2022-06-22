import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView, CreateView
from django.urls import reverse_lazy

from .forms import BookCreateForm, VideoCreateForm, TutorialCreateForm, PodcastEpisodeCreateForm, PostTypeForm
from .models import AppUser, Post, Category, PostVote


def post_list(request):
    di = {}
    d = datetime.date.today()
    post_vote = PostVote.objects.all()
    post = Post.objects.all()

    for i in range(7):
        idate = d-datetime.timedelta(days=i)
        posts = PostVote.objects.filter(post__published_at=idate, post__approved=True)[:5]
        post = sorted(posts, key=lambda obj: obj.vote_count, reverse=True)
        di[idate] = [(x.post, x.vote) for x in post]

    # di[d-datetime.timedelta(days=2)] = Post.objects.filter(date_published=d-datetime.timedelta(days=2))
    # di[d-datetime.timedelta(days=3)] = Post.objects.filter(date_published=d-datetime.timedelta(days=3))
    # di[d-datetime.timedelta(days=4)] = Post.objects.filter(date_published=d-datetime.timedelta(days=4))
    # di[d-datetime.timedelta(days=5)] = Post.objects.filter(date_published=d-datetime.timedelta(days=5))
    # di[d-datetime.timedelta(days=6)] = Post.objects.filter(date_published=d-datetime.timedelta(days=6))

    context = {'post': di, 'd': d-datetime.timedelta(days=1)}
    return render(request, 'posts.html', context)


def post_submit_page(request):
    return render(request, 'dshunt/post_submit.html')


class PostSubmitPageView(View):
    template_name = 'dshunt/post_submit.html'
    form = PostTypeForm

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form': self.form})

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        if form.is_valid():
            post_type = form.cleaned_data.get('post_type')
            post_views = {'Book': 'book-create', 'Video': 'video-create', 'Tutorial': 'tutorial-create',
                          'Podcast': 'podcast-episode-create'}
            return redirect(post_views.get(post_type))
        self.get(request)

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['form'] = PostTypeForm()
    #     context['book_form'] = BookCreateForm()
    #     context['video_form'] = VideoCreateForm()
    #     context['tutorial_form'] = TutorialCreateForm()
    #     context['podcast_form'] = PodcastEpisodeCreateForm()
    #     return context


class BookCreateView(View):
    form_class = BookCreateForm
    template_name = 'dshunt/book_create_form.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'book_form': self.form_class()})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.created_user = self.request.user
            book.post_type = 'Book'
            book.save()
            return reverse_lazy('post-list')
        else:
            return render(request, self.template_name, {'book_form': form})


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
        return redirect('home')


# CATEGORY

def category(request):
    cat = Category.objects.all()
    context = {'category':cat}
    return render(request, 'dshunt/category.html', context)

