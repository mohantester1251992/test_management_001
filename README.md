# Spectra UI Automation Platform

Spectra is a multi-tenant, web-based UI automation platform built with Django and Playwright. It enables engineering and QA teams to collaboratively design browser tests, orchestrate suites, schedule executions, and visualize quality insights.

## Features

- **Organizations & Projects** – multi-tenant isolation with RBAC memberships.
- **Visual Test Designer** – reusable steps, locator library, dataset support, inline comments.
- **Suites & Scheduling** – parallel execution policies, cron-like schedules, retries, notifications.
- **Run Orchestration** – Celery workers for orchestrator/runner queues, artifact capture (screenshots, logs).
- **Secrets & Variables** – encrypted storage with environment scoping and copy-friendly UX.
- **Reporting & Analytics** – dashboards, flaky test detection, run histories, Prometheus metrics.
- **Integrations** – REST + JWT APIs, webhooks, Slack/email notifications, CI friendly Makefile.
- **Developer Experience** – pytest test suite, management commands for demo data and healthchecks, OpenAPI schema.

## Quickstart

1. **Clone & install dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit values for DATABASE_URL, REDIS_URL, etc.
   ```

3. **Apply migrations & seed demo data**
   ```bash
   python manage.py migrate
   python manage.py seed_demo_data
   ```

4. **Run services**
   ```bash
   # Web
   python manage.py runserver 0.0.0.0:8000

   # Celery workers (separate terminals)
   celery -A backend worker -l info -Q orchestrator
   celery -A backend worker -l info -Q runner
   celery -A backend beat -l info
   ```

5. **Log in** using the demo account from the seed command (`demo@example.com` / `demo1234`).

## Architecture

- **Backend:** Django 5, Django REST Framework, Celery, PostgreSQL, Redis.
- **Frontend:** Django templates enhanced with TailwindCSS, HTMX, and Alpine.js.
- **Automation Runtime:** Playwright Python helper for browser execution (falls back to simulation when Playwright is unavailable).
- **Observability:** Structlog JSON logging, Prometheus endpoint, Sentry hooks via environment config.

### Celery Queues
- `orchestrator`: schedules suites, computes cron triggers.
- `runner`: executes Playwright test cases, records artifacts, notifies integrations.

### Key Directories

```
backend/
  apps/
    accounts/        # Custom user, dashboard, theming
    organizations/   # Multi-tenant org + membership models
    projects/        # Projects, environments, secrets, locators
    testcases/       # Visual designer models/views
    suites/          # Suites, schedules, notifications
    runner/          # Run orchestration, Celery tasks, Playwright bridge
    integrations/    # Slack/email/webhook utilities
    analytics/       # Reporting dashboards & management commands
    api/             # DRF viewsets & serializers
frontend/
  templates/         # Tailwind-powered UI pages
  static/            # Tailwind overrides & JS hooks
docs/                # OpenAPI stub, Postman collection, ERD diagram
```

## API

- JWT auth via `dj-rest-auth` (`/auth/jwt/create/`).
- Browseable schema at `/api/docs` powered by drf-spectacular.
- Example collection provided in `docs/postman_collection.json`.

## Management Commands

- `python manage.py seed_demo_data`
- `python manage.py run_healthchecks`
- `python manage.py backfill_flaky_flags`
- `python manage.py trigger_suite --suite <id> [--env <id>] [--dataset <id>]`

## Testing & Linting

```bash
pytest          # Django tests
black .
isort .
flake8
mypy backend
```

CI examples are provided in `.github/workflows/ci.yml` (see below).

## Deployment Notes

- Use `backend.settings.prod` for production configuration.
- Set `SECURE_SSL_REDIRECT=1`, `SESSION_COOKIE_SECURE=1`, and supply `SENTRY_DSN` for full observability.
- Artifacts (screenshots, videos) default to local `media/` directory; configure S3-compatible storage via Django `DEFAULT_FILE_STORAGE` if needed.

## Troubleshooting

- **Playwright Browsers**: Install browsers via `playwright install` on worker nodes.
- **Redis Connectivity**: Ensure `REDIS_URL` matches Celery broker and Django cache settings.
- **Rate Limiting**: Provided by `django-axes` and Django cache; clear entries with `python manage.py axes_reset`.

---

Spectra is ready for extension: add Git-based test sync, visual regression baselines, or custom SSO providers via Django allauth.
