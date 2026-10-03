"""
Machine Learning package — volatility forecasting.

Scope
-----
This package contains everything the *application* needs in order to
consume a volatility forecast, plus the feature engineering that model
training must reuse:

    config.py          universe, horizon and path constants
    data.py            disk-cached price history loader (yfinance)
    features.py        feature matrix + target construction
    model_registry.py  save/load of the trained artifact and its metadata

Training itself is deliberately NOT here. Fit the model offline (notebook
or script), save it with `model_registry.save_model(...)`, and the API
will pick it up. See `app/ml/README.md` for the artifact contract.

The one rule that matters: build features with `features.build_features`
in training too. If training computes features one way and the API
computes them another, the model will be fed inputs it never saw and the
predictions will be quietly wrong rather than loudly broken.
"""
