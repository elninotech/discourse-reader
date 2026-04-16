import time
from typing import Any

import requests

from discourse_reader._posts import PostsProxy
from discourse_reader._topics import TopicsProxy
from collections.abc import Iterator

from discourse_reader.models import (
    About,
    Category,
    CategoryList,
    SearchPost,
    SearchResult,
    SiteStatistics,
    TagDetail,
    User,
)


class DiscourseClient:
    topics: TopicsProxy
    posts: PostsProxy

    def __init__(self, base_url: str, requests_per_second: float | None = 4.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({"Accept": "application/json"})
        self._min_interval = 1.0 / requests_per_second if requests_per_second else 0.0
        self._last_request_time = 0.0
        self.topics = TopicsProxy(self)
        self.posts = PostsProxy(self)

    def _get(self, path: str) -> dict[str, Any]:
        self._rate_limit()
        response = self._session.get(f"{self._base_url}{path}")
        if response.status_code == 429:
            retry_after = float(response.headers.get("Retry-After", 10))
            time.sleep(retry_after)
            return self._get(path)
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    def _rate_limit(self) -> None:
        if self._min_interval <= 0:
            return
        elapsed = time.monotonic() - self._last_request_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_request_time = time.monotonic()

    def statistics(self) -> SiteStatistics:
        data = self._get("/site/statistics.json")
        return SiteStatistics.model_validate(data)

    def about(self) -> About:
        data = self._get("/about.json")
        return About.model_validate(data["about"])

    def categories(self) -> list[Category]:
        data = self._get("/categories.json")
        category_list = CategoryList.model_validate(data["category_list"])
        return category_list.categories

    def tags(self) -> list[TagDetail]:
        data = self._get("/tags.json")
        return [TagDetail.model_validate(t) for t in data["tags"]]

    def user(self, username: str) -> User:
        data = self._get(f"/u/{username}.json")
        return User.model_validate(data["user"])

    def search(self, query: str, limit: int | None = None) -> Iterator[SearchPost]:
        """Search the forum. Yields matching posts, paginating automatically."""
        page = 1
        yielded = 0
        while True:
            data = self._get(f"/search.json?q={query}&page={page}")
            result = SearchResult.model_validate(data)
            for post in result.posts:
                yield post
                yielded += 1
                if limit is not None and yielded >= limit:
                    return
            if not result.grouped_search_result.get("more_full_page_results"):
                return
            page += 1
