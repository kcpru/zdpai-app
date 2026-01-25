# todo2 backend — dokumentacja techniczna

> Szczegółowy opis architektury i użytych technologii w `backend`.

## 1. Cel i ogólny opis
Backend dostarcza REST API dla aplikacji TODO + feed postów + komentarzy, z autoryzacją JWT i rolą admina. Dane są przechowywane w PostgreSQL. Dodatkowo są dostępne endpointy do generowania motywacyjnych tekstów (Groq) i losowych avatarów (DiceBear), a także upload avatara użytkownika.

## 2. Stos technologiczny (co i do czego)
- **FastAPI** (`app/main.py`, `app/api/*`) — framework HTTP i routing API.
- **Uvicorn** — serwer ASGI uruchamiający aplikację.
- **SQLAlchemy 2.0 (ORM)** (`app/models/*`, `app/db/*`) — modele i operacje na bazie danych.
- **Alembic** (`alembic/`) — migracje schematu bazy.
- **Pydantic v2** (`app/schemas/*`) — walidacja request/response i serializacja JSON.
- **pydantic-settings** (`app/core/config.py`) — konfiguracja z `.env`.
- **python-jose** (`app/core/security.py`) — JWT encode/decode.
- **passlib[bcrypt]** (`app/core/security.py`) — hashowanie i weryfikacja haseł.
- **httpx** (`app/services/*`) — klienci HTTP do usług zewnętrznych.
- **cachetools** (`app/services/motivation.py`) — krótki cache odpowiedzi motywacyjnych.
- **PostgreSQL** — baza danych.
- **Docker / docker-compose** (`Dockerfile`, `docker-compose.yaml`, `start.sh`) — uruchamianie całości lokalnie w kontenerach.

## 3. Struktura katalogów
```
backend/
  app/
    main.py                # Tworzenie aplikacji FastAPI + CORS
    api/
      router.py            # Zbiorczy router
      routes/              # Podział na moduły endpointów
        auth.py
        user.py
        todo.py
        post.py
        motivation.py
        admin.py
        health.py
    core/
      config.py            # Settings + .env
      deps.py              # Zależności (DB, current user, admin)
      security.py          # JWT, bcrypt
    db/
      base.py              # Rejestr modeli
      session.py           # Engine + SessionLocal
      init_db.py           # Seeder
    models/                # SQLAlchemy modele
      user.py
      todo.py
      post.py
    schemas/               # Pydantic DTO (request/response)
      base.py
      auth.py
      user.py
      todo.py
      post.py
    services/
      motivation.py        # Groq prompty + cache
      avatars.py           # DiceBear avatars
    files/
      storage.py           # Dostęp do plików (upload avatarów)
  alembic/                 # Migracje
  Dockerfile
  docker-compose.yaml
  requirements.txt
  pyproject.toml
  start.sh
  docs.md                  # (ten plik)
```

## 4. Konfiguracja i środowisko
Konfiguracja jest wczytywana z `.env` (patrz `.env.example`). Klasa `Settings` w `app/core/config.py` mapuje zmienne środowiskowe.

Najważniejsze zmienne:
- **`DATABASE_URL`** — URL do PostgreSQL (np. `postgresql+psycopg2://user:pass@host:5432/db`).
- **`JWT_KEY`** — sekret do podpisu tokenów.
- **`JWT_ISSUER`** — `iss` w JWT.
- **`JWT_AUDIENCE`** — `aud` w JWT.
- **`JWT_EXPIRES_MINUTES`** — czas życia tokena.
- **`CORS_ORIGINS`** — lista originów, np. `http://localhost:5173,http://localhost:3000`.
- **`GROQ_API_KEY`** / **`GROQ_BASE_URL`** — dostęp do Groq API (motywacje).
- **`RANDOM_AVATARS_BASE_URL`** — DiceBear API (avatary).
- **`FILES_ROOT`** — root dla plików (upload avatarów).

## 5. Warstwa HTTP (API)
Routing zbiorczy w `app/api/router.py`. Każdy obszar funkcjonalny ma własny plik w `app/api/routes/*`.

### 5.1. Autoryzacja i użytkownik
**Plik:** `app/api/routes/auth.py`, `app/api/routes/user.py`

- `POST /api/user/register` — rejestracja (zwraca JWT).
- `POST /api/user/login` — logowanie (zwraca JWT).
- `GET /api/user/me` — dane zalogowanego użytkownika.
- `PUT /api/user/me` — zmiana username/email.
- `POST /api/user/change-password` — zmiana hasła.
- `GET /api/user/{user_id}` — pobierz dane publiczne (username).
- `POST /api/user/me/avatar` — upload avatara.
- `GET /api/user/me/avatar` — pobranie avatara.

**Auth header:**
```
Authorization: Bearer <jwt>
```

### 5.2. TODO listy i zadania
**Plik:** `app/api/routes/todo.py`

- `GET /api/todo/lists` — listy TODO użytkownika.
- `GET /api/todo/lists/{list_id}` — szczegóły listy.
- `POST /api/todo/lists` — nowa lista.
- `PUT /api/todo/lists/{list_id}` — update listy.
- `DELETE /api/todo/lists/{list_id}` — usuń listę.
- `GET /api/todo/lists/{list_id}/tasks` — zadania w liście.
- `POST /api/todo/lists/{list_id}/tasks` — dodaj task.
- `PUT /api/todo/tasks/{task_id}` — update całego taska.
- `PATCH /api/todo/tasks/{task_id}` — partial update (np. `isCompleted`).
- `DELETE /api/todo/tasks/{task_id}` — usuń task.

### 5.3. Posty i komentarze
**Plik:** `app/api/routes/post.py`

- `GET /api/post?start_index=0` — feed postów (paginacja offset).
- `GET /api/post/{post_id}` — pojedynczy post.
- `POST /api/post` — utwórz post z `todo_list_id`.
- `POST /api/post/{post_id}/comments` — dodaj komentarz.
- `POST /api/post/{post_id}/likes` — inkrementuj likes postu.
- `POST /api/post/comments/{comment_id}/likes` — inkrementuj likes komentarza.

### 5.4. Motywacje i avatary
**Plik:** `app/api/routes/motivation.py`

- `POST /api/motivation/list-done` — generuje krótką motywację po zakończeniu taska.
- `GET /api/motivation/random-avatar/{avatar_type}` — losowy avatar (np. `miniavs`, `bottts`).

### 5.5. Admin
**Plik:** `app/api/routes/admin.py`

- `GET /api/admin/users` — lista użytkowników.
- `PATCH /api/admin/users/{user_id}` — aktualizacja usera (username/email/is_admin).
- `DELETE /api/admin/users/{user_id}` — usuń konto.

Dostęp wymaga `is_admin = true` (sprawdzane w `app/core/deps.py`).

## 6. Modele danych (SQLAlchemy)
**Pliki:** `app/models/*`

- `User` (`Users`): `id`, `username`, `email`, `password_hash`, `is_admin`.
- `TodoList` (`TodoLists`): `id`, `name`, `created_at`, `updated_at`, `user_id`.
- `TodoTask` (`TodoTasks`): `id`, `title`, `description`, `is_completed`, `todo_list_id`.
- `Post` (`Posts`): `id`, `content`, `created_at`, `updated_at`, `todo_list_as_json`, `likes_count`.
- `PostComment` (`PostComments`): `id`, `comment_text`, `likes_count`, `post_id`, `user_id`.

Relacje:
- `User -> TodoList` (1:N)
- `TodoList -> TodoTask` (1:N)
- `Post -> PostComment` (1:N)

## 7. Schematy i serializacja (Pydantic)
**Pliki:** `app/schemas/*`

- Wspólny base: `BaseSchema` używa `alias_generator` do camelCase.
- Dzięki temu API zwraca pola w **camelCase**, np. `createdAt`, `isCompleted`.

Przykład:
- Model: `is_completed`
- API: `isCompleted`

## 8. Autoryzacja JWT
**Plik:** `app/core/security.py`
- `create_access_token()` — generuje JWT.
- `decode_token()` — waliduje JWT (`iss`, `aud`, podpis).

Zależności:
- `get_current_user` w `app/core/deps.py` — wyciąga użytkownika z JWT.
- `get_current_admin` — sprawdza rolę admina.

## 9. Seed danych
**Plik:** `app/db/init_db.py`
- Tworzy przykładowych userów, listy, taski, posty i komentarze.
- Admin (domyślny):
  - login: `admin`
  - hasło: `password`

Seed wykonywany:
- automatycznie w `start.sh` (przy starcie kontenera)
- ręcznie: `python -c "from app.db.init_db import seed_data; seed_data()"`

## 10. Migracje (Alembic)
**Folder:** `alembic/`
- `alembic.ini` — konfiguracja połączenia
- `alembic/versions/*` — migracje

Przykładowo:
```
alembic revision --autogenerate -m "add table"
alembic upgrade head
```

## 11. Pliki i upload avatarów
**Plik:** `app/files/storage.py`
- `FileManager` obsługuje zapis/odczyt plików w `FILES_ROOT`.
- Upload avatara: `POST /api/user/me/avatar`.
- Download avatara: `GET /api/user/me/avatar`.

## 12. Usługi zewnętrzne
### 12.1 Groq (motywacje)
**Plik:** `app/services/motivation.py`
- Endpoint: `/api/motivation/list-done`
- Model: `llama-3.1-8b-instant`.
- TTL cache (5s) zapobiega nadmiarowym wywołaniom.

### 12.2 DiceBear (avatary)
**Plik:** `app/services/avatars.py`
- Endpoint: `/api/motivation/random-avatar/{avatar_type}`
- Zwraca losowy SVG.

## 13. Uruchamianie (Docker)
- `Dockerfile` — obraz FastAPI + dependencies.
- `docker-compose.yaml` — backend + PostgreSQL.
- `start.sh` — uruchamia migracje + seed + uvicorn.

Przykład:
```
docker compose up --build
```

## 14. Najważniejsze pliki do startu
- `app/main.py` — punkt wejścia aplikacji.
- `app/api/router.py` — podłącza route’y.
- `app/core/config.py` — konfiguracja z `.env`.
- `app/db/session.py` — połączenie z bazą.

## 15. Częste modyfikacje
- **Nowy endpoint**: dodaj w `app/api/routes/*` + podłącz w `router.py`.
- **Nowe pole w DB**: aktualizuj model w `app/models/*` + migracja Alembic.
- **Nowy DTO**: dodaj w `app/schemas/*`.
- **Zmiana configu**: `app/core/config.py` + `.env.example`.
