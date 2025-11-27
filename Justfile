set shell := ["/bin/sh", "-c"]

backend_dir := "src/backend"
frontend_dir := "src/frontend"

sync:
	cd {{backend_dir}} && uv sync

check:
	cd {{backend_dir}} && uv run ruff check .
	cd {{backend_dir}} && uv run ruff format --check .
	cd {{backend_dir}} && PYTHONPATH=. uv run mypy .

run:
	cd {{backend_dir}} && uv run python manage.py runserver 0.0.0.0:8000

front:
	cd {{frontend_dir}} && npm run dev -- --hostname 0.0.0.0 --port 3000

front-build:
	cd {{frontend_dir}} && npm run build
