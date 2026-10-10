"""
Ollama Prompt Templates
Centralized prompt templates for AI explanations
"""

from typing import Dict


class OllamaPrompts:
    """
    Prompt templates for various financial explanations
    
    Each prompt is designed to:
    - Use existing calculation results as context
    - Generate user-friendly explanations
    - Provide actionable insights
    - Stay within financial advisory guidelines
    """
    
    # System prompts for different contexts
    SYSTEM_FINANCIAL_ADVISOR = """You are a concise financial AI assistant. Explain investment concepts clearly in simple language. Always note this is automated guidance — consult a certified advisor for personalized advice."""

    @staticmethod
    def risk_classification_explanation(
        risk_score: float,
        investor_type: str,
        age: int,
        income: float,
        savings_rate: float,
        horizon: str,
        tolerance: str
    ) -> str:
        """
        Generate prompt for explaining risk classification
        
        Args:
            risk_score: Calculated risk score (0-100)
            investor_type: Conservative, Moderate, or Aggressive
            age: User's age
            income: Monthly income
            savings_rate: Savings rate percentage
            horizon: Investment horizon
            tolerance: Risk tolerance preference
            
        Returns:
            Formatted prompt for Ollama
        """
        return f"""You have been classified as a **{investor_type}** investor with a risk score of **{risk_score}/100**.

Context:
- Age: {age} years
- Monthly Income: ₹{income:,.0f}
- Savings Rate: {savings_rate:.1f}%
- Investment Horizon: {horizon}
- Risk Tolerance: {tolerance}

Please explain:
1. Why this risk classification makes sense for this profile
2. What this means for investment strategy
3. Key factors that influenced the score
4. 2-3 practical investment tips for someone with this risk profile

Keep the explanation under 200 words, use simple language, and be encouraging."""

    @staticmethod
    def portfolio_recommendation_explanation(
        investor_type: str,
        risk_score: float,
        stocks_percent: float,
        mutual_funds_percent: float,
        gold_percent: float,
        emergency_percent: float,
        monthly_savings: float = None
    ) -> str:
        """Generate prompt for explaining portfolio allocation"""
        
        monthly_example = ""
        if monthly_savings:
            monthly_example = f" (₹{monthly_savings * stocks_percent / 100:,.0f} stocks, ₹{monthly_savings * mutual_funds_percent / 100:,.0f} MF, ₹{monthly_savings * gold_percent / 100:,.0f} gold from ₹{monthly_savings:,.0f}/month)"

        return f"""{investor_type} investor (Risk Score {risk_score:.1f}): Stocks {stocks_percent:.0f}%, Mutual Funds {mutual_funds_percent:.0f}%, Gold {gold_percent:.0f}%, Emergency {emergency_percent:.0f}%.{monthly_example}

In 3 short points: (1) why this allocation suits this investor type, (2) role of each asset class, (3) one specific Indian investment product per category. Be concise."""

    @staticmethod
    def sip_explanation(
        monthly_investment: float,
        duration_years: int,
        annual_return: float,
        total_invested: float,
        future_value: float,
        wealth_generated: float
    ) -> str:
        """Generate prompt for explaining SIP calculations"""
        
        return f"""SIP Investment Plan:
- Monthly Investment: ₹{monthly_investment:,.0f}
- Duration: {duration_years} years
- Expected Annual Return: {annual_return:.1f}%

Results:
- Total Amount Invested: ₹{total_invested:,.0f}
- Expected Future Value: ₹{future_value:,.0f}
- Wealth Generated: ₹{wealth_generated:,.0f}

Please explain:
1. How SIP helps in wealth creation over time
2. The power of compounding demonstrated by these numbers
3. Why this is better than lump-sum investing for most people
4. 2-3 practical tips for staying disciplined with SIP investments

Keep under 200 words. Use simple analogies if helpful."""

    @staticmethod
    def stock_trend_explanation(
        ticker: str,
        company_name: str,
        current_price: float,
        price_change_percent: float,
        historical_data: list,
        period: str
    ) -> str:
        """Generate prompt for explaining stock trends"""
        
        # Calculate basic trend info
        if historical_data and len(historical_data) >= 2:
            first_price = historical_data[0].get('close', current_price)
            last_price = historical_data[-1].get('close', current_price)
            overall_change = ((last_price - first_price) / first_price * 100) if first_price > 0 else 0
        else:
            overall_change = price_change_percent
        
        trend_direction = "upward" if overall_change > 0 else "downward" if overall_change < 0 else "sideways"
        
        return f"""Stock Analysis: {company_name} ({ticker})

Current Price: ₹{current_price:,.2f}
Period: {period}
Overall Trend: {overall_change:+.2f}% ({trend_direction})

Please provide:
1. Brief analysis of the price trend
2. What this trend might indicate (without making predictions)
3. Key factors investors should consider
4. Whether this looks like a good time to research further (not buy/sell advice)

Keep under 150 words. Be objective and educational, not predictive."""

    @staticmethod
    def portfolio_risk_analysis_explanation(
        total_value: float,
        expected_return: float,
        risk_score: float,
        volatility: float,
        sharpe_ratio: float = None
    ) -> str:
        """Generate prompt for explaining portfolio risk analysis"""
        
        sharpe_info = f"\n- Sharpe Ratio: {sharpe_ratio:.2f}" if sharpe_ratio else ""
        
        return f"""Portfolio Risk Analysis:
- Total Portfolio Value: ₹{total_value:,.0f}
- Expected Annual Return: {expected_return:.1f}%
- Risk Score: {risk_score:.1f}/100
- Volatility: {volatility:.1f}%{sharpe_info}

Please explain:
1. What these risk metrics mean in simple terms
2. Whether this risk level is appropriate
3. The relationship between expected return and risk
4. 2 ways to optimize the risk-return profile

Keep under 200 words. Be educational and practical."""

    @staticmethod
    def diversification_suggestions(
        diversification_score: float,
        sector_concentration: Dict,
        asset_allocation: Dict,
        areas_of_concern: list = None
    ) -> str:
        """Generate prompt for diversification improvement suggestions"""
        
        sectors_str = "\n".join([f"- {sector}: {pct:.1f}%" for sector, pct in sector_concentration.items()])
        assets_str = "\n".join([f"- {asset}: {pct:.1f}%" for asset, pct in asset_allocation.items()])
        concerns_str = "\n".join([f"- {concern}" for concern in (areas_of_concern or [])])
        
        return f"""Portfolio Diversification Analysis:
- Diversification Score: {diversification_score:.0f}/100

Sector Distribution:
{sectors_str}

Asset Allocation:
{assets_str}

Areas of Concern:
{concerns_str if concerns_str else "- None identified"}

Please provide:
1. Assessment of current diversification level
2. 3-4 specific actionable suggestions to improve diversification
3. Which sectors/assets to consider adding
4. Any over-concentration risks to address

Keep under 200 words. Be specific and actionable."""

    @staticmethod
    def monte_carlo_interpretation(
        investment_amount: float,
        duration_years: int,
        simulations: int,
        median_outcome: float,
        best_case: float,
        worst_case: float,
        probability_positive: float
    ) -> str:
        """Generate prompt for interpreting Monte Carlo simulation results"""
        
        return f"""Monte Carlo Simulation Results:
- Initial Investment: ₹{investment_amount:,.0f}
- Time Period: {duration_years} years
- Number of Simulations: {simulations:,}

Outcomes:
- Median (50th percentile): ₹{median_outcome:,.0f}
- Best Case (95th percentile): ₹{best_case:,.0f}
- Worst Case (5th percentile): ₹{worst_case:,.0f}
- Probability of Positive Returns: {probability_positive:.1f}%

Please explain:
1. What Monte Carlo simulation means in simple terms
2. How to interpret these percentile outcomes
3. What the probability figure tells us
4. How to use this information for planning

Keep under 200 words. Make it understandable for someone new to investing."""

    @staticmethod
    def stock_outlook_explanation(outlook: Dict) -> str:
        """
        Prompt for explaining a Stock Predictor outlook.

        The figures are computed upstream and handed to the model as facts.
        The rules matter more than the wording: a small local model will
        happily call a historical frequency "a prediction", say a stock
        "will" rise, or slip into buy/sell advice, and each of those would
        misstate what the numbers are. Which rules apply depends on whether
        the probability came from a trained model or is just the base rate.
        """
        symbol = '₹' if outlook['ticker'].upper().endswith(('.NS', '.BO')) else '$'
        price = outlook['last_close']
        horizon = outlook['horizon_days']

        p_up = outlook['probability_up'] * 100
        base = outlook['base_rate_up'] * 100
        diff = p_up - base

        trend = outlook['trend']
        bullish = sum(1 for s in trend['signals'] if s['bullish'])
        n_signals = len(trend['signals'])

        end = outlook['expected_range'][-1]

        def span(lo: float, hi: float) -> str:
            return (f"{symbol}{lo:,.2f} to {symbol}{hi:,.2f} "
                    f"({(lo / price - 1) * 100:+.1f}% to {(hi / price - 1) * 100:+.1f}%)")

        is_model = outlook['probability_source'] == 'ml_predicted'
        metrics = outlook.get('model_metrics') or {}
        skill = metrics.get('brier_skill_score')

        if is_model:
            source_line = f"a trained model ({outlook.get('model_version')})"
            rules = [
                "Compare the probability with the historical frequency.",
                "If they differ by less than 3 percentage points, say the model shows "
                "no meaningful edge over what the stock does anyway.",
            ]
            if skill is not None and skill <= 0:
                rules.append(
                    "The model did NOT beat the historical frequency in testing. "
                    "Say so plainly and tell the reader to treat the probability with caution."
                )
        else:
            source_line = "NOT a model: it is only the stock's own historical frequency of rising"
            rules = [
                "This probability is NOT a prediction. No trained model is loaded. "
                "It only says how often this stock rose over 21 trading days in the past. "
                "Say this clearly and do not describe it as a forecast.",
            ]

        vol_source = ("a machine-learning forecast" if outlook['volatility_source'] == 'ml_predicted'
                      else "the last 21 days of actual price swings, not a forecast")
        rsi = trend.get('rsi_14')
        rsi_text = f" RSI is {rsi} ({trend.get('rsi_state')})." if rsi is not None else ""
        rule_text = "\n".join(f"- {r}" for r in rules)

        return f"""You are explaining a stock outlook that software calculated. Use ONLY the facts below. Do not invent any number.

FACTS
- Stock: {outlook['ticker']}, last close {symbol}{price:,.2f} on {outlook['as_of']}
- Current trend (describes the past, not a forecast): {trend['label']}, with {bullish} of {n_signals} signals bullish.{rsi_text}
- Probability of closing higher in {horizon} trading days: {p_up:.1f}%
  - Where it comes from: {source_line}
  - This stock's own historical frequency of rising: {base:.1f}% (difference {diff:+.1f} percentage points)
- Likely range in {horizon} trading days (68% chance): {span(end['lower_68'], end['upper_68'])}
- Wide range (95% chance): {span(end['lower_95'], end['upper_95'])}
- Volatility behind the range: {outlook['volatility'] * 100:.1f}% a year, from {vol_source}

WRITE a plain-language explanation of under 170 words, in four short parts:
1. Trend: what it says about the recent past, and that it is not a forecast.
2. Probability: begin with this exact sentence: "The data shows a {p_up:.1f}% chance of closing higher in {horizon} trading days, compared with {base:.1f}% historically." Then say what that comparison means.
3. Range: how far the price may move. The range says nothing about which direction.
4. One sentence on the main limitation.

RULES
- Never say the stock "will" rise or fall. Say "chance of closing higher", never "will close higher".
- Never tell the reader to buy, sell or hold, and never call anything guaranteed.
{rule_text}"""

    @staticmethod
    def general_financial_query(query: str, context: Dict = None) -> str:
        """Generate prompt for general financial questions"""
        
        context_str = ""
        if context:
            context_str = "\n\nContext:\n" + "\n".join([f"- {k}: {v}" for k, v in context.items()])
        
        return f"""Financial Question: {query}{context_str}

Please provide:
1. Clear, concise answer
2. Relevant examples if helpful
3. Key considerations
4. Disclaimer about consulting certified advisors

Keep under 150 words unless more detail is needed."""
