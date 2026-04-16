import time
from collections.abc import Iterator
from typing import Any

import requests

from discourse_reader.models import About, Category, CategoryList, SiteStatistics, Topic, TopicList


class DiscourseClient:
    def __init__(self, base_url: str, requests_per_second: float | None = 4.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({"Accept": "application/json"})
        self._min_interval = 1.0 / requests_per_second if requests_per_second else 0.0
        self._last_request_time = 0.0

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

    def site_statistics(self) -> SiteStatistics:
        data = self._get("/site/statistics.json")
        return SiteStatistics.model_validate(data)

    def about(self) -> About:
        data = self._get("/about.json")
        return About.model_validate(data["about"])

    def categories(self) -> list[Category]:
        data = self._get("/categories.json")
        category_list = CategoryList.model_validate(data["category_list"])
        return category_list.categories

    def latest_topics(self, limit: int | None = None) -> Iterator[Topic]:
        return self._paginate_topics("/latest.json", limit)

    def top_topics(self, period: str = "all", limit: int | None = None) -> Iterator[Topic]:
        return self._paginate_topics(f"/top.json?period={period}", limit)

    def category_topics(self, category_slug: str, category_id: int, limit: int | None = None) -> Iterator[Topic]:
        return self._paginate_topics(f"/c/{category_slug}/{category_id}.json", limit)

    def _paginate_topics(self, path: str, limit: int | None) -> Iterator[Topic]:
        yielded = 0
        page = 0
        separator = "&" if "?" in path else "?"

        while True:
            url = f"{path}{separator}page={page}" if page > 0 else path
            data = self._get(url)
            topic_list = TopicList.model_validate(data["topic_list"])

            for topic in topic_list.topics:
                yield topic
                yielded += 1
                if limit is not None and yielded >= limit:
                    return

            if not topic_list.more_topics_url:
                return

            page += 1
