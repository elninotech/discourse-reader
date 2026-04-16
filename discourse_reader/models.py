from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

_ALLOW_EXTRA = ConfigDict(extra="allow")


class SiteStatistics(BaseModel):
    model_config = _ALLOW_EXTRA

    topics_count: int
    topics_last_day: int
    topics_7_days: int
    topics_30_days: int
    posts_count: int
    posts_last_day: int
    posts_7_days: int
    posts_30_days: int
    users_count: int
    users_last_day: int
    users_7_days: int
    users_30_days: int
    active_users_last_day: int
    active_users_7_days: int
    active_users_30_days: int
    participating_users_last_day: int
    participating_users_7_days: int
    participating_users_30_days: int
    likes_count: int
    likes_last_day: int
    likes_7_days: int
    likes_30_days: int


class CategoryModerator(BaseModel):
    model_config = _ALLOW_EXTRA

    category_id: int
    moderator_ids: list[int]


class About(BaseModel):
    model_config = _ALLOW_EXTRA

    title: str
    description: str
    extended_site_description: str
    version: str
    locale: str
    https: bool
    contact_email: str
    contact_url: str
    site_creation_date: datetime
    banner_image: str | None
    admin_ids: list[int]
    moderator_ids: list[int]
    category_moderators: list[CategoryModerator]
    can_see_about_stats: bool
    stats: SiteStatistics


class FeaturedTopic(BaseModel):
    model_config = _ALLOW_EXTRA

    id: int
    title: str
    fancy_title: str
    slug: str
    posts_count: int
    reply_count: int
    highest_post_number: int
    created_at: datetime
    last_posted_at: datetime | None
    bumped_at: datetime
    bumped: bool
    archetype: str
    image_url: str | None
    visible: bool
    closed: bool
    archived: bool
    pinned: bool
    unpinned: bool | None
    bookmarked: bool | None
    liked: bool | None
    unseen: bool


class Category(BaseModel):
    model_config = _ALLOW_EXTRA

    id: int
    name: str
    slug: str
    color: str
    text_color: str
    description: str | None
    description_text: str | None
    description_excerpt: str | None
    position: int
    topic_url: str | None
    topic_count: int
    post_count: int
    topics_day: int
    topics_week: int
    topics_month: int
    topics_year: int
    topics_all_time: int
    read_restricted: bool
    has_children: bool
    permission: int | None
    notification_level: int
    num_featured_topics: int
    minimum_required_tags: int
    default_view: str | None
    default_list_filter: str
    default_top_period: str
    sort_order: str | None
    sort_ascending: bool | None
    show_subcategory_list: bool
    subcategory_list_style: str
    navigate_to_first_post_after_read: bool
    topic_template: str | None
    uploaded_logo: str | None
    uploaded_logo_dark: str | None
    uploaded_background: str | None
    uploaded_background_dark: str | None
    custom_fields: dict[str, Any]


class CategoryList(BaseModel):
    model_config = _ALLOW_EXTRA

    can_create_category: bool
    can_create_topic: bool
    categories: list[Category]


class Tag(BaseModel):
    model_config = _ALLOW_EXTRA

    id: int
    name: str
    slug: str


class TagDetail(BaseModel):
    model_config = _ALLOW_EXTRA

    id: int | str
    name: str
    text: str
    description: str | None
    count: int
    pm_only: bool
    target_tag: str | None


class Poster(BaseModel):
    model_config = _ALLOW_EXTRA

    extras: str | None
    description: str
    user_id: int


class Topic(BaseModel):
    model_config = _ALLOW_EXTRA

    id: int
    title: str
    fancy_title: str
    slug: str
    archetype: str
    category_id: int
    posts_count: int
    reply_count: int
    highest_post_number: int
    like_count: int
    views: int
    created_at: datetime
    last_posted_at: datetime | None
    bumped_at: datetime
    bumped: bool
    last_poster_username: str
    image_url: str | None
    visible: bool
    closed: bool
    archived: bool
    pinned: bool
    pinned_globally: bool
    unpinned: bool | None
    bookmarked: bool | None
    liked: bool | None
    unseen: bool
    featured_link: str | None
    has_summary: bool
    posters: list[Poster]
    tags: list[Tag | str] = []
    tags_descriptions: dict[str, str] = {}


class TopicList(BaseModel):
    model_config = _ALLOW_EXTRA

    more_topics_url: str | None = None
    per_page: int
    topics: list[Topic]


class Post(BaseModel):
    model_config = _ALLOW_EXTRA

    id: int
    post_number: int
    post_type: int
    cooked: str
    created_at: datetime
    updated_at: datetime
    reply_count: int
    quote_count: int
    incoming_link_count: int
    reads: int
    readers_count: int
    score: float
    topic_id: int
    topic_slug: str
    version: int
    hidden: bool
    user_id: int
    username: str
    name: str | None = None
    avatar_template: str
    user_title: str | None
    trust_level: int
    moderator: bool
    admin: bool
    staff: bool
    reply_to_post_number: int | None
    deleted_at: str | None
    user_deleted: bool
    wiki: bool
    post_url: str
    posts_count: int
    primary_group_name: str | None
    flair_name: str | None
    flair_url: str | None
    flair_bg_color: str | None
    flair_color: str | None
    flair_group_id: int | None
    bookmarked: bool
    read: bool = False
    yours: bool = False
    edit_reason: str | None


class PostStream(BaseModel):
    model_config = _ALLOW_EXTRA

    posts: list[Post]
    stream: list[int]


class TopicDetail(BaseModel):
    model_config = _ALLOW_EXTRA

    id: int
    title: str
    fancy_title: str
    slug: str
    archetype: str
    category_id: int
    posts_count: int
    reply_count: int
    highest_post_number: int
    like_count: int
    views: int
    word_count: int | None
    created_at: datetime
    last_posted_at: datetime | None
    visible: bool
    closed: bool
    archived: bool
    pinned: bool
    pinned_globally: bool
    pinned_at: str | None
    pinned_until: str | None
    unpinned: bool | None
    bookmarked: bool
    featured_link: str | None
    has_summary: bool
    participant_count: int
    chunk_size: int
    image_url: str | None
    user_id: int
    deleted_at: str | None
    show_read_indicator: bool
    slow_mode_seconds: int
    current_post_number: int
    tags_descriptions: dict[str, str] = {}
    post_stream: PostStream
