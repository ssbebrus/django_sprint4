from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('posts/<int:pk>/', views.PostDetail.as_view(), name='post_detail'),
    path('category/<slug:category_slug>/', views.CategoryPosts.as_view(),
         name='category_posts'),
    path('profile/<slug:username>/', views.ProfileDetail.as_view(),
         name='profile'),
    path('profile/<slug:username>/edit/', views.ProfileUpdate.as_view(),
         name='edit_profile'),
    path('posts/create/', views.PostCreate.as_view(), name='create_post'),
    path('posts/<int:pk>/edit/', views.PostUpdate.as_view(), name='edit_post'),
    path('posts/<int:pk>/comment/', views.CommentCreate.as_view(),
         name='add_comment'),
    path('posts/<int:pk>/edit_comment/<int:comment_pk>/',
         views.CommentUpdate.as_view(), name='edit_comment'),
    path('posts/<int:pk>/delete_comment/<int:comment_pk>/',
         views.CommentDelete.as_view(), name='delete_comment'),
    path('posts/<int:pk>/delete/', views.PostDelete.as_view(),
         name='delete_post'),
]
