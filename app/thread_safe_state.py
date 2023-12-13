# encodes the state of the world in a thread-safe manner
from pydantic import BaseModel, Field
from datetime import datetime
import threading


class StateModel(BaseModel):
    sink_state: str = Field(
        ..., pattern="^(YES|NO)$"
    )  # current state of the sink, YES means it is dirty, NO means it is clean
    sink_state_timestamp: datetime  # timestamp of when the last update to the sink state was made
    sink_state_iq_id: str  # the image query id of the image that was used to update the sink state
    last_sink_clean_timestamp: datetime  # timestamp of when the sink was last clean (when the state was last set to NO)
    last_notification_timestamp: datetime  # timestamp of when the last notification was sent


class ThreadSafeState:
    def __init__(self):
        self.state = StateModel(
            sink_state="NO",
            sink_state_timestamp=datetime.now(),
            last_sink_clean_timestamp=datetime.now(),
            last_notification_timestamp=datetime.now(),
            sink_state_iq_id="",
        )
        self.lock = threading.Lock()

    def update_state(
        self,
        *,
        sink_state: str | None = None,
        sink_state_timestamp: datetime | None = None,
        last_sink_clean_timestamp: datetime | None = None,
        last_notification_timestamp: datetime | None = None,
        sink_state_iq_id: str | None = None,
    ):
        with self.lock:
            if sink_state is not None:
                self.state.sink_state = sink_state
            if sink_state_timestamp is not None:
                self.state.sink_state_timestamp = sink_state_timestamp
            if last_sink_clean_timestamp is not None:
                self.state.last_sink_clean_timestamp = last_sink_clean_timestamp
            if last_notification_timestamp is not None:
                self.state.last_notification_timestamp = last_notification_timestamp
            if sink_state_iq_id is not None:
                self.state.sink_state_iq_id = sink_state_iq_id

    def get_state(self) -> StateModel:
        with self.lock:
            return StateModel.parse_obj(self.state.dict().copy())
