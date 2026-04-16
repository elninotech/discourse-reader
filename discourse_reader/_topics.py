"""TopicsProxy — topic discovery and retrieval."""

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

from discourse_reader.models import Category, Post, PostStream, Topic, TopicDetail, TopicList

if TYPE_CHECKING:
    from discourse_reader.client import DiscourseClient


class TopicPosts:
    """Accessor for posts within a fetched topic.

    Provides convenient access to the question, accepted answer, and replies.
    Additional posts beyond the initial batch are fetched lazily.
    """

    _BATCH_SIZE = 20

    def __init__(self, client: DiscourseClient, topic_id: int, post_stream: PostStream) -> None:
        self._client = client
        self._topic_id = topic_id
        # Discourse returns only ~20 posts with the topic detail.
        # Remaining posts are fetched lazily when all() or replies() are called.
        self._posts = list(post_stream.posts)
        self._stream = list(post_stream.stream)

    def replies(self) -> Iterator[Post]:
        """Yield all posts except the opening post."""
        for post in self.all():
            if post.post_number == 1:
                continue
            yield post

    def all(self) -> Iterator[Post]:
        """Yield all posts, fetching additional batches as needed."""
        yield from self._posts
        loaded_ids = {p.id for p in self._posts}
        remaining = [pid for pid in self._stream if pid not in loaded_ids]
        for i in range(0, len(remaining), self._BATCH_SIZE):
            batch = remaining[i : i + self._BATCH_SIZE]
            ids_param = "&".join(f"post_ids[]={pid}" for pid in batch)
            data = self._client._get(f"/t/{self._topic_id}/posts.json?{ids_param}")
            for raw_post in data["post_stream"]["posts"]:
                yield Post.model_validate(raw_post)

    def __iter__(self) -> Iterator[Post]:
        return self.all()

    def __len__(self) -> int:
        return len(self._stream)

    def __repr__(self) -> str:
        return f"TopicPosts(total={len(self._stream)}, loaded={len(self._posts)})"


class TopicResult:
    """A fetched topic with convenient post access.

    All TopicDetail attributes are accessible directly (e.g. ``topic.title``).
    Use ``topic.detail`` for the raw TopicDetail model.
    """

    def __init__(
        self, detail: TopicDetail, posts: TopicPosts, accepted_post_number: int | None
    ) -> None:
        self._detail = detail
        self._accepted_post_number = accepted_post_number
        self.posts = posts

    @property
    def detail(self) -> TopicDetail:
        """The underlying TopicDetail model."""
        return self._detail

    @property
    def opening_post(self) -> Post:
        """The original post of the topic."""
        return self.posts._posts[0]

    @property
    def accepted_answer(self) -> Post | None:
        """The accepted answer, or None if the topic is unsolved.

        May fetch additional posts if the accepted answer isn't in the
        initial batch (~20 posts).
        """
        if self._accepted_post_number is None:
            return None
        for post in self.posts.all():
            if post.post_number == self._accepted_post_number:
                return post
        return None

    def __getattr__(self, name: str) -> Any:
        return getattr(self._detail, name)

    def __repr__(self) -> str:
        return f"TopicResult(id={self._detail.id}, title={self._detail.title!r})"


class TopicsProxy:
    """Topic namespace: ``client.topics``."""

    def __init__(self, client: DiscourseClient) -> None:
        self._client = client

    def get(self, topic_id: int) -> TopicResult:
        """Fetch a topic with convenient post access."""
        data = self._client._get(f"/t/{topic_id}.json")
        detail = TopicDetail.model_validate(data)
        accepted = data.get("accepted_answer")
        accepted_post_number = accepted.get("post_number") if isinstance(accepted, dict) else None
        posts = TopicPosts(self._client, topic_id, detail.post_stream)
        return TopicResult(detail, posts, accepted_post_number)

    def latest(self, limit: int | None = None) -> Iterator[Topic]:
        """Iterate latest topics across the site."""
        return self._paginate("/latest.json", limit)

    def top(self, period: str = "all", limit: int | None = None) -> Iterator[Topic]:
        """Iterate top topics for a given period."""
        return self._paginate(f"/top.json?period={period}", limit)

    def by_category(self, category: Category, limit: int | None = None) -> Iterator[Topic]:
        """Iterate topics in a specific category."""
        return self._paginate(f"/c/{category.slug}/{category.id}.json", limit)

    def by_tag(self, tag_name: str, limit: int | None = None) -> Iterator[Topic]:
        """Iterate topics with a specific tag."""
        return self._paginate(f"/tag/{tag_name}.json", limit)

    def _paginate(self, path: str, limit: int | None) -> Iterator[Topic]:
        yielded = 0
        page = 0
        separator = "&" if "?" in path else "?"

        while True:
            url = f"{path}{separator}page={page}" if page > 0 else path
            data = self._client._get(url)
            topic_list = TopicList.model_validate(data["topic_list"])

            for topic in topic_list.topics:
                yield topic
                yielded += 1
                if limit is not None and yielded >= limit:
                    return

            if not topic_list.more_topics_url:
                return

            page += 1
