class Order:
    def __init__(self, id, user, amount, status="PENDING"):
        self.id = id
        self.user = user
        self.amount = amount
        self.status = status

# Mock Database
orders_db = {
    101: Order(101, "alice", 50.00, "PENDING"),
    102: Order(102, "bob", 120.00, "SHIPPED"), # Item is in transit
    103: Order(103, "charlie", 20.00, "DELIVERED")
}

def refund_user(user, amount):
    print(f"Refunding ${amount} to {user}...")
    # Real logic would verify transaction ID, etc.
    return True

def cancel_order(order_id, user_requesting):
    order = orders_db.get(order_id)
    if not order:
        return {"error": "Order not found"}, 404

    if order.user != user_requesting:
        return {"error": "Unauthorized"}, 403

    # Vulnerability: Business Logic Flaw (State Machine Bypass)
    # The requirement is: "Orders can only be cancelled if they are PENDING."
    # The code below explicitly checks for 'DELIVERED' to block it,
    # but forgets that 'SHIPPED' orders also shouldn't be cancellable 
    # (since the item is already physically with the carrier).
    
    if order.status == "DELIVERED":
        return {"error": "Cannot cancel delivered order"}, 400
    
    # Flaw: A 'SHIPPED' order passes the check above.
    # Result: User gets a refund AND keeps the item.
    
    refund_success = refund_user(order.user, order.amount)
    if refund_success:
        order.status = "CANCELLED"
        return {"message": "Order cancelled and refunded"}, 200
    
    return {"error": "Refund failed"}, 500
