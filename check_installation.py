"""
Installation verification for the AI Smart Investment Portfolio Advisor.

Run from the repository root:

    python check_installation.py

Output is deliberately plain ASCII. The previous version used check and
cross marks, which raise UnicodeEncodeError on Windows whenever stdout
is not UTF-8 - that is, any time the output is piped or redirected to a
file, which is exactly when you would want a log of it.
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"

if os.name == "nt":
    VENV_PY = BACKEND / "venv" / "Scripts" / "python.exe"
else:
    VENV_PY = BACKEND / "venv" / "bin" / "python"

PASS, FAIL, WARN = "[ OK ]", "[FAIL]", "[WARN]"

results = []


def report(status: str, label: str, detail: str = "") -> None:
    line = f"  {status} {label}"
    if detail:
        line += f" - {detail}"
    print(line)
    results.append(status)


def run(args, **kw):
    """Run a command, returning (ok, combined output)."""
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=120, **kw)
        return p.returncode == 0, (p.stdout + p.stderr).strip()
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def heading(text: str) -> None:
    print()
    print(text)
    print("-" * len(text))


def main() -> int:
    print("=" * 62)
    print("INSTALLATION VERIFICATION")
    print("=" * 62)

    # ---- Interpreters -------------------------------------------------
    heading("1. Interpreters")

    ok, out = run([sys.executable, "--version"])
    report(PASS if ok else FAIL, "Python", out)

    ok, out = run(["node", "--version"], shell=(os.name == "nt"))
    report(PASS if ok else FAIL, "Node.js", out if ok else "not found on PATH")

    # ---- Virtual environment -----------------------------------------
    heading("2. Backend virtual environment")

    if not VENV_PY.exists():
        report(FAIL, "venv", f"missing at {VENV_PY.relative_to(ROOT)}")
        report(WARN, "next step", "cd backend && python -m venv venv")
        return summarise()

    ok, out = run([str(VENV_PY), "--version"])
    report(PASS if ok else FAIL, "venv interpreter", out)

    # ---- Dependencies -------------------------------------------------
    heading("3. Python packages")

    groups = {
        "web":      ["fastapi", "uvicorn", "pydantic"],
        "database": ["sqlalchemy", "alembic"],
        "auth":     ["jose", "bcrypt"],
        "data":     ["pandas", "numpy", "scipy"],
        "ml":       ["sklearn", "joblib", "arch", "statsmodels", "pyarrow"],
        "market":   ["yfinance"],
        "testing":  ["pytest"],
    }
    for group, mods in groups.items():
        missing = []
        for m in mods:
            ok, _ = run([str(VENV_PY), "-c", f"import {m}"])
            if not ok:
                missing.append(m)
        if missing:
            report(FAIL, f"{group:<9}", f"missing: {', '.join(missing)}")
        else:
            report(PASS, f"{group:<9}", ", ".join(mods))

    if any(r == FAIL for r in results[-len(groups):]):
        report(WARN, "next step", "cd backend && pip install -r requirements.txt")

    # ---- Configuration ------------------------------------------------
    heading("4. Configuration")

    env = BACKEND / ".env"
    if env.exists():
        text = env.read_text(encoding="utf-8", errors="replace")
        report(PASS, "backend/.env", "present")
        if "your-secret-key" in text or "change-in-production" in text:
            report(WARN, "SECRET_KEY", "still the placeholder - generate one before deploying")
        else:
            report(PASS, "SECRET_KEY", "customised")
    else:
        report(FAIL, "backend/.env", "missing - copy .env.example to .env")

    report(
        PASS if (FRONTEND / ".env").exists() else WARN,
        "frontend/.env",
        "present" if (FRONTEND / ".env").exists() else "missing (defaults will be used)",
    )

    # ---- Database -----------------------------------------------------
    heading("5. Database")

    ok, out = run([str(VENV_PY), "-m", "alembic", "current"], cwd=str(BACKEND))
    if ok:
        rev = next((l for l in out.splitlines() if "head" in l or l.strip()[:4].isalnum()), out)
        report(PASS, "migrations", rev.strip()[:60] or "applied")
    else:
        report(WARN, "migrations", "could not read state - run: alembic upgrade head")

    # ---- Application --------------------------------------------------
    heading("6. Application")

    ok, out = run(
        [str(VENV_PY), "-c",
         "from app.main import app; print(len(app.openapi()['paths']), 'paths')"],
        cwd=str(BACKEND),
    )
    report(PASS if ok else FAIL, "backend imports", out.splitlines()[-1] if out else "")

    report(
        PASS if (FRONTEND / "node_modules").exists() else FAIL,
        "node_modules",
        "present" if (FRONTEND / "node_modules").exists() else "run: cd frontend && npm install",
    )

    # ---- Optional services -------------------------------------------
    heading("7. Optional services")

    ok, out = run([str(VENV_PY), "-c",
                   "import httpx; r=httpx.get('http://localhost:11434/api/tags', timeout=5);"
                   "print(len(r.json().get('models', [])), 'model(s)')"])
    report(
        PASS if ok else WARN,
        "Ollama",
        out.splitlines()[-1] if ok else "not running - AI explanations will be unavailable",
    )

    model = BACKEND / "models" / "volatility_model.joblib"
    report(
        PASS if model.exists() else WARN,
        "volatility model",
        "present" if model.exists()
        else "not trained - forecasts fall back to historical volatility",
    )

    return summarise()


def summarise() -> int:
    failures = results.count(FAIL)
    warnings = results.count(WARN)

    print()
    print("=" * 62)
    if failures:
        print(f"RESULT: {failures} failure(s), {warnings} warning(s) - setup incomplete")
    elif warnings:
        print(f"RESULT: ready, with {warnings} warning(s) (optional items)")
    else:
        print("RESULT: all checks passed")
    print("=" * 62)

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
