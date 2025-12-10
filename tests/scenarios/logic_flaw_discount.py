from decimal import Decimal

class Cart:
    def __init__(self):
        self.items = {}
        self.discounts = []
        self.percent_discounts = []
        self.total = Decimal('0.00')

    def add_item(self, item_id, price, quantity):
        qty = int(quantity)
        
        if item_id in self.items:
            self.items[item_id]['qty'] += qty
        else:
            self.items[item_id] = {'price': Decimal(price), 'qty': qty}
        
        self.calculate_total()

    def apply_coupon(self, coupon_code):
        if coupon_code == "SAVE10":
            self.discounts.append(Decimal('10.00'))
        elif coupon_code == "PERCENT20":
            if "PERCENT20" not in self.percent_discounts:
                self.percent_discounts.append("PERCENT20")
        
        self.calculate_total()

    def calculate_total(self):
        subtotal = sum(item['price'] * item['qty'] for item in self.items.values())
        
        discount_sum = sum(self.discounts)
        percent_discount_total = Decimal('0.00')

        if "PERCENT20" in self.percent_discounts:
            percent_discount_total += subtotal * Decimal('0.20')

        self.total = subtotal - discount_sum - percent_discount_total
        return self.total

    def checkout(self, user_wallet):
        if user_wallet.balance >= self.total:
            user_wallet.deduct(self.total)
            return True
        return False