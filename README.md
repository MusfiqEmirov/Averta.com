## Averta.com

Django-based multilingual travel agency website (AZ / EN / RU). Content is managed from the Django Admin; the public site renders server-side templates with cached page/query data for performance.

### Product overview

The site is a content-driven CMS-style product: services, packages, blog, partners, FAQ, about, contact, reviews, and booking orders are stored in PostgreSQL and edited by non-developers in the admin panel.

Public users can browse content, submit contact messages, place booking requests, and leave reviews (reviews require a known customer phone number).

### Main pages

| Route | Description |
|-------|-------------|
| `/` | Home — hero booking form, about intro, packages carousel, services, blog highlights, reviews, partners, FAQ, contact section |
| `/services/` | Services listing |
| `/services/<slug>/` | Service detail — gallery, related services, booking modal entry |
| `/about/` | About page — text, gallery, video, statistics |
| `/blog/` | Blog list |
| `/blog/<slug>/` | Blog detail |
| `/faq/` | FAQ page |
| `/contact/` | Contact page — appeal form + embedded booking form |

Language switch: `POST /i18n/setlang/` (via `LocaleMiddleware`).

### Admin-managed content

- **About** — titles, rich text, gallery, optional hero video
- **Services** — multilingual names/descriptions, media, sort order, homepage flags
- **Packages** — pricing, currency, images, linked services, expiry date, booking date-field toggles
- **Blog** — posts with slugs and view counts
- **Partners** — logos and names
- **FAQ** — questions/answers, homepage visibility
- **Contact** — address, phone, email, social links, map embed
- **Media** — page background images, content galleries
- **Reviews** — moderation (`is_read`), customer flag
- **Bookings** — orders from the site; read/unread, customer flag, soft delete, Excel export
- **AppealContact** — contact form submissions

### Booking system

Booking is available in three places:

1. **Home hero form** (`#hero-booking`)
2. **Global booking modal** (opened from navbar, package cards, service pages)
3. **Contact page embed**

Behaviour:

- User chooses **Package** (single selection, radio) or **Service** (multiple checkboxes).
- Date fields depend on context:
  - **Service** — departure + return dates
  - **Package** — admin configures up to **2 of 3** fields per package: departure (`show_date_from`), return (`show_date_to`), arrival (`show_arrival_date`)
- Dates use **Air Datepicker** on the frontend; validation runs server-side in `BookingForm`.
- Successful submissions create a `Booking` record and send an email notification (if mail is configured).
- Booking forms do **not** use Turnstile captcha.
- Modal closes → selection resets automatically (`home_booking.js`).

Admin: bookings list/detail with client-side Excel export (`admin_booking_export.js`).

### Tech stack

- Python 3.11+
- Django 5.2+
- PostgreSQL 15
- Gunicorn + Nginx (Docker production stack)
- Frontend: Bootstrap 5, jQuery, Owl Carousel, Lightbox, Air Datepicker
- `django-ckeditor`, `django-cleanup`, `django-compressor` (in dependencies)
- Dependency management: **uv** (`pyproject.toml`, `uv.lock`)

### Caching

- Backend: Django `LocMemCache` with versioned keys (`services/utils/cache_utils.py`)
- Page and query helpers decorated with `@cached_page_data` / `@cached_query`
- Admin saves invalidate cache via signals (`services/signals.py`) — global `cache_version` bump
- `CACHE_SCHEMA_VERSION` in settings must be incremented when cached payload shape changes

### Tech stack — project layout

```
Averta.com/
├── averta/                    # Django project root (manage.py lives here)
│   ├── averta/                # settings, urls, wsgi
│   ├── services/              # main app (models, views, admin, forms, signals)
│   ├── templates/             # HTML templates
│   ├── static/                # dev static assets
│   ├── staticfiles/           # collectstatic output
│   ├── media/                 # uploads
│   └── locale/                # AZ source + EN/RU .po/.mo
├── docker/                    # Dockerfile, entrypoint, compose, .env
├── nginx/                     # reverse proxy config + SSL mount
├── pyproject.toml
└── uv.lock
```

Key frontend scripts:

- `static/assets/js/home_booking.js` — booking UI, date pickers, modal
- `static/assets/js/ajax_forms.js` — AJAX form submit (no full page reload)
- `static/assets/js/home_testimonial.js` — reviews carousel/form

### Environment variables

Configure via `docker/.env` (loaded by `settings.py` and `settings_local.py`).

**Required**

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Django secret |
| `ADMIN_URL` | Secret admin path (e.g. `averta-admin-xyz/`) |
| `POSTGRES_DB` | Database name |
| `POSTGRES_USER` | Database user |
| `POSTGRES_PASSWORD` | Database password |
| `POSTGRES_HOST` | Database host |
| `POSTGRES_PORT` | Database port |

**Common**

| Variable | Purpose |
|----------|---------|
| `DEBUG` | `true` / `false` (default `false` in `settings.py`) |
| `ALLOWED_HOSTS` | Comma-separated hosts |
| `CSRF_TRUSTED_ORIGINS` | Extra CSRF origins (comma-separated) |

**Email** (contact + booking notifications)

| Variable | Purpose |
|----------|---------|
| `EMAIL_HOST`, `EMAIL_PORT` | SMTP server |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | SMTP credentials |
| `EMAIL_USE_TLS`, `EMAIL_USE_SSL` | Transport security |
| `DEFAULT_FROM_EMAIL` | From address |
| `CONTACT_RECEIVER_EMAIL` | Inbox for contact/booking emails |
| `SITE_NAME` | Used in email templates (default `Averta.az`) |

**Cloudflare Turnstile** (contact forms only)

| Variable | Purpose |
|----------|---------|
| `TURNSTILE_SITE_KEY` | Public site key |
| `TURNSTILE_SECRET_KEY` | Server verification key |

Turnstile is enabled on:

- Home page contact/appeal section
- Contact page “Mesaj göndərin” form

Widget field: `cf-turnstile-response`.

### Local development

1. Install [uv](https://github.com/astral-sh/uv) and Python 3.11+.
2. Create `docker/.env` with the variables above (`POSTGRES_HOST=localhost` when DB runs locally or in Docker).
3. Install dependencies from the repo root:

```bash
uv pip sync uv.lock --system
# or inside a venv:
uv sync
```

4. Start PostgreSQL (local install or `docker compose -f docker/docker-compose.yaml up db -d`).
5. Run migrations and dev server from `averta/`:

```bash
cd averta
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py runserver
```

**Local settings:** `averta/averta/settings_local.py` is imported at the end of `settings.py` when present. It typically sets `DEBUG=True`, relaxes secure cookies, and loads `docker/.env`. For pure production deploys, omit or exclude `settings_local.py`.

**Translations** (after editing `locale/*/LC_MESSAGES/django.po`):

```bash
cd averta
python manage.py compilemessages   # requires GNU gettext (installed in Docker image)
```

On Windows without gettext, compile with Babel:

```bash
python -c "from babel.messages import pofile, mofile; ..."
```

(Docker image includes `gettext`.)

### Docker (production-style stack)

`docker/docker-compose.yaml` runs:

- **db** — PostgreSQL 15
- **web** — Gunicorn (entrypoint: migrate + collectstatic)
- **nginx** — static/media proxy, ports 80/443

```bash
docker compose -f docker/docker-compose.yaml up --build
```

Environment: `docker/.env`. SSL certs mount from `nginx/ssl/`.

### Admin panel

- URL: `https://<domain>/<ADMIN_URL>`
- Use a non-guessable `ADMIN_URL` in production.
- Admin UI language defaults to AZ (`ADMIN_LANGUAGE_CODE`).

### Public forms (AJAX)

Forms marked `data-ajax="1"` submit via `fetch` (`ajax_forms.js`). The server returns JSON for validation errors or success messages without a full page reload.

Applies to: booking, contact/appeal, review.

### Reviews (customer-only)

Review submission checks that the phone number exists on at least one booking marked **Müştərimizdir?** (`is_customer`). Unknown numbers receive a clear validation error (anti-spam / business rule).

### Security notes (production)

- Keep `DEBUG=false` and do not deploy `settings_local.py` to production.
- `settings.py` enables `SECURE_SSL_REDIRECT`, secure session/CSRF cookies behind HTTPS.
- Rotate `SECRET_KEY` and `ADMIN_URL`; restrict `ALLOWED_HOSTS`.
- Serve static/media via Nginx or CDN; do not expose admin on a predictable path.

### Notes

- `pyproject.toml` project name is legacy (`ganaqro`); the site brand is **Averta**.
- CKEditor 4 bundled with `django-ckeditor` has known upstream warnings; consider migrating to CKEditor 5 long term.
