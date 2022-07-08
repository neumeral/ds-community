import datetime

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import CreateView, DetailView, ListView
from django.views.generic.dates import DayArchiveView

from .forms import (
    BookCreateForm,
    CommentForm,
    PodcastEpisodeCreateForm,
    PostTypeForm,
    TutorialCreateForm,
    VideoCreateForm,
)
from .models import (
    Book,
    Category,
    PodcastEpisode,
    Post,
    PostType,
    PostVote,
    Tutorial,
    Video,
)


@method_decorator(login_required, name="dispatch")
class PostListHomeView(View):
    model = Post

    def get_posts_and_votes(self, posts):
        # return [(post, post.get_vote_count()) for post in posts]
        return [
            {
                "post": post,
                "vote": post.get_vote_count(),
                "is_voted": post.is_voted(self.request.user),
            }
            for post in posts
        ]

    def get(self, request, *args, **kwargs):
        object_list = []

        today = datetime.date.today()

        for i in range(7):
            object_data = {}
            post_date = today - datetime.timedelta(days=i)
            posts = self.model.objects.filter(published_at__date=post_date, approved=True)

            if posts.exists():
                sorted_posts = posts.order_by("-total_votes")[:5]
                object_data["date"] = post_date
                object_data["post_list"] = self.get_posts_and_votes(sorted_posts)
                object_data["post_count"] = posts.count()
                object_list.append(object_data)

        # Redirecting to all post list when main_posts is empty
        if not list(filter(None, object_list)):
            return redirect("posts")

        context = {
            "object_list": object_list,
            "yesterday": today - datetime.timedelta(days=1),
        }
        return render(request, "posts.html", context)


class PostListView(ListView):
    template_name = "dshunt/post_list/post_list.html"
    queryset = Post.objects.filter(approved=True).order_by("-published_at")
    paginate_by = 10

    def get_posts_and_votes(self, posts):
        # return [(post, post.get_vote_count()) for post in posts]
        return [
            {
                "post": post,
                "vote": post.get_vote_count(),
                "is_voted": post.is_voted(self.request.user),
            }
            for post in posts
        ]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        per_page = self.request.GET.get("per_page")
        if per_page:
            self.paginate_by = per_page
        context["object_list"] = self.get_posts_and_votes(context["object_list"])
        return context


class PostListByDateView(DayArchiveView):
    queryset = Post.objects.filter(approved=True).order_by("-published_at")
    date_field = "published_at"
    template_name = "dshunt/post_list/post_list.html"
    paginate_by = 10

    def get_posts_and_votes(self, posts):
        return [
            {
                "post": post,
                "vote": post.get_vote_count(),
                "is_voted": post.is_voted(self.request.user),
            }
            for post in posts
        ]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_list"] = self.get_posts_and_votes(context["post_list"])
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
                "Book": "book-create",
                "Video": "video-create",
                "Tutorial": "tutorial-create",
                "Podcast": "podcast-episode-create",
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
            book = form.save(commit=False)
            book.created_user = self.request.user
            book.post_type = PostType.BOOK
            book.save()
            return redirect("post-list")
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
    success_url = reverse_lazy("post-list")

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

    def get_comment_set(self, post):
        if self.request.GET.get("comment") == "all":
            post_comments = post.postcomment_set.order_by("-id")
        else:
            post_comments = post.postcomment_set.order_by("-id")[:5]
        for comment in post_comments:
            comment.is_commented = comment.is_commented(self.request.user)
        return post_comments

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comments"] = self.get_comment_set(self.object)
        context["comment_form"] = CommentForm()
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


# class PostDetailView(View):
#     def get(self, request, *args, **kwargs):
#         post_id = self.kwargs['id']
#         post = Post.objects.get(pk=post_id)
#         context = {}
#         context['post'] = post
#         context['object'] = post
#
#         return render(request, 'post-detail.html', context)


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

        return redirect("post-list")


def category(request):
    categories = Category.objects.all()
    context = {"categories": categories}
    return render(request, "dshunt/category.html", context)
