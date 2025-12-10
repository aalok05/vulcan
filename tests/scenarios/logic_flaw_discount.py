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
            self.percent_discounts.append(Decimal('0.20'))
        
        self.calculate_total()

    def calculate_total(self):
        subtotal = sum(item['price'] * item['qty'] for item in self.items.values())
        flat_discount = sum(self.discounts)
        percent_total = sum(self.percent_discounts)

        subtotal_after_percent = subtotal * (Decimal('1.00') - percent_total)
        self.total = subtotal_after_percent - flat_discount

        if self.total < Decimal('0.00'):
            self.total = Decimal('0.00')

        return self.total

    def checkout(self, user_wallet):
        if user_wallet.balance >= self.total:
            user_wallet.deduct(self.total)
            return True
        return False