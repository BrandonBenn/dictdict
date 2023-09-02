from posts.models import Opinion, Post
from django import forms


def text_input(name: str) -> forms.TextInput:
    return forms.TextInput(
        attrs={
            "id": name,
            "name": name,
            "placeholder": name.capitalize(),
            "class": """
            block shadow border border-gray-200 outline-none
            px-3 py-2 mt-2 w-full
            """.strip(),
        }
    )


class PostForm(forms.Form):
    class Meta:
        model = Post
        fields = ("title", "content")

    title = forms.CharField(widget=text_input("title"))
    content = forms.CharField(widget=text_input("content"), max_length=255)


class OpinionForm(forms.Form):
    class Meta:
        model = Opinion
        fields = ("content")

    content = forms.CharField(widget=text_input("content"),  max_length=255)
