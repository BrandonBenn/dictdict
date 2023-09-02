from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView
from posts.views import PostSearchView

urlpatterns = [
    path("account/", include("allauth.urls")),
    path("admin/", admin.site.urls),
    path("posts/", include("posts.urls"), name="posts"),
    path("search", PostSearchView.as_view(), name="search"),
    path("", RedirectView.as_view(pattern_name="posts"), name="home"),
]
