# Publishing Guide (GitHub)

This document describes the recommended flow to publish this POC to GitHub.

## 1) Pre-publish checklist

- Application starts with `./launch_ui.sh`.
- Tests pass with `python -m pytest -q` in the virtual environment.
- `.env` is excluded from version control.
- `.env.example` contains only placeholder values.
- `outputs/` is excluded from version control.

## 2) Initialize local Git repository (first time only)

From project root:

```bash
git init
git add .
git commit -m "Initial publish-ready POC: vision recognition"
```

## 3) Connect GitHub remote and push

Replace values below with your repository details:

```bash
git branch -M main
git remote add origin https://github.com/<your-org-or-user>/<repo-name>.git
git push -u origin main
```

## 4) Optional: create a release tag

```bash
git tag -a v0.1.0 -m "POC vision recognition v0.1.0"
git push origin v0.1.0
```

## 5) Security notes

- Never commit `.env`.
- Rotate Azure keys if credentials were ever shared outside trusted scope.
- Keep API keys in GitHub Secrets for CI/CD usage.
