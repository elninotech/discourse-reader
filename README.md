# discourse-reader

A simple Python wrapper for reading Discourse forums.

## Usage

```python
from discourse_reader import DiscourseClient

client = DiscourseClient("https://community.victronenergy.com")

# Find a category
cats = client.categories()
qa = next(c for c in cats if c.slug == "products")
print(f"{qa.name}: {qa.topic_count} topics")

# Iterate all topics in that category
for i, topic in enumerate(client.category_topics(qa.slug, qa.id)):
    print(f"[{i + 1}/{qa.topic_count}] {topic.title}")
```

## Development

```bash
uv sync
uv run pre-commit install
uv run pre-commit run --all-files
uv run pytest
```
