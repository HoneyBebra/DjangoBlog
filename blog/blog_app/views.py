from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank
)

from .models import Post
from .forms import EmailPostForm, CommentForm, SearchForm


# TODO: convert views to classes


class PostListView(ListView):
    context_object_name = 'posts'
    paginate_by = 10
    template_name = 'blog/post/list.html'

    def get_queryset(self):
        queryset = Post.published.all()

        try:
            tag_slug = self.kwargs.get('tag_slug').lower()
            tag = get_object_or_404(Tag, slug=tag_slug)
            queryset = queryset.filter(tags__in=[tag])
            self.tag = tag
        except AttributeError:
            pass

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = getattr(self, 'tag', None)
        return context


def post_detail(request, post_id, slug):
    # TODO: Remove unused variable slug

    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        id=post_id
    )
    comments = post.comments.filter(active=True)
    form = CommentForm()

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    return render(
        request,
        'blog/post/detail.html',
        {
            'post': post,
            'comments': comments,
            'form': form,
            'similar_posts': similar_posts
        }
    )


def post_share(request, post_id):
    # TODO: handle unauthorized user error

    post = get_object_or_404(
        Post, id=post_id,
        status=Post.Status.PUBLISHED
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


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )

    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()

    return render(
        request, 'blog/post/comment.html',
        {
            'post': post,
            'form': form,
            'comment': comment
        }
    )


def post_search(request):
    # TODO: Add search-field via bootstrap

    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            results = Post.published.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
            ).filter(search=search_query).order_by('-rank', '-updated')

    return render(
        request,
        'blog/post/search.html',
        {
            'form': form,
            'query': query,
            'results': results
        }
    )
