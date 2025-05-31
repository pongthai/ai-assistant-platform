class FeedbackCollector:
    def __init__(self):
        self.feedback = []

    def collect(self, message):
        self.feedback.append(message)
        print(f"📝 รับ Feedback: {message}")
