from django.urls import path
from . import views


urlpatterns = [
    path('', views.postList, name="post-list"),
    path('post/', views.PostCreateView.as_view(), name='post-create'),

    #vote
    path('post/<int:id>/vote', views.Vote.as_view(), name="postvote"),
]