from django.http import Http404
from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail

from .models import Post
from .forms import EmailPostForm


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 10
    template_name = 'blog/post/list.html'


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post/detail.html'
    context_object_name = 'post'
    queryset = Post.objects.filter(status=Post.Status.PUBLISHED)
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        post_id = self.kwargs.get('post_id')
        slug = self.kwargs.get('slug')
        queryset = self.get_queryset()

        obj = queryset.filter(id=post_id, slug=slug).first()
        if obj is None:
            raise Http404
        return obj


def post_share(request, post_id, slug):
    # TODO: convert to class
    # TODO: handle unauthorized user error

    post = get_object_or_404(
        Post, id=post_id,
        status=Post.Status.PUBLISHED,
        slug=slug
    )

    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f'{cleaned_data["name"]} recommends you read "{post.title}"'
            message = f'Read {post.title} at {post_url}\n\n' \
                      f'{cleaned_data["name"]}\'s comments: {cleaned_data["comments"]}'
            send_mail(
                subject, message, cleaned_data['email'], [cleaned_data['to']]
            )
            sent = True
    else:
        form = EmailPostForm()
    return render(
        request,
        'blog/post/share.html',
        {
            'post': post,
            'form': form,
            'sent': sent
        }
    )
