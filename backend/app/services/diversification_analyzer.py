"""
Diversification Analysis Service
Analyzes portfolio diversification based on sector and asset concentration
"""

from typing import Dict, List
import numpy as np


class DiversificationAnalyzer:
    """
    Analyzes portfolio diversification
    Calculates concentration risk and provides recommendations
    """
    
    @staticmethod
    def calculate_diversification_score(holdings: List[Dict]) -> Dict:
        """
        Calculate comprehensive diversification score
        
        Args:
            holdings: List of portfolio holdings
                [{"name": str, "value": float, "sector": str, "asset_type": str}, ...]
            
        Returns:
            dict with diversification_score, sector_concentration, asset_concentration, etc.
        """
        if not holdings or len(holdings) == 0:
            raise ValueError("No holdings provided for diversification analysis")
        
        # Calculate total portfolio value
        total_value = sum(h['value'] for h in holdings)
        
        if total_value <= 0:
            raise ValueError("Total portfolio value must be greater than 0")
        
        # Calculate concentrations
        sector_concentration = DiversificationAnalyzer._calculate_sector_concentration(holdings, total_value)
        asset_concentration = DiversificationAnalyzer._calculate_asset_concentration(holdings, total_value)
        
        # Calculate Herfindahl-Hirschman Index (HHI)
        hhi_score = DiversificationAnalyzer._calculate_hhi(holdings, total_value)
        
        # Calculate number of holdings
        num_holdings = len(holdings)
        
        # Calculate diversification score (0-100)
        diversification_score = DiversificationAnalyzer._calculate_overall_score(
            sector_concentration=sector_concentration,
            asset_concentration=asset_concentration,
            hhi_score=hhi_score,
            num_holdings=num_holdings
        )
        
        # Get warnings and recommendations
        warnings = DiversificationAnalyzer._generate_warnings(
            sector_concentration, asset_concentration, num_holdings
        )
        recommendations = DiversificationAnalyzer._generate_recommendations(
            sector_concentration, asset_concentration, num_holdings, diversification_score
        )
        
        return {
            'diversification_score': round(diversification_score, 2),
            'sector_concentration': sector_concentration,
            'asset_concentration': asset_concentration,
            'hhi_score': round(hhi_score, 4),
            'num_holdings': num_holdings,
            'total_value': round(total_value, 2),
            'warnings': warnings,
            'recommendations': recommendations
        }
    
    @staticmethod
    def _calculate_sector_concentration(holdings: List[Dict], total_value: float) -> Dict:
        """Calculate sector-wise concentration"""
        sector_values = {}
        
        for holding in holdings:
            sector = holding.get('sector', 'Unknown')
            value = holding.get('value', 0)
            
            if sector in sector_values:
                sector_values[sector] += value
            else:
                sector_values[sector] = value
        
        # Calculate percentages
        sector_percentages = {
            sector: round((value / total_value) * 100, 2)
            for sector, value in sector_values.items()
        }
        
        # Find top sector
        top_sector = max(sector_percentages.items(), key=lambda x: x[1])
        
        return {
            'sectors': sector_percentages,
            'top_sector': top_sector[0],
            'top_sector_percentage': top_sector[1],
            'num_sectors': len(sector_percentages)
        }
    
    @staticmethod
    def _calculate_asset_concentration(holdings: List[Dict], total_value: float) -> Dict:
        """Calculate asset type concentration"""
        asset_values = {}
        
        for holding in holdings:
            asset_type = holding.get('asset_type', 'Unknown')
            value = holding.get('value', 0)
            
            if asset_type in asset_values:
                asset_values[asset_type] += value
            else:
                asset_values[asset_type] = value
        
        # Calculate percentages
        asset_percentages = {
            asset_type: round((value / total_value) * 100, 2)
            for asset_type, value in asset_values.items()
        }
        
        # Find top asset
        top_asset = max(asset_percentages.items(), key=lambda x: x[1])
        
        return {
            'assets': asset_percentages,
            'top_asset': top_asset[0],
            'top_asset_percentage': top_asset[1],
            'num_asset_types': len(asset_percentages)
        }
    
    @staticmethod
    def _calculate_hhi(holdings: List[Dict], total_value: float) -> float:
        """
        Calculate Herfindahl-Hirschman Index (HHI)
        Measures market concentration
        Range: 0 (perfect diversification) to 10000 (complete concentration)
        """
        percentages = [(h['value'] / total_value) * 100 for h in holdings]
        hhi = sum(p ** 2 for p in percentages)
        return hhi / 100  # Normalize to 0-100 scale
    
    @staticmethod
    def _calculate_overall_score(
        sector_concentration: Dict,
        asset_concentration: Dict,
        hhi_score: float,
        num_holdings: int
    ) -> float:
        """
        Calculate overall diversification score (0-100)
        Higher score = Better diversification
        
        Weights:
        - Sector concentration: 35%
        - Asset concentration: 30%
        - HHI score: 20%
        - Number of holdings: 15%
        """
        # Sector score (lower concentration = higher score)
        top_sector_pct = sector_concentration['top_sector_percentage']
        if top_sector_pct > 50:
            sector_score = 0
        elif top_sector_pct > 40:
            sector_score = 30
        elif top_sector_pct > 30:
            sector_score = 60
        else:
            sector_score = 100
        
        # Asset score (lower concentration = higher score)
        top_asset_pct = asset_concentration['top_asset_percentage']
        if top_asset_pct > 70:
            asset_score = 0
        elif top_asset_pct > 60:
            asset_score = 40
        elif top_asset_pct > 50:
            asset_score = 70
        else:
            asset_score = 100
        
        # HHI score (lower HHI = higher score)
        # HHI ranges from 0 to 100 in our normalized scale
        hhi_score_normalized = max(0, 100 - hhi_score)
        
        # Number of holdings score
        if num_holdings >= 15:
            holdings_score = 100
        elif num_holdings >= 10:
            holdings_score = 80
        elif num_holdings >= 7:
            holdings_score = 60
        elif num_holdings >= 5:
            holdings_score = 40
        else:
            holdings_score = 20
        
        # Weighted average
        overall_score = (
            sector_score * 0.35 +
            asset_score * 0.30 +
            hhi_score_normalized * 0.20 +
            holdings_score * 0.15
        )
        
        return overall_score
    
    @staticmethod
    def _generate_warnings(
        sector_concentration: Dict,
        asset_concentration: Dict,
        num_holdings: int
    ) -> List[str]:
        """Generate warnings based on concentration levels"""
        warnings = []
        
        # Sector concentration warnings
        top_sector_pct = sector_concentration['top_sector_percentage']
        if top_sector_pct > 50:
            warnings.append(
                f"⚠️ High sector concentration: {sector_concentration['top_sector']} "
                f"represents {top_sector_pct}% of portfolio"
            )
        elif top_sector_pct > 40:
            warnings.append(
                f"⚠️ Moderate sector concentration in {sector_concentration['top_sector']} ({top_sector_pct}%)"
            )
        
        # Asset concentration warnings
        top_asset_pct = asset_concentration['top_asset_percentage']
        if top_asset_pct > 70:
            warnings.append(
                f"⚠️ High asset concentration: {asset_concentration['top_asset']} "
                f"represents {top_asset_pct}% of portfolio"
            )
        elif top_asset_pct > 60:
            warnings.append(
                f"⚠️ Moderate asset concentration in {asset_concentration['top_asset']} ({top_asset_pct}%)"
            )
        
        # Number of holdings warnings
        if num_holdings < 5:
            warnings.append(
                f"⚠️ Very low number of holdings ({num_holdings}). Consider adding more positions."
            )
        elif num_holdings < 10:
            warnings.append(
                f"⚠️ Limited diversification with only {num_holdings} holdings"
            )
        
        if not warnings:
            warnings.append("✅ No major concentration risks detected")
        
        return warnings
    
    @staticmethod
    def _generate_recommendations(
        sector_concentration: Dict,
        asset_concentration: Dict,
        num_holdings: int,
        diversification_score: float
    ) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Score-based recommendations
        if diversification_score >= 80:
            recommendations.append("✅ Excellent diversification! Maintain current allocation strategy")
        elif diversification_score >= 60:
            recommendations.append("👍 Good diversification with room for minor improvements")
        elif diversification_score >= 40:
            recommendations.append("⚡ Moderate diversification - consider rebalancing")
        else:
            recommendations.append("🚨 Poor diversification - immediate action recommended")
        
        # Sector-specific recommendations
        top_sector_pct = sector_concentration['top_sector_percentage']
        if top_sector_pct > 40:
            recommendations.append(
                f"Reduce {sector_concentration['top_sector']} exposure from {top_sector_pct}% to under 30%"
            )
            recommendations.append(
                f"Diversify into {sector_concentration['num_sectors']} or more sectors"
            )
        
        # Asset-specific recommendations
        top_asset_pct = asset_concentration['top_asset_percentage']
        if top_asset_pct > 60:
            recommendations.append(
                f"Reduce {asset_concentration['top_asset']} allocation from {top_asset_pct}% to 50-60%"
            )
            recommendations.append(
                "Consider adding alternative asset classes (bonds, gold, REITs)"
            )
        
        # Holdings recommendations
        if num_holdings < 10:
            target_holdings = 10 if num_holdings < 5 else 12
            recommendations.append(
                f"Increase number of holdings from {num_holdings} to at least {target_holdings}"
            )
            recommendations.append(
                "Add holdings in underrepresented sectors"
            )
        
        return recommendations
    
    @staticmethod
    def generate_sample_holdings(portfolio_value: float = 1000000, diversified: bool = True) -> List[Dict]:
        """
        Generate sample portfolio holdings for testing
        
        Args:
            portfolio_value: Total portfolio value
            diversified: True for well-diversified, False for concentrated
        """
        if diversified:
            # Well-diversified portfolio
            holdings = [
                {"name": "Reliance Industries", "value": portfolio_value * 0.08, "sector": "Energy", "asset_type": "Stocks"},
                {"name": "TCS", "value": portfolio_value * 0.08, "sector": "Technology", "asset_type": "Stocks"},
                {"name": "HDFC Bank", "value": portfolio_value * 0.07, "sector": "Banking", "asset_type": "Stocks"},
                {"name": "Infosys", "value": portfolio_value * 0.07, "sector": "Technology", "asset_type": "Stocks"},
                {"name": "ICICI Bank", "value": portfolio_value * 0.06, "sector": "Banking", "asset_type": "Stocks"},
                {"name": "SBI", "value": portfolio_value * 0.05, "sector": "Banking", "asset_type": "Stocks"},
                {"name": "Bharti Airtel", "value": portfolio_value * 0.05, "sector": "Telecom", "asset_type": "Stocks"},
                {"name": "ITC", "value": portfolio_value * 0.04, "sector": "FMCG", "asset_type": "Stocks"},
                {"name": "HDFC Mutual Fund", "value": portfolio_value * 0.15, "sector": "Diversified", "asset_type": "Mutual Funds"},
                {"name": "SBI Mutual Fund", "value": portfolio_value * 0.10, "sector": "Diversified", "asset_type": "Mutual Funds"},
                {"name": "Government Bonds", "value": portfolio_value * 0.15, "sector": "Fixed Income", "asset_type": "Bonds"},
                {"name": "Gold ETF", "value": portfolio_value * 0.10, "sector": "Commodities", "asset_type": "Gold"},
            ]
        else:
            # Concentrated portfolio (poor diversification)
            holdings = [
                {"name": "Tech Stock A", "value": portfolio_value * 0.40, "sector": "Technology", "asset_type": "Stocks"},
                {"name": "Tech Stock B", "value": portfolio_value * 0.30, "sector": "Technology", "asset_type": "Stocks"},
                {"name": "Tech Stock C", "value": portfolio_value * 0.20, "sector": "Technology", "asset_type": "Stocks"},
                {"name": "Bank Stock", "value": portfolio_value * 0.10, "sector": "Banking", "asset_type": "Stocks"},
            ]
        
        return holdings
