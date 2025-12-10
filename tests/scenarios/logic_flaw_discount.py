from decimal import Decimal

class Cart:
    def __init__(self):
        self.items = {}
        self.discounts = []
        self.used_coupons = set()
        self.total = Decimal('0.00')

    def add_item(self, item_id, price, quantity):
        qty = int(quantity)
        
        if item_id in self.items:
            self.items[item_id]['qty'] += qty
        else:
            self.items[item_id] = {'price': Decimal(price), 'qty': qty}
        
        self.calculate_total()

    def apply_coupon(self, coupon_code):
        if coupon_code in self.used_coupons:
            return

        if coupon_code == "SAVE10":
            self.discounts.append(Decimal('10.00'))
            self.used_coupons.add(coupon_code)
        elif coupon_code == "PERCENT20":
            self.total = self.total * Decimal('0.8')
            self.used_coupons.add(coupon_code)
        
        self.calculate_total()

    def calculate_total(self):
        subtotal = sum(item['price'] * item['qty'] for item in self.items.values())
        discount_sum = sum(self.discounts)
        self.total = subtotal - discount_sum

        if self.total < Decimal('0.00'):
            self.total = Decimal('0.00')

        return self.total

    def checkout(self, user_wallet):
        if user_wallet.balance >= self.total:
            user_wallet.deduct(self.total)
            return True
        return False