class Order:
    def __init__(self, id, user, amount, status="PENDING"):
        self.id = id
        self.user = user
        self.amount = amount
        self.status = status

# Mock Database
orders_db = {
    101: Order(101, "alice", 50.00, "PENDING"),
    102: Order(102, "bob", 120.00, "SHIPPED"),
    103: Order(103, "charlie", 20.00, "DELIVERED")
}

def refund_user(user, amount):
    print(f"Refunding ${amount} to {user}...")
    return True

def cancel_order(order_id, user_requesting):
    order = orders_db.get(order_id)
    if not order:
        return {"error": "Order not found"}, 404

    if order.user != user_requesting:
        return {"error": "Unauthorized"}, 403

    if order.status != "PENDING":
        return {"error": "Cannot cancel non-pending order"}, 400

    refund_success = refund_user(order.user, order.amount)
    if refund_success:
        order.status = "CANCELLED"
        return {"message": "Order cancelled and refunded"}, 200

    return {"error": "Refund failed"}, 500