from django import forms
from django_summernote.widgets import SummernoteWidget

from personal_blog.models import Comment, Contact, NewsLetter, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "featured_image", "category", "tag", "content")
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "required": True,
                    "placeholder": "Title of your post...",
                }
            ),
            "content": SummernoteWidget(),
            "category": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "tag": forms.SelectMultiple(
                attrs={
                    "class": "form-control",
                    "required": True,
                }
            ),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = "__all__"


class NewsLetterForm(forms.ModelForm):
    class Meta:
        model = NewsLetter
        fields = "__all__"


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = "__all__"
