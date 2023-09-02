from django.contrib import admin

from posts.models import Post, Opinion

admin.site.register(Post)
admin.site.register(Opinion)
