from django.db.models import Case, F, Sum, When

from personal_blog.models import Category, Post, Tag


def navigation(request):
    categories = Category.objects.all()
    tags = Tag.objects.all()[:10]
    recent_posts = Post.objects.filter(
        status="published", published_at__isnull=False
    ).order_by("-created_at")[:5]
    # Get the post with the highest views_count by summing views_count of all posts in each category
    top_categories = (
        Post.objects.filter(status="published", published_at__isnull=False)
        .values("category__pk", "category__name")
        .annotate(
            pk=F("category__pk"), name=F("category__name"), max_views=Sum("views_count")
        )
        .order_by("-views_count")
        .values("pk", "name", "max_views")
    )
    category_ids = [top_category["pk"] for top_category in top_categories]  # [2,6,5,6]
    order_by_max_views = Case(
        *[
            When(
                id=category["pk"], then=category["max_views"]
            )  # When(id=2, then=11), When(id=6,then=2)
            for category in top_categories
        ]
    )
    # top categories by views_count
    top_categories = Category.objects.filter(pk__in=category_ids).order_by(
        -order_by_max_views
    )[:4]
    return {
        "categories": categories,
        "tags": tags,
        "recent_posts": recent_posts,
        "top_categories": top_categories,
    }
