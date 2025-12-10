from decimal import Decimal

class Cart:
    def __init__(self):
        self.items = {}
        self.discounts = []
        self.total = Decimal('0.00')

    def add_item(self, item_id, price, quantity):
        # Vulnerability 1: Business Logic Flaw - Negative Quantity
        # Users can add negative quantity to reduce total or get money back
        # Semgrep won't catch this without custom rules; it's valid code.
        qty = int(quantity)
        
        if item_id in self.items:
            self.items[item_id]['qty'] += qty
        else:
            self.items[item_id] = {'price': Decimal(price), 'qty': qty}
        
        self.calculate_total()

    def apply_coupon(self, coupon_code):
        # Vulnerability 2: Business Logic Flaw - Coupon Stacking
        # No check if coupon was already applied or if it stacks
        # A user can call this loop 100 times to get 100x discount
        if coupon_code == "SAVE10":
            self.discounts.append(Decimal('10.00'))
        elif coupon_code == "PERCENT20":
            # Vulnerability 3: Logic Flaw - applying % to current total iteratively
            # If applied multiple times, it decays total exponentially
            self.total = self.total * Decimal('0.8') 
        
        self.calculate_total()

    def calculate_total(self):
        subtotal = sum(item['price'] * item['qty'] for item in self.items.values())
        
        # Apply fixed discounts
        discount_sum = sum(self.discounts)
        self.total = subtotal - discount_sum
        
        # Vulnerability 4: Logic Flaw - Total can be negative
        # If discounts > subtotal, we effectively pay the user
        return self.total

    def checkout(self, user_wallet):
        if user_wallet.balance >= self.total:
            user_wallet.deduct(self.total)
            return True
        return False
