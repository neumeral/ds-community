from django.urls import path
from . import views


urlpatterns = [
    path('', views.postList, name="post-list"),

    # category
    path('category/', views.category, name='category')
]