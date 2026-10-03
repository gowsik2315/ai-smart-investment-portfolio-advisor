# Model Artifacts

Trained volatility model artifacts live here. The API loads
`volatility_model.joblib` from this directory on first use.

`.joblib` files are gitignored, so artifacts stay on the machine that
produced them. What is version-controlled is the code that builds them
and the contract they must satisfy — see
[`../app/ml/README.md`](../app/ml/README.md).

## Expected contents

| File | Purpose |
|---|---|
| `volatility_model.joblib` | The artifact the API serves. Created by `app.ml.model_registry.save_model()`. |

Additional artifacts can sit alongside it under any name; only
`volatility_model.joblib` is loaded automatically. `GET /api/ml/cache-status`
lists every artifact found here along with whether it is still valid
against the current feature definition.

## Do not hand-pickle an estimator into this directory

A bare `joblib.dump(model, ...)` will be rejected at load time. The API
needs the feature order the model was trained on, and that only travels
with the artifact if you save it through `save_model()`. See the
contract document for why this is enforced rather than assumed.
