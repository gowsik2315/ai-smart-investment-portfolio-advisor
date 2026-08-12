"""
Monte Carlo Simulation API Routes
Handles portfolio Monte Carlo simulation requests
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
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
    RiskMetrics
)
from app.services.monte_carlo_simulator import MonteCarloSimulator
from app.services.ollama_service import ollama_service
from app.services.ollama_prompts import OllamaPrompts


router = APIRouter()

# Hardcode user_id for testing (remove auth requirement)
TEST_USER_ID = 1


@router.post("/simulate", response_model=MonteCarloSimulationResponse, status_code=status.HTTP_200_OK)
async def run_simulation(
    request: MonteCarloSimulationRequest,
    save: bool = True,
    db: Session = Depends(get_db)
):
    """
    Run Monte Carlo simulation - NO AUTH REQUIRED FOR TESTING
    
    Args:
        request: Simulation parameters
        save: Whether to save simulation to database (default: True)
    """
    try:
        # Run simulation
        simulation_result = MonteCarloSimulator.run_simulation(
            initial_investment=request.initial_investment,
            expected_return=request.expected_return,
            volatility=request.volatility,
            years=request.years,
            num_simulations=request.num_simulations,
            monthly_contribution=request.monthly_contribution
        )
        
        # Calculate risk metrics
        final_values = None  # We'd need to store or recalculate this
        # For now, skip risk metrics in response unless requested separately
        
        # Save to database if requested
        if save:
            db_simulation = MonteCarloSimulation(
                user_id=TEST_USER_ID,
                initial_investment=request.initial_investment,
                expected_return=request.expected_return,
                volatility=request.volatility,
                years=request.years,
                num_simulations=request.num_simulations,
                monthly_contribution=request.monthly_contribution,
                statistics=simulation_result['statistics'],
                scenarios=simulation_result['scenarios'],
                confidence_intervals=simulation_result['confidence_intervals'],
                percentile_paths=simulation_result['percentile_paths'],
                histogram_data=simulation_result['histogram_data'],
                simulation_name=request.simulation_name,
                notes=request.notes
            )
            
            db.add(db_simulation)
            db.commit()
            db.refresh(db_simulation)
        
        # Prepare response
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
            time_periods=simulation_result['time_periods'],
            simulation_paths=simulation_result.get('simulation_paths')
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/simulations", response_model=List[SimulationSummary])
async def get_simulations(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get user's simulation history - NO AUTH REQUIRED"""
    simulations = db.query(MonteCarloSimulation).filter(
        MonteCarloSimulation.user_id == TEST_USER_ID
    ).order_by(MonteCarloSimulation.created_at.desc()).limit(limit).all()
    
    # Convert to summary format
    summaries = []
    for sim in simulations:
        summaries.append(SimulationSummary(
            id=sim.id,
            simulation_name=sim.simulation_name,
            initial_investment=sim.initial_investment,
            years=sim.years,
            num_simulations=sim.num_simulations,
            average_case=sim.scenarios['average_case'],
            created_at=sim.created_at
        ))
    
    return summaries


@router.get("/simulations/{simulation_id}", response_model=MonteCarloSimulationDB)
async def get_simulation(
    simulation_id: int,
    db: Session = Depends(get_db)
):
    """Get specific simulation by ID - NO AUTH REQUIRED"""
    simulation = db.query(MonteCarloSimulation).filter(
        MonteCarloSimulation.id == simulation_id,
        MonteCarloSimulation.user_id == TEST_USER_ID
    ).first()
    
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    return simulation


@router.get("/latest", response_model=MonteCarloSimulationDB)
async def get_latest_simulation(db: Session = Depends(get_db)):
    """Get latest simulation - NO AUTH REQUIRED"""
    simulation = db.query(MonteCarloSimulation).filter(
        MonteCarloSimulation.user_id == TEST_USER_ID
    ).order_by(MonteCarloSimulation.created_at.desc()).first()
    
    if not simulation:
        raise HTTPException(status_code=404, detail="No simulations found")
    
    # Convert to dict to add computed field
    sim_dict = {
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
        "simulation_name": simulation.simulation_name,
        "notes": simulation.notes,
        "ai_explanation": simulation.ai_explanation,
        "created_at": simulation.created_at,
        "updated_at": simulation.updated_at,
        "time_periods": list(range(simulation.years * 12 + 1))  # Calculate time_periods
    }
    
    return sim_dict


@router.delete("/simulations/{simulation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_simulation(
    simulation_id: int,
    db: Session = Depends(get_db)
):
    """Delete a simulation - NO AUTH REQUIRED"""
    simulation = db.query(MonteCarloSimulation).filter(
        MonteCarloSimulation.id == simulation_id,
        MonteCarloSimulation.user_id == TEST_USER_ID
    ).first()
    
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    db.delete(simulation)
    db.commit()
    
    return None


@router.put("/simulations/{simulation_id}", response_model=MonteCarloSimulationDB)
async def update_simulation(
    simulation_id: int,
    simulation_name: str = None,
    notes: str = None,
    db: Session = Depends(get_db)
):
    """Update simulation name and notes - NO AUTH REQUIRED"""
    simulation = db.query(MonteCarloSimulation).filter(
        MonteCarloSimulation.id == simulation_id,
        MonteCarloSimulation.user_id == TEST_USER_ID
    ).first()
    
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    if simulation_name is not None:
        simulation.simulation_name = simulation_name
    
    if notes is not None:
        simulation.notes = notes
    
    db.commit()
    db.refresh(simulation)
    
    return simulation


@router.get("/explain")
async def explain_monte_carlo_simulation(db: Session = Depends(get_db)):
    """
    Get AI-powered explanation of Monte Carlo simulation results (cached)
    
    Returns cached AI explanation if available, otherwise generates new one.
    """
    # Get latest simulation
    simulation = db.query(MonteCarloSimulation).filter(
        MonteCarloSimulation.user_id == TEST_USER_ID
    ).order_by(MonteCarloSimulation.created_at.desc()).first()
    
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Monte Carlo simulation found. Please run a simulation first."
        )
    
    # Check if AI explanation is already cached
    if simulation.ai_explanation:
        return {
            "initial_investment": simulation.initial_investment,
            "years": simulation.years,
            "num_simulations": simulation.num_simulations,
            "mean_value": simulation.statistics['mean_value'],
            "probability_of_profit": simulation.statistics['probability_of_profit'],
            "ai_explanation": simulation.ai_explanation,
            "ai_available": True,
            "cached": True
        }
    
    # Generate new AI explanation if not cached
    stats = simulation.statistics
    scenarios = simulation.scenarios
    ci_95 = simulation.confidence_intervals['ci_95']
    
    prompt = f"""Analyze these Monte Carlo simulation results and provide actionable investment insights:

**Simulation Parameters:**
- Initial Investment: ₹{simulation.initial_investment:,.0f}
- Monthly Contribution: ₹{simulation.monthly_contribution:,.0f}
- Investment Duration: {simulation.years} years
- Expected Annual Return: {simulation.expected_return * 100:.1f}%
- Volatility: {simulation.volatility * 100:.1f}%
- Number of Simulations: {simulation.num_simulations:,}

**Key Results:**
- Mean Final Value: ₹{stats['mean_value']:,.0f}
- Median Final Value: ₹{scenarios['average_case']:,.0f}
- Best Case (95th percentile): ₹{scenarios['best_case']:,.0f}
- Worst Case (5th percentile): ₹{scenarios['worst_case']:,.0f}
- Total Contributions: ₹{stats['total_contributions']:,.0f}

**Probability Metrics:**
- Probability of Profit: {stats['probability_of_profit']:.1f}%
- Probability of Doubling: {stats['probability_of_doubling']:.1f}%

**95% Confidence Interval:**
- Range: ₹{ci_95['lower']:,.0f} to ₹{ci_95['upper']:,.0f}

Please provide:
1. What these results reveal about investment potential and risks
2. How likely are positive outcomes vs losses?
3. Is this investment strategy appropriate based on risk-return profile?
4. Specific recommendations for adjusting parameters (if needed)
5. Key takeaways for decision making

Keep it practical and data-driven. Use markdown formatting."""

    result = await ollama_service.generate_explanation(
        prompt=prompt,
        system_prompt=OllamaPrompts.SYSTEM_FINANCIAL_ADVISOR,
        temperature=0.7
    )
    
    # Cache the AI explanation in database
    if result.get("success", False) and result.get("explanation"):
        simulation.ai_explanation = result["explanation"]
        db.commit()
        db.refresh(simulation)
    
    return {
        "initial_investment": simulation.initial_investment,
        "years": simulation.years,
        "num_simulations": simulation.num_simulations,
        "mean_value": stats['mean_value'],
        "probability_of_profit": stats['probability_of_profit'],
        "ai_explanation": result.get("explanation", "AI explanation unavailable"),
        "ai_available": result.get("success", False),
        "cached": False
    }
