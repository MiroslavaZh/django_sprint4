from datetime import datetime
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from .forms import PostForm, CommentForm, UserForm
from .models import Post, Category, User, Comment

NUMBER_OF_PAGINATOR_PAGES = 10


def get_posts(**kwargs):
    """Отфильтрованное получение постов"""
    return Post.objects.select_related(
        'category',
        'location',
        'author'
    ).annotate(comment_count=Count('comments')
               ).filter(**kwargs).order_by('-pub_date')


def get_paginator(request, queryset,
                  number_of_pages=NUMBER_OF_PAGINATOR_PAGES):
    """Представление queryset в виде пагинатора, по N-шт на странице"""
    paginator = Paginator(queryset, number_of_pages)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    """Главная страница / Лента публикаций"""
    posts = get_posts(
        is_published=True,
        category__is_published=True,
        pub_date__lte=datetime.now())
    page_obj = get_paginator(request, posts)
    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def category_posts(request, category_name):
    """Отображение публикаций в категории"""
    category = get_object_or_404(
        Category,
        name=category_name,
        is_published=True)
    posts = get_posts(
        is_published=True,
        category__is_published=True,
        pub_date__lte=datetime.now(),
        category=category)
    page_obj = get_paginator(request, posts)
    context = {'category': category, 'page_obj': page_obj}
    return render(request, 'blog/post_list.html', context)


def post_detail(request, post_pk):
    """Отображение полного описания выбранной публикации"""
    post = get_object_or_404(Post, pk=post_pk)
    if request.user != post.author:
        post = get_object_or_404(
            Post,
            pk=post_pk,
            is_published=True,
            category__is_published=True,
            pub_date__lte=datetime.now())
    form = CommentForm(request.POST or None)
    comments = Comment.objects.select_related('author').filter(post=post)
    context = {'post': post, 'form': form, 'comments': comments}
    return render(request, 'blog/post_detail.html', context)


@login_required
def create_post(request):
    """Создание публикации"""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)
    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def edit_post(request, post_pk):
    """Редактирование публикации"""
    post = get_object_or_404(Post, pk=post_pk)
    if request.user != post.author:
        return redirect('blog:post_detail', post_pk=post.pk)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_pk=post.pk)
    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def delete_post(request, post_pk):
    """Удаление публикации"""
    post = get_object_or_404(Post, pk=post_pk)
    if request.user != post.author:
        return redirect('blog:post_detail', post_pk=post.pk)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')
    context = {'post': post}
    return render(request, 'blog/create.html', context)


@login_required
def add_comment(request, post_pk):
    """Добавление комментария к публикации"""
    post = get_object_or_404(Post, pk=post_pk)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_pk=post.pk)


@login_required
def edit_comment(request, post_pk, comment_pk):
    """Редактирование комментария к публикации"""
    comment = get_object_or_404(Comment, pk=comment_pk)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_pk=post_pk)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_pk=post_pk)
    context = {'comment': comment, 'form': form}
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_pk, comment_pk):
    """Удаление комментария к публикации"""
    comment = get_object_or_404(Comment, pk=comment_pk)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_pk=post_pk)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_pk=post_pk)
    context = {'comment': comment}
    return render(request, 'blog/comment.html', context)


def profile(request, username):
    """Отображение страницы пользователя"""
    profile_user = get_object_or_404(User, username=username)
    posts = get_posts(author=profile_user)
    if request.user != profile_user:
        posts = get_posts(
            is_published=True,
            category__is_published=True,
            pub_date__lte=datetime.now(),
            author=profile_user)
    page_obj = get_paginator(request, posts)
    context = {'profile': profile_user, 'page_obj': page_obj}
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    """Редактирование страницы пользователя"""
    profile_user = get_object_or_404(User, username=request.user.username)
    form = UserForm(request.POST or None, instance=profile_user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user.username)
    context = {'form': form}
    return render(request, 'blog/user.html', context)
