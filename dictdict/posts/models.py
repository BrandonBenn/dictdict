from config.models import Base
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count, OuterRef, Q, Subquery
from sql_util.utils import SubqueryCount


class PostQuerySet(models.QuerySet):
    def search(self, q: str):
        return self.collect().filter(
            Q(title__icontains=q) | Q(content__icontains=q),
        )

    def collect(self):
        return self.annotate(
            _opinion_count=SubqueryCount("opinion"),
            _impression_count=SubqueryCount("opinion__voters"),
            _top_opinion=Subquery(
                output_field=models.CharField(),
                queryset=(
                    Opinion.objects.filter(post=OuterRef("pk"))
                    .annotate(num_voters=Count("voters"))
                    .order_by("-num_voters")
                    .values("content")[:1]
                ),
            ),
        )


class Post(Base):
    class Meta:
        db_table = "posts"

    objects = PostQuerySet.as_manager()

    title = models.CharField(max_length=30)
    content = models.CharField(max_length=255)
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.DO_NOTHING,
    )

    def __str__(self):
        return f"{self.title} | {self.content}"

    @property
    def top_opinion(self) -> str:
        """
        Retrieve and cache the content of the opinion with the most votes for
        this post.
        """
        if hasattr(self, "_top_opinion"):
            return str(self._top_opinion)
        return (
            self.opinion_set.annotate(num_voters=Count("voters"))
            .order_by("-num_voters")
            .values("content")[:1]
        )

    @property
    def impression_count(self) -> int:
        """Every opinion or like on a post is considered an interaction."""
        count = 0
        if hasattr(self, "_impression_count"):
            count = self._impression_count
        else:
            count = Opinion.objects.filter(post=self).values("voters").count()

        return count + self.opinion_count

    @property
    def opinion_count(self) -> int:
        """Number of opinions submitted for a given post."""
        if hasattr(self, "_opinion_count"):
            return self._opinion_count or 0
        return self.opinion_set.count()


class Opinion(Base):
    """
    It tracks the content, voters, and timestamps for each opinion,
    allowing users to express their views and vote on them.
    """

    class Meta:
        db_table = "opinions"

    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    voters = models.ManyToManyField(get_user_model())

    def __str__(self) -> str:
        return f"{self.content} - {self.post.title}"
