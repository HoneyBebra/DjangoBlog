from django.urls import path

from . import views
from .feeds import LatestPostsFeed


app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('<slug:tag_slug>', views.PostListView.as_view(), name='post_list_by_tag'),
    path('<int:post_id>/<slug:slug>/', views.post_detail, name='post_detail'),
    path('<int:post_id>/<slug:slug>/share/', views.post_share, name='post_share'),
    path('<int:post_id>/<slug:slug>/comment/', views.post_comment, name='post_comment'),
    path('feed/', LatestPostsFeed(), name='post_feed')
]
