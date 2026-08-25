class ComparisonEngine:
    """
    Generates side-by-side spec comparisons, seller matrix, and AI verdict conclusions.
    """

    @staticmethod
    def compare_products(products_list, user_budget=None):
        if not products_list:
            return {}

        # Collect all unique spec keys
        all_spec_keys = set()
        for prod in products_list:
            for spec in prod.specs.all():
                all_spec_keys.add(spec.spec_key)

        all_spec_keys = sorted(list(all_spec_keys))

        # Build comparison grid
        grid = []
        for key in all_spec_keys:
            row = {'spec_key': key, 'values': []}
            for prod in products_list:
                spec_obj = prod.specs.filter(spec_key=key).first()
                row['values'].append(spec_obj.spec_value if spec_obj else "N/A")
            grid.append(row)

        # Calculate best pick based on price & rating
        sorted_by_val = sorted(products_list, key=lambda p: float(p.lowest_offer.effective_price if p.lowest_offer else p.base_price))
        cheapest_prod = sorted_by_val[0]
        highest_rated_prod = sorted(products_list, key=lambda p: p.rating, reverse=True)[0]

        # Generate AI Conclusion
        best_choice = products_list[0]
        savings_text = ""
        if user_budget and user_budget > float(cheapest_prod.base_price):
            diff = user_budget - float(cheapest_prod.base_price)
            savings_text = f" while staying ₹{diff:,.0f} below your budget"

        verdict = (
            f"<strong>{highest_rated_prod.title}</strong> is the top recommendation for performance and build quality with a {highest_rated_prod.rating}★ user rating. "
            f"However, <strong>{cheapest_prod.title}</strong> offers the best value at ₹{cheapest_prod.base_price:,.0f}{savings_text}."
        )

        return {
            'spec_keys': all_spec_keys,
            'grid': grid,
            'cheapest_product': cheapest_prod,
            'highest_rated_product': highest_rated_prod,
            'verdict': verdict
        }
