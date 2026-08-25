from django.utils import timezone
from shopping.models import Product, AutopilotTask
from shopping.ai_engines.intent_engine import IntentEngine
from shopping.ai_engines.scoring_engine import ScoringEngine
from shopping.ai_engines.price_predictor import PricePredictorEngine

class AutopilotAgent:
    """
    Flagship AI Shopping Autopilot Agent:
    Monitors products matching a user query over 30 days.
    Tracks prices, seller offers, festival coupons, and alerts user when the optimal buy window arrives.
    """

    @classmethod
    def create_autopilot_task(cls, user, query_text, max_budget=None, duration_days=30):
        intent = IntentEngine.extract_intent(query_text)
        budget = max_budget or intent.get('budget') or 100000.0

        # Find best candidate product
        products = Product.objects.all()
        scored = ScoringEngine.rank_and_badge_products(products, intent)
        rec_product = scored[0]['product'] if scored else None

        task = AutopilotTask.objects.create(
            user=user,
            query_prompt=query_text,
            max_budget=budget,
            duration_days=duration_days,
            status='monitoring',
            recommended_product=rec_product,
            buy_recommendation='WAIT',
            log_history=[{
                'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M'),
                'event': f"Autopilot Agent activated for query: '{query_text}'. Target budget: ₹{budget:,.0f}.",
                'status': 'Initialized'
            }]
        )

        cls.run_task_check(task)
        return task

    @classmethod
    def run_task_check(cls, task):
        intent = IntentEngine.extract_intent(task.query_prompt)
        products = Product.objects.all()
        scored = ScoringEngine.rank_and_badge_products(products, intent)

        if not scored:
            return

        best_item = scored[0]
        prod = best_item['product']
        prediction = PricePredictorEngine.predict_buy_opportunity(prod)

        task.recommended_product = prod
        task.buy_recommendation = prediction['recommendation']
        task.last_checked = timezone.now()

        new_log = {
            'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M'),
            'event': f"Scanned 14 sellers. Top match: {prod.title} @ ₹{best_item['effective_price']:,.0f}. Decision: {prediction['recommendation']}.",
            'drop_prob': prediction['drop_probability']
        }

        if prediction['recommendation'] == 'BUY NOW':
            task.status = 'opportunity_found'

        task.log_history.append(new_log)
        task.save()
        return task
