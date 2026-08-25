from django.test import TestCase, Client
from django.contrib.auth.models import User
from shopping.models import Product, Category, Brand, Seller, SellerOffer
from shopping.ai_engines.intent_engine import IntentEngine
from shopping.ai_engines.scoring_engine import ScoringEngine
from shopping.ai_engines.price_predictor import PricePredictorEngine
from shopping.ai_engines.budget_bundle_engine import BudgetBundleEngine

class AIShoppingTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        self.brand = Brand.objects.create(name='ASUS', slug='asus')
        self.product = Product.objects.create(
            title='ASUS ROG Zephyrus G16',
            slug='asus-rog-zephyrus-g16',
            category=self.category,
            brand=self.brand,
            description='High performance gaming laptop',
            base_price=78999.00,
            image_url='https://example.com/laptop.jpg'
        )
        self.seller = Seller.objects.create(name='Marketplace Prime')
        self.offer = SellerOffer.objects.create(
            product=self.product,
            seller=self.seller,
            price=78999.00,
            coupon_discount=2000.00
        )

    def test_intent_extraction(self):
        query = "Find me the best laptop under ₹80,000 for programming and gaming"
        intent = IntentEngine.extract_intent(query)
        self.assertEqual(intent['category'], 'Electronics')
        self.assertEqual(intent['budget'], 80000.0)
        self.assertIn('Programming', intent['usage'])
        self.assertIn('Gaming', intent['usage'])

    def test_scoring_engine(self):
        intent = {'budget': 80000.0, 'usage': ['Gaming']}
        score = ScoringEngine.calculate_match_score(self.product, intent)
        self.assertGreater(score, 60.0)

    def test_price_prediction(self):
        prediction = PricePredictorEngine.predict_buy_opportunity(self.product)
        self.assertIn(prediction['recommendation'], ['BUY NOW', 'WAIT FOR PRICE DROP', 'CONSIDER ALTERNATIVE'])

    def test_command_center_view(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_api_chat_endpoint(self):
        response = self.client.post(
            '/api/chat/',
            data='{"message": "Find me a laptop under 80k"}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn('reply', json_data)
