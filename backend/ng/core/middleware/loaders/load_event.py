from typing import Callable
from ._util import generate_loader_decorator, LoaderType

def load_event(source : LoaderType, input_key="event_id", output_key="event") -> Callable:
    return generate_loader_decorator(
        source=source,
        model_name="Event",
        input_key=input_key,
        output_key=output_key
    )
