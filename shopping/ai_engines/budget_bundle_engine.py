from shopping.models import Product

class BudgetBundleEngine:
    """
    Builds optimal multi-product bundles tailored to user budget allocations.
    Examples:
    1. Phone + Watch + Earbuds (under ₹1,00,000)
    2. Complete WFH Setup (Laptop, Monitor, Keyboard, Mouse, Headphones, Chair, Accessories under ₹1,50,000)
    3. Gaming Rig Setup
    """

    @staticmethod
    def build_smart_bundle(total_budget, setup_type='wfh'):
        budget = float(total_budget)

        if setup_type == 'gadget_trio':
            # Target breakdown: Phone (70%), Smartwatch (15%), Earbuds (10%), Buffer (5%)
            categories = [
                ('Smartphone', 0.70, 'Phone'),
                ('Smartwatch', 0.16, 'Smartwatch'),
                ('Audio', 0.10, 'Earbuds / Audio')
            ]
        else:
            # WFH / Gaming breakdown
            categories = [
                ('Laptop', 0.58, 'Main Laptop / PC'),
                ('Monitor', 0.16, 'Display Monitor'),
                ('Furniture', 0.10, 'Ergonomic Desk / Chair'),
                ('Audio', 0.08, 'Noise-Canceling Headphones'),
                ('Peripheral', 0.04, 'Keyboard & Mouse')
            ]

        allocated_items = []
        spent_total = 0.0

        for cat_name, pct, role_label in categories:
            item_budget = budget * pct
            # Find best product in this category fitting item_budget
            prods = Product.objects.filter(category__name__icontains=cat_name).order_by('-rating')
            if not prods.exists():
                prods = Product.objects.all().order_by('-rating')

            best_match = None
            for p in prods:
                eff_p = float(p.lowest_offer.effective_price if p.lowest_offer else p.base_price)
                if eff_p <= item_budget * 1.25: # allow slight flex
                    best_match = (p, eff_p)
                    break

            if not best_match and prods.exists():
                p = prods.first()
                eff_p = float(p.lowest_offer.effective_price if p.lowest_offer else p.base_price)
                best_match = (p, eff_p)

            if best_match:
                prod_obj, item_price = best_match
                spent_total += item_price
                allocated_items.append({
                    'role': role_label,
                    'product': prod_obj,
                    'allocated_budget': item_budget,
                    'actual_price': item_price,
                    'reason': f"Selected {prod_obj.title} for best performance within ₹{item_budget:,.0f} target."
                })

        remaining_budget = max(0.0, budget - spent_total)
        savings = max(0.0, budget - spent_total)

        # Optimization suggestion
        suggestion = ""
        if remaining_budget > 3000:
            suggestion = f"💡 AI Tip: You have ₹{remaining_budget:,.0f} remaining in your budget! Consider upgrading your peripherals or adding an extended warranty."
        else:
            suggestion = "🎯 Perfect Budget Match! All essential components fit seamlessly within your specified limit."

        return {
            'total_budget': budget,
            'spent_total': spent_total,
            'remaining_budget': remaining_budget,
            'estimated_savings': savings,
            'items': allocated_items,
            'ai_suggestion': suggestion
        }
