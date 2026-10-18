<!--
DOCUMENT GENERATION NOTES (delete this block before submission)
- Source format: Markdown. Convert to .docx/.pdf with Claude, Pandoc, or VS Code "Markdown PDF".
- Page breaks are marked with <div style="page-break-after: always;"></div>.
- Diagrams are Mermaid code blocks. Render them to images (mermaid.live, or `mmdc`) when building a Word file.
- Screenshots are in ./figures/ (relative to this file).
- Every [BRACKETED] value is a placeholder to fill in: team members, course code, guide, examiners, dates.
- Every number in this report was measured on the running system (local machine, October 2026) or computed by the project's own code. See Appendix C for how to reproduce them.
- Suggested Word styling: Times New Roman 12 pt body, 14 pt bold chapter titles, 1.5 line spacing, justified text, page numbers bottom-centre (roman numerals for front matter).
-->

<div align="center">

# AI SMART INVESTMENT PORTFOLIO ADVISOR

### FinIntelAI — Risk Profiling, Portfolio Analytics, ML-Based Volatility Forecasting and LLM-Generated Explanations for Retail Investors

<br>

**PROJECT REPORT**

<br>

Submitted by

| Name | Roll Number |
|---|---|
| GOWSIK R | 23I219 |
| [TEAM MEMBER 2] | [ROLL NO] |
| [TEAM MEMBER 3] | [ROLL NO] |
| [TEAM MEMBER 4] | [ROLL NO] |

<br>

in partial fulfilment of the requirements for the course

**[COURSE CODE] – [COURSE NAME]**

<br>

of

**BACHELOR OF TECHNOLOGY**

in

**INFORMATION TECHNOLOGY**

<br>

[MONTH YEAR]

<br>

**DEPARTMENT OF INFORMATION TECHNOLOGY**

**PSG COLLEGE OF TECHNOLOGY**

(Autonomous Institution)

**COIMBATORE – 641 004**

</div>

<div style="page-break-after: always;"></div>

<div align="center">

## PSG COLLEGE OF TECHNOLOGY

(Autonomous Institution)

**COIMBATORE – 641 004**

<br>

### BONAFIDE CERTIFICATE

</div>

Certified that this project report titled **"AI SMART INVESTMENT PORTFOLIO ADVISOR"** is the bonafide work of

| Name | Roll Number |
|---|---|
| GOWSIK R | 23I219 |
| [TEAM MEMBER 2] | [ROLL NO] |
| [TEAM MEMBER 3] | [ROLL NO] |
| [TEAM MEMBER 4] | [ROLL NO] |

who carried out the project under my supervision. It is submitted in partial fulfilment of the requirements for the course **[COURSE CODE] – [COURSE NAME]** of the degree of **Bachelor of Technology in Information Technology** of PSG College of Technology during the academic year [YYYY – YYYY].

<br><br>

| | |
|---|---|
| **[Dr. GUIDE NAME]** | **Dr. UMAMAHESWARI K** |
| Faculty Guide | Professor and Head |
| Department of Information Technology | Department of Information Technology |
| PSG College of Technology | PSG College of Technology |

<br>

Submitted for the viva-voce examination held on ____________________

<br><br>

| | |
|---|---|
| **Internal Examiner** | **External Examiner** |

<div style="page-break-after: always;"></div>

## ACKNOWLEDGEMENT

We express our sincere gratitude to **Dr. K. Prakasan**, Principal, PSG College of Technology, for providing the facilities and the academic environment that made this project possible.

We are deeply thankful to **Dr. Umamaheswari K**, Professor and Head, Department of Information Technology, for her constant encouragement and for giving us the opportunity to work on a project that combines finance, machine learning and full-stack engineering.

We thank **[Dr. PROGRAMME COORDINATOR NAME]**, Programme Coordinator, for her guidance on the course structure and evaluation.

We are especially grateful to our faculty guide, **[Dr. GUIDE NAME]**, for valuable suggestions, critical reviews and steady support at every stage, from the proposal to the final evaluation of the volatility model.

We thank all the faculty members and technical staff of the Department of Information Technology for their help. We acknowledge the open-source communities behind FastAPI, React, scikit-learn, NumPy, pandas, yfinance and Ollama, whose tools form the foundation of this system.

Finally, we thank our families and friends for their patience and encouragement throughout the project.

<div style="page-break-after: always;"></div>

## ABSTRACT

Retail participation in Indian equity and mutual-fund markets has grown rapidly, but most new investors decide without understanding their own risk capacity, the risk of the portfolio they hold, or what a range of future outcomes looks like. Human advice is expensive, commercial robo-advisors are opaque about how they reach a recommendation, and generic calculators give one deterministic number that hides uncertainty. This project presents the **AI Smart Investment Portfolio Advisor (FinIntelAI)**, a full-stack web platform that turns an investor's financial profile into a quantified risk score, an asset allocation, portfolio risk analytics and probabilistic projections. Every result comes with a plain-language explanation produced by a locally hosted large language model.

The system is built on a **FastAPI** backend (Python 3.13, SQLAlchemy 2.0, Alembic) and a **React 18** frontend with Tailwind CSS and Recharts. It exposes **58 REST operations** across **12 modules**:
- authentication (JWT, bcrypt)
- financial profiling
- weighted multi-factor risk scoring
- score-proportional asset allocation
- portfolio risk analytics (annualised volatility, Sharpe ratio, maximum drawdown)
- diversification analysis (sector and asset-class concentration with a Herfindahl–Hirschman index)
- Monte Carlo simulation (geometric Brownian motion with Itô-corrected drift, VaR and CVaR)
- SIP planning
- live market data from Yahoo Finance
- an ML volatility forecaster
- a 21-day Stock Predictor outlook
- explanations from the **Qwen2.5-3B** model served through **Ollama**

The LLM runs entirely on the user's machine, so no financial data leaves it. Explanations are cached in the database, and the Stock Predictor's explanation passes a deterministic output guard that rejects investment advice and statements of certainty.

The machine-learning component forecasts **21-trading-day forward realised volatility** from **21 engineered features** (multi-horizon realised volatility, Parkinson and Garman–Klass range estimators, momentum, RSI, drawdown and Nifty 50 market context). It was trained on 21,990 rows covering 10 NSE large-cap stocks (2017–2026), using a chronological split with a 21-trading-date embargo and walk-forward cross-validation. Out of sample (4,390 test rows), the selected ridge model on log-volatility reached RMSE 0.0676 and QLIKE 0.1949. Against naive persistence it improved RMSE by 17.8% (95% block-bootstrap interval 8.4% to 25.9%) and QLIKE by 46.4% (22.3% to 62.4%). It also beat the HAR and GARCH(1,1) baselines in point estimates, although its advantage over HAR is not statistically significant. The forecast feeds the Monte Carlo simulator and the Stock Predictor's expected price range, with a transparent fallback to historical volatility whenever no valid forecast exists.

The backend is verified by **338 automated tests** (336 passed, 2 skipped, 30 s) and by 12 black-box API checks. On a local machine:
- Typical analytical endpoints respond in **10–36 ms**.
- A 10,000-path, 10-year Monte Carlo simulation completes in **0.53 s**.
- A volatility forecast takes **117 ms**.

The project shows that a transparent, explainable and statistically honest advisory tool can be built entirely from open-source components and run on commodity hardware.

**Keywords:** Robo-advisory, Risk Profiling, Asset Allocation, Monte Carlo Simulation, Value at Risk, Volatility Forecasting, HAR Model, Ridge Regression, Large Language Models, Explainable AI, FastAPI, React.

<div style="page-break-after: always;"></div>

## TABLE OF CONTENTS

| Chapter | Title | Page |
|---|---|---|
| | Acknowledgement | i |
| | Abstract | ii |
| | List of Figures | v |
| | List of Tables | vi |
| | List of Abbreviations | viii |
| **1** | **INTRODUCTION** | 1 |
| 1.1 | Overview | 1 |
| 1.2 | Problem Context | 2 |
| 1.3 | Motivation | 3 |
| 1.4 | Objectives | 4 |
| 1.5 | Scope of the Project | 5 |
| 1.6 | Organisation of the Report | 6 |
| **2** | **LITERATURE SURVEY** | 7 |
| 2.1 | Existing Research | 7 |
| 2.2 | Related Works | 12 |
| 2.3 | Limitations of Existing Systems | 15 |
| 2.4 | Research Gap and Proposed Contribution | 16 |
| **3** | **SYSTEM REQUIREMENTS** | 17 |
| 3.1 | Project Specification | 17 |
| 3.2 | Functional Requirements | 18 |
| 3.3 | Non-Functional Requirements | 21 |
| 3.4 | Software Requirements | 22 |
| 3.5 | Hardware Requirements | 23 |
| 3.6 | External Services and Data Sources | 24 |
| **4** | **SYSTEM DESIGN** | 25 |
| 4.1 | System Architecture | 25 |
| 4.2 | Tier and Component Description | 27 |
| 4.3 | Module Design | 28 |
| 4.4 | Database Design | 30 |
| 4.5 | Key Design Patterns | 35 |
| 4.6 | Machine Learning Pipeline Design | 38 |
| 4.7 | API Design | 41 |
| 4.8 | Interaction Flows | 44 |
| 4.9 | Security Controls | 46 |
| 4.10 | User Interface Design | 47 |
| **5** | **IMPLEMENTATION** | 48 |
| 5.1 | Technology Stack | 48 |
| 5.2 | Project Structure | 50 |
| 5.3 | Backend Services | 51 |
| 5.4 | Machine Learning Implementation | 60 |
| 5.5 | LLM Explanation Layer | 65 |
| 5.6 | Frontend Implementation | 68 |
| 5.7 | Database Migrations and Configuration | 71 |
| 5.8 | Development Workflow | 72 |
| **6** | **TESTING REPORTS** | 73 |
| 6.1 | Testing Strategy | 73 |
| 6.2 | Unit Testing | 74 |
| 6.3 | Integration and API Testing | 84 |
| 6.4 | Testing Tools | 86 |
| 6.5 | Test Coverage Summary | 87 |
| **7** | **RESULTS AND ANALYSIS** | 88 |
| 7.1 | Module-wise Results | 88 |
| 7.2 | Validation of Financial Computations | 97 |
| 7.3 | Volatility Model Evaluation | 100 |
| 7.4 | Performance Benchmarks | 104 |
| 7.5 | Capacity Analysis | 106 |
| 7.6 | Security Compliance Matrix | 107 |
| 7.7 | Discussion and Known Limitations | 108 |
| **8** | **CONCLUSION** | 110 |
| **9** | **FUTURE WORK** | 112 |
| | **BIBLIOGRAPHY** | 115 |
| | **APPENDICES** | 118 |
| A | Complete API Reference | 118 |
| B | Feature Dictionary | 121 |
| C | Reproducing the Results | 122 |

*(Page numbers are indicative; update them after final formatting.)*

<div style="page-break-after: always;"></div>

## LIST OF FIGURES

| Figure No. | Title |
|---|---|
| 4.1 | Three-tier system architecture |
| 4.2 | Entity–relationship diagram |
| 4.3 | Volatility forecasting pipeline: training and serving |
| 4.4 | Leakage-safe chronological split with 21-date embargo |
| 4.5 | Sequence diagram: profile → risk → recommendation |
| 4.6 | Sequence diagram: Monte Carlo simulation with ML volatility |
| 4.7 | Sequence diagram: AI explanation with cache and output guard |
| 4.8 | Interactive API documentation (Swagger UI) |
| 4.9 | Navigation map of the user interface |
| 7.1 | Landing page |
| 7.2 | Login page |
| 7.3 | Registration page |
| 7.4 | Dashboard |
| 7.5 | Financial profile form |
| 7.6 | Risk assessment with gauge and factor breakdown |
| 7.7 | Portfolio recommendation |
| 7.8 | Portfolio risk analytics |
| 7.9 | Diversification analysis |
| 7.10 | Monte Carlo simulation using the ML volatility forecast |
| 7.11 | SIP planner |
| 7.12 | Stock Explorer with live Yahoo Finance data |
| 7.13 | Stock Predictor: 21-day outlook with expected range cone |
| 7.14 | Portfolio tracking page (placeholder, Phase 2) |
| 7.15 | Volatility model compared with baselines on the test set |
| 7.16 | Endpoint latency benchmark |

## LIST OF TABLES

| Table No. | Title |
|---|---|
| 2.1 | Summary of related works |
| 2.2 | Comparison of existing systems with the proposed system |
| 3.1 | Project specification |
| 3.2 | Functional requirements |
| 3.3 | Non-functional requirements |
| 3.4 | Software requirements |
| 3.5 | Hardware requirements |
| 3.6 | External services and data sources |
| 4.1 | Tier and component description |
| 4.2 | Module responsibilities |
| 4.3 – 4.12 | Table schemas (users … monte_carlo_simulations) |
| 4.13 | Risk-score factor weights |
| 4.14 | Diversification-score component weights |
| 4.15 | Volatility model feature groups |
| 4.16 | API endpoint summary by module |
| 4.17 | Security controls checklist |
| 5.1 | Backend technology stack |
| 5.2 | Frontend technology stack |
| 5.3 | AI/ML technology stack |
| 5.4 | Code size by component |
| 5.5 | Frontend pages and routes |
| 5.6 | Frontend service modules |
| 6.1 – 6.9 | Unit test cases by module |
| 6.10 | API integration test cases (positive paths) |
| 6.11 | API integration test cases (negative paths) |
| 6.12 | Testing tools |
| 6.13 | Test distribution and coverage by module |
| 7.1 | Module test results summary |
| 7.2 | Risk-score worked example |
| 7.3 | Allocation validation at boundary scores |
| 7.4 | SIP validation against the closed form |
| 7.5 | Monte Carlo validation against analytical results |
| 7.6 | Monte Carlo example result |
| 7.7 | Expected price range validation |
| 7.8 | Volatility model test-set scores |
| 7.9 | Block-bootstrap confidence intervals |
| 7.10 | Forecast calibration by decile |
| 7.11 | Endpoint latency benchmarks |
| 7.12 | Capacity estimates |
| 7.13 | Security compliance matrix |
| 7.14 | Proposal features: delivered and deferred |

## LIST OF ABBREVIATIONS

| Abbreviation | Expansion |
|---|---|
| API | Application Programming Interface |
| CAGR | Compound Annual Growth Rate |
| CORS | Cross-Origin Resource Sharing |
| CRUD | Create, Read, Update, Delete |
| CVaR | Conditional Value at Risk (Expected Shortfall) |
| GARCH | Generalised Autoregressive Conditional Heteroskedasticity |
| GBM | Geometric Brownian Motion |
| HAR | Heterogeneous Autoregressive (model of realised volatility) |
| HHI | Herfindahl–Hirschman Index |
| JWT | JSON Web Token |
| LLM | Large Language Model |
| MAE | Mean Absolute Error |
| NSE | National Stock Exchange of India |
| ORM | Object-Relational Mapping |
| QLIKE | Quasi-likelihood loss |
| RMSE | Root Mean Squared Error |
| RSI | Relative Strength Index |
| SIP | Systematic Investment Plan |
| SPA | Single-Page Application |
| VaR | Value at Risk |

<div style="page-break-after: always;"></div>

# CHAPTER 1 — INTRODUCTION

## 1.1 Overview

Investing is one of the few financial decisions in which the outcome is uncertain by design, yet most of the tools offered to retail investors present it as if it were certain. A typical online SIP calculator says that ₹5,000 a month at 12% for ten years "becomes" ₹11.6 lakh. It says nothing about how likely that is, what a bad decade would look like, or whether the investor can tolerate the swings along the way. Professional advisors fill this gap with risk questionnaires, allocation models and scenario analysis, but their services are expensive and rarely reach first-time investors.

The **AI Smart Investment Portfolio Advisor** (project name *FinIntelAI*) is a web platform that brings these professional techniques to an individual investor, transparently. The investor records a financial profile: age, income, savings, horizon, risk tolerance and goal. From it the platform:

1. computes a **risk score from 0 to 100** and an investor type (Conservative, Moderate or Aggressive) from five weighted factors, and shows the contribution of each factor;
2. recommends an **asset allocation** across stocks, mutual funds, gold and an emergency fund that moves smoothly with the risk score;
3. analyses a portfolio's history for **annualised volatility, Sharpe ratio and maximum drawdown**, and its holdings for **sector and asset concentration**;
4. projects future wealth with a **Monte Carlo simulation** of 1,000–50,000 paths, reporting percentile scenarios, confidence intervals, probability of profit, **Value at Risk** and **Conditional Value at Risk**;
5. plans **Systematic Investment Plans** (SIPs) and the monthly amount needed to reach a goal;
6. shows **live market data** for NSE and global stocks;
7. **forecasts volatility** with a machine-learning model trained on ten years of NSE data, and uses that forecast in the simulations and in a 21-trading-day **Stock Predictor** outlook;
8. **explains** each of these results in plain language using a large language model that runs locally on the user's machine.

The guiding principle is honesty about uncertainty. Wherever the system shows a number, it also shows where the number came from: a formula, a trained model, or a historical fallback. When a figure is not a prediction, the interface says so.

## 1.2 Problem Context

India's retail investor base has expanded sharply over the last decade. Demat accounts and monthly SIP inflows have risen to record levels, and a large share of new participants are young, first-time investors who rely on social media, peers or app defaults. Several recurring problems follow:

- **Risk capacity is not measured.** Investors choose products by recent returns rather than by their age, income stability, savings rate and horizon. Risk tolerance (what one *wants*) is confused with risk capacity (what one can *afford*).
- **Portfolio risk is invisible.** Brokerage apps show profit and loss, but rarely volatility, risk-adjusted return or the worst peak-to-trough fall. Concentration in one sector or asset class goes unnoticed.
- **Projections are deterministic.** Calculators extrapolate a fixed rate of return. The spread of outcomes and the probability of losing money, which matter most for planning, are hidden.
- **Volatility assumptions are arbitrary.** Where uncertainty is modelled at all, volatility is a manually typed constant, usually not linked to the asset's current market condition.
- **Advice is opaque or unaffordable.** SEBI-registered advisors charge fees beyond the reach of small investors. Commercial robo-advisors seldom explain the reasoning behind an allocation.
- **AI explanations can mislead.** General-purpose chatbots can state predictions as facts, give buy/sell advice, or invent numbers (hallucination), which is dangerous in a financial context.

## 1.3 Motivation

The project is motivated by three observations.

First, the quantitative methods inside professional robo-advisors are well established and not secret: questionnaire-based risk scoring, rule-based or optimised allocation, and Monte Carlo projection. They can be implemented transparently, so that every number can be traced back to a formula the user can read.

Second, volatility, the key input to any risk projection, is one of the few financial quantities that is genuinely **forecastable**. Volatility clusters: calm periods follow calm periods and turbulent periods follow turbulent ones. This is documented from Engle's ARCH model to Corsi's HAR model. Replacing a typed-in constant with a forecast that reflects current market conditions makes a simulation more realistic. Stock *direction*, by contrast, is close to unpredictable at a one-month horizon, so the system must be careful about what it claims.

Third, small open-weight language models (here Qwen2.5 with 3 billion parameters) can now run on an ordinary laptop. This makes it possible to explain results in natural language **without sending a user's financial data to a third-party cloud service**, as long as the model's output is constrained and checked.

## 1.4 Objectives

The objectives of the project are:

1. **Risk profiling:** design a transparent, multi-factor risk-scoring model that maps a financial profile to a 0–100 score and an investor category, and show each factor's contribution.
2. **Asset allocation:** generate a personalised allocation across stocks, mutual funds, gold and an emergency fund that changes continuously with the risk score, instead of jumping between three fixed templates.
3. **Portfolio analytics:** compute annualised volatility, Sharpe ratio, maximum drawdown and a composite risk score from a portfolio's value history, and assess diversification using sector, asset-class and HHI measures.
4. **Probabilistic projection:** implement a mathematically correct Monte Carlo simulator (GBM with Itô-corrected drift and monthly contributions) that reports percentile scenarios, confidence intervals, probabilities, VaR and CVaR, and is reproducible through a random seed.
5. **ML volatility forecasting:** build a leakage-safe pipeline that forecasts 21-trading-day forward realised volatility and evaluates it honestly against naive, HAR and GARCH(1,1) baselines. Serve the forecast with a guarded fallback.
6. **Stock outlook:** provide a 21-day Stock Predictor that separates *trend* (a description of the past), *probability of a rise* (compared against the historical base rate) and *expected range* (from the volatility forecast).
7. **Explainability:** generate plain-language explanations with a locally hosted LLM, cache them, and enforce deterministic guards against advice and statements of certainty.
8. **Engineering quality:** deliver a secure, documented, tested full-stack application, with JWT authentication, bcrypt hashing, input validation, versioned schema migrations, an automated test suite and interactive API documentation.

## 1.5 Scope of the Project

**In scope (delivered):**

- User registration, login and session management with JWT.
- Financial profile management and automated risk profiling.
- Score-proportional portfolio recommendation.
- Portfolio risk analytics and diversification analysis, using sample data generators so that users without broker integration can explore them.
- Monte Carlo simulation with save, list, rename and delete operations, and a choice between a manual volatility and the ML forecast.
- SIP calculation, goal-based required-SIP calculation and saved SIP plans.
- Stock search, quotes and price history from Yahoo Finance.
- ML volatility forecasting: data pipeline, feature engineering, training script, model registry, serving with fallback.
- The Stock Predictor outlook with an expected range and an AI explanation guarded at the output.
- AI explanations for risk, recommendation, portfolio analysis, diversification, Monte Carlo, SIP and stock trends.

**Out of scope for this phase (planned; see Chapter 9):**

- Real holdings tracking (buy/sell transactions, live portfolio value). The database tables exist, but the Portfolio page is a placeholder.
- Goal and retirement planning, mean–variance optimisation, automated rebalancing and a conversational chat assistant.
- PDF report export, and ETF and gold-price tracking.
- Production deployment with PostgreSQL and cloud hosting. The current system uses SQLite and runs locally.
- A trained classifier for the Stock Predictor's direction probability. The plumbing and evaluation code are complete, and until a model is trained the page shows the historical base rate, labelled "Not a prediction".
- Execution of trades. The system is an **educational decision-support tool, not a registered investment advisor**, and it never places orders.

## 1.6 Organisation of the Report

- **Chapter 2** surveys the literature on robo-advisory, portfolio theory, risk measures, Monte Carlo methods, volatility forecasting and LLMs in finance, and identifies the gap this project addresses.
- **Chapter 3** specifies the functional and non-functional requirements and the software and hardware environment.
- **Chapter 4** presents the system design: architecture, database schema, design patterns, the ML pipeline, the API, interaction flows and security controls.
- **Chapter 5** describes the implementation of the backend services, the machine-learning components, the LLM layer and the frontend, with code excerpts.
- **Chapter 6** reports unit, integration and API testing.
- **Chapter 7** presents results: module outputs, validation of the financial computations against closed-form results, the volatility model evaluation, performance benchmarks and a security compliance matrix.
- **Chapters 8 and 9** conclude the report and set out phased future work.

<div style="page-break-after: always;"></div>

# CHAPTER 2 — LITERATURE SURVEY

## 2.1 Existing Research

### 2.1.1 Robo-Advisory Systems

Robo-advisors are digital platforms that provide automated, algorithm-driven investment advice with little human intervention. Jung et al. [21] describe their typical pipeline: client profiling through a questionnaire, allocation from a small set of model portfolios, and periodic rebalancing. Beketov, Lehmann and Wittke [1], the first base paper of this project, studied the quantitative methods actually used inside robo-advisors. They found that most rely on Modern Portfolio Theory or simple rule-based allocation, and that the methods are rarely disclosed to clients. D'Acunto, Prabhala and Rossi [22] show that robo-advice improves diversification for under-diversified investors, but warn that the benefit depends on the quality and transparency of the underlying model. Sironi [35] argues for goal-based investing and better communication as the next step for automated advice.

The second base paper, **PortfolioPilot (AAAI 2026)** [2], proposes an *agentic* platform in which LLM-based agents develop and evaluate portfolio-management algorithms. It marks a shift from static rule engines towards systems that combine quantitative modules with language-model reasoning, which is the direction this project takes at a smaller and safer scale. Here the LLM explains results computed by deterministic code; it does not compute or decide.

### 2.1.2 Portfolio Theory and Risk-Adjusted Performance

Markowitz [3] formalised the trade-off between expected return and variance and showed that diversification reduces risk when assets are not perfectly correlated. Sharpe [4] introduced the reward-to-variability ratio, now the Sharpe ratio, as the standard measure of risk-adjusted return. Maximum drawdown, the largest peak-to-trough fall, complements volatility because it captures the loss an investor actually experiences [39]. Concentration is commonly measured with the Herfindahl–Hirschman Index (HHI), the sum of squared weights [20], which ranges from 1/N for an equally weighted portfolio to 1 for a single holding.

### 2.1.3 Risk Measures: VaR and CVaR

Value at Risk (VaR) is the loss threshold that is exceeded with a given small probability. Artzner et al. [11] showed that VaR is not a *coherent* risk measure, because it can penalise diversification, and that it says nothing about the size of losses beyond the threshold. Rockafellar and Uryasev [12] popularised Conditional Value at Risk (CVaR, also called expected shortfall), the average loss in the tail beyond VaR, which is coherent and convex. This project reports both measures at the 5% level from simulated terminal wealth.

### 2.1.4 Monte Carlo Simulation in Finance

Boyle [9] introduced Monte Carlo simulation to option pricing. Glasserman [10] gives a comprehensive treatment of its use in financial engineering. For long-horizon wealth projection, the standard model is geometric Brownian motion (GBM), the price process underlying the Black–Scholes framework [29]. A subtle but important detail is the **Itô correction**: if log-returns are drawn with mean μ, the arithmetic mean return is μ + σ²/2. A simulator that ignores this overstates expected wealth, increasingly so as volatility rises. Many online simulators make exactly this error; this project corrects it explicitly (Section 5.3.6) and verifies the correction against the analytical mean (Section 7.2).

### 2.1.5 Volatility Modelling and Forecasting

Engle [5] introduced the ARCH model, capturing *volatility clustering*. Bollerslev [6] generalised it to GARCH, of which GARCH(1,1) remains the most widely used benchmark. Andersen and Bollerslev [31] showed that, when evaluated against realised volatility rather than noisy squared returns, standard volatility models forecast well. Corsi [7] proposed the **Heterogeneous Autoregressive (HAR)** model, a linear regression of future realised volatility on daily, weekly and monthly realised volatility. Despite its simplicity, HAR is very hard to beat and is the standard benchmark for new volatility models. Range-based estimators by Parkinson [8] and Garman and Klass [32] use the intraday high and low, which carry more information than closing prices alone.

Evaluating volatility forecasts needs care, because true volatility is never observed. Patton [13] proved that only a few loss functions, notably MSE and **QLIKE**, rank forecasts consistently when an imperfect proxy such as realised volatility is used. QLIKE also penalises under-prediction more than over-prediction, which suits a risk tool. Diebold and Mariano [18] formalised tests of whether one forecast is significantly better than another. For dependent time-series data, the block bootstrap of Künsch [17] gives valid confidence intervals.

### 2.1.6 Machine Learning on Financial Time Series

López de Prado [14] documents why naive machine-learning practice fails on financial data. **Overlapping labels** (for example, 21-day forward targets on consecutive days) leak future information across a random train/test split, producing inflated results. He recommends chronological splits with **purging and embargo**: a gap at least as long as the label horizon between training and test data. Regularised linear models such as ridge regression [15] remain strong baselines in this setting, where signal-to-noise is low and features are highly correlated. Hastie, Tibshirani and Friedman [16] describe the **one-standard-error rule**: choose the simplest model whose cross-validated error is within one standard error of the best. The scikit-learn library [19] provides the estimators and the cross-validation tooling.

For direction (up/down) forecasting, the relevant benchmark is not 50% but the **historical base rate**, because most large stocks rise more often than they fall over a month. The Brier score [33] and the Brier *skill* score measure whether a probabilistic forecast improves on that base rate.

### 2.1.7 Large Language Models in Finance

Domain-specific LLMs such as BloombergGPT [23] show that language models can summarise and reason over financial text. Ji et al. [24] survey **hallucination**: fluent but unsupported output. In finance it can turn a historical frequency into a confident "prediction", or produce unregulated investment advice. Open-weight models such as Qwen2.5 [25] are small enough to run locally, which supports privacy but makes instruction-following less reliable. The design response in this project is to (a) give the LLM only numbers computed by deterministic code, (b) instruct it what it may not say, and (c) **check its output deterministically** and discard text that breaks the rules.

### 2.1.8 Web Application Security

Passwords must be stored with a slow, salted, adaptive hash. bcrypt [27] remains a recommended choice. Stateless authentication with JSON Web Tokens [28] suits single-page applications. The OWASP Top 10 [34] lists the most critical web risks, including broken access control, injection and cryptographic failures, and the security controls in Section 4.9 follow it.

## 2.2 Related Works

**Table 2.1: Summary of related works**

| S.No | Title and Authors | Methodology | Inferences and Drawbacks |
|---|---|---|---|
| 1 | *Robo Advisors: Quantitative Methods Inside the Robots* — Beketov, Lehmann, Wittke (2018) [1] | Survey and classification of the allocation methods used by over 200 robo-advisors | MPT and rule-based allocation dominate. Methods are seldom disclosed to clients and uncertainty is rarely communicated. **Base paper:** motivates the transparent risk and allocation engine. |
| 2 | *PortfolioPilot: An Agentic Platform for Financial Portfolio Management Algorithm Development and Evaluation* — AAAI 2026 [2] | LLM agents that generate, back-test and evaluate portfolio algorithms | Shows the value of combining quantitative modules with LLM reasoning. Agentic systems are complex to validate, and LLM output must be constrained. **Base paper:** motivates the explanation layer with deterministic guards. |
| 3 | *Portfolio Selection* — Markowitz (1952) [3] | Mean–variance optimisation | Foundation of diversification. Sensitive to estimation error in expected returns; assumes normal returns. |
| 4 | *Mutual Fund Performance* — Sharpe (1966) [4] | Reward-to-variability ratio | Standard risk-adjusted measure. Penalises upside and downside volatility equally. |
| 5 | *Generalized Autoregressive Conditional Heteroskedasticity* — Bollerslev (1986) [6] | GARCH(1,1) conditional variance model | Captures volatility clustering. Fitted per series and can be slow; tends to overreact after shocks. Used as a baseline. |
| 6 | *A Simple Approximate Long-Memory Model of Realized Volatility* — Corsi (2009) [7] | HAR regression on daily, weekly and monthly realised volatility | Simple and very hard to beat. Linear and uses only the volatility history. **Primary baseline** in this project. |
| 7 | *Volatility Forecast Comparison Using Imperfect Volatility Proxies* — Patton (2011) [13] | Theory of robust loss functions | Only MSE-type and QLIKE losses rank forecasts consistently. Justifies the use of QLIKE for model selection. |
| 8 | *Coherent Measures of Risk* — Artzner et al. (1999) [11] | Axiomatic risk-measure theory | VaR is not coherent; motivates reporting CVaR alongside VaR. |
| 9 | *Optimization of Conditional Value-at-Risk* — Rockafellar, Uryasev (2000) [12] | CVaR definition and optimisation | Coherent, tail-sensitive risk measure. Needs many scenarios to estimate stably. |
| 10 | *Options: A Monte Carlo Approach* — Boyle (1977) [9] | Simulation of asset-price paths | Flexible for path-dependent problems. Results depend on model assumptions (GBM, constant σ). |
| 11 | *Advances in Financial Machine Learning* — López de Prado (2018) [14] | Purged and embargoed cross-validation, label design | Naive cross-validation on overlapping labels leaks the future. Basis of the 21-date embargo used here. |
| 12 | *The Promises and Perils of Robo-Advising* — D'Acunto, Prabhala, Rossi (2019) [22] | Empirical study of robo-advisor users in India | Robo-advice improves diversification for under-diversified investors. Benefits depend on model quality and transparency. |
| 13 | *BloombergGPT: A Large Language Model for Finance* — Wu et al. (2023) [23] | 50B-parameter domain LLM | Strong on financial NLP tasks. Proprietary, expensive, cloud-based, and does not address advice safety. |
| 14 | *Survey of Hallucination in Natural Language Generation* — Ji et al. (2023) [24] | Survey | LLMs produce unsupported claims. Motivates grounding the prompt in computed numbers and checking the output. |

**Table 2.2: Comparison of existing systems with the proposed system**

| Capability | Online SIP calculators | Brokerage apps | Commercial robo-advisors | General LLM chatbots | **Proposed system** |
|---|---|---|---|---|---|
| Multi-factor risk profiling with factor breakdown | ✗ | Partial (questionnaire) | ✓ (opaque) | ✗ | **✓ (transparent weights)** |
| Continuous, score-proportional allocation | ✗ | ✗ | Model portfolios | ✗ | **✓** |
| Volatility, Sharpe and drawdown analytics | ✗ | Rare | Partial | ✗ | **✓** |
| Concentration and HHI analysis | ✗ | ✗ | Partial | ✗ | **✓** |
| Probabilistic projection with VaR and CVaR | ✗ | ✗ | Sometimes | ✗ | **✓ (Itô-corrected, seeded)** |
| Market-aware volatility input | ✗ | ✗ | ✗ | ✗ | **✓ (ML forecast + fallback)** |
| Honest comparison against baselines | — | — | Not disclosed | — | **✓ (naive, HAR, GARCH, bootstrap CIs)** |
| Natural-language explanations | ✗ | ✗ | Templates | ✓ (unguarded) | **✓ (local LLM + output guard)** |
| Data stays on the user's machine | ✓ | ✗ | ✗ | ✗ | **✓** |
| Cost to user | Free | Free/commission | Fee | Free/subscription | **Free, open source** |

## 2.3 Limitations of Existing Systems

The survey and the comparison above identify the following limitations:

1. **Opacity:** commercial robo-advisors do not disclose how risk scores and allocations are computed, so users cannot check whether the recommendation fits them [1], [22].
2. **Deterministic projections:** most calculators ignore uncertainty entirely, and those that simulate often omit the Itô correction and so overstate expected wealth.
3. **Static volatility:** simulation inputs are user-typed constants, unrelated to current market conditions, although volatility is demonstrably forecastable [5], [7].
4. **Unverified ML claims:** many published or marketed "AI stock predictors" evaluate with random splits on overlapping labels, which leaks future information [14], and compare against 50% rather than the base rate. Their accuracy figures are not credible.
5. **Unsafe AI text:** general-purpose LLMs give investment advice and state uncertain outcomes as facts [24]. Prompting alone does not reliably prevent this in small models.
6. **Privacy:** cloud-based tools send personal financial data to third-party servers.

## 2.4 Research Gap and Proposed Contribution

No freely available tool combines transparent risk profiling, statistically sound portfolio analytics, probabilistic projection with a market-aware volatility input, and safe natural-language explanations, while also being honest about the limits of its own predictions. This project addresses that gap with the following contributions:

- **A transparent rule-based core.** Every score and allocation is a documented formula with visible factor contributions.
- **A correct and reproducible Monte Carlo engine.** It uses Itô-corrected GBM, end-of-month contributions, VaR and CVaR, and seeds; it is validated against closed-form results.
- **A leakage-safe volatility forecaster.** It is evaluated against naive, HAR and GARCH(1,1) baselines with block-bootstrap confidence intervals, selected by the one-standard-error rule, and served behind a contract-checked registry with a plausibility guard and a labelled fallback.
- **A Stock Predictor that separates description from prediction.** Its probability is always compared with the historical base rate and labelled "Not a prediction" when no validated model exists.
- **A privacy-preserving explanation layer.** It uses a local LLM, caches results, and applies deterministic output guards that discard advice and statements of certainty rather than silently editing them.

<div style="page-break-after: always;"></div>

# CHAPTER 3 — SYSTEM REQUIREMENTS

## 3.1 Project Specification

**Table 3.1: Project specification**

| Attribute | Specification |
|---|---|
| Project title | AI Smart Investment Portfolio Advisor (FinIntelAI) |
| Domain | AI & ML · Large Language Models · FinTech · Data Analytics · Full-Stack Web Development |
| Application type | Web application (single-page frontend + REST API backend) |
| Target users | Retail investors, first-time investors, finance students |
| Market focus | Indian markets (NSE, ₹, SIPs, 6% risk-free rate), with support for global tickers |
| Backend | Python 3.13, FastAPI 0.141, SQLAlchemy 2.0, Alembic, Pydantic v2 |
| Frontend | React 18, React Router 6, Tailwind CSS, Recharts, Axios |
| Database | SQLite (development); schema is PostgreSQL-compatible through SQLAlchemy |
| Machine learning | scikit-learn 1.9, pandas, NumPy, statsmodels, arch (GARCH), joblib |
| LLM | Qwen2.5-3B served locally by Ollama |
| Market data | Yahoo Finance via yfinance, with a local Parquet cache |
| Authentication | JWT (HS256, 30-minute expiry), bcrypt (cost 12) |
| API surface | 58 REST operations in 12 modules, self-documented with OpenAPI/Swagger |
| Data model | 10 relational tables, 2 Alembic migrations |
| Code size | ≈ 9,600 lines backend application, ≈ 7,400 lines frontend, ≈ 2,600 lines tests |
| Automated tests | 338 (336 passed, 2 skipped) |
| Repository | Private GitHub repository, 8 commits (12 Aug 2026 – 10 Oct 2026) |

## 3.2 Functional Requirements

**Table 3.2: Functional requirements**

| ID | Module | Requirement |
|---|---|---|
| FR-01 | Authentication | The system shall allow a user to register with full name, e-mail and password. Duplicate e-mails shall be rejected. |
| FR-02 | Authentication | The system shall authenticate users by e-mail and password and issue a signed JWT access token. |
| FR-03 | Authentication | The system shall restrict all personal data and analysis endpoints to authenticated users, and restrict user records to their owner. |
| FR-04 | Profile | The user shall be able to create, view, update and delete a financial profile (age, monthly income, monthly savings, investment horizon, risk tolerance, financial goal). |
| FR-05 | Risk | The system shall compute a 0–100 risk score from five weighted factors and classify the user as Conservative (< 40), Moderate (40–69) or Aggressive (≥ 70). |
| FR-06 | Risk | The system shall show each factor's sub-score and a textual explanation, and shall recompute the risk profile when the financial profile changes. |
| FR-07 | Recommendation | The system shall generate a percentage allocation across stocks, mutual funds, gold and an emergency fund, summing to 100%, that varies continuously with the risk score. |
| FR-08 | Recommendation | The system shall provide a recommendation summary and investment guidance for the user's monthly savings. |
| FR-09 | Portfolio analytics | Given a series of portfolio values, the system shall compute annualised volatility, Sharpe ratio, maximum drawdown, total and average return, and a composite risk score and level. |
| FR-10 | Diversification | Given holdings (name, value, sector, asset type), the system shall compute sector and asset-class concentration, HHI and a diversification score, with warnings and recommendations. |
| FR-11 | Sample data | The system shall generate realistic sample portfolio series and holdings, so that analytics can be explored without broker integration. |
| FR-12 | Monte Carlo | The system shall simulate 1,000–50,000 wealth paths over 1–50 years with optional monthly contributions, and report percentiles, scenarios, confidence intervals, probability of profit and of doubling, VaR and CVaR. |
| FR-13 | Monte Carlo | The user shall be able to use either a manually entered volatility or the ML-forecast volatility of a chosen ticker. The source and model version shall be recorded with the simulation. |
| FR-14 | Monte Carlo | The user shall be able to save, list, view, rename, annotate and delete simulations, and fix a random seed for reproducibility. |
| FR-15 | SIP | The system shall compute the future value, total investment and wealth gained for a SIP, with a year-by-year breakdown, and the monthly SIP required to reach a target corpus. |
| FR-16 | SIP | The user shall be able to save, list, update and delete SIP plans. |
| FR-17 | Market data | The user shall be able to search stocks and view quotes, key statistics, company information and price history (1 month to 5 years). |
| FR-18 | ML forecasting | The system shall forecast 21-trading-day annualised volatility for a ticker and report whether the value came from the model (`ml_predicted`) or from trailing realised volatility (`historical_fallback`), with the reason. |
| FR-19 | ML operations | The system shall expose model metadata, a feature snapshot for any ticker, cache status, and hot reload of model artifacts without a restart. |
| FR-20 | Stock Predictor | The system shall present a 21-day outlook: a technical trend description, the probability of a higher close compared with the historical base rate, and 68% and 95% expected price ranges. |
| FR-21 | Explanations | The system shall generate plain-language AI explanations for risk, recommendation, portfolio analysis, diversification, Monte Carlo, SIP and stock outlooks, and cache them where stored. |
| FR-22 | Explanations | The Stock Predictor explanation shall be rejected if it contains investment advice, a guarantee, or a price move stated as certain. When the probability is only the base rate, the text shall state that it is not a prediction. |
| FR-23 | Dashboard | The system shall present a dashboard summarising the user's profile, risk score and quick links to every module. |
| FR-24 | Health | The system shall provide health endpoints for the API and for the LLM service. |

## 3.3 Non-Functional Requirements

**Table 3.3: Non-functional requirements**

| ID | Category | Requirement | Measured / Implemented |
|---|---|---|---|
| NFR-01 | Performance | Deterministic analytical endpoints shall respond within 100 ms on a developer laptop. | Median 10.6–35.5 ms (Table 7.11) |
| NFR-02 | Performance | A 10,000-path, 10-year Monte Carlo simulation shall complete within 2 s. | Median 0.53 s |
| NFR-03 | Performance | A volatility forecast shall complete within 1 s when price history is cached. | Median 117 ms |
| NFR-04 | Availability | Analytical features shall keep working when the LLM or the ML model is unavailable. | Explanations degrade to an error message; volatility falls back to historical, labelled |
| NFR-05 | Security | Passwords shall be stored only as salted adaptive hashes. | bcrypt, cost 12 |
| NFR-06 | Security | Protected endpoints shall reject missing, malformed or foreign-signed tokens. | Verified (IT-N1, IT-N2; unit tests) |
| NFR-07 | Security | All request bodies and path parameters shall be validated. Tickers shall be checked against a strict pattern before reaching the file system. | Pydantic v2 schemas; ticker validator (IT-N9) |
| NFR-08 | Privacy | No personal or financial data shall be sent to third-party AI services. | LLM runs locally via Ollama |
| NFR-09 | Reliability | Simulations shall be reproducible given a seed. | Verified by unit test |
| NFR-10 | Correctness | Financial formulas shall match closed-form results. | Validated (Section 7.2) |
| NFR-11 | ML integrity | No future information shall enter training features or tuning folds. | Embargo measured in dates; no-lookahead tests |
| NFR-12 | Honesty | Every prediction shall state its source; a non-prediction shall never be presented as one. | `source` fields; base-rate labelling; output guard |
| NFR-13 | Maintainability | Business logic shall live in stateless service classes, separate from HTTP routing and persistence. | Service layer (Section 4.5) |
| NFR-14 | Maintainability | The schema shall be versioned. | Alembic (2 migrations) |
| NFR-15 | Usability | The interface shall be responsive, with consistent navigation and Indian currency formatting. | Tailwind responsive layout, ₹ and lakh formatting |
| NFR-16 | Documentation | The API shall be self-documenting. | OpenAPI at `/docs` and `/redoc` |
| NFR-17 | Testability | Core algorithms shall have automated tests runnable with one command. | `pytest`: 338 tests in 30 s |

## 3.4 Software Requirements

**Table 3.4: Software requirements**

| Component | Software | Version used |
|---|---|---|
| Operating system | Windows 10/11, Linux or macOS | Windows 11 Home |
| Backend language | Python | 3.13.7 |
| Web framework | FastAPI (with Starlette, Pydantic v2) | 0.141.1 |
| ASGI server | Uvicorn | (from `requirements.txt`) |
| ORM | SQLAlchemy | 2.0.52 |
| Migrations | Alembic | 1.19.1 |
| Database | SQLite (development) / PostgreSQL (planned) | SQLite 3 |
| Authentication | python-jose (JWT), bcrypt | bcrypt 5.0.0 |
| Data and ML | NumPy, pandas, scikit-learn, statsmodels, arch, joblib, pyarrow | scikit-learn 1.9.0, statsmodels 0.15.0, arch 8.0.0, pyarrow 25.0.1 |
| Market data | yfinance | 1.5.2 |
| LLM runtime | Ollama | local server on port 11434 |
| LLM | Qwen2.5 3B (`qwen2.5:3b`) | — |
| Frontend runtime | Node.js and npm | Node 18+ |
| Frontend framework | React (Create React App, react-scripts) | 18 / 5.0.1 |
| Routing | react-router-dom | 6.21 |
| Styling | Tailwind CSS | 3.x |
| Charts | Recharts | 2.15 |
| HTTP client | Axios | 1.6 |
| Markdown rendering | react-markdown | 10.1 |
| Testing | pytest | 9.1.1 |
| Version control | Git, GitHub (private repository) | — |
| Editor | Visual Studio Code | — |
| Browser | Chrome / Edge / Firefox (latest) | — |

## 3.5 Hardware Requirements

**Table 3.5: Hardware requirements**

| Component | Minimum | Recommended | Reason |
|---|---|---|---|
| Processor | 4-core x86-64 | 8-core | Monte Carlo is vectorised; LLM inference is CPU-bound without a GPU |
| RAM | 8 GB | 16 GB | Qwen2.5-3B needs about 2–3 GB; React dev server and Python about 2 GB |
| Storage | 5 GB free | 10 GB SSD | LLM weights about 1.9 GB; Python and Node dependencies; Parquet price cache |
| GPU | Not required | NVIDIA GPU with ≥ 4 GB VRAM | Cuts LLM explanation time from about 30–55 s to a few seconds |
| Network | Broadband | Broadband | Yahoo Finance data and first-time model download |
| Display | 1366 × 768 | 1920 × 1080 | Dashboard and charts |

## 3.6 External Services and Data Sources

**Table 3.6: External services and data sources**

| Service | Purpose | Access | Failure handling |
|---|---|---|---|
| Yahoo Finance (yfinance) | Quotes, company info, OHLCV history for NSE (`.NS`) and global tickers; Nifty 50 index (`^NSEI`) | Public, no API key | Parquet cache with a 24-hour TTL; HTTP 503 with a clear message when no data and no cache exist |
| Ollama (local) | Hosts Qwen2.5-3B for explanations | `http://localhost:11434`, 180 s timeout | `/api/ollama/health`; explanation endpoints return a clear error, and analytics are unaffected |
| Trained model artifacts | `volatility_model.joblib` (and, in future, `trend_model.joblib`) | Local files under `backend/models/` (git-ignored) | Contract check at load; historical fallback when missing or invalid |

<div style="page-break-after: always;"></div>

# CHAPTER 4 — SYSTEM DESIGN

## 4.1 System Architecture

The system follows a **three-tier architecture**: a React single-page application (presentation), a FastAPI REST service (application logic), and persistence with external services (data). Within the backend, a further separation between *routers* (HTTP), *services* (business logic) and *models* (persistence) keeps every financial algorithm a pure, independently testable function.

```mermaid
flowchart TB
    subgraph P["Presentation tier — React 18 SPA (port 3000)"]
        UI["15 pages<br/>Dashboard · Profile · Risk · Recommendation · Analytics<br/>Diversification · Monte Carlo · SIP · Stocks · Predictor"]
        SV["11 service modules (Axios)<br/>JWT attached by interceptor"]
        CH["Recharts visualisations<br/>gauges · pies · fan charts · cones"]
        UI --> SV
        UI --> CH
    end

    subgraph A["Application tier — FastAPI (port 8000)"]
        R["12 routers · 58 operations<br/>Pydantic v2 validation · JWT dependency"]
        subgraph S["Service layer (stateless)"]
            S1["RiskCalculator"]
            S2["RecommendationEngine"]
            S3["PortfolioRiskAnalyzer"]
            S4["DiversificationAnalyzer"]
            S5["MonteCarloSimulator"]
            S6["SIPCalculator"]
            S7["YahooFinanceService"]
            S8["MLPredictionService"]
            S9["StockTrendService"]
            S10["OllamaService + prompts"]
            S11["ExplanationGuard"]
        end
        subgraph M["ML package (app.ml)"]
            M1["data · features · evaluation"]
            M2["model_registry · trend · trend_registry"]
        end
        R --> S
        S8 --> M
        S9 --> M
    end

    subgraph D["Data tier"]
        DB[("SQLite<br/>10 tables · Alembic")]
        PC[("Parquet price cache<br/>24 h TTL")]
        MA[("Model artifacts<br/>joblib")]
    end

    subgraph X["External / local services"]
        YF["Yahoo Finance"]
        OL["Ollama · Qwen2.5-3B<br/>(port 11434, local)"]
    end

    SV -- "HTTPS/JSON + Bearer JWT" --> R
    S --> DB
    M1 --> PC
    M1 --> YF
    S7 --> YF
    M2 --> MA
    S10 --> OL
```

**Figure 4.1: Three-tier system architecture**

## 4.2 Tier and Component Description

**Table 4.1: Tier and component description**

| Tier | Component | Technology | Responsibility |
|---|---|---|---|
| Presentation | Pages | React 18 function components with hooks | Forms, results and visualisations for each module |
| Presentation | Layout | Navbar, Footer, Layout (React Router outlet) | Consistent navigation across 12 sections; logout |
| Presentation | Common components | Button, Card, Input, Select, Loading, PieChart, RiskGauge | Reusable, styled UI primitives |
| Presentation | Service modules | Axios instance with request and response interceptors | Attach the JWT, handle 401 by redirecting to login, centralise the base URL and timeout |
| Application | Routers | FastAPI `APIRouter` per module | Parse and validate requests, enforce authentication, call services, map errors to HTTP codes |
| Application | Schemas | Pydantic v2 models | Request and response contracts and validation rules (ranges, lengths, patterns) |
| Application | Services | Plain Python classes with static methods | All financial computation, with no I/O and no framework dependencies |
| Application | ML package | `app.ml` | Data loading and caching, features, labels, splits, metrics, model contract |
| Application | Core | `config`, `database`, `security`, `dependencies` | Settings from `.env`, sessions, hashing, JWT, current-user dependency |
| Data | Relational store | SQLite via SQLAlchemy ORM | Users, profiles, analyses, simulations, plans |
| Data | Price cache | Parquet files (pyarrow) | Avoid repeated downloads; offline resilience |
| Data | Model artifacts | joblib bundles with metadata | Versioned, contract-checked estimators |
| External | Yahoo Finance | yfinance | Market data |
| External | Ollama | REST on localhost | LLM inference |

## 4.3 Module Design

**Table 4.2: Module responsibilities**

| # | Module | Router prefix | Core service | Persisted in | Ops |
|---|---|---|---|---|---|
| 1 | System | `/`, `/health` | — | — | 2 |
| 2 | Authentication | `/api/auth` | `core.security` | `users` | 3 |
| 3 | Users | `/api/users` | — | `users` | 2 |
| 4 | Financial profile | `/api/profile` | — | `financial_profiles` | 4 |
| 5 | Risk assessment | `/api/risk` | `RiskCalculator` | `risk_profiles` | 4 |
| 6 | Recommendation | `/api/recommendation` | `RecommendationEngine` | `portfolio_recommendations` | 4 |
| 7 | Portfolio analytics | `/api/portfolio-analysis` | `PortfolioRiskAnalyzer` | `portfolio_analyses` | 4 |
| 8 | Diversification | `/api/diversification-analysis` | `DiversificationAnalyzer` | `diversification_analyses` | 6 |
| 9 | Monte Carlo | `/api/monte-carlo` | `MonteCarloSimulator`, `MLPredictionService` | `monte_carlo_simulations` | 7 |
| 10 | SIP planner | `/api/sip` | `SIPCalculator` | `sip_plans` | 7 |
| 11 | Market data | `/api/market` | `YahooFinanceService`, `StockTrendService` | — (cache) | 5 |
| 12 | Machine learning | `/api/ml` | `MLPredictionService`, `StockTrendService` | artifacts, cache | 8 |
| 13 | LLM health | `/api/ollama` | `OllamaService` | — | 2 |
| | **Total** | | | | **58** |

### 4.3.1 Risk Assessment Model

The risk score is a weighted average of five sub-scores, each from 0 to 100.

**Table 4.13: Risk-score factor weights**

| Factor | Weight | Rationale | Sub-score behaviour |
|---|---|---|---|
| Risk tolerance | 35% | The investor's stated preference is the strongest single signal | Low → Medium → High maps to increasing scores |
| Investment horizon | 25% | Longer horizons allow recovery from drawdowns | Short horizon low; "10+ Years" scores 95 |
| Age | 15% | Younger investors have more human capital and time | Decreases with age (28 years scores 91.7) |
| Savings rate | 15% | Surplus income absorbs losses without forced selling | Increases with savings ÷ income (29.4% scores 59.4) |
| Income | 10% | Higher income raises capacity to bear risk | Increases with monthly income (₹85,000 scores 74.0) |

$$\text{RiskScore} = 0.15\,S_{age} + 0.10\,S_{income} + 0.15\,S_{savings} + 0.25\,S_{horizon} + 0.35\,S_{tolerance}$$

| Score range | Investor type |
|---|---|
| 0 – 39.99 | Conservative |
| 40 – 69.99 | Moderate |
| 70 – 100 | Aggressive |

### 4.3.2 Allocation Model

Rather than three fixed model portfolios, which would make a user scoring 69.9 and one scoring 70.0 receive very different advice, the allocation is a **linear function of the risk score** *s*:

$$\text{Stocks} = 10 + 0.65s,\quad \text{Mutual Funds} = 60 - 0.45s,\quad \text{Gold} = 20 - 0.15s,\quad \text{Emergency} = 10 - 0.05s$$

The coefficients sum to zero (0.65 − 0.45 − 0.15 − 0.05 = 0) and the intercepts sum to 100, so **the allocation always totals 100%**. It moves from 10/60/20/10 at *s* = 0 to 75/15/5/5 at *s* = 100.

### 4.3.3 Portfolio Analytics Model

From daily values $V_t$, daily returns are $r_t = V_t/V_{t-1} - 1$. Then:

- Annualised volatility: $\sigma = \text{std}(r_t)\,\sqrt{252}$
- Sharpe ratio: $(\bar r \cdot 252 - r_f)/\sigma$, with $r_f = 6\%$, approximating the Indian risk-free rate
- Maximum drawdown: $\min_t \left(V_t / \max_{\tau \le t} V_\tau - 1\right)$
- Composite risk score: 40% volatility, 30% Sharpe (inverted), 30% drawdown, each mapped to 0–100, giving Low, Moderate or High risk.

### 4.3.4 Diversification Model

**Table 4.14: Diversification-score component weights**

| Component | Weight | Measure |
|---|---|---|
| Sector diversification | 35% | Spread across sectors; penalises a dominant sector |
| Asset-class diversification | 30% | Spread across stocks, mutual funds, bonds and gold |
| Concentration (HHI) | 20% | $HHI = \sum_i w_i^2$, expressed in percent (lower is better) |
| Number of holdings | 15% | More positions, up to a saturation point |

Warnings are raised for a single sector, asset class or holding that exceeds a concentration threshold. Each warning comes with a specific recommendation.

### 4.3.5 Monte Carlo Model

Wealth is simulated monthly (Δt = 1/12) under GBM:

$$V_{k+1} = V_k \cdot \exp\!\left(\left(\ln(1+\mu)\,\Delta t - \tfrac{1}{2}\sigma^2\Delta t\right) + \sigma\sqrt{\Delta t}\,Z_k\right) + C, \qquad Z_k \sim \mathcal N(0,1)$$

Here μ is the expected annual return, σ the annual volatility and C the end-of-month contribution. The $-\tfrac12\sigma^2\Delta t$ term is the Itô correction, which makes $\mathbb E[V_T] = V_0(1+\mu)^T$ hold exactly when there are no contributions. Terminal values give the following:

- percentiles: the 5th is "worst case", the 50th "expected" and the 95th "best case";
- 90%, 95% and 99% confidence intervals;
- the probabilities of profit and of doubling;
- $\text{VaR}_{5\%}$ (the 5th-percentile value) and $\text{CVaR}_{5\%}$ (the mean of values at or below it).

### 4.3.6 SIP Model

For monthly investment *P*, monthly rate $r = R/12/100$ and $n$ months (payments at the start of each month):

$$FV = P \cdot \frac{(1+r)^n - 1}{r}\cdot(1+r)$$

The required SIP for a target corpus *T* inverts this: $P = T \,/\, \left[\frac{(1+r)^n - 1}{r}(1+r)\right]$.

## 4.4 Database Design

The schema has **ten tables** centred on `users`. Profile-type entities (financial profile, risk profile, recommendation) are **one-to-one** with a user and enforced by a unique `user_id`. History-type entities (analyses, simulations, plans, portfolios, transactions) are **one-to-many**. Variable-shape results such as percentile paths, histograms and concentration breakdowns are stored as JSON columns, so the schema does not need a table per chart. AI explanations are stored with the result they explain (`ai_explanation`), which doubles as the explanation cache.

```mermaid
erDiagram
    USERS ||--o| FINANCIAL_PROFILES : has
    USERS ||--o| RISK_PROFILES : has
    USERS ||--o| PORTFOLIO_RECOMMENDATIONS : receives
    USERS ||--o{ PORTFOLIO_ANALYSES : runs
    USERS ||--o{ DIVERSIFICATION_ANALYSES : runs
    USERS ||--o{ MONTE_CARLO_SIMULATIONS : runs
    USERS ||--o{ SIP_PLANS : creates
    USERS ||--o{ PORTFOLIOS : owns
    USERS ||--o{ TRANSACTIONS : records
    PORTFOLIOS ||--o{ TRANSACTIONS : contains

    USERS {
        int id PK
        string email UK
        string password_hash
        string full_name
        string phone
        bool is_active
        bool is_verified
        datetime created_at
        datetime updated_at
    }
    FINANCIAL_PROFILES {
        int id PK
        int user_id FK,UK
        int age
        float monthly_income
        float monthly_savings
        string investment_horizon
        string risk_tolerance
        string financial_goal
    }
    RISK_PROFILES {
        int id PK
        int user_id FK,UK
        float risk_score
        string investor_type
        text explanation
        text ai_explanation
    }
    PORTFOLIO_RECOMMENDATIONS {
        int id PK
        int user_id FK,UK
        float stocks_percent
        float mutual_funds_percent
        float gold_percent
        float emergency_percent
        text recommendation_summary
        text ai_explanation
    }
    PORTFOLIO_ANALYSES {
        int id PK
        int user_id FK
        float volatility
        float sharpe_ratio
        float max_drawdown
        float risk_score
        string risk_level
        json portfolio_data
        text ai_explanation
    }
    DIVERSIFICATION_ANALYSES {
        int id PK
        int user_id FK
        float diversification_score
        float hhi_score
        json sector_concentration
        json asset_concentration
        json warnings
        json holdings_data
        text ai_explanation
    }
    MONTE_CARLO_SIMULATIONS {
        int id PK
        int user_id FK
        float initial_investment
        float expected_return
        float volatility
        string volatility_source
        float predicted_volatility
        string volatility_model_version
        string volatility_ticker
        int random_seed
        json statistics
        json risk_metrics
        json percentile_paths
        text ai_explanation
    }
    SIP_PLANS {
        int id PK
        int user_id FK
        string plan_name
        float investment_amount
        int duration_months
        float expected_return_rate
        float projected_corpus
        string status
    }
    PORTFOLIOS {
        int id PK
        int user_id FK
        string portfolio_name
        json allocation
        float total_value
        string risk_level
    }
    TRANSACTIONS {
        int id PK
        int user_id FK
        int portfolio_id FK
        string transaction_type
        string asset_symbol
        float quantity
        float price_per_unit
        date transaction_date
    }
```

**Figure 4.2: Entity–relationship diagram** (key columns shown; full columns in Tables 4.3–4.12)

**Table 4.3: `users` (9 columns)**

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PK | Surrogate key |
| email | VARCHAR | UNIQUE, NOT NULL, indexed | Login identifier |
| password_hash | VARCHAR | NOT NULL | bcrypt hash (cost 12); the plain password is never stored |
| full_name | VARCHAR | NOT NULL | Display name |
| phone | VARCHAR | NULL | Optional contact |
| is_active | BOOLEAN | default TRUE | Account enabled |
| is_verified | BOOLEAN | default FALSE | Reserved for e-mail verification |
| created_at / updated_at | DATETIME | server defaults | Audit timestamps |

**Table 4.4: `financial_profiles` (10 columns)**

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PK | |
| user_id | INTEGER | FK → users.id, UNIQUE | One profile per user |
| age | INTEGER | validated 18–100 | |
| monthly_income | FLOAT | > 0 | ₹ per month |
| monthly_savings | FLOAT | ≥ 0 | ₹ per month |
| investment_horizon | VARCHAR | one of: 1-3, 3-5, 5-10, 10+ Years | Validated by schema |
| risk_tolerance | VARCHAR | enumerated (Low … High) | Stated preference |
| financial_goal | VARCHAR | one of: Wealth Creation, Retirement, House Purchase, Education, Emergency Fund | Validated by schema |
| created_at / updated_at | DATETIME | | |

**Table 4.5: `risk_profiles` (8 columns)** — id PK; user_id FK UNIQUE; risk_score FLOAT; investor_type VARCHAR; explanation TEXT (rule-based); ai_explanation TEXT (cached LLM output, cleared when the profile is recalculated); created_at; updated_at.

**Table 4.6: `portfolio_recommendations` (10 columns)** — id PK; user_id FK UNIQUE; stocks_percent, mutual_funds_percent, gold_percent, emergency_percent FLOAT (sum = 100); recommendation_summary TEXT; ai_explanation TEXT; created_at; updated_at.

**Table 4.7: `portfolio_analyses` (19 columns)** — id PK; user_id FK; volatility, volatility_percent, sharpe_ratio, max_drawdown, max_drawdown_percent, risk_score FLOAT; risk_level VARCHAR; average_return, average_return_percent, total_return, risk_free_rate FLOAT; data_points, analysis_period_days INTEGER; portfolio_data JSON; ai_explanation TEXT; created_at; updated_at.

**Table 4.8: `diversification_analyses` (14 columns)** — id PK; user_id FK; diversification_score, hhi_score FLOAT; num_holdings INTEGER; total_value FLOAT; sector_concentration, asset_concentration, warnings, recommendations, holdings_data JSON; ai_explanation TEXT; created_at; updated_at.

**Table 4.9: `monte_carlo_simulations` (24 columns)**

| Column group | Columns |
|---|---|
| Identity | id PK, user_id FK, simulation_name, notes |
| Inputs | initial_investment, expected_return, volatility, years, num_simulations, monthly_contribution, random_seed |
| **Volatility provenance** (migration 0002) | volatility_source (`manual` / `ml_predicted` / `historical_fallback`), predicted_volatility, volatility_model_version, volatility_ticker |
| Results (JSON) | statistics, scenarios, confidence_intervals, percentile_paths, histogram_data, risk_metrics |
| Explanation | ai_explanation |
| Audit | created_at, updated_at |

The provenance columns mean a saved simulation always records *which* volatility it used and *where it came from*. A result produced with a model forecast can therefore be told apart from one produced with a typed-in number, even after the model has been retrained.

**Table 4.10: `sip_plans` (22 columns)** — id PK; user_id FK; plan_name; investment_amount; frequency; start_date; end_date; duration_months; equity_percentage, debt_percentage, gold_percentage; expected_return_rate; projected_corpus; total_investment; status; is_active; installments_paid; total_invested; current_value; ai_explanation; created_at; updated_at.

**Table 4.11: `portfolios` (16 columns)** — id PK; user_id FK; portfolio_name; portfolio_type; is_active; allocation JSON; total_value; expected_return; risk_level; current_return; invested_amount; current_amount; rebalance_date; notes; created_at; updated_at. *(Reserved for Phase 2 holdings tracking.)*

**Table 4.12: `transactions` (14 columns)** — id PK; user_id FK; portfolio_id FK → portfolios.id; transaction_type; asset_type; asset_name; asset_symbol; quantity; price_per_unit; total_amount; fees; transaction_date; notes; created_at. *(Reserved for Phase 2.)*

## 4.5 Key Design Patterns

### 4.5.1 Stateless Service Layer

Every financial algorithm is a static method on a service class that takes plain values and returns plain dictionaries. Services never touch the HTTP request or the database session. This yields three benefits:

1. Algorithms can be unit-tested without a server or database. The 30 Monte Carlo tests run in milliseconds.
2. The same service is reused by several routers. `MLPredictionService` serves both the Monte Carlo and the Stock Predictor.
3. Routers stay thin: validate, authorise, call the service, persist, respond.

### 4.5.2 Graceful Degradation with Labelled Fallback

Neither the ML model nor the LLM is allowed to become a single point of failure. The volatility service always returns a usable number as long as price history exists, and **it says which kind of number it is**:

| Condition | Returned volatility | `source` | `fallback_reason` |
|---|---|---|---|
| Valid model, enough history, plausible output | Model forecast | `ml_predicted` | — |
| No artifact, or contract mismatch at load | Trailing 21-day realised volatility | `historical_fallback` | e.g. "No volatility model artifact loaded" |
| History too short for features | Trailing realised volatility | `historical_fallback` | "Insufficient history for features …" |
| Model raises an exception | Trailing realised volatility | `historical_fallback` | "Model prediction failed …" |
| Output non-finite or outside [1%, 300%] | Trailing realised volatility | `historical_fallback` | "outside the plausible range …" |
| No price data and no cache | — | — | HTTP 503 |

The Stock Predictor applies the same principle to direction. With no validated classifier, the probability shown is the stock's historical base rate, and the interface labels it **"Not a prediction"**.

### 4.5.3 Model Contract (Registry Pattern)

A trained model is saved as a **bundle**: the estimator plus metadata (model version, feature names in order, horizon, target, training date, metrics, library versions). At load time the registry checks that:

- the file is a bundle, not a bare pickle;
- the feature list matches `FEATURE_NAMES` exactly and in order;
- the horizon equals `HORIZON_DAYS`;
- the estimator has `predict` (or, for the trend model, `predict_proba` with an "up" class);
- a volatility artifact is not mistaken for a trend artifact.

Any mismatch raises `ModelContractError`, and the service falls back instead of serving silently wrong predictions. Training and inference import the *same* `config.py` and `features.py`, so they cannot drift apart.

### 4.5.4 Explanation Cache (Cache-Aside)

LLM inference on a CPU takes about 30–55 seconds, so each explanation is generated once and stored in the `ai_explanation` column of the result it explains. Subsequent requests return it immediately with `cached: true`. When the underlying result changes (for example, a recalculated risk profile), the cached explanation is set to `NULL` and regenerated on the next request.

### 4.5.5 Deterministic Output Guard

For the Stock Predictor, the LLM's text is checked by `explanation_guard.apply_outlook_guard()` before it is returned:

- **Rejected, not edited:** direct advice ("you should buy", "consider selling", "buy now"), guarantees and "risk-free" claims, and price moves stated as certain ("the stock will rise"). Negated assurances such as "does not guarantee" are permitted, so the standard disclaimer is not a false positive.
- **Appended:** if the probability is only the base rate and the text does not already say it is not a prediction, a fixed caveat sentence is added.

Rejected text is discarded rather than rewritten, because rewriting model prose would put unreviewed words into the explanation.

### 4.5.6 Leakage-Safe ML Pipeline

The pipeline enforces chronological splits with an **embargo measured in distinct trading dates** (Section 4.6). The training script verifies the embargo rather than trusting it, because on a pooled multi-ticker panel a row-based gap of 21 rows covers only about 2 dates.

### 4.5.7 Configuration as a Single Source of Truth

Runtime settings (database URL, JWT secret and expiry, CORS origins, Ollama URL, model and timeout) are read from `.env` through a Pydantic `Settings` class. ML constants (universe, horizon, embargo, plausibility bounds, cache TTL) live in `app/ml/config.py`.

## 4.6 Machine Learning Pipeline Design

### 4.6.1 Problem Formulation

- **Target:** annualised realised volatility over the **next 21 trading days**,
  $\sigma^{fwd}_t = \sqrt{252}\cdot\text{std}(r_{t+1},\dots,r_{t+21})$, where $r$ are daily log returns.
- **Universe:** 10 liquid NSE large-caps across sectors: RELIANCE, TCS, HDFCBANK, INFY, ICICIBANK, HINDUNILVR, ITC, LT, MARUTI and SUNPHARMA. The Nifty 50 (`^NSEI`) is used as market context and is never a target.
- **History:** 10 years of daily OHLCV from Yahoo Finance, cached as Parquet.

### 4.6.2 Features

**Table 4.15: Volatility model feature groups** (21 features; full dictionary in Appendix B)

| Group | Features | Intuition |
|---|---|---|
| Recent returns | `ret_1d`, `ret_lag_1` … `ret_lag_5` | Leverage effect: falls raise future volatility more than rises |
| Realised volatility (HAR core) | `rv_5`, `rv_10`, `rv_21`, `rv_63` | Volatility clusters at daily, weekly, monthly and quarterly scales |
| Term structure | `rv_ratio_5_21`, `rv_ratio_21_63` | Is short-term volatility above or below its longer-term level? |
| Range estimators | `parkinson_21`, `garman_klass_21` | High–low ranges carry information that closes alone do not |
| Activity | `volume_ratio_20` | Abnormal volume accompanies volatility shocks |
| Trend and stress | `mom_21`, `mom_63`, `rsi_14`, `drawdown_52w` | Stressed, falling markets are more volatile |
| Market context | `idx_rv_21`, `idx_mom_21` | Market-wide volatility drives single-stock volatility |

Every feature at date *t* uses only data up to and including *t*. This is enforced by tests that delete all future rows and confirm the feature row is unchanged.

### 4.6.3 Pipeline

```mermaid
flowchart LR
    A["Yahoo Finance<br/>10 NSE stocks + Nifty 50<br/>10 years daily OHLCV"] --> B["Parquet cache<br/>(24 h TTL)"]
    B --> C["features.py<br/>21 features, no look-ahead"]
    C --> D["Training table<br/>features + target_rv_21d + target_up_21d<br/>21,990 rows"]
    D --> E["Chronological split<br/>embargo = 21 distinct dates"]
    E --> F["Walk-forward CV by date<br/>QLIKE · 1-SE rule"]
    F --> G["Candidates on log σ<br/>Ridge · RandomForest · HistGB"]
    G --> H["Test once<br/>vs naive · HAR · GARCH(1,1)<br/>block bootstrap CIs"]
    H -->|"beats naive on RMSE AND QLIKE"| I["save_model()<br/>bundle + metadata"]
    I --> J["volatility_model.joblib"]
    J --> K["MLPredictionService<br/>contract check · plausibility guard"]
    K --> L["Monte Carlo σ"]
    K --> M["Stock Predictor range"]
    K -.->|"any failure"| N["historical_fallback<br/>(labelled)"]
```

**Figure 4.3: Volatility forecasting pipeline: training and serving**

### 4.6.4 Split and Embargo

Consecutive 21-day targets overlap by up to 20 days. If a training row's target window reaches into the test period, the model is partly trained on test data. The split is therefore chronological, and **the 21 distinct trading dates immediately before the test start are dropped** for every ticker.

```
 Train (all tickers)                     Embargo (21 dates)        Test (all tickers)
 2017-10-16 ─────────────── 2024-10-30 │ ░░░░░░░░░░░░░░░░░░░ │ 2024-12-03 ────────── 2026-09-08
                     17,390 rows        │    210 rows dropped  │          4,390 rows
```

**Figure 4.4: Leakage-safe chronological split with 21-date embargo**

The same embargo applies inside cross-validation, where expanding-window folds are built **by date**. No date can appear in both a training and a validation fold, and no ticker's date can straddle a fold boundary.

### 4.6.5 Model Selection and Acceptance

- Candidates are fitted on **log(volatility)** inside `TransformedTargetRegressor(func=np.log, inverse_func=np.exp)`, so predictions are always positive and errors are proportional.
- Hyperparameters are tuned by walk-forward cross-validation on **QLIKE**, which is robust to the noisy volatility proxy [13].
- **One-standard-error rule:** among families whose cross-validated QLIKE is within one standard error of the best, the simplest is chosen (Ridge, then HistGradientBoosting, then RandomForest).
- **Acceptance gate:** the model is saved only if it beats naive persistence on *both* RMSE and QLIKE on the untouched test half. A tie is not a win. The script also refuses to save if installed library versions differ from `requirements.txt`, because the artifact is a pickle.

## 4.7 API Design

The API is RESTful, uses JSON throughout, and is versioned by prefix (`/api/...`). Authentication uses an `Authorization: Bearer <JWT>` header. Errors use standard HTTP codes:
- **400**: business-rule violation.
- **401**: missing or invalid token.
- **403**: another user's resource.
- **404**: not found.
- **422**: validation failure, with field-level detail.
- **503**: market data unavailable.

**Table 4.16: API endpoint summary by module** (complete list in Appendix A)

| Module | Representative endpoints | Auth |
|---|---|---|
| System | `GET /`, `GET /health` | Public |
| Auth | `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me` | Public / JWT |
| Users | `GET` and `PUT /api/users/{user_id}` (own record only) | JWT + ownership |
| Profile | `POST`, `GET`, `PUT`, `DELETE /api/profile/` | JWT |
| Risk | `POST /api/risk/calculate`, `GET /api/risk/`, `DELETE /api/risk/`, `GET /api/risk/explain` | JWT |
| Recommendation | `POST /api/recommendation/generate`, `GET`, `DELETE`, `GET /explain` | JWT |
| Portfolio analytics | `POST /analyze`, `GET /latest`, `POST /generate-sample-data`, `GET /explain` | JWT (sample data public) |
| Diversification | `POST /analyze`, `GET /latest`, `GET /history`, `POST /generate-sample-holdings`, `DELETE /{id}`, `GET /explain` | JWT (sample data public) |
| Monte Carlo | `POST /simulate`, `GET /simulations`, `GET`, `PUT`, `DELETE /simulations/{id}`, `GET /latest`, `GET /explain` | JWT |
| SIP | `POST /calculate`, `POST /explain`, `POST` and `GET /plans`, `GET`, `PUT`, `DELETE /plans/{id}` | JWT |
| Market | `GET /search`, `GET /stock/{ticker}`, `GET /stock/{ticker}/history`, `GET /stock/{ticker}/outlook/explain`, `GET /stock/{ticker}/explain` | JWT |
| ML | `POST /predict-volatility`, `GET /model-info`, `POST /reload-model`, `GET /features/{ticker}`, `GET /trend-outlook/{ticker}`, `GET /trend-model-info`, `POST /reload-trend-model`, `GET /cache-status` | JWT |
| Ollama | `GET /api/ollama/health`, `GET /api/ollama/test` | Public |

**Example: volatility forecast**

```http
POST /api/ml/predict-volatility
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json

{ "ticker": "RELIANCE.NS" }
```

```json
{
  "ticker": "RELIANCE.NS",
  "volatility": 0.228399,
  "volatility_percent": 22.84,
  "source": "ml_predicted",
  "horizon_days": 21,
  "predicted_volatility": 0.228399,
  "historical_volatility": 0.228029,
  "model_version": "ridge-log-20261011",
  "fallback_reason": null,
  "as_of": "2026-10-14"
}
```

*(Actual response captured on 14 October 2026. The model forecast and trailing realised volatility happen to coincide closely on this date; on calmer or more turbulent dates they differ. See the compression discussion in Section 7.3.)*

![Swagger UI](figures/fig_swagger.png)

**Figure 4.8: Interactive API documentation (Swagger UI)**

## 4.8 Interaction Flows

```mermaid
sequenceDiagram
    actor U as User
    participant FE as React SPA
    participant API as FastAPI
    participant RC as RiskCalculator
    participant RE as RecommendationEngine
    participant DB as SQLite

    U->>FE: Fill financial profile
    FE->>API: POST /api/profile/ (JWT)
    API->>DB: INSERT financial_profiles
    U->>FE: Open Risk Assessment
    FE->>API: POST /api/risk/calculate
    API->>DB: SELECT profile
    API->>RC: calculate_risk_score(profile)
    RC-->>API: score 85.31, Aggressive, factor breakdown
    API->>DB: UPSERT risk_profiles (ai_explanation = NULL)
    API-->>FE: 200 risk profile
    U->>FE: Open Recommendations
    FE->>API: POST /api/recommendation/generate
    API->>RE: generate_recommendation(type, score, savings)
    RE-->>API: 65.5 / 21.6 / 7.2 / 5.7 %
    API->>DB: UPSERT portfolio_recommendations
    API-->>FE: 200 allocation + summary
```

**Figure 4.5: Sequence diagram: profile → risk → recommendation**

```mermaid
sequenceDiagram
    actor U as User
    participant FE as Monte Carlo page
    participant API as FastAPI
    participant ML as MLPredictionService
    participant YF as Yahoo / Parquet cache
    participant MC as MonteCarloSimulator
    participant DB as SQLite

    U->>FE: Choose "Use ML volatility" for RELIANCE.NS
    FE->>API: POST /api/ml/predict-volatility
    API->>ML: get_forecast("RELIANCE.NS")
    ML->>YF: load_history(ticker), load_history(^NSEI)
    ML->>ML: latest_feature_row → artifact.predict → guard [1%, 300%]
    ML-->>API: σ = 0.228, source = ml_predicted, version
    API-->>FE: forecast
    U->>FE: Run 10,000 paths, 10 years, seed 42
    FE->>API: POST /api/monte-carlo/simulate (σ, provenance)
    API->>MC: run_simulation(...)
    MC-->>API: statistics, scenarios, CIs, VaR/CVaR, paths
    API->>DB: INSERT monte_carlo_simulations (with provenance)
    API-->>FE: results → fan chart + histogram
```

**Figure 4.6: Sequence diagram: Monte Carlo simulation with ML volatility**

```mermaid
sequenceDiagram
    actor U as User
    participant FE as Stock Predictor
    participant API as FastAPI
    participant TS as StockTrendService
    participant LLM as Ollama (Qwen2.5-3B)
    participant G as ExplanationGuard

    U->>FE: Click "Explain"
    FE->>API: GET /api/market/stock/RELIANCE.NS/outlook/explain
    API->>TS: get_outlook(ticker)
    TS-->>API: trend, probability (base rate 49.2%), range
    API->>LLM: prompt with computed numbers + rules
    LLM-->>API: draft text
    API->>G: apply_outlook_guard(text, outlook)
    alt advice / guarantee / certainty found
        G-->>API: (None, reason)
        API-->>FE: explanation unavailable (reason)
    else acceptable
        G-->>API: text (+ "not a prediction" caveat if missing)
        API-->>FE: explanation
    end
```

**Figure 4.7: Sequence diagram: AI explanation with cache and output guard**

## 4.9 Security Controls

**Table 4.17: Security controls checklist**

| # | Control | Implementation | Status |
|---|---|---|---|
| 1 | Password storage | bcrypt with per-password salt, cost factor 12; 72-byte limit measured in bytes, not characters | ✅ |
| 2 | Authentication | JWT (HS256), 30-minute expiry, `type: access` claim, subject = user id | ✅ |
| 3 | Token validation | Signature, expiry and type checked on every protected route through a FastAPI dependency | ✅ |
| 4 | Authorisation (ownership) | All queries are filtered by the current user's id; `/api/users/{id}` returns 403 for other users | ✅ |
| 5 | Input validation | Pydantic v2 schemas with ranges, lengths, e-mail format; 422 with field detail | ✅ |
| 6 | Path-traversal defence | Ticker validated against a strict symbol pattern before building any cache path; the hostile-ticker test never produces a path outside the cache | ✅ |
| 7 | SQL injection | SQLAlchemy ORM with bound parameters; no string-built SQL | ✅ |
| 8 | CORS | Allow-list from `ALLOWED_ORIGINS` (comma-separated) | ✅ |
| 9 | Secrets management | Secrets read from `.env`, which is git-ignored | ✅ (secret must be rotated before deployment) |
| 10 | Model-artifact integrity | Contract check at load; bare pickles refused; the artifact must not reference the training script | ✅ |
| 11 | AI output safety | Deterministic guard against advice, guarantees and certainty; base-rate caveat | ✅ |
| 12 | Data privacy | LLM inference local; no third-party AI calls | ✅ |
| 13 | Error handling | Domain errors mapped to explicit HTTP codes with readable messages; unhandled exceptions return a generic 500 without a stack trace | ✅ |
| 14 | Rate limiting / brute-force protection | Not implemented (bcrypt cost slows guessing to about 1 attempt/s/core) | ⏳ Planned |
| 15 | HTTPS / TLS | Local HTTP only | ⏳ Planned for deployment |
| 16 | Refresh tokens / revocation | Not implemented (short 30-minute expiry instead) | ⏳ Planned |

## 4.10 User Interface Design

The interface is a single-page application with a persistent top navigation bar. Public routes are `/`, `/login` and `/register`. Every other page loads its data from JWT-protected endpoints. If the token is missing or expired, the Axios response interceptor receives HTTP 401, clears the stored token and redirects to `/login`. Protection is therefore enforced by the API, not by a client-side route guard; adding a `ProtectedRoute` wrapper is listed as an improvement.

```mermaid
flowchart LR
    H["Home /"] --> L["Login"]
    H --> R["Register"]
    R --> L
    L --> D["Dashboard"]
    D --> P["Financial Profile"]
    P --> RA["Risk Assessment"]
    RA --> PR["Recommendations"]
    D --> PA["Portfolio Analytics"]
    D --> DV["Diversification"]
    D --> MC["Monte Carlo"]
    D --> SIP["SIP Planner"]
    D --> SE["Stock Explorer"]
    SE -->|"See the 21-day outlook"| SP["Stock Predictor"]
    D --> PF["Portfolio (Phase 2)"]
```

**Figure 4.9: Navigation map of the user interface**

Design principles:
- one primary action per card;
- results shown as both numbers and charts;
- colour-coded risk levels (green, amber, red);
- every AI section loaded asynchronously, so slow LLM inference never blocks the numerical results;
- explicit labels for any value that is not a prediction.

<div style="page-break-after: always;"></div>

# CHAPTER 5 — IMPLEMENTATION

## 5.1 Technology Stack

**Table 5.1: Backend technology stack**

| Layer | Technology | Purpose in this project |
|---|---|---|
| Language | Python 3.13.7 | Backend, ML and scripts |
| Web framework | FastAPI 0.141.1 | Async REST API, dependency injection, automatic OpenAPI |
| Validation | Pydantic v2 | Request and response schemas, settings management |
| ASGI server | Uvicorn | Serves the FastAPI application |
| ORM | SQLAlchemy 2.0.52 | Declarative models, sessions, relationships |
| Migrations | Alembic 1.19.1 | Versioned schema (`0001_baseline`, `0002_add_volatility_provenance`) |
| Database | SQLite | Zero-configuration development database |
| Security | bcrypt 5.0.0, python-jose | Password hashing (cost 12); JWT HS256 |
| HTTP client | httpx | Async calls to Ollama |
| Market data | yfinance 1.5.2 | OHLCV, quotes and company information |
| Numerics | NumPy, pandas | Vectorised simulation, time-series features |
| Storage format | pyarrow 25.0.1 (Parquet) | Price-history cache |

**Table 5.2: Frontend technology stack**

| Technology | Version | Purpose |
|---|---|---|
| React | 18 | Component-based SPA |
| Create React App (react-scripts) | 5.0.1 | Build tooling, dev server, hot reload |
| React Router | 6.21 | Client-side routing (15 pages) |
| Tailwind CSS | 3.x | Utility-first responsive styling |
| Recharts | 2.15 | Line, area, bar, pie and composed charts |
| Axios | 1.6 | HTTP client with JWT and 401 interceptors |
| react-markdown | 10.1 | Renders LLM explanations written in Markdown |

**Table 5.3: AI/ML technology stack**

| Technology | Version | Purpose |
|---|---|---|
| scikit-learn | 1.9.0 | Ridge, HistGradientBoosting, RandomForest, TransformedTargetRegressor, pipelines, metrics |
| statsmodels | 0.15.0 | Statistical modelling library installed with the ML stack |
| arch | 8.0.0 | GARCH(1,1) baseline |
| joblib | — | Model bundle serialisation |
| Ollama | — | Local LLM server |
| Qwen2.5-3B (`qwen2.5:3b`) | — | Explanation model (about 1.9 GB, runs on CPU) |

**Table 5.4: Code size by component** (non-blank lines, measured)

| Component | Lines |
|---|---|
| Backend application (`backend/app`: routers, services, models, schemas, core, ml) | 9,637 |
| Dataset preparation and training scripts (`backend/ml`, `backend/scripts`) | 1,282 |
| Backend tests (`backend/tests`) | 2,564 |
| Frontend (`frontend/src`) | 7,355 |
| **Total** | **20,838** |

## 5.2 Project Structure

```
AI Smart Investment Portfolio Advisor/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app, CORS, router registration
│   │   ├── core/                      # config.py, database.py, security.py, dependencies.py
│   │   ├── models/                    # 10 SQLAlchemy models
│   │   ├── schemas/                   # Pydantic request/response schemas
│   │   ├── api/                       # 12 routers (auth, users, profile, risk, recommendation,
│   │   │                              #   portfolio_analysis, diversification_analysis, monte_carlo,
│   │   │                              #   sip, market, ml, ollama_health)
│   │   ├── services/                  # risk_calculator, recommendation_engine,
│   │   │                              #   portfolio_risk_analyzer, diversification_analyzer,
│   │   │                              #   monte_carlo_simulator, sip_calculator,
│   │   │                              #   yahoo_finance_service, ml_prediction_service,
│   │   │                              #   stock_trend_service, ollama_service, ollama_prompts,
│   │   │                              #   explanation_guard
│   │   └── ml/                        # config, data, features, evaluation,
│   │                                  #   model_registry, trend, trend_registry
│   ├── ml/                            # prepare_volatility_dataset.py, prepare_trend_dataset.py
│   ├── scripts/train_volatility_model.py
│   ├── alembic/versions/              # 0001_baseline, 0002_add_volatility_provenance
│   ├── models/                        # trained artifacts (git-ignored)
│   ├── data_cache/                    # Parquet price cache (git-ignored)
│   ├── tests/                         # 9 test modules, 338 tests
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── App.js                     # routes
│       ├── context/                   # AuthContext
│       ├── pages/                     # 15 pages
│       ├── components/Layout/         # Navbar, Footer, Layout
│       ├── components/common/         # Button, Card, Input, Select, Loading, PieChart, RiskGauge
│       └── services/                  # api.js + 10 domain services
├── docs/                              # testing.md, report/
├── README.md · ARCHITECTURE.md · PROJECT_BRIEF.md
```

## 5.3 Backend Services

### 5.3.1 Application Bootstrap and Core

`app/main.py` creates the FastAPI application and configures CORS from `ALLOWED_ORIGINS`. It then registers the 12 routers under `/api/...`. `core/config.py` loads `.env` into a typed `Settings` object (database URL, `SECRET_KEY`, `ALGORITHM = "HS256"`, `ACCESS_TOKEN_EXPIRE_MINUTES = 30`, Ollama URL, model, a 180-second timeout and an enable flag). `core/dependencies.py` provides two dependencies:
- `get_db`, which yields a session per request;
- `get_current_user`, which decodes the bearer token, checks its signature, expiry and `type`, and returns the user id, or raises 401.

### 5.3.2 Authentication and Security

Passwords are hashed with bcrypt at cost 12. Because bcrypt silently truncates input at **72 bytes**, the registration schema rejects any password longer than 72 *bytes*. A multibyte password is measured in bytes, not characters, so two different long passwords can never collapse to the same hash. Tokens carry `sub` (user id), `exp` and `type: "access"`. A token signed with a different key, a malformed token, or one of the wrong type is rejected; each case has a unit test (Table 6.8).

The user router enforces ownership explicitly:

```python
def _authorise_self(user_id: int, current_user_id: int) -> None:
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own user record",
        )
```

### 5.3.3 Risk Calculator

```python
# app/services/risk_calculator.py (excerpt)
weights = {'age': 0.15, 'income': 0.10, 'savings': 0.15,
           'horizon': 0.25, 'tolerance': 0.35}

total_score = (age_score * weights['age'] + income_score * weights['income'] +
               savings_score * weights['savings'] + horizon_score * weights['horizon'] +
               tolerance_score * weights['tolerance'])
risk_score = round(total_score, 2)

if risk_score < 40:
    investor_type = "Conservative"
elif risk_score < 70:
    investor_type = "Moderate"
else:
    investor_type = "Aggressive"
```

The rule-based explanation lists every factor with its sub-score and a reason ("Younger age allows for higher risk capacity"), so the user sees exactly why the score came out as it did (Figure 7.6). When the profile is updated, the risk profile is recomputed and the cached AI explanation is cleared.

### 5.3.4 Recommendation Engine

```python
# app/services/recommendation_engine.py (excerpt)
risk_score = max(0.0, min(100.0, risk_score))
stocks_percent       = 10.0 + (risk_score / 100.0) * 65.0   # 10% -> 75%
mutual_funds_percent = 60.0 - (risk_score / 100.0) * 45.0   # 60% -> 15%
gold_percent         = 20.0 - (risk_score / 100.0) * 15.0   # 20% ->  5%
emergency_percent    = 10.0 - (risk_score / 100.0) *  5.0   # 10% ->  5%
# rounded to 0.1; any rounding residue is absorbed by mutual funds so the total is exactly 100
```

The engine also produces a recommendation summary for the investor type, taking the user's monthly savings into account.

### 5.3.5 Portfolio Risk Analyzer and Diversification Analyzer

```python
# app/services/portfolio_risk_analyzer.py (excerpt)
returns = np.diff(values) / values[:-1]
volatility = np.std(returns, ddof=1) * np.sqrt(252)              # annualised
sharpe = (np.mean(returns) * 252 - 0.06) / volatility            # rf = 6%
running_max = np.maximum.accumulate(values)
max_drawdown = ((values - running_max) / running_max).min()      # <= 0
```

The composite risk score combines volatility (40%), Sharpe (30%, inverted so a higher Sharpe lowers risk) and drawdown (30%), and is classified as Low, Moderate or High. The sample-data generator produces a GBM-like daily series from user-chosen initial value, days (30–1,260), volatility and expected return, so the analytics can be explored without a broker connection.

The diversification analyzer aggregates holdings by sector and asset type. It computes $HHI = \sum w_i^2$ (in percent) and combines four component scores with weights 35/30/20/15 (Table 4.14). It emits graded warnings ("High sector concentration: Banking represents 45% of portfolio", "Moderate sector concentration …", "High asset concentration …"), each paired with a recommendation. Two sample portfolios ("well diversified", 12 holdings across 8 sectors and 4 asset types, and "concentrated") demonstrate the range of the score.

### 5.3.6 Monte Carlo Simulator

The simulator is fully vectorised in NumPy. All random shocks for all paths and months are drawn in one call, and only the monthly contribution loop runs in Python (120 iterations for 10 years).

```python
# app/services/monte_carlo_simulator.py (excerpt)
rng = np.random.default_rng(random_seed)           # reproducible when seeded
num_periods = years * PERIODS_PER_YEAR              # monthly steps
dt = 1.0 / PERIODS_PER_YEAR

# Per-step log-return parameters, with the Ito correction so the
# simulated arithmetic mean matches `expected_return`.
step_sigma = volatility * np.sqrt(dt)
step_drift = dt * np.log1p(expected_return) - 0.5 * (step_sigma ** 2)

growth_factors = np.exp(
    rng.normal(step_drift, step_sigma, size=(num_simulations, num_periods))
)
portfolio_values = np.zeros((num_simulations, num_periods + 1))
portfolio_values[:, 0] = initial_investment
for period in range(num_periods):
    grown = portfolio_values[:, period] * growth_factors[:, period]
    if monthly_contribution > 0:
        grown += monthly_contribution                # end-of-month contribution
    portfolio_values[:, period + 1] = grown
```

Validation rejects non-positive investment, horizons outside 1–50 years, path counts outside 1,000–50,000, negative volatility, returns ≤ −100% and negative contributions. Volatility above 100% is deliberately allowed, because a single stock's forecast can exceed it in a crisis. The result contains:
- statistics (mean, median, standard deviation, min, max, total contributions);
- scenarios (5th, 50th and 95th percentiles);
- 90%, 95% and 99% confidence intervals;
- the probabilities of profit and of doubling;
- VaR and CVaR at 5%;
- percentile paths (10/25/50/75/90) for the fan chart, a histogram, and 20 sample paths.

The route persists the inputs and results together with the **volatility provenance** fields.

### 5.3.7 SIP Calculator

```python
# app/services/sip_calculator.py (logic)
r = annual_return_rate / 12 / 100
n = years * 12
future_value = P * (((1 + r) ** n - 1) / r) * (1 + r)
wealth_generated = future_value - P * n
```

A year-by-year table feeds the growth chart (Figure 7.11). `calculate_required_sip` inverts the formula for goal-based planning. For example, a ₹1 crore corpus in 15 years at 12% requires **₹19,818.62 per month**.

### 5.3.8 Market Data Service

`YahooFinanceService` wraps yfinance for search, quotes (price, change, 52-week range, market cap, volume, open, high, low, previous close), company profile (sector, industry, description, website) and history over 1 month to 5 years. Values are formatted for the Indian context (₹, crore). The ML package uses its own loader (`app.ml.data.load_history`), which:
- validates the ticker against a strict pattern;
- caches each download as Parquet for 24 hours;
- serves a stale cache if the network fails.

### 5.3.9 ML Prediction Service

`MLPredictionService` lazily loads the volatility artifact once, then serves forecasts with an in-memory TTL cache. Its fallback logic is the core of the "never silently wrong" design:

```python
# app/services/ml_prediction_service.py (excerpt)
artifact = self._ensure_model()
if artifact is None:
    return fallback(self._load_error or "No volatility model artifact loaded")
try:
    features, as_of = latest_feature_row(history, index_history)
except ValueError as exc:
    return fallback(f"Insufficient history for features: {exc}")
try:
    predicted = artifact.predict(features)
except Exception as exc:
    return fallback(f"Model prediction failed: {exc}")
if not np.isfinite(predicted):
    return fallback(f"Model returned a non-finite value ({predicted})")
if not (MIN_PLAUSIBLE_VOLATILITY <= predicted <= MAX_PLAUSIBLE_VOLATILITY):   # [0.01, 3.00]
    return fallback(f"Model returned {predicted:.4f}, outside the plausible range ...")
return VolatilityForecast(ticker=ticker, volatility=float(predicted), source=SOURCE_ML,
                          predicted_volatility=float(predicted), historical_volatility=historical_vol,
                          model_version=artifact.model_version, as_of=...)
```

`POST /api/ml/reload-model` reloads the artifact without restarting the server. `GET /api/ml/features/{ticker}` returns the exact feature row the model would see, which is useful for debugging and for the viva demonstration.

### 5.3.10 Stock Trend Service (Stock Predictor)

`StockTrendService.get_outlook(ticker)` assembles three deliberately separate parts.

1. **Current trend (descriptive).** Four technical signals: price vs its 50-day average, 50-day vs 200-day average, 21-day momentum and 63-day momentum. The score is $(2\cdot\text{bullish} - n)/n$, labelled Bullish (≥ 0.5), Bearish (≤ −0.5) or Neutral. RSI(14) is reported as overbought, oversold or neutral, but not scored.
2. **Probability of a higher close in 21 trading days.** If a validated trend classifier is loaded, its probability is used (`ml_predicted`). Otherwise the stock's **historical base rate**, the share of its last 756 completed 21-day windows that ended higher, is shown and labelled "Not a prediction".
3. **Expected range.** Log-normal bands centred on today's price with no directional drift:

```python
# app/ml/trend.py (excerpt)
for k in range(horizon + 1):
    spread = sigma * math.sqrt(k / TRADING_DAYS_PER_YEAR)
    path.append({
        "day": k, "median": round(price, 2),
        "lower_68": round(price * math.exp(-Z_68 * spread), 2),
        "upper_68": round(price * math.exp( Z_68 * spread), 2),
        "lower_95": round(price * math.exp(-Z_95 * spread), 2),
        "upper_95": round(price * math.exp( Z_95 * spread), 2),
    })
```

Here σ is the ML volatility forecast, or the historical fallback. The range says *how far* the price may move, not *which way*; direction lives only in the probability.

## 5.4 Machine Learning Implementation

### 5.4.1 Data Layer (`app/ml/data.py`)

- `validate_ticker()` normalises symbols and rejects anything outside a strict pattern, such as `../../etc/passwd` or shell metacharacters. Such input raises a validation error (HTTP 422), never a server error.
- `load_history(ticker, period)` returns a clean OHLCV DataFrame from the Parquet cache (24-hour TTL) or Yahoo Finance.

### 5.4.2 Feature Engineering (`app/ml/features.py`)

```python
# Parkinson range volatility:  sigma = sqrt(mean(ln(H/L)^2) / (4 ln 2)) * sqrt(252)
def _parkinson(high, low, window):
    hl = np.log(high / low) ** 2
    mean_hl = hl.rolling(window, min_periods=window).mean()
    return np.sqrt(mean_hl / (4.0 * np.log(2.0))) * ANNUALISE

# Garman-Klass: 0.5 ln(H/L)^2 - (2 ln2 - 1) ln(C/O)^2, floored at zero before the root
def _garman_klass(open_, high, low, close, window):
    term = 0.5 * np.log(high / low) ** 2 - (2.0 * np.log(2.0) - 1.0) * np.log(close / open_) ** 2
    mean_term = term.rolling(window, min_periods=window).mean()
    return np.sqrt(mean_term.clip(lower=0.0)) * ANNUALISE
```

`build_features()` returns exactly `FEATURE_NAMES`, in order. `build_training_table()` appends the two labels, `target_rv_21d` (the regression target) and `target_up_21d` (the direction label for the future classifier), drops incomplete rows, and optionally adds a ticker column for pooled panels. The direction label is **not** a feature, and tests assert that the feature set remains exactly 21 columns. `chronological_split()` embargoes by distinct dates on pooled panels. `latest_feature_row()` produces the single inference row.

### 5.4.3 Evaluation Utilities (`app/ml/evaluation.py`)

- Point metrics: RMSE, MAE, R², and **QLIKE**, $\frac{\sigma^2}{\hat\sigma^2} - \ln\frac{\sigma^2}{\hat\sigma^2} - 1$. QLIKE is non-negative and penalises under-forecasting more heavily.
- Baselines: **naive persistence** (forecast = trailing `rv_21`) and **HAR**, a linear regression (scikit-learn `LinearRegression`) of the target on `rv_5`, `rv_21` and `rv_63`, the weekly, monthly and quarterly realised-volatility components.
- `compare_forecasts()` scores every forecast on the same rows and reports the percentage improvement over a chosen baseline.

### 5.4.4 Training Script (`scripts/train_volatility_model.py`, 743 lines)

The script runs end to end in nine stages:

1. **Environment check.** Installed versions of numpy, pandas, scikit-learn, scipy and joblib are compared with `requirements.txt`. A mismatch blocks saving.
2. **Panel build.** 10 tickers plus the index over 10 years: 21,990 complete rows from 2017-10-16 to 2026-09-08.
3. **Split and embargo verification.** The embargo is measured in distinct trading dates and, if it falls short, the panel is re-split by date:

```python
gap = date_gap(all_dates, last_train, first_test)
if gap < EMBARGO_DAYS:
    train, test = split_by_date(panel, test_fraction, EMBARGO_DAYS)
assert gap >= EMBARGO_DAYS, f"embargo is {gap} dates, need >= {EMBARGO_DAYS}"
assert last_train < first_test, "train and test overlap in time"
```

4. **Walk-forward folds by date** (expanding window, same embargo, at least 30 dates per validation block):

```python
for k in range(n_folds):
    v0 = start + k * block
    v1 = start + (k + 1) * block if k < n_folds - 1 else n
    t_end = v0 - embargo                       # train = dates[:t_end]
    tr_dates, va_dates = dates[:t_end], dates[v0:v1]
    assert date_gap(dates, tr_dates[-1], va_dates[0]) >= embargo
```

5. **Candidates on log-volatility.** Every family is wrapped so that predictions are exponentiated back and can never be negative:

```python
def wrap(regressor):
    return TransformedTargetRegressor(regressor=regressor, func=np.log, inverse_func=np.exp)

def make_ridge(alpha):
    return wrap(Pipeline([("scale", StandardScaler()), ("ridge", Ridge(alpha=alpha))]))

def make_hist_gb(max_depth, max_iter):
    # early_stopping=False on purpose: the default carves a RANDOM 10% validation
    # split, which on overlapping 21-day targets leaks neighbouring rows.
    return wrap(HistGradientBoostingRegressor(learning_rate=0.05, max_depth=max_depth,
                max_iter=max_iter, min_samples_leaf=300, l2_regularization=10.0,
                early_stopping=False, random_state=RANDOM_STATE))
```

   The ridge α grid was widened to 300,000 after the first run found its optimum at the grid edge (10,000). The final optimum, **α = 30,000**, is interior.

6. **One-standard-error family selection:**

```python
se = best[lowest]["qlike_std"] / np.sqrt(n_folds - 1)
threshold = cv[lowest] + se
within = [family for family in FAMILIES if cv[family] <= threshold]   # simplest first
return within[0], ...
```

7. **Single test evaluation** against naive persistence, HAR and (with `--garch`) GARCH(1,1), refitted periodically per ticker. A 21-date block bootstrap (4,000 resamples) gives confidence intervals on the improvements.
8. **Acceptance:** the model must beat naive on both RMSE and QLIKE. HAR and GARCH are reported for context but do not gate saving.
9. **Save** through `save_model()`, with metrics and provenance embedded, version `ridge-log-<YYYYMMDD>`. A final guard asserts that the pickled object does not reference the script's `__main__` module, so the API can load it.

The script defines no lambdas and no classes, so every saved object is importable from installed libraries alone. `--dry-run` evaluates without saving and `--force-save` overrides the gate explicitly.

### 5.4.5 Model Registry

`save_model()` writes a dictionary bundle containing:
- `estimator`
- `model_version`
- `feature_names`
- `horizon_days`
- `target`
- `trained_at`
- `metrics`
- library versions

`load_model(strict=True)` refuses a bare pickle, a feature list that differs in content or order, a different horizon, or an object without `predict`. `trend_registry` applies the same contract to classifiers, and additionally requires `predict_proba` and an "up" class found through `classes_` rather than assumed to be column 1. The live model reports itself as follows:

```json
{"model_loaded": true, "horizon_days": 21,
 "model": {"model_version": "ridge-log-20261011", "estimator": "TransformedTargetRegressor",
           "target": "target_rv_21d", "trained_at": "2026-10-11T05:41:56+00:00", "n_features": 21}}
```

## 5.5 LLM Explanation Layer

### 5.5.1 Ollama Service

`OllamaService` sends a non-streaming request to the local Ollama server:

```python
payload = {"model": self.model,                      # "qwen2.5:3b"
           "prompt": full_prompt, "stream": False,
           "options": {"temperature": temperature, "num_predict": max_tokens}}
async with httpx.AsyncClient(timeout=self.timeout) as client:      # 180 s
    response = await client.post(f"{self.base_url}/api/generate", json=payload)
```

Structured explanations use temperature 0.3 for consistency. If Ollama is disabled or unreachable, the service returns a structured error (`OLLAMA_DISABLED` or a connection error) and the page shows a friendly message while all numerical results remain available.

### 5.5.2 Prompt Design (`ollama_prompts.py`)

Each module has a prompt template filled **only with numbers the backend has already computed**: the risk factors and score, the allocation, the volatility, Sharpe and drawdown, the HHI and warnings, the Monte Carlo percentiles and VaR, the SIP totals, and the outlook figures. The model is asked to explain, never to calculate. The Stock Predictor prompt adds explicit rules, each enforced by a unit test (Table 6.5):

- If the probability is the base rate, it must be described as *not a prediction*.
- If a model's probability is shown, it must be compared with the base rate. A model that failed to beat history must be called out, and one that beat it must not be accused of failing.
- The range must be framed as carrying **no direction**.
- The trend must be framed as describing **the past**.
- The probability sentence is supplied verbatim for the model to copy, preventing numeric hallucination.
- The currency follows the exchange (₹ for `.NS`, $ otherwise).
- The volatility source (model or historical) is stated honestly.
- Advice and certainty are always forbidden.

### 5.5.3 Output Guard

Section 4.5.5 describes the guard. Its core:

```python
asserted = _NEGATED_ASSURANCE.sub("", cleaned)      # "does not guarantee" is fine
advice = _ADVICE.search(asserted)
if advice:
    return None, f"contains advice or a guarantee ('{advice.group(0)}')"
certain = _CERTAINTY.search(cleaned)
if certain:
    return None, f"states a price move as certain ('{certain.group(0)}')"
if outlook.get("probability_source") != "ml_predicted" and not _NOT_A_PREDICTION.search(cleaned):
    cleaned = f"{cleaned}\n\n{BASE_RATE_CAVEAT}"
return cleaned, None
```

The advice pattern is deliberately specific (for example, "you should buy" or "consider selling"), because single words like "buy" or "hold" occur in harmless text ("threshold", "buyers"). A unit test confirms that ordinary probability language ("the price will close higher with probability …") is not a false positive.

### 5.5.4 Caching

Explanations for risk, recommendation, portfolio analysis, diversification and Monte Carlo are stored in the `ai_explanation` column of the result and returned with `cached: true` on later requests. On a CPU-only laptop, the first explanation takes roughly **30–55 seconds**; cached responses return in milliseconds.

## 5.6 Frontend Implementation

**Table 5.5: Frontend pages and routes**

| Route | Page | Key elements |
|---|---|---|
| `/` | Home | Hero, feature overview, call to action |
| `/login`, `/register` | Login, Register | Validated forms, error display, redirect on success |
| `/dashboard` | Dashboard | Profile summary, risk score, savings rate, quick links to all modules |
| `/profile` | FinancialProfile | Create and edit the profile; triggers recomputation |
| `/risk-assessment` | RiskAssessment | `RiskGauge` (0–100), category legend, factor breakdown, next steps |
| `/portfolio-recommendation` | PortfolioRecommendation | Allocation donut, four allocation cards, regenerate action, AI analysis, next steps |
| `/portfolio` | Portfolio | Placeholder for Phase 2 holdings tracking |
| `/portfolio-analytics` | PortfolioAnalytics | Sample-data form, risk ring, metric cards, AI analysis |
| `/diversification` | DiversificationAnalysis | Sector pie, asset bar chart, HHI, warnings, recommendations |
| `/monte-carlo` | MonteCarloSimulation | Manual or ML volatility, percentile fan chart, histogram, VaR and CVaR, saved runs |
| `/sip-planner` | SIPPlanner | Calculator, presets, yearly growth chart, save plan, AI insights |
| `/stocks` | StockExplorer | Search, quick access, quote grid, history chart with period selector, link to outlook |
| `/stock-predictor` | StockPredictor | Trend card, probability vs base rate, 68%/95% range cone, table toggle, guarded AI explanation |
| `*` | NotFound | 404 page |

**Table 5.6: Frontend service modules**

| Service | Endpoints wrapped |
|---|---|
| `api.js` | Axios instance: base URL from `REACT_APP_API_BASE_URL`, 60 s timeout, JWT request interceptor, 401 response interceptor |
| `authService.js` | register, login, me, logout |
| `profileService.js` | profile CRUD |
| `riskService.js` | calculate, get, delete, explain |
| `recommendationService.js` | generate, get, delete, explain |
| `portfolioAnalysisService.js` | analyse, latest, sample data, explain |
| `diversificationService.js` | analyse, latest, history, sample holdings, delete, explain |
| `monteCarloService.js` | simulate, list, get, update, delete, latest, explain |
| `sipService.js` | calculate, explain, plans CRUD |
| `marketService.js` | search, stock info, history, explanations |
| `mlService.js` | predict-volatility, model-info, features, trend-outlook, cache-status |

**State and authentication.** `AuthContext` stores the token and user, and exposes `login`/`logout`. The request interceptor attaches `Authorization: Bearer <token>`. The response interceptor clears the token and redirects to `/login` on HTTP 401.

**Visualisation.** Recharts renders:
- the Monte Carlo percentile paths (p10, p25, p50, p75, p90 over time) and terminal-value histogram;
- the SIP invested-versus-value lines;
- the diversification pie and bar charts;
- the stock price history;
- the Stock Predictor cone, six months of closes followed by 68% and 95% bands out to +21 trading days.

A "Show as table" toggle gives an accessible alternative to the chart.

**Asynchronous AI sections.** Each page renders its numerical results immediately and requests the AI explanation separately, showing "Generating AI insights…". Slow inference therefore never blocks the numbers.

## 5.7 Database Migrations and Configuration

| Migration | Description |
|---|---|
| `0001_baseline` | Creates all ten tables with keys, unique constraints and indexes |
| `0002_add_volatility_provenance` | Adds `volatility_source`, `predicted_volatility`, `volatility_model_version`, `volatility_ticker` and `random_seed` to `monte_carlo_simulations` |

Commands:

```bash
cd backend
alembic upgrade head          # apply migrations
alembic revision -m "..."     # create a new migration
```

`.env` keys (backend): `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `ALLOWED_ORIGINS` (comma-separated), `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `OLLAMA_TIMEOUT`, `OLLAMA_ENABLED`. Frontend: `REACT_APP_API_BASE_URL`, `REACT_APP_API_TIMEOUT`.

## 5.8 Development Workflow

```bash
# 1. LLM (one-time model download, then keep running)
ollama pull qwen2.5:3b
ollama serve

# 2. Backend
cd backend
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --host 127.0.0.1 --port 8000

# 3. Frontend
cd frontend
npm install
npm start                      # http://localhost:3000

# 4. Tests
cd backend && pytest -q        # 336 passed, 2 skipped

# 5. Volatility model (optional; artifacts are git-ignored)
python scripts/train_volatility_model.py --dry-run --garch   # evaluate only
python scripts/train_volatility_model.py --garch             # save if accepted
```

The code is kept in a private GitHub repository with descriptive conventional-commit messages (`feat:`, `feat(ml):`). Model artifacts, the price cache, the SQLite database and `.env` files are git-ignored.

<div style="page-break-after: always;"></div>

# CHAPTER 6 — TESTING REPORTS

## 6.1 Testing Strategy

Testing focused on the parts of the system where a silent error would mislead a user: the financial mathematics, the machine-learning pipeline (where data leakage produces results that look good and are wrong), the security layer, and the AI output guard. Four levels were used:

| Level | What is tested | How |
|---|---|---|
| Unit | Pure functions and classes: simulator, security, features, labels, splits, metrics, registries, trend service, prompt builder, output guard, training-script helpers | `pytest`, synthetic data with known answers, property-style assertions |
| Component / API | FastAPI endpoints with dependencies overridden (explanation endpoints with a stubbed LLM) | FastAPI `TestClient` inside `pytest` |
| Black-box integration | The running server over HTTP: positive flows and negative paths | Python `httpx` scripts against `localhost:8000` |
| System / UI | Every page rendered with real data, in a real browser | Manual walkthrough plus automated screenshots (Puppeteer-core with Microsoft Edge) |

Design principles of the test suite:
- **Known answers.** Zero volatility must reproduce exact compounding, and a synthetic series with known volatility must be recovered by the realised-volatility feature.
- **Properties, not snapshots.** CVaR ≤ VaR, percentiles are ordered, confidence intervals nest, paths stay positive.
- **Adversarial inputs.** Hostile tickers, over-long passwords, forged tokens, models that raise exceptions or return NaN.
- **Tests that prove a bug exists before proving it is fixed.** For example, `test_a_row_based_embargo_really_does_leak_on_a_pooled_panel` demonstrates the leak that the date-based embargo prevents.

**Overall result:** 338 tests collected, **336 passed, 2 skipped, 0 failed**, in **29.99 s** (pytest 9.1.1, Python 3.13.7). The two skips are by design. A test that checks the serving guard rejects an *overflowed* prediction is parametrised over three model families, and it is skipped for HistGradientBoosting and RandomForest because tree ensembles cannot extrapolate beyond their training range and so cannot overflow.

## 6.2 Unit Testing

The tables below list representative test cases for each module. The complete set is in `backend/tests/`.

**Table 6.1: Monte Carlo simulator (`test_monte_carlo_simulator.py`, 30 tests)**

| Test ID | Function | Input | Expected Output | Result |
|---|---|---|---|---|
| MC-01 | `run_simulation` | σ = 0, fixed return, no contributions | Every path equals exact compound growth $V_0(1+\mu)^T$ | Pass |
| MC-02 | `run_simulation` | Same parameters, same seed, run twice | Identical results | Pass |
| MC-03 | `run_simulation` | Same parameters, different seeds | Results differ | Pass |
| MC-04 | `run_simulation` | High volatility | No path value ever ≤ 0 (GBM is positive) | Pass |
| MC-05 | `run_simulation` | Many paths, moderate σ | Mean log-growth matches the Itô-corrected drift | Pass |
| MC-06 | `run_simulation` | σ low vs σ high | Higher σ gives a wider terminal distribution | Pass |
| MC-07 | `run_simulation` | With vs without monthly contribution | Contributions raise both total invested and outcome | Pass |
| MC-08 | `calculate_risk_metrics` | Simulated terminal values | VaR and CVaR present; CVaR ≤ VaR | Pass |
| MC-09 | `calculate_risk_metrics` | Simulated terminal values | VaR equals the 5th percentile of terminal values | Pass |
| MC-10 | `_calculate_statistics` | Any run | Probabilities of loss and profit sum to 100% | Pass |
| MC-11 | `_calculate_scenarios`, `_calculate_confidence_intervals` | Any run | worst ≤ expected ≤ best; 90% ⊂ 95% ⊂ 99% intervals | Pass |
| MC-12 | percentile paths | Any run | p10 ≤ p25 ≤ p50 ≤ p75 ≤ p90 at every step; length = periods + 1 | Pass |
| MC-13 | validation | Investment ≤ 0, years 0 or 51, 500 paths, σ < 0, return ≤ −100% | `ValueError` | Pass |
| MC-14 | validation | σ > 1 (above 100%) | Accepted (crisis-level forecasts are legitimate) | Pass |

**Table 6.2: Security (`test_security.py`, 16 tests)**

| Test ID | Function | Input | Expected Output | Result |
|---|---|---|---|---|
| SEC-01 | `get_password_hash`, `verify_password` | A valid password | Hash verifies against the same password | Pass |
| SEC-02 | `verify_password` | Wrong password | `False` | Pass |
| SEC-03 | `get_password_hash` | Same password hashed twice | Different hashes (salted) | Pass |
| SEC-04 | `get_password_hash` | Any password | Hash prefix shows bcrypt with cost 12 | Pass |
| SEC-05 | `get_password_hash` | Password of exactly 72 bytes | Accepted | Pass |
| SEC-06 | `get_password_hash` | Password of 73 bytes | Clear error, not silent truncation | Pass |
| SEC-07 | `UserCreate` schema | Multibyte password under 72 characters but over 72 bytes | Rejected (measured in bytes) | Pass |
| SEC-08 | `UserCreate` schema | Password shorter than 8 characters | Validation error | Pass |
| SEC-09 | `UserCreate` schema | "not-an-email" | Validation error | Pass |
| SEC-10 | `create_access_token`, `decode` | A user id | Decoded subject equals the user id | Pass |
| SEC-11 | `create_access_token` | Any subject | Token carries `type: access` | Pass |
| SEC-12 | `decode_access_token` | Garbage string | `None` | Pass |
| SEC-13 | `decode_access_token` | Token signed with a different key | Rejected (`None`) | Pass |

**Table 6.3: Feature engineering and labels (`test_ml_features.py`, 50 tests)**

| Test ID | Function | Input | Expected Output | Result |
|---|---|---|---|---|
| FE-01 | `build_features` | Synthetic OHLCV | Exactly `FEATURE_NAMES`, in declared order; index preserved | Pass |
| FE-02 | `build_features` | Synthetic OHLCV | No ±∞; later rows fully populated | Pass |
| FE-03 | `build_features` | Rising and falling series | `drawdown_52w` ≤ 0; RSI within [0, 100]; volatility features > 0 | Pass |
| FE-04 | `_realised_vol` | GBM series with known σ | Recovered realised volatility ≈ generating σ | Pass |
| FE-05 | `build_features` | Frame missing a column | `ValueError` | Pass |
| FE-06 | features no-lookahead | History truncated after date *t* | Feature row at *t* unchanged | Pass |
| FE-07 | index features no-lookahead | Index history with future values removed | `idx_*` features at *t* unchanged | Pass |
| FE-08 | target | Synthetic series | Target equals forward realised volatility, not the trailing window | Pass |
| FE-09 | target | Last 21 rows | NaN (future unknown) | Pass |
| FE-10 | `target_up_21d` | Rising and falling series | Always 1 and always 0 respectively; forward return of exactly 0 is "down" | Pass |
| FE-11 | `target_up_21d` | Any series | Values only {0, 1, NaN}; same known and unknown rows as the volatility target | Pass |
| FE-12 | `FEATURE_NAMES` | — | Direction label not a feature; feature count still 21 | Pass |
| FE-13 | `build_training_table` | Synthetic panel | Columns = features + both labels; adding the label costs no rows | Pass |
| FE-14 | `chronological_split` | Pooled multi-ticker panel | Train strictly precedes test; embargo counts **dates**, not rows; every ticker in both halves | Pass |
| FE-15 | `chronological_split` | Fraction 1.5; tiny panel | `ValueError` | Pass |
| FE-16 | `latest_feature_row` | Short history | Raises; with enough history returns one row in declared order | Pass |

**Table 6.4: Evaluation metrics and baselines (`test_ml_evaluation.py`, 20 tests)**

| Test ID | Function | Input | Expected Output | Result |
|---|---|---|---|---|
| EV-01 | `score` | Forecast = actual | RMSE = MAE = QLIKE = 0 | Pass |
| EV-02 | `rmse`, `mae` | Same total error, concentrated vs spread | RMSE penalises concentrated error more | Pass |
| EV-03 | `qlike` | Random positive pairs | Always ≥ 0 | Pass |
| EV-04 | `qlike` | Under-forecast vs over-forecast of equal ratio | Under-forecast penalised more | Pass |
| EV-05 | `qlike` | Zero or negative forecasts | Dropped; all non-positive gives NaN | Pass |
| EV-06 | `qlike` | Several forecasts | Ranking matches Patton's formulation | Pass |
| EV-07 | `naive_persistence` | Table with `rv_21` | Forecast equals trailing `rv_21`; missing column raises | Pass |
| EV-08 | `fit_har`, `predict_har` | Training table | Fits and predicts; missing columns raise | Pass |
| EV-09 | `compare_forecasts` | Model + baselines | Each scored on the same rows with % improvement | Pass |
| EV-10 | `compare_forecasts` | Non-overlapping or no scorable forecast | Skipped or raises | Pass |

**Table 6.5: AI explanation prompts and output guard (`test_ml_explain.py`, 53 tests)**

| Test ID | Function | Input | Expected Output | Result |
|---|---|---|---|---|
| EX-01 | prompt builder | Outlook with base-rate probability | Prompt instructs "not a prediction" | Pass |
| EX-02 | prompt builder | Outlook with model probability | Prompt does not claim "not a prediction" and asks for comparison with the base rate | Pass |
| EX-03 | prompt builder | Model worse / better than history | Failure must be called out / not wrongly alleged | Pass |
| EX-04 | prompt builder | Any outlook | Advice and certainty forbidden; range framed as directionless; trend framed as past | Pass |
| EX-05 | prompt builder | Any outlook | Probability sentence supplied verbatim; numbers come from the outlook | Pass |
| EX-06 | prompt builder | `.NS` vs US ticker | ₹ vs $ currency | Pass |
| EX-07 | prompt builder | Fallback volatility | Source stated as historical, not model | Pass |
| EX-08 | `apply_outlook_guard` | "You should buy this stock", "guaranteed returns" | Rejected with reason | Pass |
| EX-09 | `apply_outlook_guard` | "The stock will definitely rise" | Rejected (certainty) | Pass |
| EX-10 | `apply_outlook_guard` | Empty text | Rejected | Pass |
| EX-11 | `apply_outlook_guard` | "…will close higher with probability 49%…", "does not guarantee" | Accepted (no false positive) | Pass |
| EX-12 | `apply_outlook_guard` | Base-rate outlook, text without caveat | Caveat appended once; not duplicated if present | Pass |
| EX-13 | `apply_outlook_guard` | Model-probability outlook | No base-rate caveat added; text otherwise untouched | Pass |
| EX-14 | explain endpoint | Stubbed LLM returns advice | Response withholds the text and gives the reason | Pass |

**Table 6.6: Model registry and prediction service (`test_ml_registry_and_service.py`, 22 tests)**

| Test ID | Function | Input | Expected Output | Result |
|---|---|---|---|---|
| RG-01 | `save_model` → `load_model` | Fitted estimator | Metadata preserved; loaded model predicts; summary JSON-serialisable | Pass |
| RG-02 | `VolatilityModelArtifact.predict` | Features in shuffled column order | Same prediction (order-insensitive) | Pass |
| RG-03 | `load_model` | Missing file | `FileNotFoundError` | Pass |
| RG-04 | `load_model` | Different or reordered feature list; different horizon | `ModelContractError` | Pass |
| RG-05 | `load_model` | Bare pickle, not a bundle | `ModelContractError` | Pass |
| RG-06 | `save_model` | Object without `predict` | Refused at save | Pass |
| RG-07 | `load_model(strict=False)` | Mismatched artifact | Loads for inspection only | Pass |
| PS-01 | `get_forecast` | No model loaded | `historical_fallback` with reason | Pass |
| PS-02 | `get_forecast` | Valid model | `ml_predicted` with model version | Pass |
| PS-03 | `get_forecast` | Model returns an implausible value, or raises | Falls back with reason | Pass |
| PS-04 | `get_forecast` | History too short | Falls back | Pass |
| PS-05 | `_historical_volatility` | Normal / too-short history | Annualised and positive / `None` | Pass |

**Table 6.7: Stock Predictor and trend registry (`test_ml_trend.py`, 69 tests)**

| Test ID | Function | Input | Expected Output | Result |
|---|---|---|---|---|
| TR-01 | `build_trend_target` | Synthetic series | Label matches an independent computation; last 21 rows unlabelled | Pass |
| TR-02 | `build_trend_training_table` | Synthetic series | Features + target only; forward return not leaked into the table | Pass |
| TR-03 | `technical_trend_signal` | Steady uptrend / downtrend | Bullish / Bearish on every signal; label agrees with score | Pass |
| TR-04 | `technical_trend_signal` | Short history | Signals needing more data omitted; RSI reported but not scored | Pass |
| TR-05 | `base_rate_up` | Always rising / always falling / mixed | 1.0 / 0.0 / strictly between; too few windows gives `None` | Pass |
| TR-06 | `expected_range` | σ = 0 | All bands collapse to the price | Pass |
| TR-07 | `expected_range` | Any σ | 22 points (day 0–21); day 0 zero width; width ∝ √t | Pass |
| TR-08 | `expected_range` | Any σ | Horizon band matches the closed form; 95% band contains 68%; symmetric in log space | Pass |
| TR-09 | `expected_range` | Extreme σ | Lower bound still positive | Pass |
| TR-10 | `evaluate_trend_probabilities` | p = base rate | Brier skill score = 0 | Pass |
| TR-11 | `evaluate_trend_probabilities` | Good vs confidently wrong probabilities | Skill > 0 vs < 0 | Pass |
| TR-12 | trend registry | Round trip | Metadata preserved; probability in [0, 1]; "up" class found via `classes_` | Pass |
| TR-13 | trend registry | Regressor without `predict_proba`; estimator without "up" class; volatility artifact | Refused | Pass |
| TR-14 | `StockTrendService` | No model | Base rate used and labelled | Pass |
| TR-15 | `StockTrendService` | Model raises or returns invalid probability | Falls back to base rate | Pass |

**Table 6.8: Market-data input safety (`test_ml_data.py`, 28 tests)**

| Test ID | Function | Input | Expected Output | Result |
|---|---|---|---|---|
| DA-01 | `validate_ticker` | `reliance.ns`, `^NSEI`, `BRK-B` | Accepted and normalised | Pass |
| DA-02 | `validate_ticker` | `../../etc/passwd`, `A;rm -rf`, empty, over-long | Rejected | Pass |
| DA-03 | `load_history` | Invalid ticker | `PriceDataError` | Pass |
| DA-04 | `_cache_path` | Valid tickers | Path stays inside the cache directory; existing filenames unchanged | Pass |
| DA-05 | `_cache_path` | Hostile tickers | Never produces a path | Pass |
| DA-06 | request schema | Valid ticker | Normalised | Pass |
| DA-07 | request schema | Hostile ticker | Validation error (422), not a server error (500) | Pass |

**Table 6.9: Training script guards (`test_train_volatility_script.py`, 50 tests)**

| Test ID | Function | Input | Expected Output | Result |
|---|---|---|---|---|
| TS-01 | source constraints | Script source | No lambdas, no classes; ridge grid extends past the original edge | Pass |
| TS-02 | `date_gap` | Two dates | Counts distinct dates strictly between; unknown date raises | Pass |
| TS-03 | embargo verification | Pooled panel, row-based split | **Leak demonstrated**: fewer than 21 dates between halves | Pass |
| TS-04 | `split_panel` | Row-based split | Detected and repaired by re-splitting on dates; correct split left alone | Pass |
| TS-05 | `date_folds` | Training half | Every fold keeps the embargo; train precedes validation; no shared dates; window expands | Pass |
| TS-06 | `date_folds` | Too many folds | Aborts instead of silently shrinking blocks | Pass |
| TS-07 | `select_family` | Ridge within 1 SE of best | Ridge chosen | Pass |
| TS-08 | `select_family` | Ridge clearly worse | Best family chosen; tie between non-linear families goes to the simpler | Pass |
| TS-09 | `acceptance` | Beats naive on both / one / tie | Accept / reject / reject | Pass |
| TS-10 | `parse_requirements` | Requirements file | Pins read, comments ignored; real file pins every compared library | Pass |
| TS-11 | estimators | Normal, unusual and absurd inputs | Predictions positive and finite; overflow rejected by serving guard | Pass (2 skipped by design) |
| TS-12 | estimators | Pickle round trip | Identical predictions; no reference to the script's `__main__` | Pass |

## 6.3 Integration and API Testing

Integration tests were run against the live server (`uvicorn` on port 8000, SQLite, Ollama running) using the demo account.

**Table 6.10: API integration test cases (positive paths)**

| Test ID | Scenario | Endpoint(s) | Expected | Actual | Result |
|---|---|---|---|---|---|
| IT-01 | Login | `POST /api/auth/login` | 200 + JWT | 200, token issued | Pass |
| IT-02 | Current user | `GET /api/auth/me` | 200, own record | 200 | Pass |
| IT-03 | Read profile | `GET /api/profile/` | 200, saved profile | 200 (age 28, ₹85,000, ₹25,000, 10+ Years, High) | Pass |
| IT-04 | Risk calculation | `POST /api/risk/calculate` | Score 0–100 with type | 85.31, Aggressive | Pass |
| IT-05 | Recommendation | `POST /api/recommendation/generate` | Allocation summing to 100% | 65.5 / 21.6 / 7.2 / 5.7 | Pass |
| IT-06 | SIP | `POST /api/sip/calculate` (₹5,000, 12%, 10 y) | FV ≈ ₹11.62 L | ₹11,61,695.38 | Pass |
| IT-07 | Portfolio analytics | sample data → `POST /analyze` (252 points) | Metrics + risk level | Vol 14.71%, Sharpe 0.91, MDD −5.80%, Moderate | Pass |
| IT-08 | Diversification | sample holdings → `POST /analyze` (12 holdings) | Score + HHI | 95.0, HHI 9.78 | Pass |
| IT-09 | Monte Carlo | `POST /api/monte-carlo/simulate` (10k paths) | Full result, saved with provenance | Saved, `volatility_source = ml_predicted` | Pass |
| IT-10 | Volatility forecast | `POST /api/ml/predict-volatility` | `ml_predicted`, model version | 0.2284, `ridge-log-20261011` | Pass |
| IT-11 | Stock outlook | `GET /api/ml/trend-outlook/RELIANCE.NS` | Trend, probability, range | Bearish, 49.2% base rate, bands | Pass |
| IT-12 | Live quote | `GET /api/market/stock/RELIANCE.NS` | Quote and profile | ₹1,174.60, Energy | Pass |
| IT-13 | Model info | `GET /api/ml/model-info` | Loaded, 21 features | `model_loaded: true`, `n_features: 21` | Pass |
| IT-14 | LLM health | `GET /api/ollama/health` | Ollama reachable | `available`, model `qwen2.5:3b` present | Pass |

**Table 6.11: API integration test cases (negative paths)**

| Test ID | Scenario | Request | Expected | Actual response | Result |
|---|---|---|---|---|---|
| IT-N1 | No token | `GET /api/auth/me` | 401 | 401 "Not authenticated" | Pass |
| IT-N2 | Forged token | `GET /api/profile/` with `Bearer abc.def.ghi` | 401 | 401 "Invalid authentication credentials" | Pass |
| IT-N3 | Wrong password | `POST /api/auth/login` | 401 | 401 "Incorrect email or password" | Pass |
| IT-N4 | Duplicate e-mail | `POST /api/auth/register` | 400 | 400 "Email already registered" | Pass |
| IT-N5 | Invalid registration body | 1-character name, 3-character password | 422 | 422 with field-level errors | Pass |
| IT-N6 | Another user's record | `GET /api/users/{other_id}` | 403 | 403 "You can only access your own user record" | Pass |
| IT-N7 | Too few simulations | `num_simulations = 500` | 422 | 422 `greater_than_equal` on `num_simulations` | Pass |
| IT-N8 | Negative volatility | `volatility = −0.1` | 422 | 422 on `volatility` | Pass |
| IT-N9 | Path traversal | `ticker = "../../etc/passwd"` | 422 | 422 "Value error" on `ticker` | Pass |
| IT-N10 | Zero SIP amount | `monthly_investment = 0` | 422 | 422 `greater_than` | Pass |
| IT-N11 | Unknown ticker | `GET /api/ml/trend-outlook/ZZZZNOTREAL.NS` | Graceful error | 503 "Price data unavailable for ZZZZNOTREAL.NS…" | Pass |
| IT-N12 | Model info | `GET /api/ml/model-info` | 200 | 200, model loaded | Pass |

**System / UI testing.** All 15 pages were opened in Microsoft Edge with the demo account, data was populated through the UI and API, and full-page screenshots were captured automatically (Figures 7.1–7.14). No JavaScript page errors were recorded during the run. The Portfolio page renders its Phase 2 placeholder, as expected.

## 6.4 Testing Tools

**Table 6.12: Testing tools**

| Tool | Version | Purpose |
|---|---|---|
| pytest | 9.1.1 | Unit and component test runner (fixtures, parametrisation) |
| FastAPI TestClient (Starlette) | bundled | In-process API tests with dependency overrides |
| httpx | — | Black-box HTTP integration checks and latency benchmarks |
| Swagger UI (`/docs`) | bundled | Manual exploratory API testing |
| Puppeteer-core + Microsoft Edge (headless) | — | Automated UI walkthrough and screenshots |
| NumPy / pandas synthetic generators | — | Known-answer data (GBM with known σ, monotone series) |
| Python `time.perf_counter` | — | Latency measurement (warm-up + 5–7 timed runs, median and max) |
| Browser DevTools | — | Network and console inspection |

## 6.5 Test Coverage Summary

Line coverage was not instrumented (`pytest-cov` is not part of the environment). The table below shows coverage by **module and behaviour**: what each test module exercises and how many test cases it contains.

**Table 6.13: Test distribution and coverage by module**

| Test module | Tests | Module(s) under test | Behaviours covered |
|---|---|---|---|
| `test_ml_trend.py` | 69 | `ml/trend.py`, `ml/trend_registry.py`, `services/stock_trend_service.py` | Labels, signals, base rate, expected range, Brier skill, registry contract, fallback |
| `test_ml_explain.py` | 53 | `services/ollama_prompts.py`, `services/explanation_guard.py`, explain endpoint | Prompt rules and facts, guard rejects and accepts, caveat, endpoint behaviour |
| `test_ml_features.py` | 50 | `ml/features.py` | 21 features, no look-ahead, targets, direction label, training table, date embargo |
| `test_train_volatility_script.py` | 50 | `scripts/train_volatility_model.py` | Embargo verification, date folds, 1-SE rule, acceptance, environment pins, pickle safety |
| `test_monte_carlo_simulator.py` | 30 | `services/monte_carlo_simulator.py` | Determinism, GBM properties, VaR/CVaR, consistency, validation |
| `test_ml_data.py` | 28 | `ml/data.py`, ML request schemas | Ticker validation, cache-path safety, 422 vs 500 |
| `test_ml_registry_and_service.py` | 22 | `ml/model_registry.py`, `services/ml_prediction_service.py` | Contract enforcement, fallback paths, plausibility guard |
| `test_ml_evaluation.py` | 20 | `ml/evaluation.py` | RMSE, MAE, QLIKE properties, naive and HAR baselines, comparison |
| `test_security.py` | 16 | `core/security.py`, user schemas | bcrypt, byte limits, JWT round trip and rejection |
| **Total** | **338** | | **336 passed · 2 skipped · 0 failed · 29.99 s** |

Modules covered by integration and UI testing rather than unit tests: the risk calculator, recommendation engine, portfolio risk analyzer, diversification analyzer, SIP calculator and the CRUD routers. Their outputs were validated against closed-form results in Section 7.2. Adding unit tests for them is part of Phase 1 future work.

<div style="page-break-after: always;"></div>

# CHAPTER 7 — RESULTS AND ANALYSIS

## 7.1 Module-wise Results

All results below were produced by the running system with the demo profile: age 28, monthly income ₹85,000, monthly savings ₹25,000, horizon 10+ years, risk tolerance High.

**Table 7.1: Module test results summary**

| Module | Unit tests | Integration checks | Output verified against | Status |
|---|---|---|---|---|
| Authentication and users | 16 | 8 | Expected HTTP codes | ✅ Working |
| Financial profile | — | 1 | Stored values | ✅ Working |
| Risk assessment | — | 1 | Hand calculation (Table 7.2) | ✅ Working |
| Recommendation | — | 1 | Closed form (Table 7.3) | ✅ Working |
| Portfolio analytics | — | 1 | Input σ of the sample series | ✅ Working |
| Diversification | — | 1 | HHI definition | ✅ Working |
| Monte Carlo | 30 | 3 | Analytical log-normal results (Table 7.5) | ✅ Working |
| SIP planner | — | 2 | Closed form (Table 7.4) | ✅ Working |
| Market data | 28 | 2 | Yahoo Finance | ✅ Working |
| ML volatility | 142 | 3 | Baselines on held-out data (Section 7.3) | ✅ Working (model trained) |
| Stock Predictor | 69 | 2 | Closed-form range (Table 7.7) | ✅ Working (base rate; classifier pending) |
| AI explanations | 53 | 1 | Guard rules | ✅ Working |
| Portfolio tracking | — | — | — | ⏳ Placeholder (Phase 2) |

### 7.1.1 Landing, Login and Registration

![Landing page](figures/fig_home.png)
**Figure 7.1: Landing page**

![Login page](figures/fig_login.png)
**Figure 7.2: Login page**

![Registration page](figures/fig_register.png)
**Figure 7.3: Registration page**

### 7.1.2 Dashboard and Financial Profile

The dashboard summarises the profile (savings rate 29.4%), the risk score (85.3, Aggressive) and quick links to every module. Because holdings tracking is not yet implemented, the portfolio value tiles at the top show ₹0. They will be populated in Phase 2.

![Dashboard](figures/fig_dashboard.png)
**Figure 7.4: Dashboard**

![Financial profile](figures/fig_financial_profile.png)
**Figure 7.5: Financial profile form**

### 7.1.3 Risk Assessment

The demo profile scores **85.3 (Aggressive)**. The page shows the semicircular gauge, the category legend, and each factor's sub-score with its reasoning: age 91.7, income 74.0, savings rate 59.4, horizon 95.0, tolerance 90.0.

![Risk assessment](figures/fig_risk_assessment.png)
**Figure 7.6: Risk assessment with gauge and factor breakdown**

*Observation:* the rule-based explanation text and the three cards below it show a tier-level guideline (Equity 70%, Debt 20%, Gold 10% for Aggressive). The Recommendation page uses the finer, score-proportional allocation (65.5 / 21.6 / 7.2 / 5.7). The two are consistent in direction but not identical, and aligning them is listed in Section 7.7.

### 7.1.4 Portfolio Recommendation

The recommendation engine returns **Stocks 65.5%, Mutual Funds 21.6%, Gold 7.2%, Emergency Fund 5.7%**, shown as a donut chart and four cards, followed by an AI-generated analysis.

![Recommendation](figures/fig_recommendation.png)
**Figure 7.7: Portfolio recommendation**

### 7.1.5 Portfolio Risk Analytics

A one-year sample series (₹1,00,000 start, 252 days, 15% volatility, 10% expected return) gives:
- **risk score 39.0 (Moderate)**;
- volatility **14.71%**, which correctly recovers the 15% used to generate the series;
- Sharpe **0.91**;
- maximum drawdown **−5.80%**;
- total return **+20.06%**, with an annualised average of 19.44% and an excess return of 13.44% over the 6% risk-free rate.

![Portfolio analytics](figures/fig_portfolio_analytics.png)
**Figure 7.8: Portfolio risk analytics**

### 7.1.6 Diversification Analysis

The "well diversified" sample portfolio of ₹10 lakh (12 holdings, 8 sectors, 4 asset types) scores **95.0 (Excellent)** with **HHI 9.78** and no concentration warnings. The largest sector is Diversified at 25% and the largest asset class is Stocks at 50%. The "concentrated" sample scores **17.0** with **HHI 30.0** and **3 warnings**, showing that the score separates the two cases clearly.

![Diversification](figures/fig_diversification.png)
**Figure 7.9: Diversification analysis**

### 7.1.7 Monte Carlo Simulation with ML Volatility

**Table 7.6: Monte Carlo example result** (₹1,00,000 initial, ₹5,000 per month, 10 years, 12% expected return, **σ = 22.8% from the ML forecast for RELIANCE.NS**, 10,000 paths, seed 42)

| Metric | Value |
|---|---|
| Total invested | ₹7.00 L |
| Mean terminal value | ₹14.20 L |
| Median (expected case) | ₹12.29 L |
| Best case (95th percentile) | ₹29.09 L |
| Worst case (5th percentile) | ₹5.76 L |
| VaR (5%) | ₹5.76 L, a shortfall of 17.8% of the amount invested |
| CVaR (5%) | ₹4.89 L, a shortfall of 30.1% of the amount invested |
| Probability of profit | 88.5% |
| Probability of doubling | 39.5% |
| 90% confidence interval | ₹5.76 L – ₹29.09 L |
| 95% confidence interval | ₹5.06 L – ₹35.00 L |
| 99% confidence interval | ₹3.88 L – ₹49.48 L |

*Sanity check:* the deterministic value of the same plan at 12% is ₹3.11 L (lump sum) plus ₹11.10 L (contributions), totalling ₹14.20 L. That equals the simulated **mean**, as the Itô correction requires. The **median** (₹12.29 L) is lower, because the log-normal distribution is right-skewed. A deterministic calculator would present ₹14.2 L as "the" outcome, while the simulation shows that more than half of outcomes fall below it and that 1 in 20 ends below ₹5.76 L.

![Monte Carlo](figures/fig_monte_carlo.png)
**Figure 7.10: Monte Carlo simulation using the ML volatility forecast**

### 7.1.8 SIP Planner

₹5,000 per month for 10 years at 12% gives **total invested ₹6,00,000, wealth generated ₹5,61,695 and future value ₹11,61,695**, with a year-by-year growth chart.

![SIP planner](figures/fig_sip_planner.png)
**Figure 7.11: SIP planner**

### 7.1.9 Stock Explorer

The Stock Explorer shows live data for Reliance Industries (RELIANCE.NS) on 14 October 2026:
- price ₹1,174.60, up ₹7.90 (0.68%);
- 52-week range ₹1,152.20 – ₹1,611.80;
- sector Energy;
- a one-year price chart with period selection.

A link opens the 21-day outlook for the same stock.

![Stock explorer](figures/fig_stock_explorer.png)
**Figure 7.12: Stock Explorer with live Yahoo Finance data**

### 7.1.10 Stock Predictor

For RELIANCE.NS on 14 October 2026:

- **Current trend: Bearish.** All four signals are bearish: price below its 50-day average, 50-day below 200-day, and price down over both 21 and 63 trading days. RSI is 34 (neutral). The trend is labelled "Describes the past, not a forecast".
- **Chance of closing higher in 21 trading days: 49.2%.** No trend classifier is loaded, so this is the stock's own historical frequency, and the page displays a **"Not a prediction"** banner.
- **Expected range (σ = 22.8%, ML forecast):** likely (68%) **₹1,099.65 – ₹1,254.66**; wide (95%) **₹1,032.21 – ₹1,336.63**, centred on today's price.

![Stock predictor](figures/fig_stock_predictor.png)
**Figure 7.13: Stock Predictor: 21-day outlook with expected range cone**

### 7.1.11 Portfolio Page (Phase 2)

![Portfolio placeholder](figures/fig_portfolio.png)
**Figure 7.14: Portfolio tracking page (placeholder, Phase 2)**

## 7.2 Validation of Financial Computations

Each deterministic module was checked against an independent calculation.

**Table 7.2: Risk-score worked example** (demo profile)

| Factor | Sub-score | Weight | Contribution |
|---|---|---|---|
| Age (28) | 91.67 | 0.15 | 13.75 |
| Income (₹85,000) | 74.00 | 0.10 | 7.40 |
| Savings rate (29.4%) | 59.41 | 0.15 | 8.91 |
| Horizon (10+ Years) | 95.00 | 0.25 | 23.75 |
| Tolerance (High) | 90.00 | 0.35 | 31.50 |
| **Total** | | **1.00** | **85.31 → Aggressive** |

System output: **85.31, Aggressive**. ✅ Match.

**Table 7.3: Allocation validation at boundary and demo scores**

| Risk score | Stocks | Mutual funds | Gold | Emergency | Sum |
|---|---|---|---|---|---|
| 0 | 10.0 | 60.0 | 20.0 | 10.0 | 100.0 |
| 50 | 42.5 | 37.5 | 12.5 | 7.5 | 100.0 |
| 85.31 (demo) | 65.5 | 21.6 | 7.2 | 5.7 | 100.0 |
| 100 | 75.0 | 15.0 | 5.0 | 5.0 | 100.0 |

All values equal the closed form of Section 4.3.2. ✅

**Table 7.4: SIP validation against the closed form**

| Case | Closed form | System | Difference |
|---|---|---|---|
| FV of ₹5,000/month, 12%, 10 years: $5000 \cdot \frac{1.01^{120}-1}{0.01}\cdot 1.01$ | ₹11,61,695.38 | ₹11,61,695.38 | 0 |
| Required SIP for ₹1 crore, 15 years, 12% | ₹19,818.62 | ₹19,818.62 | 0 |

**Table 7.5: Monte Carlo validation against analytical results** (₹1,00,000, μ = 12%, σ = 15%, 10 years, no contributions, 10,000 paths, seed 42). Under the model, $\ln(V_T/V_0) \sim \mathcal N\!\left(T(\ln 1.12 - \sigma^2/2),\ \sigma^2 T\right)$, with mean 1.0208 and standard deviation 0.4743.

| Quantity | Analytical | Simulated | Relative error |
|---|---|---|---|
| Mean $\mathbb E[V_T] = V_0 \cdot 1.12^{10}$ | ₹3,10,585 | ₹3,10,332 | −0.08% |
| Median $V_0 e^{1.0208}$ | ₹2,77,539 | ₹2,78,079 | +0.19% |
| 5th percentile | ₹1,27,196 | ₹1,27,900 | +0.55% |
| 95th percentile | ₹6,05,590 | ₹6,00,629 | −0.82% |
| P(profit) = Φ(2.152) | 98.43% | 98.71% | +0.28 pp |
| P(doubling) = Φ(0.691) | 75.51% | 76.29% | +0.78 pp |

All differences are within the sampling error expected from 10,000 paths. Agreement of the **mean** confirms the Itô correction. Without it, the simulated mean would be about 12% too high (×$e^{0.5\cdot0.0225\cdot10}$ ≈ 1.119). ✅

**Table 7.7: Expected price range validation** (RELIANCE.NS, close ₹1,174.60, σ = 0.228399, 21 days, spread = σ√(21/252) = 0.065933)

| Band | Closed form | System |
|---|---|---|
| 68% lower = 1174.60·e^(−0.065933) | ₹1,099.65 | ₹1,099.65 |
| 68% upper = 1174.60·e^(+0.065933) | ₹1,254.66 | ₹1,254.66 |
| 95% lower = 1174.60·e^(−1.96·0.065933) | ₹1,032.21 | ₹1,032.21 |
| 95% upper = 1174.60·e^(+1.96·0.065933) | ₹1,336.63 | ₹1,336.63 |

✅ Exact match.

## 7.3 Volatility Model Evaluation

### 7.3.1 Experimental Setup

| Item | Value |
|---|---|
| Universe | 10 NSE large caps; Nifty 50 as market context |
| Panel | 21,990 rows, 2017-10-16 to 2026-09-08 |
| Train | 17,390 rows, to 2024-10-30 |
| Embargo | 21 distinct trading dates (210 rows dropped) |
| Test | 4,390 rows, 2024-12-03 to 2026-09-08 (untouched until model selection was final) |
| Target | 21-day forward realised volatility (annualised) |
| Cross-validation | Walk-forward by date, expanding window, 21-date embargo, selection on QLIKE |
| Candidates | Ridge, HistGradientBoosting, RandomForest, all on log-volatility |
| Selected | **Ridge, α = 30,000** (one-standard-error rule) |
| Artifact | `ridge-log-20261011` |

In cross-validation the three families scored QLIKE 0.184, 0.186 and 0.191, against a fold-to-fold spread of about 0.05. They were indistinguishable within noise, so the rule selected the simplest, ridge.

### 7.3.2 Test-Set Results

**Table 7.8: Volatility model test-set scores** (4,390 rows; every forecast scored on the same rows; lower is better except R²)

| Model | RMSE | MAE | QLIKE | R² |
|---|---|---|---|---|
| **Ridge on log-volatility (selected)** | **0.0676** | **0.0532** | **0.1949** | **0.190** |
| HAR (Corsi) | 0.0706 | 0.0563 | 0.2036 | 0.118 |
| GARCH(1,1) | 0.0792 | 0.0652 | 0.2340 | −0.111 |
| Naive persistence (trailing 21-day RV) | 0.0823 | 0.0616 | 0.3638 | −0.199 |

```mermaid
xychart-beta
    title "Test-set QLIKE (lower is better)"
    x-axis ["Ridge (selected)", "HAR", "GARCH(1,1)", "Naive"]
    y-axis "QLIKE" 0 --> 0.4
    bar [0.1949, 0.2036, 0.2340, 0.3638]
```

**Figure 7.15: Volatility model compared with baselines on the test set**

**Table 7.9: Block-bootstrap confidence intervals** (blocks of 21 dates, 4,000 resamples; improvement = % reduction in loss)

| Comparison | Metric | Improvement | 95% interval | Significant? |
|---|---|---|---|---|
| Model vs naive | QLIKE | +46.4% | +22.3% to +62.4% | **Yes** |
| Model vs naive | RMSE | +17.8% | +8.4% to +25.9% | **Yes** |
| Model vs HAR | QLIKE | +4.3% | −2.8% to +10.8% | No |
| Model vs HAR | RMSE | +4.2% | −0.2% to +8.7% | No (marginal) |

**Interpretation.** The model clearly and significantly beats naive persistence, the forecast an investor implicitly uses when typing in "last month's volatility". It also beats HAR and GARCH(1,1) in point estimates on every metric. However, the improvement over HAR is **not statistically distinguishable from zero**, so the honest claim is: *better than naive, at least as good as the strongest standard benchmark.* This is consistent with the literature, where HAR is notoriously hard to beat [7].

### 7.3.3 Calibration and the Compression Weakness

**Table 7.10: Forecast calibration by decile of prediction**

| | Lowest decile | … | Highest decile |
|---|---|---|---|
| Mean prediction | 0.191 | … | 0.262 |
| Mean actual | 0.157 | … | 0.297 |
| Actual ÷ predicted | 0.82 | … | 1.14 |

Predictions span 0.18–0.31, while realised volatility spans 0.08–0.56. The forecasts are **compressed toward the average**: calm periods are over-forecast by about 18% and the most volatile decile is under-forecast by about 14%. Compression is expected from a heavily regularised model (α = 30,000) trained on a low signal-to-noise target, because shrinking toward the mean minimises average loss. For a risk tool, though, under-forecasting in turbulent periods is the costly direction: it makes the Monte Carlo spread and the price-range cone too narrow exactly when caution matters most. Section 9 proposes remedies, including quantile or regime-aware models, post-hoc recalibration, and asymmetric loss.

### 7.3.4 Stock Predictor Direction Model

The direction-classifier pipeline is complete: labels, training table, registry contract, Brier-skill evaluation, serving and fallback, all covered by tests. However, no classifier has yet been trained and validated. Until one beats the base rate on Brier skill on held-out data, the system shows the base rate and labels it as such. This is deliberate. Over a one-month horizon, stock direction is close to unpredictable, and showing an unvalidated "AI prediction" would be misleading.

## 7.4 Performance Benchmarks

Measured on the development laptop (Windows 11, CPU only), backend running without auto-reload after the frontend had finished compiling. Each endpoint had one warm-up call, then 7 timed calls (5 for Monte Carlo, 3 for live Yahoo quotes).

**Table 7.11: Endpoint latency benchmarks**

| Operation | Median (ms) | Max (ms) |
|---|---|---|
| Health check | 3.6 | 4.3 |
| SIP calculation (₹5,000/month, 12%, 10 years) | 10.6 | 12.5 |
| Current user (`/auth/me`) | 13.2 | 16.2 |
| Get financial profile | 13.4 | 17.8 |
| Calculate risk profile | 18.3 | 21.3 |
| Generate portfolio recommendation | 21.4 | 25.7 |
| Diversification analysis (12 holdings) | 27.0 | 30.0 |
| Portfolio risk analysis (252 daily values) | 35.5 | 39.0 |
| Stock Predictor outlook (cached history) | 49.4 | 61.7 |
| Stock info (live Yahoo Finance) | 62.5 | 64.4 |
| Volatility forecast (model inference, cached history) | 116.8 | 131.3 |
| Monte Carlo, 10,000 paths × 10 years | 526.8 | 580.7 |
| Login (bcrypt verify + JWT issue) | 946.9 | 995.4 |
| Monte Carlo, 50,000 paths × 10 years | 2,749.6 | 2,830.4 |
| AI explanation, first request (Qwen2.5-3B on CPU) | ≈ 30,000–55,000 | — |
| AI explanation, cached | ≈ same as a database read | — |

```mermaid
xychart-beta
    title "Median latency (ms) for core endpoints"
    x-axis ["SIP", "Risk", "Recommend", "Diversify", "Analytics", "Outlook", "Vol. forecast", "MC 10k"]
    y-axis "ms" 0 --> 600
    bar [10.6, 18.3, 21.4, 27.0, 35.5, 49.4, 116.8, 526.8]
```

**Figure 7.16: Endpoint latency benchmark**

Observations:
- All deterministic analytics respond in **under 40 ms**, well inside NFR-01.
- **Login time is dominated by bcrypt** (912 ms for the hash verification alone). This is intentional: cost 12 makes offline password guessing expensive.
- Monte Carlo scales linearly with path count: 5× the paths take 5.2× the time.
- LLM explanations are the only slow operation. Asynchronous loading and database caching hide this cost after the first request. A GPU would reduce it to a few seconds.

## 7.5 Capacity Analysis

**Table 7.12: Capacity estimates** (derived from the measurements above for a single Uvicorn worker; not load-tested)

| Resource | Measurement | Implication |
|---|---|---|
| Monte Carlo throughput | 10,000 × 120 = 1.2 M path-months in 0.53 s | ≈ 2.3 M path-months/s per worker |
| Monte Carlo memory (50k paths, 10 y) | 50,000 × 120 shocks + 50,000 × 121 values (float64) | ≈ 100 MB peak per request; the 50,000-path cap bounds it |
| Analytical endpoints | 10–36 ms | ≈ 30–90 requests/s per worker, sequentially |
| Login | ≈ 0.95 s CPU (bcrypt) | ≈ 1 login/s per core; also throttles brute force |
| LLM explanations | 30–55 s each, serialised by Ollama | ≈ 1–2 new explanations per minute; caching is essential |
| SQLite | Single writer | Adequate for single-user and demo use; PostgreSQL needed for concurrent users |
| Price cache | Parquet per ticker, 24 h TTL | Repeat forecasts avoid network calls; stale cache served if offline |

## 7.6 Security Compliance Matrix

**Table 7.13: Security compliance matrix (OWASP Top 10, 2021)**

| OWASP category | Control in this system | Evidence | Status |
|---|---|---|---|
| A01 Broken Access Control | JWT on 50 of 58 operations; per-user query filtering; ownership check on `/users/{id}` | IT-N1, IT-N2, IT-N6 | ✅ Compliant (sample-data and Ollama endpoints are public: low-risk, but should be authenticated before deployment) |
| A02 Cryptographic Failures | bcrypt cost 12; HS256-signed tokens; secrets in `.env` | SEC-01…13 | ⚠️ Partial: development `.env` uses a placeholder `SECRET_KEY`; no TLS locally |
| A03 Injection | ORM bound parameters; strict ticker pattern; Pydantic validation | IT-N9, DA-02, DA-05 | ✅ Compliant |
| A04 Insecure Design | Fallbacks labelled; output guard; acceptance gate for models | Sections 4.5, 5.4 | ✅ Compliant |
| A05 Security Misconfiguration | CORS allow-list; settings from environment, not code | Config | ⚠️ Partial: production hardening pending |
| A06 Vulnerable Components | Pinned versions in `requirements.txt`; training checks pins | TS-10 | ✅ Compliant (no automated CVE scan yet) |
| A07 Identification & Authentication Failures | Salted adaptive hashing; byte-accurate length limit; 30-minute tokens | SEC-05…07, IT-N3 | ⚠️ Partial: no rate limiting or lockout |
| A08 Software & Data Integrity Failures | Model bundles contract-checked; bare pickles refused; no script references in pickles | RG-04, RG-05, TS-12 | ✅ Compliant (artifacts are local and trusted) |
| A09 Logging & Monitoring Failures | Server-side logging of fallbacks and failures | Logs | ⚠️ Partial: no central monitoring |
| A10 Server-Side Request Forgery | Outbound calls only to fixed hosts (Yahoo Finance, localhost Ollama); tickers validated | DA-02 | ✅ Compliant |

## 7.7 Discussion and Known Limitations

**What worked well:**

1. **Correctness by construction.** Closed-form validation (Tables 7.2–7.7) shows that every deterministic computation matches its mathematical definition exactly, and that the simulator matches log-normal theory within sampling error.
2. **Honest ML.** The volatility model's evaluation was designed so that it could fail. It has an untouched test half, a verified date embargo, strong baselines and confidence intervals. It produced a modest but real improvement, reported with its limits.
3. **Graceful degradation.** The application remained fully usable without the model and without the LLM, and it always reports which situation applies.
4. **Safe explanations.** Guarding the output, rather than relying on prompting alone, makes the "no advice, no certainty" promise testable.

**Known limitations** (all carried into Chapter 9):

| # | Limitation | Impact |
|---|---|---|
| L1 | Volatility forecasts are compressed (Section 7.3.3) | Spreads too narrow in turbulent markets |
| L2 | Advantage over HAR not statistically significant; one test regime (Dec 2024 – Sep 2026) | Claims limited to "no worse than HAR" |
| L3 | Stock Predictor classifier not trained | Probability is the base rate only |
| L4 | Portfolio tracking not implemented; dashboard value tiles show ₹0 | No real holdings analysis |
| L5 | Risk page shows tier guideline (70/20/10) while the recommendation is score-proportional | Minor inconsistency in the UI |
| L6 | UI says AI insights "may take 10–15 seconds"; CPU inference takes 30–55 s | Expectation mismatch |
| L7 | Risk weights and thresholds are expert-chosen, not empirically calibrated | Score is transparent but not validated against outcomes |
| L8 | GBM assumes constant σ and normal log-returns (no fat tails or jumps); the expected return is user-supplied | Tail risk may be understated |
| L9 | Savings greater than income is not rejected by the profile schema | Possible nonsensical input |
| L10 | No rate limiting; placeholder dev secret; some public utility endpoints; no client-side route guard | Must be fixed before deployment |
| L11 | No line-coverage measurement; no frontend automated tests; no CI pipeline | Regression risk in untested modules |
| L12 | SQLite and local deployment only | Not multi-user production-ready |

**Table 7.14: Proposal features: delivered and deferred**

| Proposal feature | Status |
|---|---|
| User authentication and profiles | ✅ Delivered |
| Risk profiling | ✅ Delivered |
| Portfolio recommendation | ✅ Delivered |
| Portfolio analytics (volatility, Sharpe, drawdown) | ✅ Delivered |
| Diversification analysis | ✅ Delivered |
| Monte Carlo simulation | ✅ Delivered (with ML volatility and VaR/CVaR) |
| SIP planner | ✅ Delivered |
| Live stock data | ✅ Delivered |
| Stock Predictor | ✅ Delivered (trend, base-rate probability, ML-driven range); classifier pending |
| AI explanations (LLM) | ✅ Delivered (local, cached, guarded) |
| ML volatility forecasting | ✅ Delivered (trained and evaluated) |
| Portfolio tracking (holdings, transactions) | ⏳ Phase 2 (schema exists) |
| Goal planning and retirement planning | ⏳ Phase 2 |
| Portfolio optimisation (mean–variance) | ⏳ Phase 3 |
| Automated rebalancing alerts | ⏳ Phase 3 |
| Conversational AI chat assistant | ⏳ Phase 3 |
| PDF report export | ⏳ Phase 2 |
| ETF and gold-price tracking | ⏳ Phase 2 |
| PostgreSQL and cloud deployment | ⏳ Phase 4 |

<div style="page-break-after: always;"></div>

# CHAPTER 8 — CONCLUSION

This project designed, implemented and evaluated the **AI Smart Investment Portfolio Advisor (FinIntelAI)**, a full-stack platform that gives retail investors the quantitative tools of a professional advisor: risk profiling, asset allocation, portfolio risk analytics, diversification analysis, probabilistic projection, SIP planning and market data. It explains every result in plain language, and it is honest about what is and is not a prediction.

The main outcomes are:

1. **A complete, working system.** It comprises a FastAPI backend with 58 REST operations across 12 modules and 10 database tables, and a React frontend with 15 pages and rich visualisations. The system runs entirely on a laptop, including the language model.

2. **Transparent, verified financial computation.**
   - The risk score, allocation, portfolio analytics, diversification score and SIP calculations are documented formulas whose outputs were checked against independent closed-form calculations, with exact agreement.
   - The Monte Carlo engine uses Itô-corrected geometric Brownian motion. Its simulated mean, median, percentiles and probabilities match log-normal theory within sampling error (mean error −0.08%).

3. **A rigorously evaluated volatility forecaster.**
   - It is trained on ten years of NSE data with 21 leakage-checked features, a chronological split with a verified 21-date embargo, walk-forward cross-validation and the one-standard-error rule.
   - On 4,390 untouched test rows, the selected ridge model reduced QLIKE by 46.4% and RMSE by 17.8% relative to naive persistence; both improvements are statistically significant.
   - It outperformed GARCH(1,1) and matched or slightly exceeded the HAR benchmark.
   - The forecast drives the Monte Carlo spread and the Stock Predictor's price range, and a labelled fallback is used whenever the model cannot be trusted.

4. **A Stock Predictor that separates description from prediction.** It shows a technical trend (the past), the probability of a rise compared against the stock's own base rate (labelled "Not a prediction" until a validated classifier exists) and a direction-free expected range.

5. **Safe, private AI explanations.**
   - A locally hosted Qwen2.5-3B model explains every module's output, so no financial data leaves the user's machine.
   - Explanations are cached.
   - For the Stock Predictor, a deterministic guard discards text that gives advice, offers guarantees or states price moves as certain.

6. **Engineering quality.**
   - Security: bcrypt (cost 12), JWT, ownership checks and strict input validation.
   - Versioned migrations and self-documenting OpenAPI.
   - **338 automated tests** (336 passed, 2 skipped by design), plus black-box API checks covering both positive and negative paths.
   - Analytical endpoints respond in 10–36 ms, and a 10,000-path simulation completes in about half a second.

The project also made its limits clear:
- the volatility forecasts are compressed toward the mean;
- the advantage over HAR is not statistically significant;
- the direction classifier and holdings tracking remain to be built;
- the system is not yet hardened for multi-user deployment.

Reporting these openly is itself a result. It shows how a financial AI tool can earn trust: by being explicit about uncertainty, testing its claims against strong baselines, and refusing to present a historical frequency as a forecast.

In summary, the project demonstrates that an explainable, statistically honest and privacy-preserving investment advisory platform can be built from open-source components and run on commodity hardware, providing a sound foundation for the features planned in the next phases.

<div style="page-break-after: always;"></div>

# CHAPTER 9 — FUTURE WORK

Future work is organised into four phases, in order of dependency and value.

### Phase 1 — Consolidation (short term)

| # | Item | Addresses |
|---|---|---|
| 1.1 | Unit tests for the risk calculator, recommendation engine, portfolio analyzer, diversification analyzer and SIP calculator; line-coverage reporting with `pytest-cov`; a continuous-integration pipeline (GitHub Actions) | L11 |
| 1.2 | Frontend tests with React Testing Library and an end-to-end smoke test | L11 |
| 1.3 | Align the Risk page's guideline with the score-proportional recommendation; correct the AI loading-time message | L5, L6 |
| 1.4 | Validate savings ≤ income; add a client-side `ProtectedRoute` | L9, L10 |
| 1.5 | Authenticate the sample-data and Ollama utility endpoints; rate-limit login (for example with `slowapi`); enforce a strong `SECRET_KEY` at startup | L10 |
| 1.6 | Recalibrate volatility forecasts (isotonic or linear recalibration on a validation window), and evaluate quantile regression or an asymmetric loss to reduce under-forecasting in turbulent regimes | L1 |

### Phase 2 — Portfolio Tracking and Planning (medium term)

| # | Item | Proposal feature |
|---|---|---|
| 2.1 | Holdings and transactions (buy/sell, fees), live valuation through Yahoo Finance, realised and unrealised P&L, XIRR; drive Portfolio Analytics and Diversification from real holdings instead of sample data; populate the dashboard value tiles | Portfolio tracking (L4) |
| 2.2 | Goal-based planning: multiple goals with target amounts and dates; required SIP per goal; probability of reaching each goal from Monte Carlo | Goal planning |
| 2.3 | Retirement planning: corpus estimation with inflation, post-retirement withdrawals (sequence-of-returns risk via simulation), safe withdrawal rate | Retirement planning |
| 2.4 | ETF and gold-price tracking: NSE ETFs, sovereign gold bonds, MCX gold proxies | ETF/gold tracking |
| 2.5 | PDF report export: profile, risk, allocation, simulations and explanations in a downloadable report | PDF reports |

### Phase 3 — Intelligence (medium to long term)

| # | Item | Proposal feature |
|---|---|---|
| 3.1 | Train and validate the Stock Predictor direction classifier, using the existing contract. It is deployed only if its Brier skill score over the base rate is positive with a bootstrap interval that excludes zero | Stock Predictor (L3) |
| 3.2 | Mean–variance and risk-parity optimisation with constraints (long-only, sector caps), using the ML volatility forecasts and a shrunk covariance matrix | Portfolio optimisation |
| 3.3 | Rebalancing alerts when allocation drifts beyond a tolerance band, with tax- and cost-aware suggestions | Rebalancing |
| 3.4 | Conversational assistant: retrieval-augmented chat over the user's own results, with tool calls to the existing deterministic services and the same output guard applied to every answer | AI chat assistant |
| 3.5 | Extend the guard to every explanation (not only the Stock Predictor), and add an evaluation set of adversarial prompts | Safety |
| 3.6 | Richer volatility models (regime-switching, realised-GARCH, LightGBM with monotone constraints) and a longer, multi-regime test (including 2020) | L2 |
| 3.7 | Empirical calibration of risk-score weights against questionnaire data or the behaviour of real investors | L7 |
| 3.8 | Fat-tailed simulation (Student-t shocks, bootstrapped historical returns, jump-diffusion) | L8 |

### Phase 4 — Production Deployment (long term)

| # | Item |
|---|---|
| 4.1 | PostgreSQL with connection pooling (the SQLAlchemy models and Alembic migrations carry over) |
| 4.2 | Containerisation (Docker Compose: API, frontend, database, Ollama) and cloud deployment (for example AWS ECS or EC2 with RDS) behind HTTPS |
| 4.3 | Refresh tokens and revocation, e-mail verification (the `is_verified` column exists), password reset, optional two-factor authentication |
| 4.4 | Background job queue (Celery or RQ with Redis) for LLM explanations and model retraining; scheduled monthly retraining with automatic acceptance testing |
| 4.5 | Monitoring and logging (Prometheus/Grafana, structured logs), dependency vulnerability scanning |
| 4.6 | GPU-backed or quantised LLM serving to cut explanation latency to seconds |
| 4.7 | Regulatory review: clear "educational tool" positioning, consistent with the SEBI (Investment Advisers) Regulations, 2013 [36] |

<div style="page-break-after: always;"></div>

# BIBLIOGRAPHY

[1] M. Beketov, K. Lehmann and M. Wittke, "Robo Advisors: quantitative methods inside the robots," *Journal of Asset Management*, vol. 19, no. 6, pp. 363–370, 2018.

[2] "PortfolioPilot: An Agentic Platform for Financial Portfolio Management Algorithm Development and Evaluation," in *Proceedings of the AAAI Conference on Artificial Intelligence (AAAI-26)*, 2026. [Complete the author list from the proceedings.]

[3] H. Markowitz, "Portfolio selection," *The Journal of Finance*, vol. 7, no. 1, pp. 77–91, 1952.

[4] W. F. Sharpe, "Mutual fund performance," *The Journal of Business*, vol. 39, no. 1, pp. 119–138, 1966.

[5] R. F. Engle, "Autoregressive conditional heteroscedasticity with estimates of the variance of United Kingdom inflation," *Econometrica*, vol. 50, no. 4, pp. 987–1007, 1982.

[6] T. Bollerslev, "Generalized autoregressive conditional heteroskedasticity," *Journal of Econometrics*, vol. 31, no. 3, pp. 307–327, 1986.

[7] F. Corsi, "A simple approximate long-memory model of realized volatility," *Journal of Financial Econometrics*, vol. 7, no. 2, pp. 174–196, 2009.

[8] M. Parkinson, "The extreme value method for estimating the variance of the rate of return," *The Journal of Business*, vol. 53, no. 1, pp. 61–65, 1980.

[9] P. P. Boyle, "Options: A Monte Carlo approach," *Journal of Financial Economics*, vol. 4, no. 3, pp. 323–338, 1977.

[10] P. Glasserman, *Monte Carlo Methods in Financial Engineering*. New York: Springer, 2003.

[11] P. Artzner, F. Delbaen, J.-M. Eber and D. Heath, "Coherent measures of risk," *Mathematical Finance*, vol. 9, no. 3, pp. 203–228, 1999.

[12] R. T. Rockafellar and S. Uryasev, "Optimization of conditional value-at-risk," *Journal of Risk*, vol. 2, no. 3, pp. 21–41, 2000.

[13] A. J. Patton, "Volatility forecast comparison using imperfect volatility proxies," *Journal of Econometrics*, vol. 160, no. 1, pp. 246–256, 2011.

[14] M. López de Prado, *Advances in Financial Machine Learning*. Hoboken, NJ: Wiley, 2018.

[15] A. E. Hoerl and R. W. Kennard, "Ridge regression: Biased estimation for nonorthogonal problems," *Technometrics*, vol. 12, no. 1, pp. 55–67, 1970.

[16] T. Hastie, R. Tibshirani and J. Friedman, *The Elements of Statistical Learning*, 2nd ed. New York: Springer, 2009.

[17] H. R. Künsch, "The jackknife and the bootstrap for general stationary observations," *The Annals of Statistics*, vol. 17, no. 3, pp. 1217–1241, 1989.

[18] F. X. Diebold and R. S. Mariano, "Comparing predictive accuracy," *Journal of Business & Economic Statistics*, vol. 13, no. 3, pp. 253–263, 1995.

[19] F. Pedregosa *et al.*, "Scikit-learn: Machine learning in Python," *Journal of Machine Learning Research*, vol. 12, pp. 2825–2830, 2011.

[20] S. A. Rhoades, "The Herfindahl–Hirschman index," *Federal Reserve Bulletin*, vol. 79, pp. 188–189, 1993.

[21] D. Jung, V. Dorner, F. Glaser and S. Morana, "Robo-advisory: Digitalization and automation of financial advisory," *Business & Information Systems Engineering*, vol. 60, no. 1, pp. 81–86, 2018.

[22] F. D'Acunto, N. Prabhala and A. G. Rossi, "The promises and perils of robo-advising," *The Review of Financial Studies*, vol. 32, no. 5, pp. 1983–2020, 2019.

[23] S. Wu *et al.*, "BloombergGPT: A large language model for finance," arXiv:2303.17564, 2023.

[24] Z. Ji *et al.*, "Survey of hallucination in natural language generation," *ACM Computing Surveys*, vol. 55, no. 12, pp. 1–38, 2023.

[25] Qwen Team (A. Yang *et al.*), "Qwen2.5 technical report," arXiv:2412.15115, 2024.

[26] J. W. Wilder, *New Concepts in Technical Trading Systems*. Greensboro, NC: Trend Research, 1978.

[27] N. Provos and D. Mazières, "A future-adaptable password scheme," in *Proceedings of the USENIX Annual Technical Conference (FREENIX Track)*, 1999.

[28] M. Jones, J. Bradley and N. Sakimura, "JSON Web Token (JWT)," RFC 7519, Internet Engineering Task Force, 2015.

[29] F. Black and M. Scholes, "The pricing of options and corporate liabilities," *Journal of Political Economy*, vol. 81, no. 3, pp. 637–654, 1973.

[30] R. S. Tsay, *Analysis of Financial Time Series*, 3rd ed. Hoboken, NJ: Wiley, 2010.

[31] T. G. Andersen and T. Bollerslev, "Answering the skeptics: Yes, standard volatility models do provide accurate forecasts," *International Economic Review*, vol. 39, no. 4, pp. 885–905, 1998.

[32] M. B. Garman and M. J. Klass, "On the estimation of security price volatilities from historical data," *The Journal of Business*, vol. 53, no. 1, pp. 67–78, 1980.

[33] G. W. Brier, "Verification of forecasts expressed in terms of probability," *Monthly Weather Review*, vol. 78, no. 1, pp. 1–3, 1950.

[34] OWASP Foundation, "OWASP Top 10: 2021." [Online]. Available: https://owasp.org/Top10/

[35] P. Sironi, *FinTech Innovation: From Robo-Advisors to Goal Based Investing and Gamification*. Chichester: Wiley, 2016.

[36] Securities and Exchange Board of India, *SEBI (Investment Advisers) Regulations, 2013*.

[37] S. Ramírez, "FastAPI documentation." [Online]. Available: https://fastapi.tiangolo.com/

[38] Meta Open Source, "React documentation." [Online]. Available: https://react.dev/

[39] M. Magdon-Ismail and A. F. Atiya, "Maximum drawdown," *Risk Magazine*, vol. 17, no. 10, pp. 99–102, 2004.

[40] Ollama, "Ollama documentation." [Online]. Available: https://github.com/ollama/ollama

<div style="page-break-after: always;"></div>

# APPENDICES

## Appendix A — Complete API Reference

| # | Method | Path | Auth | Description |
|---|---|---|---|---|
| 1 | GET | `/` | – | Root (service information) |
| 2 | GET | `/health` | – | Health check |
| 3 | POST | `/api/auth/register` | – | Register |
| 4 | POST | `/api/auth/login` | – | Login, returns JWT |
| 5 | GET | `/api/auth/me` | JWT | Current user |
| 6 | GET | `/api/users/{user_id}` | JWT (own) | Get user |
| 7 | PUT | `/api/users/{user_id}` | JWT (own) | Update user |
| 8 | POST | `/api/profile/` | JWT | Create financial profile |
| 9 | GET | `/api/profile/` | JWT | Get financial profile |
| 10 | PUT | `/api/profile/` | JWT | Update financial profile |
| 11 | DELETE | `/api/profile/` | JWT | Delete financial profile |
| 12 | POST | `/api/risk/calculate` | JWT | Calculate risk profile |
| 13 | GET | `/api/risk/` | JWT | Get risk profile |
| 14 | DELETE | `/api/risk/` | JWT | Delete risk profile |
| 15 | GET | `/api/risk/explain` | JWT | AI explanation of risk profile (cached) |
| 16 | POST | `/api/recommendation/generate` | JWT | Generate recommendation |
| 17 | GET | `/api/recommendation/` | JWT | Get recommendation |
| 18 | DELETE | `/api/recommendation/` | JWT | Delete recommendation |
| 19 | GET | `/api/recommendation/explain` | JWT | AI explanation of recommendation |
| 20 | POST | `/api/portfolio-analysis/analyze` | JWT | Analyse portfolio series |
| 21 | GET | `/api/portfolio-analysis/latest` | JWT | Latest analysis |
| 22 | POST | `/api/portfolio-analysis/generate-sample-data` | – | Sample portfolio series |
| 23 | GET | `/api/portfolio-analysis/explain` | JWT | AI explanation of analysis |
| 24 | POST | `/api/diversification-analysis/analyze` | JWT | Analyse holdings |
| 25 | GET | `/api/diversification-analysis/latest` | JWT | Latest analysis |
| 26 | GET | `/api/diversification-analysis/history` | JWT | Analysis history |
| 27 | POST | `/api/diversification-analysis/generate-sample-holdings` | – | Sample holdings |
| 28 | DELETE | `/api/diversification-analysis/{analysis_id}` | JWT | Delete analysis |
| 29 | GET | `/api/diversification-analysis/explain` | JWT | AI explanation of diversification |
| 30 | POST | `/api/monte-carlo/simulate` | JWT | Run simulation (`?save=false` to skip saving) |
| 31 | GET | `/api/monte-carlo/simulations` | JWT | List simulations |
| 32 | GET | `/api/monte-carlo/simulations/{simulation_id}` | JWT | Get simulation |
| 33 | DELETE | `/api/monte-carlo/simulations/{simulation_id}` | JWT | Delete simulation |
| 34 | PUT | `/api/monte-carlo/simulations/{simulation_id}` | JWT | Rename or annotate simulation |
| 35 | GET | `/api/monte-carlo/latest` | JWT | Latest simulation |
| 36 | GET | `/api/monte-carlo/explain` | JWT | AI explanation of simulation |
| 37 | POST | `/api/sip/calculate` | JWT | Calculate SIP |
| 38 | POST | `/api/sip/explain` | JWT | AI explanation of SIP |
| 39 | POST | `/api/sip/plans` | JWT | Create SIP plan |
| 40 | GET | `/api/sip/plans` | JWT | List SIP plans |
| 41 | GET | `/api/sip/plans/{plan_id}` | JWT | Get SIP plan |
| 42 | PUT | `/api/sip/plans/{plan_id}` | JWT | Update SIP plan |
| 43 | DELETE | `/api/sip/plans/{plan_id}` | JWT | Delete SIP plan |
| 44 | GET | `/api/market/search` | JWT | Search stocks |
| 45 | GET | `/api/market/stock/{ticker}` | JWT | Stock quote and profile |
| 46 | GET | `/api/market/stock/{ticker}/history` | JWT | Price history |
| 47 | GET | `/api/market/stock/{ticker}/outlook/explain` | JWT | Guarded AI explanation of 21-day outlook |
| 48 | GET | `/api/market/stock/{ticker}/explain` | JWT | AI trend explanation |
| 49 | POST | `/api/ml/predict-volatility` | JWT | Volatility forecast (model or labelled fallback) |
| 50 | GET | `/api/ml/model-info` | JWT | Volatility model metadata |
| 51 | POST | `/api/ml/reload-model` | JWT | Hot-reload volatility model |
| 52 | GET | `/api/ml/features/{ticker}` | JWT | Feature snapshot |
| 53 | GET | `/api/ml/trend-outlook/{ticker}` | JWT | 21-day outlook |
| 54 | GET | `/api/ml/trend-model-info` | JWT | Trend model metadata |
| 55 | POST | `/api/ml/reload-trend-model` | JWT | Hot-reload trend model |
| 56 | GET | `/api/ml/cache-status` | JWT | Price cache and artifact listing |
| 57 | GET | `/api/ollama/health` | – | LLM availability |
| 58 | GET | `/api/ollama/test` | – | LLM test generation |

## Appendix B — Feature Dictionary

| # | Feature | Definition (at date *t*, data up to *t* only) |
|---|---|---|
| 1 | `ret_1d` | Log return $\ln(C_t/C_{t-1})$ |
| 2–6 | `ret_lag_1` … `ret_lag_5` | `ret_1d` lagged 1–5 days |
| 7 | `rv_5` | Annualised std of log returns over 5 days ($\times\sqrt{252}$) |
| 8 | `rv_10` | Same, 10 days |
| 9 | `rv_21` | Same, 21 days (also the naive-persistence forecast) |
| 10 | `rv_63` | Same, 63 days |
| 11 | `rv_ratio_5_21` | `rv_5 / rv_21` |
| 12 | `rv_ratio_21_63` | `rv_21 / rv_63` |
| 13 | `parkinson_21` | $\sqrt{\overline{\ln(H/L)^2}/(4\ln 2)}\cdot\sqrt{252}$ over 21 days |
| 14 | `garman_klass_21` | $\sqrt{\max(0,\overline{0.5\ln(H/L)^2-(2\ln2-1)\ln(C/O)^2})}\cdot\sqrt{252}$ over 21 days |
| 15 | `volume_ratio_20` | Volume ÷ 20-day mean volume |
| 16 | `mom_21` | $\ln(C_t/C_{t-21})$ |
| 17 | `mom_63` | $\ln(C_t/C_{t-63})$ |
| 18 | `rsi_14` | Relative Strength Index, 14 days, simple averages [26] |
| 19 | `drawdown_52w` | $C_t / \max(C_{t-251..t}) - 1$ (≤ 0) |
| 20 | `idx_rv_21` | `rv_21` of the Nifty 50 |
| 21 | `idx_mom_21` | `mom_21` of the Nifty 50 |
| Label | `target_rv_21d` | Annualised realised volatility over days *t*+1 … *t*+21 |
| Label | `target_up_21d` | 1 if $C_{t+21} > C_t$, else 0 (not a feature) |

## Appendix C — Reproducing the Results

| Result | How to reproduce |
|---|---|
| Test results (Chapter 6) | `cd backend && pytest -q` |
| Volatility model evaluation (Section 7.3) | `python scripts/train_volatility_model.py --dry-run --garch` (needs network access on first run for Yahoo Finance; results vary slightly as new data arrives) |
| Model metadata | `GET /api/ml/model-info` |
| Monte Carlo validation (Table 7.5) | `MonteCarloSimulator.run_simulation(100000, 0.12, 0.15, 10, 10000, 0, random_seed=42)` |
| Monte Carlo example (Table 7.6) | Monte Carlo page: ₹1,00,000, ₹5,000/month, 10 years, 12%, "Use ML volatility" for RELIANCE.NS, 10,000 paths, seed 42 |
| Risk and allocation (Tables 7.2–7.3) | Demo profile (age 28, ₹85,000, ₹25,000, 10+ Years, High) → Risk → Recommendations |
| SIP (Table 7.4) | `SIPCalculator.calculate_sip(5000, 12, 10)`; `calculate_required_sip(10_000_000, 12, 15)` |
| Expected range (Table 7.7) | `GET /api/ml/trend-outlook/RELIANCE.NS` (values depend on the date's close and forecast) |
| Latency (Table 7.11) | Run the server without `--reload`, wait for the frontend to compile, then time each endpoint with one warm-up and 5–7 measured calls |

Market-dependent figures (prices, forecasts, outlooks) were captured on **14 October 2026** and will differ on other dates.

---

*End of Report*
