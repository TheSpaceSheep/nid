# Project Instructions for Coding Agents

## Critical Setup Details

- **Tailwind rebuild**: After editing templates, run `npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify`
- **Database config**: Uses dj-database-url. SQLite default, PostgreSQL via DATABASE_URL env var
- **Static files**: WhiteNoiseMiddleware is position-sensitive - must be after SecurityMiddleware
- **HTMX middleware**: django_htmx.middleware.HtmxMiddleware must be last in MIDDLEWARE list
- **Templates**: Global templates in `/templates`, app templates follow Django convention

## Running Commands

- Use `uv run` prefix for all Django management commands (e.g., `uv run python manage.py migrate`)
- Dev server: `uv run python manage.py runserver`
- Migrations: `uv run python manage.py makemigrations && uv run python manage.py migrate`

## FCM Setup (when needed)

1. Uncomment FCM code in config/settings.py (bottom of file)
2. Get service account JSON from Firebase Console
3. Set FCM_CREDENTIALS_PATH in .env
4. Import statement must be inside settings.py, not at top

## Deployment

- Dockerfile uses uv - deps installed via `uv sync --frozen --no-dev`
- Static files collected during Docker build, not runtime
- fly.toml configured for auto-stop/start to minimize costs
