from django.shortcuts import render
from .models import Post, Category
import datetime

def postList(request):
    di = {}
    d = datetime.date.today()
    post = Post.objects.all()
    di[f"Today - {datetime.date.today()}"] = Post.objects.filter(date_published=d)
    di[f"Yesterday - {d-datetime.timedelta(days=1)}"] = Post.objects.filter(date_published=d-datetime.timedelta(days=1))

    for i in range(2,7):
        di[d-datetime.timedelta(days=i)] = Post.objects.filter(date_published=d-datetime.timedelta(days=i))
    
    # di[d-datetime.timedelta(days=2)] = Post.objects.filter(date_published=d-datetime.timedelta(days=2))
    # di[d-datetime.timedelta(days=3)] = Post.objects.filter(date_published=d-datetime.timedelta(days=3))
    # di[d-datetime.timedelta(days=4)] = Post.objects.filter(date_published=d-datetime.timedelta(days=4))
    # di[d-datetime.timedelta(days=5)] = Post.objects.filter(date_published=d-datetime.timedelta(days=5))
    # di[d-datetime.timedelta(days=6)] = Post.objects.filter(date_published=d-datetime.timedelta(days=6))
    print(di)
    
    return render(request, 'layout.html', {'post':di})

def category(request):
    cat = Category.objects.all()
    context = {'category':cat}
    return render(request, 'category.html', context)