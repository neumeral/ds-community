import datetime
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView, CreateView, DetailView, ListView
from django.views.generic.dates import DayArchiveView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .forms import BookCreateForm, VideoCreateForm, TutorialCreateForm, PodcastEpisodeCreateForm, PostTypeForm
from .forms import CommentForm
from .models import Post, PostVote, Book, Video, Tutorial, PodcastEpisode


@method_decorator(login_required, name='dispatch')
class PostListHomeView(View):
    model = Post

    def get_posts_and_votes(self, posts):
        # return [(post, post.get_vote_count()) for post in posts]
        return [
            {
                'post': post,
                'vote': post.get_vote_count(),
                'is_voted': post.is_voted(self.request.user)
            } for post in posts]

    def get(self, request, *args, **kwargs):
        object_list = []

        today = datetime.date.today()

        for i in range(7):
            object_data = {}
            post_date = today-datetime.timedelta(days=i)
            posts = self.model.objects.filter(published_at__date=post_date, approved=True)

            if posts.exists():
                sorted_posts = sorted(posts, key=lambda obj: obj.get_vote_count(), reverse=True)[:5]
                object_data['date'] = post_date
                object_data['post_list'] = self.get_posts_and_votes(sorted_posts)
                object_data['post_count'] = posts.count()
            object_list.append(object_data)

        # Redirecting to all post list when main_posts is empty
        if not object_list:
            return render('posts')

        context = {'object_list': object_list, 'yesterday': today-datetime.timedelta(days=1)}
        return render(request, 'posts.html', context)


class PostListView(ListView):
    template_name = 'dshunt/post_list/post_list.html'
    queryset = Post.objects.filter(approved=True).order_by('-published_at')

    def get_posts_and_votes(self, posts):
        # return [(post, post.get_vote_count()) for post in posts]
        return [
            {
                'post': post,
                'vote': post.get_vote_count(),
                'is_voted': post.is_voted(self.request.user)
            } for post in posts]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.core.paginator import Paginator
        per_page = self.request.GET.get('per_page', 10)
        page_number = self.request.GET.get('page', 1)

        paginator = Paginator(self.queryset, per_page)
        page_obj = paginator.page(page_number)
        context['paginator'] = paginator
        context['page_obj'] = page_obj
        context['is_paginated'] = True
        context['object_list'] = self.get_posts_and_votes(page_obj.object_list)
        return context


class PostListByDateView(DayArchiveView):
    queryset = Post.objects.filter(approved=True).order_by('-published_at')
    date_field = 'published_at'
    template_name = 'dshunt/post_list/post_list.html'
    paginate_by = 10

    def get_posts_and_votes(self, posts):
        return [
            {
                'post': post,
                'vote': post.get_vote_count(),
                'is_voted': post.is_voted(self.request.user)
            } for post in posts]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = self.get_posts_and_votes(context['post_list'])
        return context


# Book, Video, Tutorial, Podcast Lists

class BookListView(ListView):
    queryset = Book.objects.books()
    template_name = 'dshunt/post_list/post_list.html'
    paginate_by = 10

    def get_posts_and_votes(self, posts):
        return [
            {
                'post': post,
                'vote': post.get_vote_count(),
                'is_voted': post.is_voted(self.request.user)
            } for post in posts]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = self.get_posts_and_votes(self.queryset)
        return context


class VideoListView(BookListView):
    queryset = Video.objects.videos()


class TutorialListView(BookListView):
    queryset = Tutorial.objects.tutorials()


class PodcastEpisodeListView(BookListView):
    queryset = PodcastEpisode.objects.podcasts()


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


# Post Detail

class PostDetailView(View):

    def get_comment_set(self, post):
        post_comments = post.postcomment_set.order_by('-id')
        for comment in post_comments:
            comment.is_commented = comment.is_commented(self.request.user)

    def get(self, request, *args, **kwargs):
        post_id = self.kwargs['id']
        post = get_object_or_404(Post, id=post_id)
        post_comments = post.postcomment_set.order_by('-id')

        self.get_comment_set(post)

        context = {}
        context['post'] = post
        context['object'] = post
        context['comments'] = post_comments
        # print("Com ==>> ", context['comments'])
        # print("Type ==>> ", type(context['comments']))
        context['comment_form'] = CommentForm()

        return render(request, 'dshunt/post_detail/post-detail.html', context)


class CommentCreateView(CreateView):
    form_class = CommentForm
    template_name = 'dshunt/post_detail/post_comment_form.html'
    # success_url = reverse_lazy('post-detail', )

    def form_valid(self, form):
        form.instance.created_user = self.request.user
        post_pk = self.kwargs['pk']
        form.instance.post = Post.objects.get(pk=post_pk)
        return super().form_valid(form)


# Voting to Post

class Vote(View):
    def get(self, request, *args, **kwargs):
        post = Post.objects.get(id=kwargs['id'])
        vote = PostVote(post=post, created_user=request.user)
        vote.save()
        return redirect('post-list')


# CATEGORY

def category(request):
    cat = Category.objects.all()
    context = {'category':cat}
    return render(request, 'dshunt/category.html', context)
