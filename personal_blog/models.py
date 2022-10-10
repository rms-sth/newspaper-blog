from django.db import models


class TimeStampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # does not create table for TimeStampModel


class Category(TimeStampModel):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Tag(TimeStampModel):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


# ORM => Object relational mapping => sql
class Post(TimeStampModel):
    STATUS_CHOICES = [
        ("published", "published"),
        ("unpublished", "unpublished"),
    ]

    title = models.CharField(max_length=256)
    featured_image = models.ImageField(upload_to="post_images/%Y/%m/%d", blank=False)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, blank=False, null=False
    )
    tag = models.ManyToManyField(Tag)
    author = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    content = models.TextField()
    published_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="unpublished"
    )
    views_count = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return self.title

    # Fat models
    @property
    def latest_comments(self):
        comments = Comment.objects.filter(post=self).order_by("-created_at")
        return comments


class NewsLetter(TimeStampModel):
    email = models.EmailField()

    def __str__(self):
        return self.email


class Contact(TimeStampModel):
    message = models.TextField()
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=256)

    def __str__(self):
        return self.subject

    class Meta:
        ordering = ("-created_at",)


class Comment(TimeStampModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    description = models.TextField()
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()

    def __str__(self):
        return self.description[:100]


################## Relationship in database
# 1 - 1
# 1 - M
# M - M


###################### 1 - 1 ################
# 1 user can have only 1 profile
# 1 profile is associated to only 1 user
# OneToOneField => DJANGO => any place


###################### 1 - M ################
# 1 category can have M post
# 1 post is associated to only 1 category
# ForeignKey => DJANGO => use in M

###################### M - M ################
# 1 tag can have M post
# 1 post is associated to M tag
# ManyToManyField => DJANGO => any place
