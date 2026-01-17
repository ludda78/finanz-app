# Release Guide – Finanzapp

This document defines the **official release process** for Finanzapp.  
Its purpose is to ensure that every release is **stable, reproducible, and traceable**.

The process is intentionally lightweight and optimized for a **single-maintainer or small-team workflow**.

---

## 1. Release Principles

- Releases are created **only from `main`**
- `main` must always be production-ready
- Every release is tied to a **Git tag**
- Production systems run **tags, not branches**
- Stability has priority over speed

---

## 2. When to Create a Release

A new release should be created when one or more of the following applies:

- Bugfixes affecting correctness or data integrity
- User-facing improvements
- New completed features
- Internal refactorings that improve stability

Do **not** create releases for:
- work-in-progress changes
- experimental features
- untested refactors

---

## 3. Pre-Release Checklist

Before merging into `main`, verify:

### Code & Functionality
- [ ] Backend starts without errors
- [ ] Frontend builds successfully
- [ ] Monthly overview works correctly
- [ ] Yearly overview works correctly
- [ ] Ist/Soll calculations are correct
- [ ] No debug output enabled

### Repository State
- [ ] `develop` is stable
- [ ] Working tree is clean
- [ ] All relevant changes are committed
- [ ] Documentation updated if needed

---

## 4. Release Workflow

### Step 1: Merge `develop` into `main`

```bash
git checkout main
git pull
git merge develop
```

Resolve conflicts if necessary and verify functionality.

---

### Step 2: Create Release Commit (if needed)

If minor release-specific adjustments are required (e.g. documentation):

```bash
git commit -m "Prepare release vX.Y.Z"
```

---

### Step 3: Create Git Tag

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

Tag format:
```
v0.MINOR.PATCH
```

Examples:
- `v0.1.0`
- `v0.1.1`
- `v0.2.0`

---

### Step 4: Create GitHub Release

On GitHub:

- Select the tag `vX.Y.Z`
- Title: `Release vX.Y.Z`
- Description should include:
  - Summary of changes
  - Notable fixes or improvements
  - Known limitations (if any)

---

## 5. Post-Release Verification

After deploying the new release:

- [ ] Backend starts correctly in production
- [ ] Frontend loads correctly
- [ ] Database migrations (if any) are applied
- [ ] Core workflows verified manually

---

## 6. Rollback Procedure

If a release causes issues:

```bash
git checkout vPREVIOUS
```

Restart services. No additional steps should be required.

---

## 7. Versioning Strategy

Finanzapp uses **semantic versioning (simplified)**:

- **MINOR**: new features or noticeable improvements
- **PATCH**: bugfixes and small corrections

Major version `1.0.0` will be used once:
- data model is stable
- core features are complete
- breaking changes are unlikely

---

## 8. Common Mistakes to Avoid

- Deploying from `develop`
- Running production on a branch instead of a tag
- Skipping manual verification
- Creating releases without documentation updates

---

## 9. Summary

A good release is:
- boring
- predictable
- reversible

If a release feels rushed, it probably is.

---

This guide is part of the official Finanzapp documentation.

