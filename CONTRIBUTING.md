# Contributing to Finanzapp

Thank you for your interest in contributing to **Finanzapp**. This document describes how changes should be made in a structured, traceable, and stable way.

The goal is a **clear and maintainable workflow** with minimal overhead.

---

## 1. Project Overview

Finanzapp is a locally operated application for managing household finances.

- Backend: FastAPI (Python 3.11), PostgreSQL
- Frontend: Vue 3, Bootstrap 5
- Target platform: Raspberry Pi (local)

The project focuses on:
- Stability
- Transparency of financial data
- Clear separation between development and production environments

---

## 2. Branch Strategy (binding)

There are two main branches:

### `main`
- **Production branch**
- Contains only tested and stable code
- Every merge into `main` is versioned (Git tag / GitHub release)

### `develop`
- **Development branch**
- Current state of ongoing development
- May temporarily contain unfinished features

### Feature branches (optional)

For larger changes, feature branches may be used:

```
feature/<short-description>
```

Examples:
- `feature/category-stats`
- `feature/monthly-summary`

Feature branches are **always merged into `develop`** and deleted afterwards.

---

## 3. Development Workflow

1. Always start from `develop`
   ```bash
   git checkout develop
   git pull
   ```

2. Optional: create a feature branch
   ```bash
   git checkout -b feature/<name>
   ```

3. Implement your changes

4. Commit changes (small, clear commits)
   ```bash
   git commit -m "Short description of the change"
   ```

5. Merge into `develop`
   ```bash
   git checkout develop
   git merge feature/<name>
   ```

6. Delete the feature branch
   ```bash
   git branch -d feature/<name>
   ```

---

## 4. Commits & Commit Messages

Commit messages should be:
- concise
- unambiguous
- descriptive

Recommended format:

```
<verb> <object / scope>
```

Examples:
- `Fix ist value persistence in monthly view`
- `Add scroll-to-top button`
- `Refactor yearly overview calculation`

---

## 5. Releases & Versioning

Releases are created **exclusively from `main`**.

### Versioning

A simplified semantic versioning scheme is used:

```
v0.MINOR.PATCH
```

Examples:
- `v0.1.0` – Initial release
- `v0.1.1` – Bugfix
- `v0.2.0` – New feature

### Release Process

1. `develop` is stable
2. Merge `develop` → `main`
3. Create a tag:
   ```bash
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin vX.Y.Z
   ```
4. Create a GitHub release

---

## 6. Configuration (Dev vs. Prod)

The codebase is identical across all environments.

Differences are handled **exclusively via configuration**:

- `.env.dev`
- `.env.prod`

Examples:
- Database URL
- Debug flags
- API endpoints

⚠️ **No production-specific logic in code.**

---

## 7. Quality & Stability Checks

Before merging into `main`, ensure:

- Backend starts without errors
- Frontend builds successfully
- Core features (month / year / account balance) work correctly
- Known limitations are documented

---

## 8. Issues & Ongoing Development

New ideas, bugs, or improvements should be tracked using GitHub Issues.

Recommended labels:
- `bug`
- `enhancement`
- `refactor`
- `idea`

This keeps planning and history transparent – even for single-developer projects.

---

## 9. Guiding Principles

- Stability over feature quantity
- Transparency over automation
- Clear separation of planning (planned balance) and reality (actual balance)

---

Thank you for contributing to Finanzapp.

