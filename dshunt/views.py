import datetime

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseNotFound
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.views.generic.dates import DayArchiveView
from django.core.paginator import Paginator

from .forms import (
    UserProfileUpdateForm,
    BookCreateForm,
    CommentForm,
    PodcastEpisodeCreateForm,
    PostTypeForm,
    TutorialCreateForm,
    VideoCreateForm,
    CollectionForm,
    CollectionListForm,
    AddtoCollectionForm
)
from .models import (
    UserProfile,
    Book,
    Category,
    PodcastEpisode,
    Post,
    PostType,
    PostVote,
    Tutorial,
    Video,
    Collection,
    AppUser
)
from django.contrib.auth.mixins import LoginRequiredMixin


# User

class UserProfileDetailsView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        user = get_object_or_404(AppUser, pk=self.kwargs['pk'])
        user_obj, created = UserProfile.objects.get_or_create(user=user, defaults={'headline': 'Headline'})
        context = dict()
        context['object'] = user_obj
        context['post_count'] = Post.objects.filter(approved=True, created_user=user).count()
        return render(self.request, 'dshunt/user/user_profile_detail.html', context)


class UserProfileUpdateView(UpdateView):
    form_class = UserProfileUpdateForm
    model = UserProfile
    pk_url_kwarg = 'pk'
    template_name = 'dshunt/user/user_update_form.html'


class UserSubmittedListView(ListView):
    paginate_by = 10
    page_kwarg = 'page'
    template_name = 'dshunt/user/user_post_list.html'

    def get_queryset(self):
        return Post.objects.filter(created_user_id=self.kwargs['pk'])

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['add_to_coll_form'] = CollectionListForm()
        return context


class UserUpvotedPostListView(UserSubmittedListView):
    def get_queryset(self):
        return Post.objects.filter(postvote__created_user_id=self.kwargs['pk'])


class UserApprovedPostListView(UserSubmittedListView):
    def get_queryset(self):
        return Post.objects.filter(created_user_id=self.kwargs['pk'], approved=True)


@method_decorator(login_required, name="dispatch")
class PostListHomeView(View):
    model = Post

    def update_post_context(self, posts):
        for post in posts:
            post.is_voted = post.is_voted(self.request.user)

    def get(self, request, *args, **kwargs):
        object_list = []

        today = datetime.date.today()

        for i in range(7):
            object_data = {}
            post_date = today - datetime.timedelta(days=i)
            posts = self.model.objects.filter(published_at__date=post_date, approved=True)

            if posts.exists():
                object_data["date"] = post_date
                object_data["post_count"] = posts.count()
                posts = posts.order_by("-total_votes")[:5]
                self.update_post_context(posts)
                object_data["post_list"] = posts
                object_list.append(object_data)

        # Redirecting to all post list when main_posts is empty
        if not list(filter(None, object_list)):
            return redirect("posts")

        context = {
            "object_list": object_list,
            "yesterday": today - datetime.timedelta(days=1),
        }
        return render(request, "posts.html", context)


class PostListByDateView(DayArchiveView):
    queryset = Post.objects.filter(approved=True).order_by("-total_votes")
    date_field = "published_at"
    template_name = "dshunt/post_list/post_list.html"
    paginate_by = 10

    def update_post_context(self, posts):
        for post in posts:
            post.is_voted = post.is_voted(self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        self.update_post_context(context["object_list"])
        return context


class PostListView(ListView):
    template_name = "dshunt/post_list/post_list.html"
    queryset = Post.objects.filter(approved=True).order_by("-published_at")
    paginate_by = 10

    def update_post_context(self, posts):
        for post in posts:
            post.is_voted = post.is_voted(self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['add_to_coll_form'] = CollectionListForm()
        per_page = self.request.GET.get("per_page")
        if per_page:
            self.paginate_by = per_page

        self.update_post_context(context["object_list"])
        return context


class BookListView(PostListView):
    queryset = Book.objects.all().sorted_by_upvotes()
    template_name = "dshunt/post_list/post_list.html"


class VideoListView(PostListView):
    queryset = Video.objects.all().sorted_by_upvotes()


class TutorialListView(PostListView):
    queryset = Tutorial.objects.all().sorted_by_upvotes()


class PodcastEpisodeListView(PostListView):
    queryset = PodcastEpisode.objects.all().sorted_by_upvotes()


class PostSubmitPageView(View):
    """
    Create Post
    """

    template_name = "dshunt/post_submit.html"
    form = PostTypeForm

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"post_type_form": self.form})

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        if form.is_valid():
            post_type = form.cleaned_data.get("post_type")
            post_views = {
                "book": "book-create",
                "video": "video-create",
                "tutorial": "tutorial-create",
                "podcast": "podcast-episode-create",
            }
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
    template_name = "dshunt/book_create_form.html"
    post_type_form = PostTypeForm(initial={"post_type": PostType.BOOK})

    def get(self, request, *args, **kwargs):
        return render(
            request,
            self.template_name,
            {"post_type_form": self.post_type_form, "form": self.form_class()},
        )

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            from django.utils import timezone
            book = form.save(commit=False)
            book.created_user = self.request.user
            book.post_type = PostType.BOOK
            book.published_at = timezone.now()
            book.save()
            return redirect("posts")
        else:
            return render(
                request,
                self.template_name,
                {"form": self.post_type_form, "book_form": form},
            )


class VideoCreateView(CreateView):
    form_class = VideoCreateForm
    template_name = "dshunt/video_create_form.html"
    initial = {"post_type": PostType.VIDEO}
    post_type = PostType.VIDEO
    success_url = reverse_lazy("posts")

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["form"] = self.form_class
        context["post_type_form"] = PostTypeForm(initial=self.initial)
        return context

    def form_valid(self, form):
        form.instance.post_type = self.post_type
        form.instance.created_user = self.request.user
        return super().form_valid(form)


@login_required()
def tutotrial_create(request):
    post_type_form = PostTypeForm(initial={"post_type": PostType.TUTORIAL})
    form = TutorialCreateForm()
    context = {"post_type_form": post_type_form, "form": form}

    if request.method == "POST":
        form = TutorialCreateForm(request.POST)
        if form.is_valid():
            tutorial = form.instance
            # tutorial = form.save(commit=False)
            tutorial.post_type = PostType.TUTORIAL
            tutorial.created_user = request.user
            tutorial.save()
            return redirect("post-list")
        else:
            context["form"] = form
            return render(request, "dshunt/tutorial_create_from.html", context)
    else:
        return render(request, "dshunt/tutorial_create_form.html", context)


class PodcastEpisodeCreateView(VideoCreateView):
    form_class = PodcastEpisodeCreateForm
    template_name = "dshunt/podcast_episode_create_form.html"
    initial = {"post_type": PostType.PODCAST}
    post_type = PostType.PODCAST


class PostDetailView(DetailView):
    queryset = Post.objects.filter(approved=True)
    template_name = "dshunt/post_detail/post_detail.html"

    def get_comments(self, post):
        return post.postcomment_set.order_by('-id')

    def get_comment_set(self, post_comments):
        if self.request.GET.get("comment") is None:
            post_comments = post_comments[:5]
        for comment in post_comments:
            comment.is_commented = comment.is_commented(self.request.user)
        return post_comments

    def get_context_data(self, **kwargs):
        post_comments = self.get_comments(self.object)
        context = super().get_context_data(**kwargs)
        context["comments"] = self.get_comment_set(post_comments)
        context["comment_form"] = CommentForm()
        context["comments_count"] = post_comments.count()

        return context


class CommentCreateView(CreateView):
    form_class = CommentForm
    template_name = "dshunt/post_detail/post_comment_form.html"
    # success_url = reverse_lazy('post-detail', )

    def form_valid(self, form):
        form.instance.created_user = self.request.user
        post_pk = self.kwargs["pk"]
        form.instance.post = Post.objects.get(pk=post_pk)
        return super().form_valid(form)

    def form_invalid(self, form):
        return redirect("post-detail", pk=self.kwargs.get("pk"))


class Vote(View):
    def get(self, request, *args, **kwargs):
        post_id = kwargs["id"]
        post = get_object_or_404(Post, pk=post_id)

        with transaction.atomic():
            vote, created = PostVote.objects.get_or_create(
                post=post, created_user=request.user
            )
            if created:
                post.total_votes += 1
                post.save()
                vote.save()

        return redirect("posts")


def category(request):
    categories = Category.objects.all()
    context = {"categories": categories}
    return render(request, "dshunt/category.html", context)


# Collections

@login_required
def collection_create_view(request):
    form = CollectionForm()

    if request.method == 'POST':
        form = CollectionForm(request.POST)
        if form.is_valid():
            posts = form.cleaned_data.get('posts')
            form.instance.created_user = request.user
            form.save()
            for post in posts:
                form.instance.posts.add(post)
            return redirect('collection-list')
        else:
            return render(request, 'dshunt/collection/collection_form.html', {'form':  form})
    return render(request, 'dshunt/collection/collection_form.html', {'form':  form})


@login_required
def collection_list_view(request):
    per_page = request.GET.get('per_page', 10)
    page = request.GET.get('page', 1)
    is_paginated = True

    collections = Collection.objects.filter(created_user=request.user)
    paginator = Paginator(collections, int(per_page))
    page_obj = paginator.page(int(page))
    context = dict()
    # object_list = page_obj.object_list
    # context['object_list'] = object_list
    context['paginator'] = paginator
    context['page_obj'] = page_obj
    context['is_paginated'] = is_paginated

    return render(request, 'dshunt/collection/collection_list.html', context)


@login_required
def collection_detail_view(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    posts = collection.posts.select_related()
    context = {'collection': collection,
               'add_to_coll_form': AddtoCollectionForm(),
               'post_list': posts.order_by('title'),
               'posts_count': posts.count()
               }
    return render(request, template_name='dshunt/collection/collection_detail.html', context=context)


@login_required
def add_post_to_collection_view(request, pk):

    if request.method == 'POST':

        model_name = request.GET.get('model')
        if model_name == 'collection':
            form = AddtoCollectionForm(request.POST)
            coll_obj = Collection.objects.get(id=pk)
            post = request.POST['post']
            col_id = pk
        elif model_name == 'post':
            form = AddtoCollectionForm(request.POST)
            coll_obj = request.POST['collection']
            post = Post.objects.get(pk=pk)
            col_id = coll_obj
        else:
            return HttpResponseNotFound('Get request not found')

        if form.is_valid():
            coll_obj.posts.add(post)
            return redirect('collection-detail', pk=col_id)
        else:
            return redirect('collection-detail', pk=col_id)
    else:
        return redirect('root')


# Staff Picks

@login_required
def staff_pick_collection_list(request):
    per_page = request.GET.get('per_page', 10)
    page = request.GET.get('page', 1)
    is_paginated = True

    collections = Collection.objects.filter(is_staffpick=True, created_user=request.user)

    paginator = Paginator(collections, int(per_page))
    page_obj = paginator.page(int(page))
    context = dict()
    # object_list = page_obj.object_list
    # context['object_list'] = object_list
    context['paginator'] = paginator
    context['page_obj'] = page_obj
    context['is_paginated'] = is_paginated

    return render(request, 'dshunt/collection/collection_list.html', context)

