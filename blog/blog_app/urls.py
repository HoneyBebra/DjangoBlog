from django.urls import path
from . import views


app_name = 'blog_app'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('<int:post_id>/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('<int:post_id>/<slug:slug>/share/', views.post_share, name='post_share')
]
