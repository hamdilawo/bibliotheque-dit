# DIT Library

## Prerequisites

- Docker & Docker Compose
- Python 3.14+

---

## Getting Started

Choose one of the two methods below.

---

### 🐳 Method 1 — Docker only

#### 1. Set up environment files

```bash
cp .env.example .env.prod
```

Then create `.env.docker.db`:

```dotenv
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
```

> ⚠️ Make sure the DB credentials in `.env.docker.db` match the database section in `.env.prod`.

#### 2. Start the services

```bash
docker compose --env-file .env.docker.db up --build --remove-orphans
```

#### 3. Open the app

Navigate to [http://localhost:8008/api/docs/](http://localhost:8008/api/docs/)

---

### 🛠️ Method 2 — Manual

#### 1. Install `uv` (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 2. Start the database

```bash
docker compose up db
```

#### 3. Apply migrations

```bash
uv run python manage.py migrate
```

#### 4. Run the development server

```bash
uv run python manage.py runserver
```

#### 5. Open the app

Navigate to [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)

---

### 🔑 Authenticate on the API docs

Once the app is running, open the docs URL above and set the following cookie in your browser:

**Cookie name:** `access_token`

**Cookie value:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwidXNlcl9pZCI6IjAwMDEiLCJ1c2VyX3JvbGUiOiJzdHVkZW50IiwidXNlcl9lbWFpbCI6ImpvaG4uZG9lQGNnbC5kZXYiLCJpc19hY3RpdmUiOnRydWUsImlhdCI6MTUxNjIzOTAyMiwiZXhwIjoxNzgwOTYwNDg0fQ.3F-VsntKXg17zcmd3IDfzvoFmeSr7cGsA1dLKKctFLo
```

> 💡 You can set cookies via your browser's DevTools → **Application** → **Cookies** → select the localhost URL → add a new entry with the name and value above.