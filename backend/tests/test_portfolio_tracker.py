"""
Tests for the portfolio tracker.

The tracker is the only place in the project that does accounting, and
an accounting error is silent: the number still looks like money. These
tests check it against hand-computed answers and against properties that
must hold whatever the ledger contains.
"""

from datetime import date, timedelta
from types import SimpleNamespace

import pytest

from app.services.portfolio_tracker import (
    PRICE_LAST_TRADE,
    PRICE_LIVE,
    InsufficientHoldingError,
    PortfolioTracker,
)

TODAY = date(2026, 10, 1)


def txn(
    txn_type="Buy",
    name="Reliance Industries",
    symbol="RELIANCE.NS",
    qty=10.0,
    price=1000.0,
    fees=0.0,
    days_ago=0,
    asset_type="Stocks",
    txn_id=None,
):
    """A transaction-shaped object. The tracker never touches the DB."""
    return SimpleNamespace(
        id=txn_id if txn_id is not None else int(days_ago) + 1,
        transaction_type=txn_type,
        asset_type=asset_type,
        asset_name=name,
        asset_symbol=symbol,
        quantity=qty,
        price_per_unit=price,
        total_amount=qty * price,
        fees=fees,
        transaction_date=TODAY - timedelta(days=days_ago),
    )


class TestBuildHoldings:
    def test_single_buy_becomes_one_holding(self):
        result = PortfolioTracker.build_holdings([txn(qty=10, price=1000)])

        assert len(result["holdings"]) == 1
        holding = result["holdings"][0]
        assert holding["quantity"] == 10
        assert holding["cost_basis"] == 10_000
        assert holding["average_cost"] == 1000

    def test_fees_are_part_of_cost_basis(self):
        result = PortfolioTracker.build_holdings([txn(qty=10, price=1000, fees=50)])

        # 10,000 paid for the shares plus 50 to acquire them.
        assert result["holdings"][0]["cost_basis"] == 10_050
        assert result["holdings"][0]["average_cost"] == 1005

    def test_two_buys_average_their_cost(self):
        result = PortfolioTracker.build_holdings([
            txn(qty=10, price=1000, days_ago=10),
            txn(qty=10, price=1200, days_ago=5),
        ])

        holding = result["holdings"][0]
        assert holding["quantity"] == 20
        assert holding["cost_basis"] == 22_000
        assert holding["average_cost"] == 1100

    def test_sip_instalments_count_as_purchases(self):
        result = PortfolioTracker.build_holdings([
            txn(txn_type="SIP", qty=5, price=100, days_ago=2),
            txn(txn_type="SIP", qty=5, price=120, days_ago=1),
        ])

        assert result["holdings"][0]["quantity"] == 10
        assert result["holdings"][0]["cost_basis"] == 1100

    def test_partial_sale_books_profit_at_average_cost(self):
        result = PortfolioTracker.build_holdings([
            txn(qty=10, price=1000, days_ago=10),      # basis 10,000
            txn(txn_type="Sell", qty=4, price=1500, days_ago=1),
        ])

        # Sold 4 at 1,500 = 6,000; those 4 cost 4,000. Profit 2,000.
        assert result["realised_pnl"] == 2000
        holding = result["holdings"][0]
        assert holding["quantity"] == 6
        assert holding["cost_basis"] == 6000          # basis follows the units

    def test_sale_fees_reduce_realised_profit(self):
        result = PortfolioTracker.build_holdings([
            txn(qty=10, price=1000, days_ago=10),
            txn(txn_type="Sell", qty=4, price=1500, fees=100, days_ago=1),
        ])

        assert result["realised_pnl"] == 1900

    def test_selling_everything_closes_the_position(self):
        result = PortfolioTracker.build_holdings([
            txn(qty=10, price=1000, days_ago=10),
            txn(txn_type="Sell", qty=10, price=1100, days_ago=1),
        ])

        assert result["holdings"] == []
        assert len(result["closed_positions"]) == 1
        assert result["realised_pnl"] == 1000

    def test_overselling_is_refused(self):
        with pytest.raises(InsufficientHoldingError):
            PortfolioTracker.build_holdings([
                txn(qty=10, price=1000, days_ago=10),
                txn(txn_type="Sell", qty=11, price=1100, days_ago=1),
            ])

    def test_a_sale_dated_before_its_purchase_is_refused(self):
        # Entered later, but dated earlier: on the day of the sale
        # nothing was held, so the ledger is impossible.
        with pytest.raises(InsufficientHoldingError):
            PortfolioTracker.build_holdings([
                txn(qty=10, price=1000, days_ago=5),
                txn(txn_type="Sell", qty=5, price=1100, days_ago=20),
            ])

    def test_dividend_is_income_not_a_position_change(self):
        result = PortfolioTracker.build_holdings([
            txn(qty=10, price=1000, days_ago=10),
            txn(txn_type="Dividend", qty=1, price=500, days_ago=1),
        ])

        holding = result["holdings"][0]
        assert holding["quantity"] == 10            # unchanged
        assert holding["cost_basis"] == 10_000      # unchanged
        assert result["dividend_income"] == 500
        assert result["realised_pnl"] == 0

    def test_different_assets_stay_separate(self):
        result = PortfolioTracker.build_holdings([
            txn(name="Reliance", symbol="RELIANCE.NS", qty=10, price=1000),
            txn(name="TCS", symbol="TCS.NS", qty=5, price=3000, days_ago=1),
        ])

        assert len(result["holdings"]) == 2

    def test_same_name_different_asset_type_stays_separate(self):
        result = PortfolioTracker.build_holdings([
            txn(name="Gold", symbol=None, asset_type="Gold", qty=10, price=100),
            txn(name="Gold", symbol=None, asset_type="ETF", qty=10, price=100, days_ago=1),
        ])

        assert len(result["holdings"]) == 2

    def test_symbol_matches_case_insensitively(self):
        result = PortfolioTracker.build_holdings([
            txn(symbol="reliance.ns", qty=10, price=1000),
            txn(symbol="RELIANCE.NS", qty=10, price=1000, days_ago=1),
        ])

        assert len(result["holdings"]) == 1
        assert result["holdings"][0]["quantity"] == 20

    def test_unknown_transaction_type_is_rejected(self):
        with pytest.raises(ValueError):
            PortfolioTracker.build_holdings([txn(txn_type="Gift")])

    def test_holdings_are_ordered_by_size(self):
        result = PortfolioTracker.build_holdings([
            txn(name="Small", symbol="S.NS", qty=1, price=100),
            txn(name="Large", symbol="L.NS", qty=100, price=100, days_ago=1),
        ])

        assert [h["asset_name"] for h in result["holdings"]] == ["Large", "Small"]


class TestValueHoldings:
    def test_live_price_drives_market_value_and_profit(self):
        derived = PortfolioTracker.build_holdings([txn(qty=10, price=1000)])
        valued = PortfolioTracker.value_holdings(
            derived["holdings"], {"RELIANCE.NS": 1200.0}
        )

        holding = valued[0]
        assert holding["price_source"] == PRICE_LIVE
        assert holding["market_value"] == 12_000
        assert holding["unrealised_pnl"] == 2000
        assert holding["unrealised_pnl_percent"] == 20.0

    def test_missing_price_falls_back_and_says_so(self):
        derived = PortfolioTracker.build_holdings([txn(qty=10, price=1000)])
        valued = PortfolioTracker.value_holdings(derived["holdings"], {})

        holding = valued[0]
        assert holding["price_source"] == PRICE_LAST_TRADE
        assert holding["current_price"] == 1000
        # Priced from its own purchase, so it cannot show a gain. The
        # label is what tells the caller this is not a real flat return.
        assert holding["unrealised_pnl"] == 0

    def test_holding_without_a_symbol_uses_its_last_price(self):
        derived = PortfolioTracker.build_holdings([
            txn(name="Gold Bar", symbol=None, asset_type="Gold", qty=10, price=6000),
        ])
        valued = PortfolioTracker.value_holdings(derived["holdings"], {"RELIANCE.NS": 1.0})

        assert valued[0]["price_source"] == PRICE_LAST_TRADE
        assert valued[0]["market_value"] == 60_000

    def test_weights_sum_to_one_hundred(self):
        derived = PortfolioTracker.build_holdings([
            txn(name="A", symbol="A.NS", qty=10, price=1000),
            txn(name="B", symbol="B.NS", qty=10, price=3000, days_ago=1),
        ])
        valued = PortfolioTracker.value_holdings(
            derived["holdings"], {"A.NS": 1000.0, "B.NS": 3000.0}
        )

        assert sum(h["weight_percent"] for h in valued) == pytest.approx(100.0, abs=0.05)

    def test_zero_cost_basis_does_not_divide_by_zero(self):
        holdings = [{
            "asset_name": "Free", "asset_symbol": None, "asset_type": "Stocks",
            "quantity": 1.0, "cost_basis": 0.0, "realised_pnl": 0.0,
            "dividend_income": 0.0, "last_price": 0.0, "transaction_count": 1,
            "average_cost": 0.0,
        }]

        assert PortfolioTracker.value_holdings(holdings, {})[0]["unrealised_pnl_percent"] == 0.0


class TestSummarise:
    def test_totals_add_up(self):
        derived = PortfolioTracker.build_holdings([
            txn(qty=10, price=1000, days_ago=20),
            txn(txn_type="Sell", qty=4, price=1500, days_ago=5),
            txn(txn_type="Dividend", qty=1, price=200, days_ago=1),
        ])
        valued = PortfolioTracker.value_holdings(
            derived["holdings"], {"RELIANCE.NS": 1400.0}
        )
        summary = PortfolioTracker.summarise(
            valued, derived["realised_pnl"], derived["dividend_income"]
        )

        assert summary["invested_amount"] == 6000      # 6 units at 1,000
        assert summary["current_value"] == 8400        # 6 units at 1,400
        assert summary["unrealised_pnl"] == 2400
        assert summary["realised_pnl"] == 2000
        assert summary["dividend_income"] == 200
        assert summary["total_gain"] == 4600           # 2,400 + 2,000 + 200
        assert summary["num_holdings"] == 1

    def test_empty_portfolio_is_all_zeros_not_an_error(self):
        summary = PortfolioTracker.summarise([], 0.0, 0.0)

        assert summary["num_holdings"] == 0
        assert summary["invested_amount"] == 0
        assert summary["current_value"] == 0
        assert summary["total_return_percent"] == 0.0

    def test_price_source_counts_are_reported(self):
        derived = PortfolioTracker.build_holdings([
            txn(name="A", symbol="A.NS", qty=1, price=100),
            txn(name="B", symbol="B.NS", qty=1, price=100, days_ago=1),
        ])
        valued = PortfolioTracker.value_holdings(derived["holdings"], {"A.NS": 150.0})
        summary = PortfolioTracker.summarise(valued)

        assert summary["holdings_priced_live"] == 1
        assert summary["holdings_priced_from_last_trade"] == 1


def prices(symbol, pairs):
    """{symbol: {iso date: close}} from (days_ago, close) pairs."""
    return {symbol: {(TODAY - timedelta(days=d)).isoformat(): p for d, p in pairs}}


class TestValueSeries:
    def test_price_movement_drives_the_index(self):
        # Hold 10 units; price 100 -> 110 is a 10% day.
        result = PortfolioTracker.build_value_series(
            [txn(qty=10, price=100, days_ago=2)],
            prices("RELIANCE.NS", [(2, 100.0), (1, 110.0)]),
        )

        values = [p["value"] for p in result["series"]]
        assert values[0] == 100                       # rebased
        assert values[-1] == pytest.approx(110, rel=1e-6)

    def test_series_is_an_index_rebased_to_100_not_a_balance(self):
        # Two portfolios with identical returns but very different sizes
        # must produce the identical index, because the level is a scale
        # and only the shape carries information.
        history = prices("RELIANCE.NS", [(2, 100.0), (1, 125.0)])
        small = PortfolioTracker.build_value_series([txn(qty=1, price=100, days_ago=2)], history)
        large = PortfolioTracker.build_value_series([txn(qty=5000, price=100, days_ago=2)], history)

        assert [p["value"] for p in small["series"]] == [p["value"] for p in large["series"]]
        assert small["series"][0]["value"] == 100

    def test_opening_value_reports_what_the_index_started_from(self):
        result = PortfolioTracker.build_value_series(
            [txn(qty=10, price=100, days_ago=2)],
            prices("RELIANCE.NS", [(2, 100.0), (1, 110.0)]),
        )

        # The index says 100; this says what that 100 was worth in rupees.
        assert result["opening_value"] == 1000

    def test_rebasing_does_not_change_any_risk_metric(self):
        from app.services.portfolio_risk_analyzer import PortfolioRiskAnalyzer

        closes = [100.0, 104.0, 99.0, 103.0, 97.0, 101.0]
        history = prices("RELIANCE.NS", [(len(closes) - i, c) for i, c in enumerate(closes)])
        result = PortfolioTracker.build_value_series(
            [txn(qty=7, price=100, days_ago=len(closes))], history
        )

        indexed = PortfolioRiskAnalyzer.calculate_portfolio_risk(result["series"])
        # The same shape scaled back up to rupees must score identically.
        rupees = PortfolioRiskAnalyzer.calculate_portfolio_risk([
            {"date": p["date"], "value": p["value"] * result["opening_value"] / 100.0}
            for p in result["series"]
        ])

        assert indexed["volatility"] == pytest.approx(rupees["volatility"])
        assert indexed["sharpe_ratio"] == pytest.approx(rupees["sharpe_ratio"])
        assert indexed["max_drawdown"] == pytest.approx(rupees["max_drawdown"])
        assert indexed["total_return"] == pytest.approx(rupees["total_return"])

    def test_a_deposit_is_not_counted_as_a_return(self):
        # Price never moves, but a second buy triples the holding. A raw
        # value series would show a huge "gain"; a time-weighted one is flat.
        result = PortfolioTracker.build_value_series(
            [
                txn(qty=10, price=100, days_ago=3),
                txn(qty=20, price=100, days_ago=2, txn_id=99),
            ],
            prices("RELIANCE.NS", [(3, 100.0), (2, 100.0), (1, 100.0)]),
        )

        values = [p["value"] for p in result["series"]]
        assert values == [pytest.approx(v) for v in [values[0]] * len(values)], values

    def test_a_sale_is_not_counted_as_a_loss(self):
        result = PortfolioTracker.build_value_series(
            [
                txn(qty=10, price=100, days_ago=3),
                txn(txn_type="Sell", qty=8, price=100, days_ago=2, txn_id=99),
            ],
            prices("RELIANCE.NS", [(3, 100.0), (2, 100.0), (1, 100.0)]),
        )

        values = [p["value"] for p in result["series"]]
        assert max(values) == pytest.approx(min(values))

    def test_returns_compound_across_days(self):
        result = PortfolioTracker.build_value_series(
            [txn(qty=1, price=100, days_ago=3)],
            prices("RELIANCE.NS", [(3, 100.0), (2, 110.0), (1, 121.0)]),
        )

        values = [p["value"] for p in result["series"]]
        # +10% then +10% again -> 121, i.e. the index compounds.
        assert values[-1] / values[0] == pytest.approx(1.21, rel=1e-6)

    def test_a_deposit_before_a_rise_does_not_inflate_the_return(self):
        # Buy 1 unit, it doubles; then buy 99 more at the new price and
        # nothing moves. Time-weighted return must stay +100%, not +~100x.
        result = PortfolioTracker.build_value_series(
            [
                txn(qty=1, price=100, days_ago=4),
                txn(qty=99, price=200, days_ago=2, txn_id=99),
            ],
            prices("RELIANCE.NS", [(4, 100.0), (3, 200.0), (2, 200.0), (1, 200.0)]),
        )

        values = [p["value"] for p in result["series"]]
        assert values[-1] / values[0] == pytest.approx(2.0, rel=1e-6)

    def test_dividends_count_towards_the_return(self):
        result = PortfolioTracker.build_value_series(
            [
                txn(qty=10, price=100, days_ago=3),
                txn(txn_type="Dividend", qty=1, price=50, days_ago=2, txn_id=99),
            ],
            prices("RELIANCE.NS", [(3, 100.0), (2, 100.0), (1, 100.0)]),
        )

        values = [p["value"] for p in result["series"]]
        # Price flat, but 50 of income on 1,000 held is a 5% gain.
        assert values[-1] / values[0] == pytest.approx(1.05, rel=1e-6)

    def test_holdings_without_price_history_are_excluded_not_held_flat(self):
        result = PortfolioTracker.build_value_series(
            [
                txn(qty=1, price=100, days_ago=2),
                txn(name="Gold Bar", symbol=None, asset_type="Gold",
                    qty=1000, price=100, days_ago=2, txn_id=99),
            ],
            prices("RELIANCE.NS", [(2, 100.0), (1, 200.0)]),
        )

        values = [p["value"] for p in result["series"]]
        # The priced holding doubled. Carrying the unpriceable one flat
        # would have diluted that to roughly +0.1%.
        assert values[-1] / values[0] == pytest.approx(2.0, rel=1e-6)
        assert result["excluded_holdings"] == ["Gold Bar"]
        assert result["coverage"]["priced_holdings"] == 1
        assert result["coverage"]["total_holdings"] == 2

    def test_coverage_is_reported_by_invested_value(self):
        result = PortfolioTracker.build_value_series(
            [
                txn(qty=1, price=100, days_ago=2),                      # 100
                txn(name="Gold", symbol=None, asset_type="Gold",
                    qty=1, price=900, days_ago=2, txn_id=99),           # 900
            ],
            prices("RELIANCE.NS", [(2, 100.0), (1, 100.0)]),
        )

        assert result["coverage"]["priced_value_percent"] == 10.0

    def test_missing_days_carry_the_last_known_price(self):
        # A gap in the price data must not read as a crash to zero.
        history = {"RELIANCE.NS": {
            (TODAY - timedelta(days=3)).isoformat(): 100.0,
            (TODAY - timedelta(days=1)).isoformat(): 100.0,
        }}
        history["RELIANCE.NS"][(TODAY - timedelta(days=2)).isoformat()] = 0.0

        result = PortfolioTracker.build_value_series(
            [txn(qty=1, price=100, days_ago=3)], history
        )

        assert all(p["value"] > 0 for p in result["series"])

    def test_no_transactions_gives_an_empty_series(self):
        result = PortfolioTracker.build_value_series([], {})

        assert result["series"] == []
        assert result["coverage"]["total_holdings"] == 0

    def test_no_price_history_gives_an_empty_series(self):
        result = PortfolioTracker.build_value_series([txn(qty=1, price=100)], {})

        assert result["series"] == []

    def test_an_unbuildable_series_still_says_what_was_missing(self):
        # Reporting zero holdings here would hide the reason the series
        # is empty, which is exactly what the caller needs to explain.
        result = PortfolioTracker.build_value_series(
            [txn(name="Gold Bar", symbol=None, asset_type="Gold", qty=10, price=6000)],
            {},
        )

        assert result["series"] == []
        assert result["coverage"]["total_holdings"] == 1
        assert result["coverage"]["priced_holdings"] == 0
        assert result["excluded_holdings"] == ["Gold Bar"]

    def test_series_is_chronological_and_shaped_for_the_analyzer(self):
        result = PortfolioTracker.build_value_series(
            [txn(qty=1, price=100, days_ago=3)],
            prices("RELIANCE.NS", [(3, 100.0), (2, 105.0), (1, 102.0)]),
        )

        dates = [p["date"] for p in result["series"]]
        assert dates == sorted(dates)
        assert all(set(p) == {"date", "value"} for p in result["series"])


class TestValueSeriesFeedsTheAnalyzer:
    def test_a_known_volatility_is_recovered_end_to_end(self):
        # A series the analyzer can score: alternating +/- moves give a
        # stable, non-zero volatility, and the pipeline must preserve it.
        from app.services.portfolio_risk_analyzer import PortfolioRiskAnalyzer

        closes = [100.0, 102.0, 100.0, 102.0, 100.0, 102.0, 100.0, 102.0]
        history = prices("RELIANCE.NS", [
            (len(closes) - i, c) for i, c in enumerate(closes)
        ])

        result = PortfolioTracker.build_value_series(
            [txn(qty=10, price=100, days_ago=len(closes))], history
        )
        metrics = PortfolioRiskAnalyzer.calculate_portfolio_risk(result["series"])

        assert metrics["volatility"] > 0
        assert metrics["max_drawdown"] < 0          # it did fall from a peak
        assert metrics["data_points"] == len(result["series"])


class TestSectorResolution:
    def test_sector_comes_from_market_data_when_available(self):
        derived = PortfolioTracker.build_holdings([txn(qty=10, price=1000)])
        valued = PortfolioTracker.value_holdings(
            derived["holdings"], {"RELIANCE.NS": 1200.0}, sectors={"RELIANCE.NS": "Energy"}
        )

        assert valued[0]["sector"] == "Energy"

    def test_equity_without_a_sector_lookup_is_unclassified(self):
        derived = PortfolioTracker.build_holdings([txn(qty=10, price=1000)])
        valued = PortfolioTracker.value_holdings(derived["holdings"], {"RELIANCE.NS": 1200.0})

        assert valued[0]["sector"] == "Unclassified"

    def test_gold_and_bonds_are_their_own_sector(self):
        derived = PortfolioTracker.build_holdings([
            txn(name="SGB 2032", symbol=None, asset_type="Gold", qty=10, price=6000),
            txn(name="Govt Bond", symbol=None, asset_type="Bonds", qty=5, price=1000, days_ago=1),
        ])
        valued = PortfolioTracker.value_holdings(derived["holdings"], {})

        sectors = {h["asset_name"]: h["sector"] for h in valued}
        assert sectors == {"SGB 2032": "Gold", "Govt Bond": "Bonds"}

    def test_a_sector_is_never_invented_for_an_unknown_equity(self):
        # An unlisted stock must not borrow the sector of another symbol.
        derived = PortfolioTracker.build_holdings([
            txn(name="Unlisted Co", symbol=None, asset_type="Stocks", qty=1, price=100),
        ])
        valued = PortfolioTracker.value_holdings(
            derived["holdings"], {}, sectors={"RELIANCE.NS": "Energy"}
        )

        assert valued[0]["sector"] == "Unclassified"

    def test_sector_lookup_is_case_insensitive(self):
        derived = PortfolioTracker.build_holdings([txn(symbol="reliance.ns", qty=1, price=100)])
        valued = PortfolioTracker.value_holdings(
            derived["holdings"], {"RELIANCE.NS": 100.0}, sectors={"reliance.ns": "Energy"}
        )

        assert valued[0]["sector"] == "Energy"


class TestSectorCoverage:
    def test_fully_classified_portfolio_reports_full_coverage(self):
        derived = PortfolioTracker.build_holdings([txn(qty=10, price=1000)])
        valued = PortfolioTracker.value_holdings(
            derived["holdings"], {"RELIANCE.NS": 1000.0}, sectors={"RELIANCE.NS": "Energy"}
        )

        coverage = PortfolioTracker.sector_coverage(valued)
        assert coverage["classified_holdings"] == 1
        assert coverage["unclassified_holdings"] == 0
        assert coverage["classified_value_percent"] == 100.0

    def test_coverage_is_measured_by_value_not_by_count(self):
        # One tiny classified holding and one huge unclassified one:
        # counting holdings would say 50%, which would overstate how
        # much of the portfolio the sector score actually describes.
        derived = PortfolioTracker.build_holdings([
            txn(name="Known", symbol="K.NS", qty=1, price=100),
            txn(name="Unknown", symbol=None, asset_type="Stocks", qty=1, price=900, days_ago=1),
        ])
        valued = PortfolioTracker.value_holdings(
            derived["holdings"], {"K.NS": 100.0}, sectors={"K.NS": "Technology"}
        )

        coverage = PortfolioTracker.sector_coverage(valued)
        assert coverage["classified_holdings"] == 1
        assert coverage["unclassified_holdings"] == 1
        assert coverage["classified_value_percent"] == 10.0
        assert coverage["unclassified_value"] == 900

    def test_empty_portfolio_does_not_divide_by_zero(self):
        coverage = PortfolioTracker.sector_coverage([])

        assert coverage["total_holdings"] == 0
        assert coverage["classified_value_percent"] == 0.0


class TestDiversificationShape:
    def test_holdings_convert_to_the_analyzer_contract(self):
        derived = PortfolioTracker.build_holdings([txn(qty=10, price=1000)])
        valued = PortfolioTracker.value_holdings(derived["holdings"], {"RELIANCE.NS": 1200.0})

        shaped = PortfolioTracker.to_diversification_holdings(valued)

        assert shaped == [{
            "name": "Reliance Industries",
            "value": 12_000,
            "sector": "Unclassified",
            "asset_type": "Stocks",
        }]

    def test_worthless_holdings_are_excluded(self):
        holdings = [{
            "asset_name": "Dead", "asset_type": "Stocks", "market_value": 0.0,
        }]

        assert PortfolioTracker.to_diversification_holdings(holdings) == []


class TestMultiplePortfolios:
    """Holdings are keyed by asset, not by which portfolio they sit in."""

    def test_the_same_stock_in_two_portfolios_is_one_position(self):
        # This is the property that makes an all-portfolios view correct:
        # holding Reliance in two folders is still one concentrated bet.
        result = PortfolioTracker.build_holdings([
            txn(qty=10, price=1000, days_ago=5),
            txn(qty=10, price=1200, days_ago=3, txn_id=99),
        ])

        assert len(result["holdings"]) == 1
        assert result["holdings"][0]["quantity"] == 20
        assert result["holdings"][0]["average_cost"] == 1100

    def test_a_scoped_ledger_yields_only_its_own_holdings(self):
        # The API narrows by portfolio_id before calling the tracker, so
        # scoping is just a shorter ledger; the maths must not change.
        everything = [
            txn(name="A", symbol="A.NS", qty=10, price=100, days_ago=5),
            txn(name="B", symbol="B.NS", qty=5, price=200, days_ago=4, txn_id=98),
        ]
        just_a = [everything[0]]

        combined = PortfolioTracker.build_holdings(everything)
        scoped = PortfolioTracker.build_holdings(just_a)

        assert len(combined["holdings"]) == 2
        assert len(scoped["holdings"]) == 1
        assert scoped["holdings"][0]["asset_name"] == "A"
        # The scoped position is identical to its share of the combined one.
        combined_a = next(h for h in combined["holdings"] if h["asset_name"] == "A")
        assert scoped["holdings"][0]["cost_basis"] == combined_a["cost_basis"]

    def test_weights_are_relative_to_the_scope_analysed(self):
        everything = [
            txn(name="A", symbol="A.NS", qty=10, price=100, days_ago=5),
            txn(name="B", symbol="B.NS", qty=10, price=100, days_ago=4, txn_id=98),
        ]

        combined = PortfolioTracker.value_holdings(
            PortfolioTracker.build_holdings(everything)["holdings"],
            {"A.NS": 100.0, "B.NS": 100.0},
        )
        scoped = PortfolioTracker.value_holdings(
            PortfolioTracker.build_holdings([everything[0]])["holdings"],
            {"A.NS": 100.0},
        )

        assert {h["asset_name"]: h["weight_percent"] for h in combined} == {"A": 50.0, "B": 50.0}
        assert scoped[0]["weight_percent"] == 100.0
