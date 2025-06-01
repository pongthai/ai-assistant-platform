class OrderManager:
    def __init__(self):
        self.orders = []

    def add_item(self, item):
        self.orders.append(item)
        print(f"➕ เพิ่มเมนู: {item}")

    def summarize_order(self):
        return f"📦 รวมออร์เดอร์: {', '.join(self.orders)}"
