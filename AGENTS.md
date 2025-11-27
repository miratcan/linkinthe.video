# Repository Guidelines

## Project Structure & Module Organization
- `src/backend/config`: Django settings, URLs, and WSGI entry point. `manage.py` lives in the same folder for CLI tasks.
- `src/backend/user` and `src/backend/video`: Domain apps for authentication/user data and video features. Add new models, views, and admin registrations here.
- `src/frontend`: Next.js 14 app router UI with Tailwind/shadcn/ui. Use `app/` for routes/layouts, `components/ui` for reusable pieces, and `lib/` for helpers.
- `business/`: Product, brand, and research notes; keep aligned when implementing features but avoid shipping changes here unless requested.
- Backend dependency metadata lives in `src/backend/pyproject.toml` with the lockfile at `src/backend/uv.lock`.

## Setup & Environment
- Python 3.11; dependencies managed with `uv`. Sync once via `just sync` (wraps `cd src/backend && uv sync`).
- Create `.env` from `.env.example`; set `SECRET_KEY`, `DATABASE_URL`, and email/Resend values. Defaults run SQLite and console email locally.
- Run migrations after model changes: `cd src/backend && uv run python manage.py migrate`.

## Build, Test, and Development Commands
- Backend dev server: `just run` or `cd src/backend && uv run python manage.py runserver 0.0.0.0:8000`.
- Backend lint/type-check: `just check` to run Ruff lint + format checks and `mypy` with Django stubs.
- Backend DB: `just migrate` applies migrations (SQLite default). Keep `.env` aligned with database engine.
- Backend tests: `cd src/backend && uv run python manage.py test` (use `--pattern` to target files).
- Frontend dev server: `just front` (after `npm install` in `src/frontend`) starts Next.js on port 3000; `just front-build` runs `next build`.

## Coding Style & Naming Conventions
- Ruff enforces line length 100, double quotes, space indentation, and import sorting; run `uv run ruff format .` to autofix layout issues.
- Type hints are required (`mypy` runs in strict-ish mode); annotate new functions and models.
- Use concise, descriptive names; keep app names singular (`user`, `video`) and prefer snake_case for modules and functions.

## Testing Guidelines
- Use Django `TestCase`/`SimpleTestCase` in each app’s `tests.py` (or split into `tests/test_*.py` as suites grow) and keep tests isolated with fixtures/factories.
- Cover new endpoints, model behaviors, and migrations; aim for deterministic tests that avoid external services (mock email/resend calls).

## Commit & Pull Request Guidelines
- Commit messages: short imperative summaries (e.g., "Add video slug uniqueness check"); include migration context when relevant.
- PRs should describe the change, note migrations and new settings, and include repro/verification steps. Link issues or tickets; add screenshots/JSON samples for API behavior when useful.

## Security & Configuration
- Do not commit `.env` or secrets. Update `.env.example` when adding required configuration.
- Set `ALLOWED_HOSTS` and `DEBUG` appropriately per environment; provide a real `RESEND_API_KEY` outside local development before enabling email sending.
