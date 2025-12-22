from django.urls import include, path
from . import views

app_name = 'blog'

# URL для постов
post_urls = [
    path('create/', views.create_post, name='create_post'),
    path('post/<int:post_pk>/', views.post_detail, name='post_detail'),
    path('post/<int:post_pk>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:post_pk>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:post_pk>/comment/add/', views.add_comment, name='add_comment'),
    path('post/<int:post_pk>/comment/<int:comment_pk>/edit/', views.edit_comment, name='edit_comment'),
    path('post/<int:post_pk>/comment/<int:comment_pk>/delete/', views.delete_comment, name='delete_comment'),
]

# URL для категорий
category_urls = [
    path('category/<str:category_name>/', views.category_posts, name='category_posts'),
]

# URL для профиля пользователя
profile_urls = [
    path('edit/', views.edit_profile, name='edit_profile'),
    path('user/<str:username>/', views.profile, name='profile'),  # теперь str вместо slug
]

# Главные URL проекта
urlpatterns = [
    path('', views.index, name='index'),
    path('posts/', include(post_urls)),
    path('categories/', include(category_urls)),
    path('profile/', include(profile_urls)),
]
