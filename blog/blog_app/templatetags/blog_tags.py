from django import template
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown

from blog_app.models import Post


register = template.Library()


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}


@register.simple_tag
def get_most_commented_post(count=5):
    return Post.published.annotate(
        total_comments=Count('comments')
    ).filter(total_comments__gt=0).order_by('-total_comments', '-publish')[:count]


@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))
