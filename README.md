## Averta.com

A Django-based web project. The site includes a multilingual UI (AZ/EN/RU), admin-managed content (About, services, packages, blog, partners, FAQ, etc.), and a standard Django static/media setup.

### Product overview

This project is built as a content-driven website where most sections are managed from the Django Admin (CMS-like workflow). The frontend renders server-side HTML templates and consumes database-backed content such as services, packages, blog posts, partners, FAQs, and site-wide settings.

### Main pages & sections

- Home page
  - About intro (dynamic)
  - Packages slider (dynamic)
  - Services explorer/listing (dynamic)
  - Blog highlights (dynamic)
  - Testimonials / reviews (dynamic)
  - Partners strip (dynamic)
  - FAQ section (dynamic)
  - Contact form (dynamic)
- Services listing + service detail pages (dynamic)
  - Service detail pages include a media/gallery experience and related services section
- About page (dynamic)
  - About content, gallery, video block, and statistics/metrics
- Blog list + blog detail pages (dynamic)
- FAQ page (dynamic)
- Contact page (form)

### Dynamic content (Admin-managed)

Content is designed to be edited by non-developers through the Django Admin panel. Typical dynamic entities include:

- About content (titles, rich text, images, gallery, optional video)
- Services and service detail content (including media)
- Packages (cards, pricing, metadata)
- Blog posts and blog-related blocks
- Partners (logos/names)
- FAQ items
- Contact information / site settings

### Tech stack

- Python 3.11+
- Django 5.2+
- PostgreSQL
- Gunicorn (production)
- `django-ckeditor`, `django-cleanup`, `django-compressor`

### Key functionality

- **Server-side rendered UI** with Django templates (`averta/templates/`)
- **Multilingual (AZ/EN/RU)** with `LocaleMiddleware` and a language switch endpoint
- **Rich-text editing** via `django-ckeditor`
- **Static/media management**
  - `STATICFILES_DIRS` for development assets
  - `STATIC_ROOT` for collected assets in production
  - `MEDIA_ROOT` for uploaded images/media
- **Caching** using Django’s local memory cache for improved response times
- **Production-ready containerization** (Docker + Gunicorn)

### Project structure (high level)

- `averta/manage.py`: Django management entrypoint
- `averta/averta/`: project configuration (`settings.py`, `urls.py`, `wsgi.py`, `asgi.py`)
- `averta/services/`: main app (site content and pages)
- `averta/templates/`: HTML templates
- `averta/static/`: static files for development
- `averta/staticfiles/`: `collectstatic` output (for deployment)
- `averta/media/`: uploaded media (for deployment)
- `docker/`: Docker files (`Dockerfile`, `entrypoint.sh`)

### Environment variables

`averta/averta/settings.py` uses the following variables:

- `SECRET_KEY`
- `DEBUG` (currently hardcoded as `True` in settings; use a separate production configuration)
- `ALLOWED_HOSTS` (comma-separated)
- `CSRF_TRUSTED_ORIGINS` (comma-separated, for additional origins)
- `ADMIN_URL` (required; used to hide the admin route in production)
- PostgreSQL:
  - `POSTGRES_DB`
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`
  - `POSTGRES_HOST`
  - `POSTGRES_PORT`
- Email (optional):
  - `EMAIL_BACKEND`
  - `EMAIL_HOST`
  - `EMAIL_PORT`
  - `EMAIL_HOST_USER`
  - `EMAIL_HOST_PASSWORD`
  - `EMAIL_USE_TLS`

### Captcha (Cloudflare Turnstile)

Cloudflare Turnstile checkbox is implemented for **contact forms only**:

- Home page contact form (appeal/contact section)
- Contact page “Mesaj göndərin” form

Required environment variables:

- `TURNSTILE_SITE_KEY`
- `TURNSTILE_SECRET_KEY`

Notes:

- The widget posts a token via `cf-turnstile-response`, verified server-side.
- Booking forms do **not** include captcha.

### Local run (high level)

- Create and activate a Python virtual environment
- Install dependencies from `pyproject.toml`/`uv.lock`
- Provide PostgreSQL connection via environment variables
- Run migrations
- Collect static files (`collectstatic`)
- Start the Django development server

### Run with Docker

`docker/Dockerfile` + `docker/entrypoint.sh`:

- Waits for PostgreSQL to be ready
- Runs migrations and collects static files
- Starts the app with Gunicorn

Local Docker development uses `docker/docker-compose-local.yaml`. Environment variables are typically provided via `docker/.env`.

### Admin panel

The admin route is defined by the `ADMIN_URL` environment variable. In production, always use a unique path.

### I18N / Languages

AZ/EN/RU languages are enabled. Language switching is available via `i18n/setlang/` and `LocaleMiddleware` is used.

### Static files

- Development: `averta/static/`
- Production: `collectstatic` outputs to `STATIC_ROOT` at `averta/staticfiles/`

### Notes

- `DEBUG` should be disabled in production and Django’s security checklist should be followed.
- Static and media assets can be served from a dedicated storage/CDN in production.

### Form UX (no page refresh)

Public-facing forms are progressively enhanced to submit via AJAX (fetch) so users can see success/error feedback **without a full page refresh**.

### Reviews (customer-only)

Submitting a review requires the phone number to exist in bookings marked as a customer (an anti-spam/business rule). If the phone is not recognized, the form returns a clear error message.

