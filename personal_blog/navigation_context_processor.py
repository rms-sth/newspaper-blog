from personal_blog.models import Category, Post, Tag


def navigation(request):
    categories = Category.objects.all()
    tags = Tag.objects.all()
    recent_posts = Post.objects.filter(status="published").order_by("-created_at")[:5]
    return {
        "categories": categories,
        "tags": tags,
        "recent_posts": recent_posts,
    }
