from django.urls import path
from . import views


urlpatterns = [
    path('', views.postList, name="post-list"),
    path('submitpost/<id>', views.postSubmit, name="post-submit")
]