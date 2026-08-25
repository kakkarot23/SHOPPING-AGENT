class ScoringEngine:
    """
    Ranks products on a 0-100 match scale using multi-criteria weighted scoring:
    - Performance / Spec alignment (25%)
    - Price & Value score relative to budget (20%)
    - Customer Rating & Reviews score (20%)
    - Feature match score (15%)
    - Seller & Reliability score (10%)
    - Warranty & Returns (5%)
    - Delivery speed (5%)
    """

    @staticmethod
    def calculate_match_score(product, intent, user_weights=None):
        weights = user_weights or {
            'performance': 25,
            'price': 20,
            'reviews': 20,
            'features': 15,
            'reliability': 10,
            'warranty': 5,
            'delivery': 5
        }

        # Normalize weights
        total_w = sum(weights.values()) or 100
        w_perf = weights.get('performance', 25) / total_w
        w_price = weights.get('price', 20) / total_w
        w_rev = weights.get('reviews', 20) / total_w
        w_feat = weights.get('features', 15) / total_w
        w_rel = weights.get('reliability', 10) / total_w
        w_warr = weights.get('warranty', 5) / total_w
        w_del = weights.get('delivery', 5) / total_w

        # 1. Performance / Spec score
        perf_score = 80.0
        if product.rating > 4.5:
            perf_score += 15
        elif product.rating > 4.0:
            perf_score += 10

        # 2. Price Score
        price_score = 85.0
        budget = intent.get('budget')
        effective_p = float(product.base_price)
        if product.lowest_offer:
            effective_p = float(product.lowest_offer.effective_price)

        if budget and budget > 0:
            if effective_p <= budget:
                savings_pct = (budget - effective_p) / budget
                price_score = 75.0 + min(savings_pct * 40.0, 25.0)
            else:
                over_pct = (effective_p - budget) / budget
                price_score = max(10.0, 75.0 - (over_pct * 100.0))

        # 3. Review score
        rev_score = (product.rating / 5.0) * 100.0

        # 4. Feature match score
        feat_score = 70.0
        required_features = intent.get('required_features', [])
        if required_features:
            matched_count = 0
            for feat in required_features:
                if any(feat.lower() in str(s.spec_value).lower() or feat.lower() in str(s.spec_key).lower() for s in product.specs.all()):
                    matched_count += 1
                elif any(feat.lower() in tag.lower() for tag in product.usage_tags):
                    matched_count += 1
            feat_score = 50.0 + (matched_count / len(required_features)) * 50.0

        # Brand bonus
        preferred_brands = intent.get('brands', [])
        brand_bonus = 5.0 if product.brand.name.capitalize() in preferred_brands else 0.0

        # 5. Reliability score
        rel_score = float(product.brand.sustainability_rating)

        # 6. Warranty score
        warr_score = min(100.0, product.warranty_months * 4.0 + product.return_window_days * 2.0)

        # 7. Delivery score
        del_score = 90.0
        if product.lowest_offer:
            del_days = product.lowest_offer.delivery_days
            del_score = max(50.0, 100.0 - (del_days * 10.0))

        raw_score = (
            (perf_score * w_perf) +
            (price_score * w_price) +
            (rev_score * w_rev) +
            (feat_score * w_feat) +
            (rel_score * w_rel) +
            (warr_score * w_warr) +
            (del_score * w_del) +
            brand_bonus
        )

        final_score = round(min(99.0, max(60.0, raw_score)), 1)
        return final_score

    @classmethod
    def rank_and_badge_products(cls, products_list, intent, user_weights=None):
        scored_items = []
        for prod in products_list:
            score = cls.calculate_match_score(prod, intent, user_weights)
            scored_items.append((prod, score))

        # Sort descending by score
        scored_items.sort(key=lambda x: x[1], reverse=True)

        results = []
        for idx, (prod, score) in enumerate(scored_items):
            badge = None
            badge_class = ""
            if idx == 0:
                badge = "🥇 Best Overall"
                badge_class = "badge-overall"
            elif idx == 1:
                badge = "🥈 Best Value"
                badge_class = "badge-value"
            elif idx == 2:
                badge = "🥉 Best Performance"
                badge_class = "badge-performance"
            elif idx == 3:
                badge = "Best Budget"
                badge_class = "badge-budget"

            results.append({
                'product': prod,
                'score': score,
                'badge': badge,
                'badge_class': badge_class,
                'effective_price': prod.lowest_offer.effective_price if prod.lowest_offer else prod.base_price
            })

        return results
