from django.shortcuts import render
from .models import Post
# Create your views here.
def posts_lists(request):
    posts = Post.objects.all().order_by("-date")
    return render(request, "posts/posts_lists.html", {"posts": posts})