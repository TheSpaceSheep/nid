- **Tailwind**: before working, always run tailwind's watch mode in the background.
    - `npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch`
- **Templates**: Global templates in `/templates`, app templates follow Django convention

- Migrations: `uv run python manage.py makemigrations && uv run python manage.py migrate`
- Django dev server: `uv run python manage.py runserver`
- Use `uv run` prefix for all Django management commands
