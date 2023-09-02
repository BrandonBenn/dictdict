from typing import Any

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.base import TemplateView

from posts.forms import OpinionForm, PostForm
from posts.models import Opinion, Post


class PostSearchView(View):
    """View for searching posts"""

    def get(self, request: HttpRequest) -> HttpResponse:
        q = request.GET.get("q", "")
        context = {}
        if q.isspace():
            context["posts"] = Post.objects.collect().all()
        else:
            context["posts"] = Post.objects.search(q).all()
        return render(request, "posts/_post_list.html", context)


class NewPostView(LoginRequiredMixin, TemplateView):
    """View for new posts"""

    template_name = "posts/new.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["form"] = PostForm()
        return context


class EditPostView(LoginRequiredMixin, TemplateView):
    template_name = "posts/edit.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["form"] = PostForm()
        context["post"] = get_object_or_404(Post, pk=kwargs["post_id"])
        return context


class OpinionPostView(LoginRequiredMixin, View):
    """View for opinions"""

    def post(self, request: HttpRequest, post_id: int) -> HttpResponse:
        context = {}
        form = OpinionForm(request.POST)
        if form.is_valid():
            post = get_object_or_404(Post.objects.collect().filter(pk=post_id))
            content = form.cleaned_data.get("content")
            post.opinion_set.create(content=content)
            context["opinions"] = post.opinion_set.all()
            return render(request, "posts/_opinion_list.html", context)

        context["form"] = form
        response = TemplateResponse(
            request, "posts/show.html", context, headers={"HX-Refresh": "true"}
        )
        return response


class PostView(View):
    """View for posts"""

    def get(
        self,
        request: HttpRequest,
        post_id: int | None = None,
    ) -> HttpResponse:
        context = {}
        if post_id:
            post = get_object_or_404(Post.objects.collect().filter(pk=post_id))
            context["post"] = post
            context["opinions"] = post.opinion_set.all()
            return render(request, "posts/show.html", context)

        context["posts"] = list(Post.objects.collect())
        return render(request, "posts/index.html", context)

    @method_decorator(login_required)
    def post(
        self,
        request: HttpRequest,
        post_id: int | None = None,
    ) -> HttpResponse:
        context = {}
        form = PostForm(request.POST)
        if form.is_valid():
            title, content = form.cleaned_data.values()
            post = request.user.post_set.create(title=title, content=content)
            context["post"] = post
            return render(request, "posts/show.html", context)

        context["form"] = form
        return render(request, "posts/new.html", context)

    @method_decorator(login_required)
    def patch(self, request: HttpRequest, post_id: int) -> HttpResponse:
        context = {}
        form = PostForm(request.POST)
        post = get_object_or_404(Post, pk=post_id)
        if form.is_valid():
            post.content = form.cleaned_data["content"]
            context["post"] = post
            return render(request, "posts/show.html", context)

        context["form"] = form
        return render(request, "posts/edit.html", context)

    def delete(self, request: HttpRequest, post_id: int) -> HttpResponse:
        ...


@login_required
@require_http_methods(["POST"])
def opinion_like(request: HttpRequest, opinion_id: int) -> HttpResponse:
    "Toggle opinion like"

    opinion = get_object_or_404(Opinion, pk=opinion_id)
    if opinion.voters.filter(pk=request.user.id).exists():
        opinion.voters.remove(request.user)
    else:
        opinion.voters.add(request.user)
    return HttpResponse(opinion.voters.count(), content_type="text/plain")
