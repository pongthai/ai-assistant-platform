from menu_engine.order_manager import OrderManager
from feedback.feedback_collector import FeedbackCollector

def main():
    order_mgr = OrderManager()
    fb = FeedbackCollector()

    order_mgr.add_item("ข้าวผัดกุ้ง")
    order_mgr.add_item("น้ำมะนาวโซดา")
    print(order_mgr.summarize_order())

    fb.collect("อร่อยมากครับ บริการดี")

if __name__ == "__main__":
    main()
