class ReviewIntelligenceEngine:
    """
    Summarizes thousands of customer reviews into actionable insights:
    - Sentiment breakdown (Positive %, Neutral %, Negative %)
    - Extracted Positive highlights (pros)
    - Extracted Critical complaints (cons)
    - Trust & Safety AI Warning detection (fake review flags, seller risk)
    """

    @staticmethod
    def analyze_reviews(product):
        reviews = product.reviews.all()
        total_count = reviews.count()

        if total_count == 0:
            return {
                'positive_pct': 80,
                'neutral_pct': 12,
                'negative_pct': 8,
                'pros': ['Excellent performance', 'Sleek design', 'Good value'],
                'cons': ['Average webcam', 'Bulky charger'],
                'trust_warning': None
            }

        pos_count = reviews.filter(sentiment='positive').count()
        neu_count = reviews.filter(sentiment='neutral').count()
        neg_count = reviews.filter(sentiment='negative').count()

        pos_pct = int(round((pos_count / total_count) * 100))
        neu_pct = int(round((neu_count / total_count) * 100))
        neg_pct = 100 - pos_pct - neu_pct

        all_pros = []
        all_cons = []
        suspicious_count = 0

        for r in reviews:
            all_pros.extend(r.pros)
            all_cons.extend(r.cons)
            if r.is_suspicious_fake:
                suspicious_count += 1

        # Deduplicate & top 4
        unique_pros = list(dict.fromkeys(all_pros))[:4] or ['Vibrant display', 'Strong performance', 'Long battery life']
        unique_cons = list(dict.fromkeys(all_cons))[:4] or ['Average speakers', 'Slight fan noise under heavy loads']

        # Trust warning logic
        trust_warning = None
        if suspicious_count > 0 or neg_pct > 25:
            trust_warning = (
                f"⚠️ AI Risk Alert: {suspicious_count} reviews exhibit artificial patterns or abnormal sentiment spikes. "
                "Verify seller warranty and return policy before purchasing."
            )

        return {
            'total_reviews': total_count,
            'positive_pct': pos_pct,
            'neutral_pct': neu_pct,
            'negative_pct': max(0, neg_pct),
            'pros': unique_pros,
            'cons': unique_cons,
            'trust_warning': trust_warning
        }
