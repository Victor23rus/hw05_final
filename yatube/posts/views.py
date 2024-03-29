from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User
from .utils import paginate_page


def index(request):
    page_obj = paginate_page(Post.objects.all(), request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    page_obj = paginate_page(group.posts.all(), request)
    context = {
        'page_obj': page_obj,
        'group': group,
    }

    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author_id = get_object_or_404(User, username=username)
    page_obj = paginate_page(author_id.posts.all(), request)
    following = author_id.following.exists()
    context = {
        'page_obj': page_obj,
        'author_id': author_id,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, pk=post_id)
    comments = Comment.objects.filter(post=post)
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }

    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=post.author)
    context = {'form': form}
    return render(request, 'posts/post_create.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post.pk)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.pk)
    context = {
        'form': form,
        'is_edit': True,
        'post': post,
    }
    return render(request, 'posts/post_create.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author_id__following__user=request.user)
    page_obj = paginate_page(posts, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author_post = get_object_or_404(User, username=username)
    if author_post != request.user:
        Follow.objects.get_or_create(user=request.user, author=author_post)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author_post = get_object_or_404(User, username=username)
    Follow.objects.get(user=request.user, author=author_post).delete()
    return redirect('posts:profile', username=username)
