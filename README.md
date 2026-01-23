# Finanzapp

Finanzapp is a self-hosted web application for managing personal household finances. It focuses on recurring items, ad-hoc transactions, and planned vs. actual account balances, with a clear separation between frontend and backend.

This repository represents a stable and practically usable baseline starting with release **v1.0.1**.

---

## Architecture

The application consists of three main components:

### Frontend

* Vue 3 (Vue CLI / Webpack)
* Bootstrap 5
* Built as static assets (`dist/`)
* Served via nginx

### Backend

* FastAPI (Python 3.11)
* PostgreSQL
* Runs as a systemd service

### Reverse Proxy

* nginx
* Serves the frontend
* Proxies `/api/*` requests to the backend

```
Browser
  → nginx
    → /            → Frontend (Vue)
    → /api/*       → FastAPI backend
```

---

## Production Setup

### Frontend

```bash
npm install
npm run build
```

The generated `dist/` directory is served by nginx.

### Backend

```bash
pip install -r requirements.txt
```

The backend is typically run as a systemd service and listens on `0.0.0.0`.

---

## Configuration

Configuration is handled via environment variables.

Common examples:

* `DATABASE_URL`
* `API_BASE_URL` (used by the frontend)

Exact values depend on the target environment and are intentionally not hard-coded.

---

## Documentation

User-facing documentation is maintained separately:

* **User Guide:** `docs/user-guide.md`

This README intentionally focuses on system-level and operational aspects.

---

## Status and Branching

* Core functionality implemented (monthly and yearly overview, fixed expenses and income)
* Backend and frontend integration stable
* Critical baseline issues fixed as of `v1.0.1`
* Frontend error handling is still minimal

Branching model:

* `main` – stable, deployable state
* `dev` – ongoing development and refactoring

---

## License

Private project. No license granted.
