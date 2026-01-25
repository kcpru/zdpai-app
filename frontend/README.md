# todo2 frontend

Frontend aplikacji **todo2** zbudowany na **React + Vite**.

## Wymagania
- Node.js (LTS)

## Konfiguracja
Frontend komunikuje się z backendem przez zmienną środowiskową:

- `VITE_API_URL` — bazowy URL do API (np. `http://localhost:8000/api`).

Jeśli nie ustawisz `.env`, kod ma fallback do `http://localhost:8080/api`.

Przykład `frontend/.env`:

	VITE_API_URL=http://localhost:8000/api

## Instalacja

	cd frontend
	npm install

## Uruchomienie (dev)

	cd frontend
	npm run dev

## Build produkcyjny

	cd frontend
	npm run build

Podgląd buildu lokalnie:

	cd frontend
	npm run preview

## Formatowanie i lint

	cd frontend
	npm run format
	npm run lint
