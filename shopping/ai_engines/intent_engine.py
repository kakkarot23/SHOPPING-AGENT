import re

class IntentEngine:
    """
    Converts natural language user prompts into structured shopping requirements:
    - Category
    - Budget (max, min)
    - Brand preference
    - Usage intent (coding, gaming, daily use, fitness, wedding, calls, etc.)
    - Specs requirements (16GB RAM, RTX GPU, lightweight, 15 inch, etc.)
    - Recipient & Occasion (if gift)
    - Delivery requirements
    """

    @staticmethod
    def extract_intent(query_text):
        query_lower = query_text.lower()

        # Category matching
        category = None
        if any(w in query_lower for w in ['laptop', 'notebook', 'macbook']):
            category = 'Electronics'
            sub_type = 'Laptop'
        elif any(w in query_lower for w in ['phone', 'smartphone', 'mobile', 'iphone', 'galaxy']):
            category = 'Electronics'
            sub_type = 'Smartphone'
        elif any(w in query_lower for w in ['headphone', 'earbud', 'earphone', 'audio', 'airpods']):
            category = 'Electronics'
            sub_type = 'Audio'
        elif any(w in query_lower for w in ['watch', 'smartwatch']):
            category = 'Electronics'
            sub_type = 'Smartwatch'
        elif any(w in query_lower for w in ['camera', 'lens', 'mirrorless']):
            category = 'Electronics'
            sub_type = 'Camera'
        elif any(w in query_lower for w in ['shoe', 'sneaker', 'running']):
            category = 'Fashion'
            sub_type = 'Footwear'
        elif any(w in query_lower for w in ['shirt', 'trousers', 'outfit', 'dress']):
            category = 'Fashion'
            sub_type = 'Clothing'
        elif any(w in query_lower for w in ['desk', 'chair', 'furniture', 'wfh setup']):
            category = 'Furniture'
            sub_type = 'Furniture'
        elif any(w in query_lower for w in ['gift', 'present', 'sister', 'brother', 'wedding']):
            category = 'Gift'
            sub_type = 'Gift'
        else:
            category = 'General'
            sub_type = 'General'

        # Budget extraction (e.g. under 80000, under ₹80,000, 80k, 1 lakh, 5000)
        budget = None
        # Match "under 80,000", "under ₹80k", "under 1 lakh"
        lakh_match = re.search(r'(under|below|budget|within|for)\s*(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*(lakh|lakhs|l)', query_lower)
        k_match = re.search(r'(under|below|budget|within|for)\s*(?:₹|rs\.?|inr)?\s*(\d+)\s*(k|thousand)', query_lower)
        num_match = re.search(r'(under|below|budget|within|for|price)\s*(?:₹|rs\.?|inr)?\s*([\d,]{4,8})', query_lower)
        raw_num = re.search(r'(?:₹|rs\.?)\s*([\d,]+)', query_lower)

        if lakh_match:
            budget = float(lakh_match.group(2)) * 100000
        elif k_match:
            budget = float(k_match.group(2)) * 1000
        elif num_match:
            clean_num = num_match.group(2).replace(',', '')
            budget = float(clean_num)
        elif raw_num:
            clean_num = raw_num.group(1).replace(',', '')
            budget = float(clean_num)
        else:
            # Fallback check for numbers like 80000
            standalone_nums = re.findall(r'\b\d{4,6}\b', query_lower)
            if standalone_nums:
                budget = float(standalone_nums[0])

        # Brands extraction
        known_brands = ['apple', 'sony', 'samsung', 'dell', 'lenovo', 'asus', 'hp', 'nike', 'bose', 'sennheiser', 'jbl', 'canon', 'logitech']
        matched_brands = [b.capitalize() for b in known_brands if b in query_lower]

        # Usage / Purpose
        usage_hints = []
        if 'gaming' in query_lower:
            usage_hints.append('Gaming')
        if any(w in query_lower for w in ['coding', 'programming', 'developer']):
            usage_hints.append('Programming')
        if any(w in query_lower for w in ['video editing', 'editing', 'creator', 'design']):
            usage_hints.append('Content Creation')
        if any(w in query_lower for w in ['daily', 'casual', 'office', 'work']):
            usage_hints.append('Daily Use')
        if any(w in query_lower for w in ['running', 'fitness', 'sports', 'gym']):
            usage_hints.append('Fitness')
        if any(w in query_lower for w in ['gift', 'wedding', 'birthday', 'anniversary']):
            usage_hints.append('Gifting')

        # Features / Specs requirements
        specs_required = []
        if 'lightweight' in query_lower or 'thin' in query_lower or 'portable' in query_lower:
            specs_required.append('Lightweight')
        if 'battery' in query_lower:
            specs_required.append('Long Battery Life')
        if '16gb' in query_lower or 'ram' in query_lower:
            specs_required.append('High RAM')
        if 'rtx' in query_lower or 'gpu' in query_lower or 'graphics' in query_lower:
            specs_required.append('Dedicated GPU')
        if 'oled' in query_lower or 'display' in query_lower:
            specs_required.append('Vibrant Display')

        return {
            'original_query': query_text,
            'category': category,
            'sub_type': sub_type,
            'budget': budget,
            'brands': matched_brands,
            'usage': usage_hints,
            'required_features': specs_required,
            'is_gift_query': 'gift' in query_lower or 'present' in query_lower or 'sister' in query_lower or 'brother' in query_lower,
            'is_comparison_query': 'compare' in query_lower or 'vs' in query_lower or 'difference' in query_lower,
            'is_bundle_query': 'setup' in query_lower or 'bundle' in query_lower or 'combo' in query_lower
        }
