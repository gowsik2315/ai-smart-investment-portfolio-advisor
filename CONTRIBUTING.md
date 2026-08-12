# Contributing to AI Smart Investment Portfolio Advisor

Thanks for taking the time to contribute! This guide covers everything you need to get started.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Branch Naming](#branch-naming)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

---

## Code of Conduct

Be respectful, inclusive, and constructive. We welcome contributors of all experience levels.

---

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/your-username/ai-smart-investment-portfolio-advisor.git
   cd ai-smart-investment-portfolio-advisor
   ```
3. **Set up the project** by following the [README](README.md) setup instructions
4. **Create a branch** for your work (see [Branch Naming](#branch-naming))

---

## Development Workflow

```bash
# 1. Keep your fork up to date
git remote add upstream https://github.com/ORIGINAL_OWNER/ai-smart-investment-portfolio-advisor.git
git fetch upstream
git checkout main
git merge upstream/main

# 2. Create your feature branch
git checkout -b feature/your-feature-name

# 3. Make your changes, then commit
git add <specific-files>
git commit -m "feat: add portfolio rebalancing endpoint"

# 4. Push and open a PR
git push origin feature/your-feature-name
```

---

## Branch Naming

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature/<short-description>` | `feature/pdf-export` |
| Bug fix | `fix/<short-description>` | `fix/auth-token-refresh` |
| Docs | `docs/<short-description>` | `docs/api-examples` |
| Refactor | `refactor/<short-description>` | `refactor/risk-service` |
| Chore | `chore/<short-description>` | `chore/update-deps` |

---

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <short summary>

[optional body]

[optional footer]
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples:**
```
feat: add Monte Carlo export to CSV
fix: resolve CORS issue on production build
docs: update API endpoint table in README
refactor: extract risk scoring into separate service
```

---

## Pull Request Process

1. Ensure your branch is up to date with `main`
2. Fill in the PR template completely
3. Link the related issue (e.g. `Closes #42`)
4. Verify the app runs without errors locally
5. Keep PRs focused — one feature or fix per PR
6. Request a review from at least one maintainer

PRs will be merged once approved and all checks pass.

---

## Coding Standards

### Backend (Python)

- Follow **PEP 8** style
- Use **type hints** on all function signatures
- Write **docstrings** for all public functions and classes
- Keep route handlers thin — business logic belongs in `services/`
- Never commit secrets or hardcoded credentials
- Add new dependencies to `requirements.txt`

```python
# Good
async def calculate_risk_score(profile: FinancialProfile) -> float:
    """Calculate normalized risk score (0-100) from financial profile."""
    ...

# Bad
async def calc(p):
    ...
```

### Frontend (React / JavaScript)

- Use **functional components** with hooks
- Keep components small and focused
- Use the existing `services/` layer for all API calls — no direct `fetch`/`axios` in components
- Follow existing naming conventions (`PascalCase` for components, `camelCase` for functions)
- Remove unused imports and variables before committing

### General

- No commented-out dead code in PRs
- No `console.log` / `print` debug statements left in
- Test your changes end-to-end before opening a PR

---

## Reporting Bugs

Open a [Bug Report issue](../../issues/new?template=bug_report.md) and include:

- Steps to reproduce
- Expected vs actual behavior
- Screenshots or logs if applicable
- Environment (OS, Python version, Node version)

---

## Suggesting Features

Open a [Feature Request issue](../../issues/new?template=feature_request.md) and describe:

- The problem you're trying to solve
- Your proposed solution
- Any alternatives you considered

---

## Questions?

Open a [Discussion](../../discussions) or an issue labeled `question`.
