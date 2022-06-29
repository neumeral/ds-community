import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView, CreateView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required

from .forms import BookCreateForm, VideoCreateForm, TutorialCreateForm, PodcastEpisodeCreateForm, PostTypeForm
from .models import Post


class PostListHomeView(View):

    def get_posts_and_votes(self, posts):
        return [(post, post.get_vote_count()) for post in posts]

    def get(self, request, *args, **kwargs):
        main_posts = {}
        today = datetime.date.today()

        for i in range(7):
            post_date = today-datetime.timedelta(days=i)
            posts = Post.objects.filter(published_at=post_date, approved=True)

            if posts.exists():
                posts = sorted(posts, key=lambda obj: obj.vote_count, reverse=True)
                main_posts[post_date] = self.get_posts_and_votes(posts)

    # di[d-datetime.timedelta(days=2)] = Post.objects.filter(date_published=d-datetime.timedelta(days=2))
    # di[d-datetime.timedelta(days=3)] = Post.objects.filter(date_published=d-datetime.timedelta(days=3))
    # di[d-datetime.timedelta(days=4)] = Post.objects.filter(date_published=d-datetime.timedelta(days=4))
    # di[d-datetime.timedelta(days=5)] = Post.objects.filter(date_published=d-datetime.timedelta(days=5))
    # di[d-datetime.timedelta(days=6)] = Post.objects.filter(date_published=d-datetime.timedelta(days=6))

        context = {'post_list': main_posts, 'yesterday': today-datetime.timedelta(days=1)}
        return render(request, 'posts.html', context)


def post_submit_page(request):
    return render(request, 'dshunt/post_submit.html')


class PostSubmitPageView(View):
    template_name = 'dshunt/post_submit.html'
    form = PostTypeForm

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'post_type_form': self.form})

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        if form.is_valid():
            post_type = form.cleaned_data.get('post_type')
            post_views = {'Book': 'book-create', 'Video': 'video-create', 'Tutorial': 'tutorial-create',
                          'Podcast': 'podcast-episode-create'}
            return redirect(post_views.get(post_type))
        self.get(request, *args, **kwargs)

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
    post_type_form = PostTypeForm(initial={'post_type': 'Book'})

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'post_type_form': self.post_type_form, 'form': self.form_class()})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.created_user = self.request.user
            book.post_type = 'Book'
            book.save()
            return redirect('post-list')
        else:
            return render(request, self.template_name, {'form': self.post_type_form, 'book_form': form})


class VideoCreateView(CreateView):
    form_class = VideoCreateForm
    template_name = 'dshunt/video_create_form.html'
    initial = {'post_type': 'Video'}
    post_type = 'Video'
    success_url = reverse_lazy('post-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['form'] = self.form_class
        context['post_type_form'] = PostTypeForm(initial=self.initial)
        return context

    def form_valid(self, form):
        form.instance.post_type = self.post_type
        form.instance.created_user = self.request.user
        return super().form_valid(form)


@login_required()
def tutotrial_create(request):
    post_type_form = PostTypeForm(initial={'post_type': 'Tutorial'})
    form = TutorialCreateForm()
    context = {'post_type_form': post_type_form, 'form': form}

    if request.method == 'POST':
        form = TutorialCreateForm(request.POST)
        if form.is_valid():
            tutorial = form.instance
            # tutorial = form.save(commit=False)
            tutorial.post_type = 'Tutorial'
            tutorial.created_user = request.user
            tutorial.save()
            return redirect('post-list')
        else:
            context['form'] = form
            return render(request, 'dshunt/tutorial_create_from.html', context)
    else:
        return render(request, 'dshunt/tutorial_create_form.html', context)


class PodcastEpisodeCreateView(VideoCreateView):
    form_class = PodcastEpisodeCreateForm
    template_name = 'dshunt/podcast_episode_create_form.html'
    initial = {'post_type': 'Podcast'}
    post_type = 'Podcast'


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

