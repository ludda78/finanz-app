# Deployment Guide – Finanzapp

This document describes how to deploy **Finanzapp** in a clean and reproducible way, with a clear separation between **development** and **production** environments.

The primary target platform is a **Raspberry Pi** running Linux.

---

## 1. Deployment Goals

- Stable production system for daily use
- Separate development environment for testing and changes
- Identical codebase in all environments
- Configuration-driven behavior (no env-specific code)
- Simple operation and recovery

---

## 2. Recommended Directory Layout

It is strongly recommended to keep **dev** and **prod** deployments separate on the filesystem.

```text
/opt/finanzapp/
├── prod/
│   ├── backend/
│   ├── frontend/
│   ├── .env
│   └── logs/
└── dev/
    ├── backend/
    ├── frontend/
    ├── .env
    └── logs/
```

- `prod` always runs a **released version** (tag from `main`)
- `dev` tracks the `develop` branch

---

## 3. Git Strategy for Deployment

### Production

```bash
git clone https://github.com/<user>/finanz-app.git
cd finanz-app
git checkout main
git pull
git checkout vX.Y.Z
```

Production should always run on a **specific Git tag**, never on a moving branch.

### Development

```bash
git clone https://github.com/<user>/finanz-app.git
cd finanz-app
git checkout develop
git pull
```

---

## 4. Environment Configuration

### Environment Files

Each environment uses its own `.env` file:

- `.env.prod`
- `.env.dev`

Example:

```env
# Backend
DATABASE_URL=postgresql://finanzapp:***@localhost:5432/finanzapp
DEBUG=false

# Frontend
VUE_APP_API_URL=http://localhost:8000
```

⚠️ Never commit `.env` files to Git.

---

## 5. Backend Deployment (FastAPI)

### Recommended Runtime

- Python 3.11
- Virtual environment per deployment

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Start Backend

Development:
```bash
uvicorn main:app --reload --port 8001
```

Production:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

For production use, running via a process manager (e.g. systemd) is recommended.

---

## 6. Frontend Deployment (Vue 3)

### Development

```bash
npm install
npm run serve
```

Default dev port:
- `http://localhost:8081`

### Production

```bash
npm install
npm run build
```

The build output (`dist/`) should be served by a web server (e.g. nginx).

---

## 7. Port Mapping (Recommended)

| Environment | Backend | Frontend |
|------------|---------|----------|
| Production | 8000    | 80       |
| Development| 8001    | 8081     |

---

## 8. Database (PostgreSQL)

- One database per environment is recommended
- Example:
  - `finanzapp_prod`
  - `finanzapp_dev`

Backups should be taken regularly (daily recommended).

---

## 9. Updates & Rollback

### Updating Production

1. Stop services
2. Fetch latest tags
3. Checkout new version
4. Restart services

```bash
git fetch --tags
git checkout vX.Y.Z
```

### Rollback

```bash
git checkout vPREVIOUS
```

Rollback is instant because no state is stored in the codebase.

---

## 10. Operational Notes

- Monitor disk space and memory (Raspberry Pi)
- Keep database backups off-device if possible
- Prefer stability over frequent updates

---

## 11. Future Improvements

- Docker-based deployment
- Automated backups
- CI-driven build artifacts

---

This deployment guide is intentionally simple and pragmatic, optimized for local and long-running operation.

