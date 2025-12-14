# Repository Guidelines

## Project Structure & Module Organization

- `manage.py`: main entry point (uses `mix.settings`).
- `mix/`: project package (`settings.py`, `urls.py`, `views.py`, `wsgi.py`/`asgi.py`).
- Apps: `posts/` (blog posts) and `users/` (auth flows).
- Templates: project-level `templates/` (e.g., `home.html`) plus app templates under `posts/templates/posts/`.
- Assets: `static/` for source assets, `staticfiles/` for `collectstatic` output, and `media/` for uploaded files.
- `db.sqlite3`: local dev database (avoid committing changes unless explicitly intended).
- `django/`: vendored Django source tree; treat as upstream/framework code unless you are intentionally changing Django itself.

## Build, Test, and Development Commands

Run from the repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ./django
python manage.py migrate
python manage.py runserver
```

Common tasks:
- Tests: `python manage.py test` (or scope: `python manage.py test posts users`)
- Migrations: `python manage.py makemigrations posts users` then `python manage.py migrate`
- Static bundle: `python manage.py collectstatic`
- Admin user: `python manage.py createsuperuser`

## Coding Style & Naming Conventions

- Python: 4-space indentation, PEP 8 naming, and grouped imports (stdlib / third-party / local).
- Views are function-based and `snake_case` (e.g., `posts_lists`, `post_page`).
- Keep template context keys consistent with existing patterns (`posts` for lists, `post` for detail pages).
- URL names and `app_name` namespaces (`posts`, `users`) should remain stable to avoid breaking templates.
- No repo-wide formatter is enforced; keep changes minimal and match surrounding style.

## Testing Guidelines

- Use Django’s built-in test runner (`django.test.TestCase`).
- Prefer app-local tests in `posts/tests.py` and `users/tests.py`; name test methods `test_*`.

## Commit & Pull Request Guidelines

- Commit messages in history are short and descriptive (often a single sentence); keep yours one line and avoid “WIP”.
- PRs should include: a brief description, how to test locally, and screenshots for template/CSS changes.
- Call out migrations and avoid committing secrets (use `.env`, which is gitignored) or production-only settings.

## Agent Notes

- Follow repository-specific conventions in `.github/copilot-instructions.md` when making changes to `posts/` or `mix/`.
