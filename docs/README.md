# Documentation

## Start here

| Document | What it covers |
|---|---|
| [../README.md](../README.md) | Project overview, installation, feature summary |
| [../ARCHITECTURE.md](../ARCHITECTURE.md) | System design, layering, API surface, data flow |
| [../backend/app/ml/README.md](../backend/app/ml/README.md) | **ML integration contract** — read before training the volatility model |

## Guides

| Document | What it covers |
|---|---|
| [deployment.md](deployment.md) | Deployment notes and environment configuration |
| [testing.md](testing.md) | Manual test walkthroughs per module |
| [../CONTRIBUTING.md](../CONTRIBUTING.md) | Branching, commit format, PR process |

## Module reference

One document per feature module: data model, endpoints, algorithm and
frontend wiring.

| Module | Document |
|---|---|
| Financial Profile | [modules/financial-profile.md](modules/financial-profile.md) |
| Risk Profiling | [modules/risk-profiling.md](modules/risk-profiling.md) |
| Portfolio Recommendation | [modules/portfolio-recommendation.md](modules/portfolio-recommendation.md) |
| Portfolio Analytics | [modules/portfolio-analytics.md](modules/portfolio-analytics.md) |
| Diversification Analysis | [modules/diversification.md](modules/diversification.md) |
| Monte Carlo Simulation | [modules/monte-carlo.md](modules/monte-carlo.md) |
| SIP Planner | [modules/sip-planner.md](modules/sip-planner.md) |
| Stock Explorer | [modules/stock-explorer.md](modules/stock-explorer.md) |
| Stock Predictor | [modules/stock-predictor.md](modules/stock-predictor.md) |

## Live API reference

With the backend running, interactive docs are generated from the code
itself and are always current:

- Swagger UI — http://localhost:8000/docs
- ReDoc — http://localhost:8000/redoc

## A note on these documents

This project previously carried ~50 overlapping status reports at the
repository root. They contradicted one another and several described
behaviour that had since changed — notably claiming endpoints required
no authentication and that passwords were stored in plain text, neither
of which is true.

They were consolidated into the set above. The originals remain in git
history and can be recovered with:

```bash
git log --diff-filter=D --name-only          # list what was removed
git show <commit>:PROJECT_COMPLETE_STATUS.md # read any one of them
```

Where a document describes behaviour, prefer the code and the live API
docs as the authority.
