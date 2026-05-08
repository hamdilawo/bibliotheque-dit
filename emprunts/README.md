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
docker compose up --build --env-file .env.docker.db --remove-orphans
```

---

### 🛠️ Method 2 — Manual

#### 1. Install `uv` (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 2. Start the services

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

---

### Access the API docs

Navigate to the docs URL and use the token defined in `.env` (see `.env.example` for reference).