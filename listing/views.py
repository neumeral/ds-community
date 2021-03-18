from django.shortcuts import render,redirect
from .models import Post,Category
from accounts.models import AppUser
from django.views.generic import CreateView
import datetime

def postList(request):
    di = {}
    d = datetime.date.today()
    post = Post.objects.all()
    di[f"Today - {datetime.date.today()}"] = Post.objects.filter(date_published=d, approved=True)
    di[f"Yesterday - {d-datetime.timedelta(days=1)}"] = Post.objects.filter(date_published=d-datetime.timedelta(days=1), approved=True)

    for i in range(2,7):
        di[d-datetime.timedelta(days=i)] = Post.objects.filter(date_published=d-datetime.timedelta(days=i),approved=True)
    
    # di[d-datetime.timedelta(days=2)] = Post.objects.filter(date_published=d-datetime.timedelta(days=2))
    # di[d-datetime.timedelta(days=3)] = Post.objects.filter(date_published=d-datetime.timedelta(days=3))
    # di[d-datetime.timedelta(days=4)] = Post.objects.filter(date_published=d-datetime.timedelta(days=4))
    # di[d-datetime.timedelta(days=5)] = Post.objects.filter(date_published=d-datetime.timedelta(days=5))
    # di[d-datetime.timedelta(days=6)] = Post.objects.filter(date_published=d-datetime.timedelta(days=6))
    
    return render(request, 'layout.html', {'post':di})


def postSubmit(request,id):
    if request.method == "POST":
        user = AppUser.objects.get(id=id)
        post_type = request.POST.get('post-type')
        category = request.POST.get('category')
        category = Category.objects.get(name=category)
        title = request.POST.get('title')
        description = request.POST.get('description')
        link = request.POST.get('link')

        post = Post(
            post_type=post_type, category=category, title=title, description=description, link=link,
            submitted_user=user
            )
        post.save()
        return redirect(postList)
    else:
        category = Category.objects.all()
        context = {'category' : category}
        return render(request, 'listing/post_submit.html', context)
