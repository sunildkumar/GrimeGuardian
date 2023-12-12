# encodes the state of the world in a thread-safe manner
from pydantic import BaseModel, Field
from datetime import datetime
import threading


class StateModel(BaseModel):
    sink_state: str = Field(..., pattern="^(YES|NO)$")
    sink_timestamp: datetime


class ThreadSafeState:
    def __init__(self):
        self.state = StateModel(sink_state="NO", sink_timestamp=datetime.now())
        self.lock = threading.Lock()

    def update_state(self, sink_state: str, sink_timestamp: datetime):
        with self.lock:
            self.state.sink_state = sink_state
            self.state.sink_timestamp = sink_timestamp

    def get_state(self) -> StateModel:
        with self.lock:
            return StateModel.parse_obj(self.state.dict().copy())
