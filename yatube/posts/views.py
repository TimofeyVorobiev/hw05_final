from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow
from .utils import posts_on_page


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
  #  form = CommentForm()
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)

    if not form.is_valid():
        return render(request, 'posts/post_create.html', {'form': form})

    post = form.save(commit=False)
    post.author = request.user
    form.save()
    return redirect('posts:profile', username=post.author)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post
                    )

    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post_id)

    return render(request, 'posts/post_create.html', {
        'form': form, 'is_edit': True
    })


def index(request):
    posts = Post.objects.select_related('group', 'author')
    page_number = request.GET.get('page')
    page_obj = posts_on_page(page_number, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')
    page_number = request.GET.get('page')

    page_obj = posts_on_page(page_number, posts)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('group')
    page_number = request.GET.get('page')
    user = request.user
    following = False
    if request.user.is_authenticated:
        following = user.is_authenticated and author.following.exists()
    page_obj = posts_on_page(page_number, posts)
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'author': author,
        'post': post,
        'comments': comments,
        'form': form
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    page_number = request.GET.get('page')
    page_obj = posts_on_page(page_number, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(
            user=request.user, author=author
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)
