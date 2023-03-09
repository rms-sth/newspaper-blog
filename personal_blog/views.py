from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from personal_blog.forms import (
    CategoryForm,
    CommentForm,
    ContactForm,
    NewsLetterForm,
    PostForm,
    TagForm,
)
from personal_blog.models import Category, Post, Tag

one_week_ago = timezone.now() - timedelta(days=7)

PAGINATE_BY = 1


class HomePageView(ListView):
    model = Post
    template_name = "aznews/index.html"
    # template_name = "blog/index.html"
    context_object_name = "posts"
    queryset = Post.objects.filter(status="published").order_by("-published_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["top_posts"] = Post.objects.filter(status="published").order_by(
            "-views_count"
        )[:3]
        # getting most viewed single post
        context["most_viewed"] = (
            Post.objects.filter(status="published").order_by("-views_count").first()
        )
        # get all top post for this week
        context["weekly_top_posts"] = Post.objects.filter(
            status="published", published_at__gte=one_week_ago
        ).order_by("-views_count")[:7]
        context["top_categories"] = Category.objects.all()[:4]
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "aznews/main/blog/detail/post_detail.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        obj = self.get_object()
        obj.views_count += 1
        obj.save()

        # getting next and previous posts
        context = super().get_context_data(**kwargs)

        context["previous_post"] = (
            Post.objects.filter(id__lt=obj.id, status="published")
            .order_by("-id")
            .first()
        )  # ORM
        context["next_post"] = (
            Post.objects.filter(id__gt=obj.id, status="published")
            .order_by("id")
            .first()
        )
        return context


class PostListView(ListView):
    model = Post
    template_name = "aznews/main/blog/post_list.html"
    context_object_name = "posts"
    queryset = Post.objects.filter(
        status="published", published_at__isnull=False
    ).order_by("-published_at")
    paginate_by = 1


class DraftListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "aznews/main/blog/post_list.html"
    context_object_name = "posts"
    queryset = Post.objects.filter(published_at__isnull=True)
    paginate_by = PAGINATE_BY


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_create.html"
    success_url = reverse_lazy("draft-list")

    def form_valid(self, form):
        form.instance.author = self.request.user  # logged in user
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        post = get_object_or_404(Post, pk=pk)
        post.delete()
        return redirect("home")


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_create.html"
    success_url = reverse_lazy("home")


class PostPublishView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        post = get_object_or_404(Post, pk=pk)
        post.status = "published"
        post.published_at = timezone.now()
        post.save()
        return redirect("home")


# class PostUpdateView(LoginRequiredMixin, View):  # View is generic
#     def get(self, request, pk, *args, **kwargs):
#         post = get_object_or_404(Post, pk=pk)
#         form = PostForm(instance=post)
#         return render(
#             request,
#             "blog/post_create.html",
#             {"form": form},
#         )

#     def post(self, request, pk, *args, **kwargs):
#         post = get_object_or_404(Post, pk=pk)
#         form = PostForm(request.POST, instance=post)
#         if form.is_valid():
#             form.save()
#             return redirect("post-detail", pk=pk)


# class PostByTag(View):
#     template_name = "aznews/main/blog/post_list.html"

#     def get(self, request, tag_id, *args, **kwargs):
#         posts = Post.objects.filter(tag=tag_id)
#         return render(
#             request,
#             self.template_name,
#             {"posts": posts},
#         )


class PostByTag(ListView):
    model = Post
    template_name = "aznews/main/blog/post_list.html"
    context_object_name = "posts"
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        super().get_queryset()
        queryset = Post.objects.filter(
            status="published",
            tag=self.kwargs["tag_id"],
        )
        return queryset


# class PostByCategory(View):
#     template_name = "aznews/main/blog/post_list.html"

#     def get(self, request, cat_id, *args, **kwargs):
#         posts = Post.objects.filter(category=cat_id)
#         return render(
#             request,
#             self.template_name,
#             {"posts": posts},
#         )


class PostByCategory(ListView):
    model = Post
    template_name = "aznews/main/blog/post_list.html"
    context_object_name = "posts"
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        super().get_queryset()
        queryset = Post.objects.filter(
            status="published",
            category=self.kwargs["cat_id"],
        ) # select * from post where status = 'published' and category = 1;
        return queryset


class ContactView(View):
    template_name = "aznews/contact.html"
    form_class = ContactForm

    def get(self, request, *args, **kwargs):
        return render(
            request,
            self.template_name,
        )

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Successfully submitted the form. We will contact you soon."
            )
        else:
            messages.error(request, "Sorry Something went wrong.")
        return render(request, self.template_name)


class NewsLetterView(View):
    form_class = NewsLetterForm

    def post(self, request, *args, **kwargs):
        is_ajax = request.headers.get("x-requested-with")
        if is_ajax == "XMLHttpRequest":  # is this an ajax request ???
            form = self.form_class(request.POST)
            if form.is_valid():
                form.save()
                return JsonResponse({"success": True}, status=200)
        return JsonResponse({"success": False}, status=400)


class PostSearchView(View):
    template_name = "aznews/main/blog/post_search.html"

    # def get(self, request, *args, **kwargs):
    #     posts = Post.objects.filter(status="published")
    #     return render(
    #         request,
    #         self.template_name,
    #         {"posts": posts},
    #     )

    def get(self, request, *args, **kwargs):
        print(request.GET)
        query = request.GET["query"]
        post_list = Post.objects.filter(
            (Q(title__icontains=query) | Q(content__icontains=query))
            & Q(status="published")
        ).order_by("-published_at")
        # pagination start
        page = request.GET.get("page", 1)
        paginator = Paginator(post_list, PAGINATE_BY)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        # pagination end
        return render(
            request,
            self.template_name,
            {"page_obj": posts, "query": query},
        )


class AboutView(TemplateView):
    template_name = "aznews/about.html"


class CommentCreateView(View):
    form_class = CommentForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        post_id = request.POST["post"]
        if form.is_valid():
            form.save()
        return redirect("post-detail", post_id)


# class CommentListView(View):
#     template_name = "aznews/main/blog/detail/post_detail.html"

#     def get(self, request, *args, **kwargs):
#         return render(
#             request,
#             self.template_name,
#         )


#################### Category #########################
class TagDetailView(DetailView):
    model = Tag
    template_name = "blog/tag_detail.html"
    context_object_name = "tag"


class TagListView(LoginRequiredMixin, ListView):
    model = Tag
    template_name = "blog/tag_list.html"
    context_object_name = "tags"


class TagCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = TagForm
    template_name = "blog/tag_create.html"
    success_url = reverse_lazy("tag-list")


class TagDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        tag = get_object_or_404(Tag, pk=pk)
        tag.delete()
        return redirect("tag-list")


class TagUpdateView(LoginRequiredMixin, UpdateView):
    model = Tag
    form_class = TagForm
    template_name = "blog/tag_create.html"
    success_url = reverse_lazy("home")


####################### Category #######################
class CategoryDetailView(DetailView):
    model = Category
    template_name = "blog/category_detail.html"
    context_object_name = "category"


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = "blog/category_list.html"
    context_object_name = "categories"


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = CategoryForm
    template_name = "blog/category_create.html"
    success_url = reverse_lazy("category-list")


class CategoryDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return redirect("category-list")


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "blog/category_create.html"
    success_url = reverse_lazy("home")
