from django.db.models import Count
from django.shortcuts import render
from blog.models import Comment, Post, Tag


def serialize_post(post, serialize_tags=True):
    tags = post.tags.all()
    if not serialize_tags:
        tags = []

    serialized_post = {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': getattr(post, 'comments_count', None),
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in tags],
        'first_tag_title': tags[0].title if len(tags) else '',
    }
    return serialized_post


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_count,
    }


def index(request):

    most_popular_posts = Post.objects.popular() \
        .prefetch_related('author') \
        .fetch_tags() \
        .fetch_with_comments_count()[-5:]

    fresh_posts = Post.objects \
        .prefetch_related('author') \
        .fetch_tags() \
        .annotate(comments_count=Count('comments')) \
        .order_by('published_at')

    most_fresh_posts = list(fresh_posts)[-5:]

    popular_tags = Tag.objects.popular()
    most_popular_tags = list(popular_tags)[-5:]

    context = {
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = Post.objects.annotate(likes_count=Count('likes')).get(slug=slug)
    comments = Comment.objects.prefetch_related('author').filter(post=post)
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    related_tags = post.tags.post_count()

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': post.likes_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in related_tags],
    }

    most_popular_tags = list(Tag.objects.popular())[-5:]

    most_popular_posts = list(Post.objects.popular().prefetch_related('author'))[-5:]

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [serialize_post(post, False) for post in most_popular_posts],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)

    most_popular_tags = list(Tag.objects.popular())[-5:]

    most_popular_posts = list(Post.objects.popular().prefetch_related('author'))[-5:]

    related_posts = tag.posts.popular() \
        .prefetch_related('author') \
        .fetch_tags() \
        .fetch_with_comments_count()[:20]

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [serialize_post(post, False) for post in most_popular_posts],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
