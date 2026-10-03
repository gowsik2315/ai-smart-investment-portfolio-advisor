"""
Monte Carlo Simulation API Routes
Handles portfolio Monte Carlo simulation requests.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.monte_carlo_simulation import MonteCarloSimulation
from app.schemas.monte_carlo_simulation import (
    MonteCarloSimulationRequest,
    MonteCarloSimulationResponse,
    MonteCarloSimulationDB,
    SimulationSummary,
    Statistics,
    Scenarios,
    ConfidenceIntervals,
    HistogramData,
    PercentilePaths,
    RiskMetrics,
    VolatilityProvenance,
)
from app.ml.data import PriceDataError
from app.services.monte_carlo_simulator import MonteCarloSimulator
from app.services.ml_prediction_service import (
    SOURCE_MANUAL,
    volatility_prediction_service,
)
from app.services.ollama_service import ollama_service
from app.services.ollama_prompts import OllamaPrompts

logger = logging.getLogger(__name__)

router = APIRouter()


def _resolve_volatility(request: MonteCarloSimulationRequest) -> VolatilityProvenance:
    """
    Decide which sigma this run uses, and record where it came from.

    When `use_predicted_volatility` is set, the forecasting service is
    consulted. That service has its own internal fallback to trailing
    realised volatility, so the only failure reaching here is a total
    absence of price data — at which point a caller-supplied volatility
    is used if there is one, and otherwise the request fails.
    """
    if not request.use_predicted_volatility:
        return VolatilityProvenance(
            source=SOURCE_MANUAL,
            volatility_used=request.volatility,
        )

    try:
        forecast = volatility_prediction_service.get_forecast(request.ticker)
    except PriceDataError as exc:
        if request.volatility is not None:
            logger.warning(
                "Volatility forecast unavailable for %s (%s); using the "
                "supplied value instead", request.ticker, exc,
            )
            return VolatilityProvenance(
                source=SOURCE_MANUAL,
                volatility_used=request.volatility,
                ticker=request.ticker,
                fallback_reason=f"Forecast unavailable, used supplied volatility: {exc}",
            )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                f"Could not forecast volatility for {request.ticker} and no "
                f"fallback volatility was supplied: {exc}"
            ),
        )

    return VolatilityProvenance(
        source=forecast.source,
        volatility_used=forecast.volatility,
        predicted_volatility=forecast.predicted_volatility,
        model_version=forecast.model_version,
        ticker=forecast.ticker,
        fallback_reason=forecast.fallback_reason,
    )


@router.post("/simulate", response_model=MonteCarloSimulationResponse, status_code=status.HTTP_200_OK)
async def run_simulation(
    request: MonteCarloSimulationRequest,
    save: bool = True,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """
    Run a Monte Carlo simulation.

    Sigma comes either from the request or, when
    `use_predicted_volatility` is set, from the volatility forecasting
    model. The response's `volatility_provenance` always states which.

    Args:
        request: Simulation parameters
        save: Persist the run (default True). When False no row is
            created, and `/explain` cannot describe this run — see the
            note on that endpoint.
    """
    provenance = _resolve_volatility(request)

    try:
        simulation_result = MonteCarloSimulator.run_simulation(
            initial_investment=request.initial_investment,
            expected_return=request.expected_return,
            volatility=provenance.volatility_used,
            years=request.years,
            num_simulations=request.num_simulations,
            monthly_contribution=request.monthly_contribution,
            random_seed=request.random_seed,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    simulation_id: Optional[int] = None

    if save:
        try:
            db_simulation = MonteCarloSimulation(
                user_id=current_user_id,
                initial_investment=request.initial_investment,
                expected_return=request.expected_return,
                volatility=provenance.volatility_used,
                years=request.years,
                num_simulations=request.num_simulations,
                monthly_contribution=request.monthly_contribution,
                volatility_source=provenance.source,
                predicted_volatility=provenance.predicted_volatility,
                volatility_model_version=provenance.model_version,
                volatility_ticker=provenance.ticker,
                random_seed=request.random_seed,
                statistics=simulation_result['statistics'],
                scenarios=simulation_result['scenarios'],
                confidence_intervals=simulation_result['confidence_intervals'],
                percentile_paths=simulation_result['percentile_paths'],
                histogram_data=simulation_result['histogram_data'],
                risk_metrics=simulation_result['risk_metrics'],
                simulation_name=request.simulation_name,
                notes=request.notes,
                ai_explanation=None,  # fresh run, no explanation yet
            )

            db.add(db_simulation)
            db.commit()
            db.refresh(db_simulation)
            simulation_id = db_simulation.id
        except Exception as exc:  # noqa: BLE001
            db.rollback()
            logger.exception("Failed to persist Monte Carlo simulation")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Simulation ran but could not be saved: {exc}",
            )

    return MonteCarloSimulationResponse(
        initial_investment=simulation_result['initial_investment'],
        expected_return=simulation_result['expected_return'],
        volatility=simulation_result['volatility'],
        years=simulation_result['years'],
        num_simulations=simulation_result['num_simulations'],
        monthly_contribution=simulation_result['monthly_contribution'],
        statistics=Statistics(**simulation_result['statistics']),
        scenarios=Scenarios(**simulation_result['scenarios']),
        confidence_intervals=ConfidenceIntervals(**simulation_result['confidence_intervals']),
        histogram_data=HistogramData(**simulation_result['histogram_data']),
        percentile_paths=PercentilePaths(**simulation_result['percentile_paths']),
        risk_metrics=RiskMetrics(**simulation_result['risk_metrics']),
        time_periods=simulation_result['time_periods'],
        simulation_paths=simulation_result.get('simulation_paths'),
        volatility_provenance=provenance,
        random_seed=request.random_seed,
        simulation_id=simulation_id,
    )


@router.get("/simulations", response_model=List[SimulationSummary])
async def get_simulations(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """List the current user's saved simulations, newest first."""
    simulations = db.query(MonteCarloSimulation).filter(
        MonteCarloSimulation.user_id == current_user_id
    ).order_by(MonteCarloSimulation.created_at.desc()).limit(limit).all()

    return [
        SimulationSummary(
            id=sim.id,
            simulation_name=sim.simulation_name,
            initial_investment=sim.initial_investment,
            years=sim.years,
            num_simulations=sim.num_simulations,
            average_case=sim.scenarios['average_case'],
            volatility_source=sim.volatility_source,
            created_at=sim.created_at,
        )
        for sim in simulations
    ]


def _serialise(simulation: MonteCarloSimulation) -> dict:
    """Shape a stored row for MonteCarloSimulationDB, adding time_periods."""
    return {
        "id": simulation.id,
        "user_id": simulation.user_id,
        "initial_investment": simulation.initial_investment,
        "expected_return": simulation.expected_return,
        "volatility": simulation.volatility,
        "years": simulation.years,
        "num_simulations": simulation.num_simulations,
        "monthly_contribution": simulation.monthly_contribution,
        "statistics": simulation.statistics,
        "scenarios": simulation.scenarios,
        "confidence_intervals": simulation.confidence_intervals,
        "percentile_paths": simulation.percentile_paths,
        "histogram_data": simulation.histogram_data,
        "risk_metrics": simulation.risk_metrics,
        "volatility_source": simulation.volatility_source,
        "predicted_volatility": simulation.predicted_volatility,
        "volatility_model_version": simulation.volatility_model_version,
        "volatility_ticker": simulation.volatility_ticker,
        "random_seed": simulation.random_seed,
        "simulation_name": simulation.simulation_name,
        "notes": simulation.notes,
        "ai_explanation": simulation.ai_explanation,
        "created_at": simulation.created_at,
        "updated_at": simulation.updated_at,
        # X-axis for the chart; derived rather than stored
        "time_periods": list(range(simulation.years * 12 + 1)),
    }


@router.get("/simulations/{simulation_id}", response_model=MonteCarloSimulationDB)
async def get_simulation(
    simulation_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """Fetch one of the current user's simulations by id."""
    simulation = db.query(MonteCarloSimulation).filter(
        MonteCarloSimulation.id == simulation_id,
        MonteCarloSimulation.user_id == current_user_id
    ).first()

    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")

    return _serialise(simulation)


@router.get("/latest", response_model=MonteCarloSimulationDB)
async def get_latest_simulation(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """Fetch the current user's most recent simulation."""
    simulation = db.query(MonteCarloSimulation).filter(
        MonteCarloSimulation.user_id == current_user_id
    ).order_by(MonteCarloSimulation.created_at.desc()).first()

    if not simulation:
        raise HTTPException(status_code=404, detail="No simulations found")

    return _serialise(simulation)


@router.delete("/simulations/{simulation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_simulation(
    simulation_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """Delete one of the current user's simulations."""
    simulation = db.query(MonteCarloSimulation).filter(
        MonteCarloSimulation.id == simulation_id,
        MonteCarloSimulation.user_id == current_user_id
    ).first()

    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")

    db.delete(simulation)
    db.commit()

    return None


@router.put("/simulations/{simulation_id}", response_model=MonteCarloSimulationDB)
async def update_simulation(
    simulation_id: int,
    simulation_name: Optional[str] = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """Rename a simulation or update its notes."""
    simulation = db.query(MonteCarloSimulation).filter(
        MonteCarloSimulation.id == simulation_id,
        MonteCarloSimulation.user_id == current_user_id
    ).first()

    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")

    if simulation_name is not None:
        simulation.simulation_name = simulation_name

    if notes is not None:
        simulation.notes = notes

    db.commit()
    db.refresh(simulation)

    return _serialise(simulation)


def _build_explanation_prompt(simulation: MonteCarloSimulation) -> str:
    """
    Compose the Ollama prompt for a stored simulation.

    Two deliberate choices here:

    1. The median leads, not the mean. Terminal values are lognormal, so
       at high volatility the sample mean is dominated by a handful of
       enormous paths and badly overstates the typical outcome. The
       median is the figure a user should anchor on, and that matters
       more once sigma comes from a model and can be far above the 15%
       someone would type by hand.

    2. The volatility's provenance is stated. The model must not describe
       trailing realised volatility as a forecast, so it is told which it
       is looking at.
    """
    stats = simulation.statistics
    scenarios = simulation.scenarios
    ci_95 = simulation.confidence_intervals['ci_95']
    risk = simulation.risk_metrics or {}

    source_labels = {
        "ml_predicted": (
            f"forecast by the volatility model "
            f"({simulation.volatility_model_version or 'unversioned'})"
            f"{f' for {simulation.volatility_ticker}' if simulation.volatility_ticker else ''}"
        ),
        "historical_fallback": (
            "trailing 21-day realised volatility (the volatility model was "
            "unavailable, so this is a historical measure and NOT a forecast)"
        ),
        "manual": "entered manually by the user",
    }
    volatility_origin = source_labels.get(
        simulation.volatility_source or "manual", "of unrecorded origin"
    )

    risk_block = ""
    if risk:
        risk_block = f"""
**Downside Risk:**
- Value at Risk (5th percentile): Rs {risk.get('var_5_percent', 0):,.0f}
- Shortfall vs contributions at VaR: Rs {risk.get('var_loss_amount', 0):,.0f} ({risk.get('var_loss_percent', 0):.1f}%)
- Conditional VaR (mean of worst 5%): Rs {risk.get('cvar_5_percent', 0):,.0f}
"""

    return f"""Analyse these Monte Carlo simulation results and provide actionable investment insights.

**Simulation Parameters:**
- Initial Investment: Rs {simulation.initial_investment:,.0f}
- Monthly Contribution: Rs {simulation.monthly_contribution:,.0f}
- Investment Duration: {simulation.years} years
- Expected Annual Return: {simulation.expected_return * 100:.1f}%
- Annual Volatility: {simulation.volatility * 100:.1f}% — {volatility_origin}
- Number of Simulations: {simulation.num_simulations:,}
- Model: geometric Brownian motion, monthly steps

**Key Results (anchor on the MEDIAN — the distribution is right-skewed, so the mean overstates the typical outcome):**
- Median Final Value: Rs {scenarios['average_case']:,.0f}
- Mean Final Value: Rs {stats['mean_value']:,.0f}
- Best Case (95th percentile): Rs {scenarios['best_case']:,.0f}
- Worst Case (5th percentile): Rs {scenarios['worst_case']:,.0f}
- Total Contributions: Rs {stats['total_contributions']:,.0f}

**Probability Metrics:**
- Probability of Profit: {stats['probability_of_profit']:.1f}%
- Probability of Doubling: {stats['probability_of_doubling']:.1f}%
{risk_block}
**95% Confidence Interval:**
- Range: Rs {ci_95['lower']:,.0f} to Rs {ci_95['upper']:,.0f}

Please provide:
1. What these results reveal about investment potential and risks
2. How likely are positive outcomes vs losses?
3. Is this strategy appropriate given the risk-return profile?
4. Specific recommendations for adjusting parameters, if needed
5. Key takeaways for decision making

Keep it practical and data-driven. Use markdown formatting."""


@router.get("/explain")
async def explain_monte_carlo_simulation(
    simulation_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """
    AI-generated explanation of a simulation's results (cached per run).

    Args:
        simulation_id: Which run to explain. Defaults to the most recent
            saved run.

    Pass `simulation_id` from the `/simulate` response whenever you have
    it. Relying on "latest" is only correct if that run was saved: with
    `save=false` no row is written, and the explanation returned would
    describe an earlier simulation with different parameters while
    appearing to describe the one just run.

    The explanation is cached on the row, so repeat calls are instant and
    each run keeps its own explanation.
    """
    query = db.query(MonteCarloSimulation).filter(
        MonteCarloSimulation.user_id == current_user_id
    )

    if simulation_id is not None:
        simulation = query.filter(MonteCarloSimulation.id == simulation_id).first()
        if not simulation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Simulation {simulation_id} not found",
            )
    else:
        simulation = query.order_by(MonteCarloSimulation.created_at.desc()).first()
        if not simulation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Monte Carlo simulation found. Please run a simulation first.",
            )

    def payload(explanation: str, available: bool, cached: bool) -> dict:
        return {
            "simulation_id": simulation.id,
            "initial_investment": simulation.initial_investment,
            "years": simulation.years,
            "num_simulations": simulation.num_simulations,
            "median_value": simulation.scenarios.get('average_case'),
            "mean_value": simulation.statistics['mean_value'],
            "probability_of_profit": simulation.statistics['probability_of_profit'],
            "volatility": simulation.volatility,
            "volatility_source": simulation.volatility_source,
            "ai_explanation": explanation,
            "ai_available": available,
            "cached": cached,
        }

    if simulation.ai_explanation:
        return payload(simulation.ai_explanation, True, True)

    result = await ollama_service.generate_explanation(
        prompt=_build_explanation_prompt(simulation),
        system_prompt=OllamaPrompts.SYSTEM_FINANCIAL_ADVISOR,
        temperature=0.7,
    )

    if result.get("success", False) and result.get("explanation"):
        simulation.ai_explanation = result["explanation"]
        db.commit()
        db.refresh(simulation)

    return payload(
        result.get("explanation", "AI explanation unavailable"),
        result.get("success", False),
        False,
    )
