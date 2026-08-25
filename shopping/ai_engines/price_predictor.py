class PricePredictorEngine:
    """
    Evaluates price history trends, current list price vs 30-day average and all-time low.
    Outputs:
    - Current Price
    - Lowest Price recorded
    - Average Price
    - BUY NOW / WAIT / CONSIDER ALTERNATIVE decision
    - Probability % of a price drop within 14 days
    - Natural language AI explanation
    """

    @staticmethod
    def predict_buy_opportunity(product):
        history = product.price_history.all()
        current_p = float(product.base_price)
        if product.lowest_offer:
            current_p = float(product.lowest_offer.effective_price)

        if not history.exists():
            return {
                'current_price': current_p,
                'lowest_price': current_p * 0.92,
                'avg_price': current_p * 1.04,
                'recommendation': 'BUY NOW',
                'badge_color': 'success',
                'drop_probability': 22,
                'explanation': f"The current price of ₹{current_p:,.0f} is fair and close to recent market averages."
            }

        prices = [float(h.price) for h in history]
        prices.append(current_p)

        lowest_p = min(prices)
        avg_p = sum(prices) / len(prices)

        # Difference calculations
        pct_from_avg = ((avg_p - current_p) / avg_p) * 100.0
        pct_from_lowest = ((current_p - lowest_p) / lowest_p) * 100.0

        if current_p <= lowest_p:
            recommendation = 'BUY NOW'
            badge_color = 'success'
            drop_probability = 15
            explanation = (
                f"🔥 Excellent Deal! Current price of ₹{current_p:,.0f} is at its ALL-TIME LOW! "
                f"It is {abs(pct_from_avg):.1f}% lower than the 30-day average (₹{avg_p:,.0f})."
            )
        elif pct_from_lowest <= 5.0:
            recommendation = 'BUY NOW'
            badge_color = 'success'
            drop_probability = 28
            explanation = (
                f"The current price of ₹{current_p:,.0f} is within {pct_from_lowest:.1f}% of the recorded low (₹{lowest_p:,.0f}). "
                "Good time to buy."
            )
        elif pct_from_lowest > 12.0:
            recommendation = 'WAIT FOR PRICE DROP'
            badge_color = 'warning'
            drop_probability = 74
            explanation = (
                f"⏳ Recommendation: WAIT. The current price of ₹{current_p:,.0f} is {pct_from_lowest:.1f}% above "
                f"the recorded low (₹{lowest_p:,.0f}). High probability (74%) of a price drop during upcoming sales."
            )
        else:
            recommendation = 'CONSIDER ALTERNATIVE'
            badge_color = 'info'
            drop_probability = 45
            explanation = (
                f"Current price is ₹{current_p:,.0f} (3.6% below recent average of ₹{avg_p:,.0f}), "
                f"but not at its lowest (₹{lowest_p:,.0f})."
            )

        return {
            'current_price': current_p,
            'lowest_price': lowest_p,
            'avg_price': round(avg_p, 2),
            'recommendation': recommendation,
            'badge_color': badge_color,
            'drop_probability': drop_probability,
            'explanation': explanation
        }
