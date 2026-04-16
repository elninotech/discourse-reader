"""PostsProxy — single-post retrieval by global ID."""

from __future__ import annotations

from typing import TYPE_CHECKING

from discourse_reader.models import Post

if TYPE_CHECKING:
    from discourse_reader.client import DiscourseClient


class PostsProxy:
    """Post namespace: ``client.posts``."""

    def __init__(self, client: DiscourseClient) -> None:
        self._client = client

    def get(self, post_id: int) -> Post:
        """Fetch a single post by its global ID."""
        data = self._client._get(f"/posts/{post_id}.json")
        return Post.model_validate(data)
