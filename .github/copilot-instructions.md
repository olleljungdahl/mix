# Copilot instructions — mix repository

Purpose: Help AI coding agents become productive quickly in this Django-based repo.

- **Project Type:** Django project (project package `mix/`) embedded alongside a full `django/` source tree at the repo root.
- **Entry point:** `manage.py` (DJANGO_SETTINGS_MODULE set to `mix.settings`).

Quick start (developer shell):
```
python3 -m venv .venv
source .venv/bin/activate
# Use the bundled Django implementation so imports resolve to the repo's `django/` package
pip install -e ./django
# When dependencies are added, prefer `pip install -r requirements.txt` if present
python manage.py migrate
python manage.py runserver
```

Key locations & patterns (explicit examples):
- **Settings:** `mix/settings.py` — uses SQLite (`db.sqlite3`), `TEMPLATES['DIRS']` → `BASE_DIR / 'templates'`, `STATICFILES_DIRS` → `static/`, and `MEDIA_ROOT` → `media/`.
- **URLs:** `mix/urls.py` — top-level routes; `posts` is included at `path('posts/', include('posts.urls'))`.
- **App:** `posts` — see `posts/models.py` (model `Post`), `posts/views.py` (functions `posts_lists` and `post_page`), and `posts/urls.py` (two routes: list and `<slug:slug>`).
- **Templates:** Project-level `templates/` + app `templates/posts/` — views render `home.html`, `about.html`, `posts/posts_lists.html`, and `posts/post_page.html`.
- **Media/static:** `ImageField` in `Post` uses `default='fallback.png'` — media assets live under `media/` (dev) and static files under `static/`.

Testing and quick checks:
- Run app-specific tests: `python manage.py test posts`.
- Run all tests (this repo includes a full Django test tree): `python manage.py test` — may be large.

Conventions & observable patterns (follow these precisely):
- Views in `posts/views.py` return templates with context keys named `posts` or `post`. New views should use the same keys to keep templates consistent.
- Slug-based lookups use `Post.objects.get(slug=slug)` (see `post_page`) rather than `get_object_or_404` — this pattern is used in existing code (be aware of possible DoesNotExist exceptions).
- Static and media are configured for DEBUG/dev only (`urlpatterns += static(...)` in `mix/urls.py`). For local dev rely on Django's static/media serving.
- The repo's `django/` folder is the authoritative Django implementation for this workspace. Prefer installing it editable (`pip install -e ./django`) for reproducible imports instead of pulling from PyPI.

When making changes, check these files first:
- `mix/settings.py`, `mix/urls.py`, `mix/views.py`
- `posts/models.py`, `posts/views.py`, `posts/urls.py`, `posts/templates/` (for template variable names)
- `templates/` and `static/` for assets and site pages

Notes for AI agents (what to do and what not to assume):
- Assume the project runs locally with the repo-root `django/` package; do not assume an external Django installation unless `pip install` has been run.
- Do not modify `django/` unless fixing a framework-level bug; prefer changes inside `mix/` or `posts/` for app behaviour.
- Prefer minimal, incremental edits. Use existing variable names and URL names (see `app_name='posts'` in `posts/urls.py`).

If anything in these notes is unclear or you want examples for a specific change (add view, migration, template, or tests), tell me which area and I'll expand with concrete diffs and runnable commands.
