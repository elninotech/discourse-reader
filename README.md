# discourse-reader

A typed, read-only Python client for the Discourse forum API.

## Install

```bash
pip install discourse-reader
```

## Quick start

```python
from discourse_reader import DiscourseClient

client = DiscourseClient("https://community.victronenergy.com")

# Browse categories
for cat in client.categories():
    print(f"{cat.name}: {cat.topic_count} topics")

# Get a topic with all its posts
topic = client.topics.get(12345)
print(topic.title)
print(topic.opening_post.cooked)       # the original post (HTML)
print(topic.accepted_answer)           # accepted answer or None
for reply in topic.posts.replies():
    print(reply.username, reply.cooked)
```

## API

### Site-level (flat on client)

```python
client.about()                         # About
client.statistics()                    # SiteStatistics
client.categories()                    # list[Category]
client.tags()                          # list[TagDetail]
client.user("username")                # User
client.search("query", limit=50)       # Iterator[SearchPost]
```

### Topics (`client.topics`)

```python
client.topics.latest(limit=100)        # Iterator[Topic]
client.topics.top(period="monthly")    # Iterator[Topic]
client.topics.by_category(cat)         # Iterator[Topic]  (pass a Category)
client.topics.by_tag("tag-name")       # Iterator[Topic]
client.topics.get(topic_id)            # TopicResult
```

All listing methods are lazy iterators with optional `limit`.

### TopicResult

`topics.get()` returns a `TopicResult` which delegates to `TopicDetail` for attributes like `title`, `category_id`, `views`, etc.

```python
topic = client.topics.get(12345)
topic.title                            # str (delegated to TopicDetail)
topic.opening_post                     # Post  -- the original post
topic.accepted_answer                  # Post | None
topic.detail                           # raw TopicDetail model
```

### Posts (`topic.posts`)

Discourse delivers ~20 posts with the topic detail. The rest are fetched lazily in batches when you iterate.

```python
topic.posts.all()                      # Iterator[Post] -- everything
topic.posts.replies()                  # Iterator[Post] -- everything except OP
len(topic.posts)                       # total post count
for post in topic.posts:               # same as .all()
    ...
```

### Single post

```python
client.posts.get(post_id)             # Post by global ID
```

### Extra fields

All models use `extra="allow"` -- core fields are typed, plugin fields land in `model_extra`:

```python
topic.detail.model_extra.get("accepted_answer")   # solved plugin data
post.model_extra.get("accepted_answer")            # per-post flag
```

## Rate limiting

Default: 4 requests/second. Configurable via constructor. Automatic 429 retry with `Retry-After`.

```python
client = DiscourseClient("https://...", requests_per_second=2)    # slower
client = DiscourseClient("https://...", requests_per_second=None)  # no limit
```

## Development

```bash
uv sync
uv run pre-commit install
uv run pre-commit run --all-files
uv run pytest
```
