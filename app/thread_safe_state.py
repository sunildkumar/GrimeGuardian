# encodes the state of the world in a thread-safe manner
from pydantic import BaseModel, Field
from datetime import datetime
import threading


class StateModel(BaseModel):
    sink_state: str = Field(
        ..., pattern="^(YES|NO)$"
    )  # current state of the sink, YES means it is dirty, NO means it is clean
    sink_state_timestamp: datetime  # timestamp of when the last update to the sink state was made
    last_sink_clean_timestamp: datetime  # timestamp of when the sink was last clean (when the state was last set to NO)


class ThreadSafeState:
    def __init__(self):
        self.state = StateModel(
            sink_state="NO",
            sink_state_timestamp=datetime.now(),
            last_sink_clean_timestamp=datetime.now(),
        )
        self.lock = threading.Lock()

    def update_state(
        self,
        *,
        sink_state: str | None = None,
        sink_state_timestamp: datetime | None = None,
        last_sink_clean_timestamp: datetime | None = None
    ):
        with self.lock:
            if sink_state is not None:
                self.state.sink_state = sink_state
            if sink_state_timestamp is not None:
                self.state.sink_state_timestamp = sink_state_timestamp
            if last_sink_clean_timestamp is not None:
                self.state.last_sink_clean_timestamp = last_sink_clean_timestamp

    def get_state(self) -> StateModel:
        with self.lock:
            return StateModel.parse_obj(self.state.dict().copy())
