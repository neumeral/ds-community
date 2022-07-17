from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    # path('accounts/', include('django.contrib.auth.urls')),
    path("accounts/", include("allauth.urls")),

    # Post List
    path("", views.PostListHomeView.as_view(), name="root"),
    path("posts/", views.PostListView.as_view(), name="posts"),
    path(
        "posts/<int:year>/<int:month>/<int:day>/",
        views.PostListByDateView.as_view(month_format="%m"),
        name="posts-list-by-date",
    ),
    path("books/", views.BookListView.as_view(), name="book-list"),
    path("videos/", views.VideoListView.as_view(), name="video-list"),
    path("tutorials/", views.TutorialListView.as_view(), name="tutorial-list"),
    path(
        "podcast-episodes/", views.PodcastEpisodeListView.as_view(), name="podcast-list"
    ),

    # Post Submit
    path("post/", views.PostSubmitPageView.as_view(), name="post-submit"),
    path("books/new/", views.BookCreateView.as_view(), name="book-create"),
    path("videos/new/", views.VideoCreateView.as_view(), name="video-create"),
    path("tutorials/new/", views.tutotrial_create, name="tutorial-create"),
    path(
        "podcast-episode/new/",
        views.PodcastEpisodeCreateView.as_view(),
        name="podcast-episode-create",
    ),

    # Post Detail
    path("posts/<int:pk>/", views.PostDetailView.as_view(), name="post-detail"),
    path(
        "posts/<int:pk>/comments/new/",
        views.CommentCreateView.as_view(),
        name="post-comment-create",
    ),

    # vote
    path("post/<int:id>/vote", views.Vote.as_view(), name="post-vote"),

    # Collection
    path('collections/', views.collection_list_view, name='collection-list'),
    path('collections/<int:pk>/', views.collection_detail_view, name='collection-detail'),
    path('collections/new/', views.collection_create_view, name='collection-create'),
    path('collections/<int:pk>/post/new/', views.add_post_to_collection_view, name='add-to-collection'),

    # category
    path("category/", views.category, name="category"),
]
