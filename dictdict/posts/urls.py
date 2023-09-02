from django.urls import path

from posts.views import (
    NewPostView,
    EditPostView,
    PostView,
    OpinionPostView,
    opinion_like,
)

urlpatterns = [
    path("new/", NewPostView.as_view(), name="post_new"),
    path("<int:post_id>/edit/", EditPostView.as_view(), name="post_edit"),
    path("<int:post_id>/", PostView.as_view(), name="posts"),
    path("", PostView.as_view(), name="posts"),
    path("<int:post_id>/opinions/",
         OpinionPostView.as_view(), name="opinions"),
    path("opinions/<int:opinion_id>", opinion_like, name="opinion_like"),
]
