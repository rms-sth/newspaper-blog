from django.contrib import admin

from personal_blog.models import Category, Comment, Contact, NewsLetter, Post, Tag

# admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Contact)
admin.site.register(NewsLetter)


class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "author")


admin.site.register(Post, PostAdmin)
