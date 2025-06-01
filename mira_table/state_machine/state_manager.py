from enum import Enum

class State(Enum):
    START = "start"
    GREETING = "greeting"
    LISTENING = "listening"
    CONFIRMING = "confirming"
    THANK_YOU = "thank_you"
    END = "end"

class StateManager:
    def __init__(self):
        self.state = State.START

    def set_state(self, new_state: State):
        print(f"🔁 [State] {self.state.value} → {new_state.value}")
        self.state = new_state

    def get_state(self) -> State:
        return self.state