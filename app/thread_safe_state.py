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
    last_dirty_sink_notification_timestamp: datetime | None  # timestamp of when the last notification was sent to alert that the sink is dirty

    kitchen_state: str = Field(
        ..., pattern="^(YES|NO)$"
    )  # current state of the kitchen, YES means it is occupied, NO means it is empty
    kitchen_state_timestamp: datetime  # timestamp of when the last update to the kitchen state was made
    kitchen_state_iq_id: str  # the image query id of the image that was used to update the kitchen state
    last_occupied_kitchen_notification_timestamp: datetime | None  # timestamp of when the last notification was sent to alert that the kitchen is occupied


class ThreadSafeState:
    def __init__(self):
        self.state = StateModel(
            sink_state="NO",
            sink_state_timestamp=datetime.now(),
            sink_state_iq_id="",
            last_sink_clean_timestamp=datetime.now(),
            last_dirty_sink_notification_timestamp=None,
            kitchen_state="NO",
            kitchen_state_timestamp=datetime.now(),
            kitchen_state_iq_id="",
            last_occupied_kitchen_notification_timestamp=None,
        )
        self.lock = threading.Lock()

    def update_state(
        self,
        *,
        sink_state: str | None = None,
        sink_state_timestamp: datetime | None = None,
        sink_state_iq_id: str | None = None,
        last_sink_clean_timestamp: datetime | None = None,
        last_dirty_sink_notification_timestamp: datetime | None = None,
        kitchen_state: str | None = None,
        kitchen_state_timestamp: datetime | None = None,
        kitchen_state_iq_id: str | None = None,
        last_occupied_kitchen_notification_timestamp: datetime | None = None,
    ):
        with self.lock:
            if sink_state is not None:
                self.state.sink_state = sink_state
            if sink_state_timestamp is not None:
                self.state.sink_state_timestamp = sink_state_timestamp
            if last_sink_clean_timestamp is not None:
                self.state.last_sink_clean_timestamp = last_sink_clean_timestamp
            if last_dirty_sink_notification_timestamp is not None:
                self.state.last_dirty_sink_notification_timestamp = (
                    last_dirty_sink_notification_timestamp
                )
            if sink_state_iq_id is not None:
                self.state.sink_state_iq_id = sink_state_iq_id
            if kitchen_state is not None:
                self.state.kitchen_state = kitchen_state
            if kitchen_state_timestamp is not None:
                self.state.kitchen_state_timestamp = kitchen_state_timestamp
            if kitchen_state_iq_id is not None:
                self.state.kitchen_state_iq_id = kitchen_state_iq_id
            if last_occupied_kitchen_notification_timestamp is not None:
                self.state.last_occupied_kitchen_notification_timestamp = (
                    last_occupied_kitchen_notification_timestamp
                )

    def get_state(self) -> StateModel:
        with self.lock:
            return StateModel.model_validate(self.state.model_dump().copy())
